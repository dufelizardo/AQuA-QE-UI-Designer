from ..models import StateSpec, UIScreen
from ..services.llm_service import complete_json
from ._normalizacao import item_para_string, lista_de_dicts

_ESTADOS_REFERENCIA = ["hover", "focus", "disabled", "loading", "error", "success"]

_SYSTEM = (
    "Você define, para cada tela e os componentes Material Design 3 já identificados nela, "
    "quais estados de interação (ex.: hover, focus, disabled, loading, error, success) são "
    "relevantes considerar durante a implementação, e o contexto real em que cada um ocorre "
    "quando o trecho de origem da tela descreve um ponto assíncrono/de espera específico (ex.: "
    "'enquanto consulta horários disponíveis') — nunca invente um contexto que o trecho de "
    "origem não sustente; deixe o contexto vazio quando a fonte não descrever nada específico "
    "para aquele estado. Baseie-se apenas nos componentes informados; nunca sugira estados para "
    "uma tela sem componentes identificados. Cada estado deve ser um objeto "
    '{"estado": "...", "contexto": "..."}, nunca só uma string solta.'
)


def _campo_texto(item: dict, chave: str) -> str:
    valor = item.get(chave, "")
    if isinstance(valor, str):
        return valor
    return item_para_string(valor) if valor else ""


def _construir_estados(bruto) -> list[StateSpec]:
    """Constrói a lista de `StateSpec` a partir da resposta bruta do LLM para uma tela, com a
    mesma postura defensiva do resto do agente (pode chegar como lista de objetos, lista de
    strings simples, dict de estado->contexto, ou uma string com repr de dict/list embutido)."""
    estados = []
    for item in lista_de_dicts(bruto, "estado"):
        nome = _campo_texto(item, "estado")
        if not nome:
            continue
        estados.append(StateSpec(name=nome, context=_campo_texto(item, "contexto")))
    return estados


def define_component_states(screens: list[UIScreen]) -> list[UIScreen]:
    """Define os estados de interação relevantes para os componentes já identificados em cada
    tela (hover/focus/disabled/loading/error/success), com o contexto real do estado quando o
    trecho de origem da tela descreve um ponto assíncrono/de espera específico."""
    telas_com_componentes = [tela for tela in screens if tela.components]
    if not telas_com_componentes:
        return screens

    telas_para_prompt = [
        {
            "nome": tela.name,
            "componentes": [componente.name for componente in tela.components],
            "trecho_fonte": tela.source_reference,
        }
        for tela in telas_com_componentes
    ]
    prompt = (
        f"Telas, componentes e trecho de origem:\n{telas_para_prompt}\n\n"
        f"Estados possíveis de referência: {', '.join(_ESTADOS_REFERENCIA)}\n\n"
        'Responda apenas em JSON: {"telas": [{"nome": "...", "estados": [{"estado": "...", '
        '"contexto": "..."}]}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    estados_por_tela = {
        item.get("nome", ""): _construir_estados(item.get("estados", []))
        for item in dados.get("telas", [])
        if isinstance(item, dict)
    }
    for tela in screens:
        if tela.components:
            tela.states = estados_por_tela.get(tela.name, []) or tela.states
    return screens
