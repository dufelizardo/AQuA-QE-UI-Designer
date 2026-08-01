from ..services.llm_service import complete_json
from ._normalizacao import texto_ou_lista

_SYSTEM = (
    "Você descreve notas de layout responsivo para uma UI Specification, sempre citando as "
    "window size classes reais do Material Design 3 (compact/medium/expanded) como a "
    "referência de breakpoint — nunca invente números de breakpoint fora dessa referência "
    "(GR-UI-5). Responda em prosa objetiva, como uma única string de texto."
)


def define_responsive_layout(texto_uxs: str, contexto: dict) -> str:
    """Gera notas de layout responsivo citando as window size classes do Material Design 3
    (compact/medium/expanded) — nunca breakpoints numéricos inventados (GR-UI-5)."""
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        'Responda apenas em JSON: {"notas_responsivas": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return texto_ou_lista(dados.get("notas_responsivas", ""))
