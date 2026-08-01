from ..models import ComponentSpec, UIScreen
from ..services.llm_service import complete_json
from ._material_design_3_catalog import COMPONENTES_MD3
from ._material_symbols_catalog import ICONES_MATERIAL_SYMBOLS
from ._normalizacao import item_para_string, lista_de_dicts, lista_de_strings

_SYSTEM = (
    "Você identifica, para cada tela de navegação descrita em uma UX Specification, quais "
    "componentes do catálogo fechado do Material Design 3 (listado abaixo) se aplicam, com "
    "variante/tamanho/ícone/notas de configuração quando fizerem sentido para o componente, e a "
    "hierarquia visual da tela (do elemento mais importante ao menos importante — ex.: "
    '["Título", "Descrição", "Botão principal", "Links auxiliares"]). Nunca cite um componente '
    "fora do catálogo informado (GR-UI-1, o guardrail mais importante deste agente) — se nenhum "
    "componente do catálogo se aplicar claramente a uma tela, deixe a lista de componentes dessa "
    "tela menor, nunca invente um nome de componente novo. Variante/tamanho devem usar apenas "
    "vocabulário real de variante/estilo do Material Design 3 (ex.: 'Filled'/'Outlined'/'Text' "
    "para Buttons, 'Small'/'Center Aligned' para Top App Bar) — nunca invente um rótulo fora "
    "desse vocabulário; deixe vazio se não houver uma variante real aplicável. O ícone, quando "
    "houver, deve ser exatamente um nome do catálogo fechado Material Symbols informado abaixo, "
    "ou deve ser deixado vazio — nunca invente um nome de ícone fora dele. Baseie-se apenas nas "
    "telas/fluxos realmente descritos na UX Specification; nunca invente uma tela que não esteja "
    "lá (GR-UI-5)."
)


def _campo_texto(item: dict, chave: str) -> str:
    """Extrai um campo de texto simples de um item de componente, com a mesma defesa aplicada
    em toda skill deste agente para o caso do LLM devolver um objeto/lista onde se esperava uma
    string simples."""
    valor = item.get(chave, "")
    if isinstance(valor, str):
        return valor
    return item_para_string(valor) if valor else ""


def _construir_componente(item: dict) -> ComponentSpec | None:
    """Constrói um `ComponentSpec` a partir de um item já normalizado para dict — descarta o
    componente inteiro se o nome estiver fora do catálogo fechado Material Design 3 (GR-UI-1),
    mas nunca descarta por causa só de um ícone inválido (GR-UI-7: o ícone volta para "" nesse
    caso, o componente continua)."""
    nome = _campo_texto(item, "nome")
    if nome not in COMPONENTES_MD3:
        return None
    icone = _campo_texto(item, "icone")
    if icone not in ICONES_MATERIAL_SYMBOLS:
        icone = ""
    return ComponentSpec(
        name=nome,
        variant=_campo_texto(item, "variante"),
        size=_campo_texto(item, "tamanho"),
        icon=icone,
        notes=_campo_texto(item, "notas"),
    )


def identify_screens_and_components(texto_uxs: str, contexto: dict) -> list[UIScreen]:
    """Identifica as telas da UX Specification e, para cada uma, os componentes do catálogo
    fechado Material Design 3 que se aplicam (com variante/tamanho/ícone/notas quando fizerem
    sentido) e a hierarquia visual da tela — descarta qualquer componente fora do catálogo em
    vez de repassá-lo adiante (GR-UI-1), e qualquer ícone fora do catálogo Material Symbols
    volta para "" sem invalidar o componente (GR-UI-7)."""
    catalogo = ", ".join(COMPONENTES_MD3)
    icones = ", ".join(ICONES_MATERIAL_SYMBOLS)
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        f"Catálogo fechado de componentes Material Design 3: {catalogo}\n\n"
        f"Catálogo fechado de ícones Material Symbols: {icones}\n\n"
        'Responda apenas em JSON: {"telas": [{"nome": "...", "componentes": [{"nome": "...", '
        '"variante": "...", "tamanho": "...", "icone": "...", "notas": "..."}], '
        '"hierarquia": ["..."], "trecho_fonte": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    telas = []
    for item in dados.get("telas", []):
        if not isinstance(item, dict):
            continue
        componentes_brutos = lista_de_dicts(item.get("componentes", []), "nome")
        componentes = [
            componente
            for componente in (
                _construir_componente(bruto) for bruto in componentes_brutos
            )
            if componente is not None
        ]
        telas.append(
            UIScreen(
                name=item.get("nome", ""),
                components=componentes,
                hierarchy=lista_de_strings(item.get("hierarquia", [])),
                source_reference=item.get("trecho_fonte", ""),
            )
        )
    return telas
