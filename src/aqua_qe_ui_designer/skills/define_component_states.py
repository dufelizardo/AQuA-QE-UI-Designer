from ..models import UIScreen
from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_ESTADOS_REFERENCIA = ["hover", "focus", "disabled", "loading", "error", "success"]

_SYSTEM = (
    "Você define, para cada tela e os componentes Material Design 3 já identificados nela, "
    "quais estados de interação (ex.: hover, focus, disabled, loading, error, success) são "
    "relevantes considerar durante a implementação. Baseie-se apenas nos componentes "
    "informados; nunca sugira estados para uma tela sem componentes identificados. Cada "
    "estado deve ser uma única string de texto (ex.: 'hover', 'disabled'), nunca um objeto."
)


def define_component_states(screens: list[UIScreen]) -> list[UIScreen]:
    """Define os estados de interação relevantes para os componentes já identificados em cada
    tela (hover/focus/disabled/loading/error/success)."""
    telas_com_componentes = [tela for tela in screens if tela.components]
    if not telas_com_componentes:
        return screens

    telas_para_prompt = [
        {"nome": tela.name, "componentes": tela.components} for tela in telas_com_componentes
    ]
    prompt = (
        f"Telas e componentes:\n{telas_para_prompt}\n\n"
        f"Estados possíveis de referência: {', '.join(_ESTADOS_REFERENCIA)}\n\n"
        'Responda apenas em JSON: {"telas": [{"nome": "...", "estados": ["..."]}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    estados_por_tela = {
        item.get("nome", ""): lista_de_strings(item.get("estados", []))
        for item in dados.get("telas", [])
        if isinstance(item, dict)
    }
    for tela in screens:
        if tela.components:
            tela.states = estados_por_tela.get(tela.name, []) or tela.states
    return screens
