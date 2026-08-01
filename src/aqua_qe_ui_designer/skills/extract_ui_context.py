from ..services.llm_service import complete_json

_SYSTEM = (
    "Responda sempre em português.\n\n"
    "Você extrai um título curto e um resumo do problema/contexto a partir do texto de uma UX "
    "Specification já pronta, para orientar a especificação visual (UI Specification) que a "
    "consome. Baseie-se apenas no que a UX Specification realmente descreve — nunca invente "
    "contexto que não esteja lá (GR-UI-5). Esta etapa só extrai contexto textual; nunca "
    "descreva um render visual como se já existisse (GR-UI-4)."
)


def extract_ui_context(texto_uxs: str) -> dict:
    """Extrai título e contexto do problema a partir do texto da UX Specification de origem."""
    prompt = (
        f"UX Specification:\n{texto_uxs}\n\n"
        'Responda apenas em JSON: {"titulo": "...", "contexto": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return {
        "title": dados.get("titulo", ""),
        "context_problem": dados.get("contexto", ""),
    }
