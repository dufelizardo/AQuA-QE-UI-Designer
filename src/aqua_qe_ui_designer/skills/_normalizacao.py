"""Normalização defensiva de respostas do LLM (via `complete_json`) que deveriam ser uma
string simples ou uma lista de strings simples, mas às vezes chegam em formatos variados:
uma lista de objetos (`{"nome": ..., "descricao": ...}`), um dict de chave -> detalhe
aninhado, um dict de chave -> string vazia (cada item como chave, não como valor), ou até uma
STRING cujo próprio conteúdo é um repr Python de dict/list (aspas simples) em vez de um
objeto/array JSON de verdade.

Esse exato problema (em formas ligeiramente diferentes a cada vez) já apareceu em várias
skills do agente irmão AQuA-QE UX Designer (`identify_user_flows`, `design_information_architecture`,
`review_accessibility`, `review_ux_specification`, `extract_ux_context` — duas vezes). Este
módulo concentra a defesa genérica num único lugar, para que toda skill deste agente que pede
"uma lista de itens" ou "várias coisas como uma única string" a um LLM reutilize a mesma
lógica testada, em vez de reimplementá-la a cada arquivo novo (ver `tests/test_normalizacao.py`
para os casos de regressão cobertos).
"""

import ast


def item_para_string(item, campos_prioritarios: tuple[str, ...] = ()) -> str:
    """Defesa contra o LLM devolver um objeto em vez de string para um item de uma lista.

    `campos_prioritarios` define, em ordem, quais chaves tentar primeiro como "rótulo"
    principal do item (ex.: `("nome", "passo")`) — o restante do objeto (se houver algo em
    outra chave com valor) é anexado como complemento, separado por ": ".
    """
    if isinstance(item, dict):
        for campo in campos_prioritarios:
            valor = item.get(campo)
            if valor:
                complemento = next(
                    (
                        v
                        for k, v in item.items()
                        if k != campo and k not in campos_prioritarios and v
                    ),
                    "",
                )
                return f"{valor}: {complemento}" if complemento else str(valor)
        valor = next((v for v in item.values() if v), "")
        return str(valor) if valor else str(item)
    return str(item)


def valor_para_string(valor) -> str:
    """Achata um valor (string, lista ou dict aninhado) numa string legível de uma linha —
    usado para os valores dentro de um dict devolvido no lugar de uma string (ver
    `dict_para_texto`)."""
    if isinstance(valor, dict):
        partes = [f"{chave}: {valor_para_string(sub)}" for chave, sub in valor.items() if sub]
        return "; ".join(partes)
    if isinstance(valor, list):
        return ", ".join(item_para_string(item) for item in valor)
    return str(valor) if valor else ""


def dict_para_texto(dicionario: dict) -> str:
    """Achata um dict devolvido no lugar de uma string — cobre um dict de nome->detalhes (com
    sub-dict de descrição/estados/etc.), um dict de item->'' (cada item como chave, valor
    vazio), e um dict com uma única chave-artefato mapeando para a lista de itens de verdade
    (ex.: `{"caminho": [...]}`) — nesse último caso a chave não tem valor de rótulo real, então
    é descartada."""
    if len(dicionario) == 1:
        ((unica_chave, unico_valor),) = dicionario.items()
        if isinstance(unico_valor, list):
            return "\n".join(item_para_string(item) for item in unico_valor)
    linhas = []
    for chave, valor in dicionario.items():
        detalhe = valor_para_string(valor)
        linhas.append(f"{chave}: {detalhe}" if detalhe else str(chave))
    return "\n".join(linhas)


def string_como_estrutura(valor: str):
    """Defesa contra o LLM devolver uma string cujo próprio conteúdo é um repr de dict/list
    Python (aspas simples) em vez de prosa — nesse caso as checagens de
    isinstance(dict)/isinstance(list) não disparam sozinhas, porque o campo já chega como
    string."""
    texto = valor.strip()
    if not texto or texto[0] not in "{[":
        return None
    try:
        estrutura = ast.literal_eval(texto)
    except (ValueError, SyntaxError):
        return None
    return estrutura if isinstance(estrutura, (dict, list)) else None


def texto_ou_lista(valor, campos_prioritarios: tuple[str, ...] = ("nome",)) -> str:
    """Defesa contra o LLM devolver uma lista, um dict, ou uma string com repr de dict/list
    embutido em vez de uma única string de prosa. `campos_prioritarios` (padrão `("nome",)`,
    o rótulo mais comum visto ao vivo) é repassado para `item_para_string` quando a lista
    contém objetos em vez de strings simples."""
    if isinstance(valor, dict):
        return dict_para_texto(valor)
    if isinstance(valor, list):
        return "\n".join(item_para_string(item, campos_prioritarios) for item in valor)
    if isinstance(valor, str):
        estrutura = string_como_estrutura(valor)
        if estrutura is not None:
            return texto_ou_lista(estrutura, campos_prioritarios)
    return valor or ""


def lista_de_strings(valor, campos_prioritarios: tuple[str, ...] = ()) -> list[str]:
    """Normaliza um valor que deveria ser `list[str]` — cobre o LLM devolvendo uma lista de
    objetos, uma única string, um dict, ou uma string com repr de dict/list embutido."""
    if isinstance(valor, list):
        return [item_para_string(item, campos_prioritarios) for item in valor]
    if isinstance(valor, dict):
        return [linha for linha in dict_para_texto(valor).split("\n") if linha]
    if isinstance(valor, str):
        estrutura = string_como_estrutura(valor)
        if estrutura is not None:
            return lista_de_strings(estrutura, campos_prioritarios)
        return [valor] if valor else []
    return []


def lista_de_dicts(valor, campo_rotulo: str) -> list[dict]:
    """Normaliza um valor que deveria ser uma lista de objetos (dicts) com mais de um campo
    nomeado por item (ex.: `{"estado": "...", "contexto": "..."}`, quando uma única string por
    item não é suficiente para capturar a estrutura pedida ao LLM) — cobre o LLM devolvendo uma
    lista de objetos de verdade, uma lista de strings simples (cada uma vira um dict com
    `campo_rotulo` só), um dict de chave->detalhe aninhado, ou uma string com repr de dict/list
    embutido. `campo_rotulo` é a chave usada como rótulo principal do item quando ele chega como
    string simples em vez de objeto (ex.: `"estado"`, `"nome"`)."""
    if isinstance(valor, str):
        estrutura = string_como_estrutura(valor)
        if estrutura is not None:
            return lista_de_dicts(estrutura, campo_rotulo)
        return [{campo_rotulo: valor}] if valor else []
    if isinstance(valor, dict):
        itens = []
        for chave, detalhe in valor.items():
            if isinstance(detalhe, dict):
                item = dict(detalhe)
                item.setdefault(campo_rotulo, chave)
                itens.append(item)
            else:
                itens.append({campo_rotulo: chave})
        return itens
    if isinstance(valor, list):
        itens = []
        for item in valor:
            if isinstance(item, dict):
                itens.append(item)
            elif isinstance(item, str):
                if not item:
                    continue
                estrutura = string_como_estrutura(item)
                itens.append(estrutura if isinstance(estrutura, dict) else {campo_rotulo: item})
            elif item:
                itens.append({campo_rotulo: str(item)})
        return itens
    return []
