from ..models import UISpecification
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você transforma apontamentos de um revisor de UI em perguntas diretas e acionáveis para "
    "quem propôs a UI Specification responder."
)


def generate_ui_clarifying_questions(spec: UISpecification) -> list[str]:
    """Transforma os review_notes da UI Specification em perguntas diretas e acionáveis."""
    if not spec.review_notes:
        return []
    prompt = (
        f"Apontamentos do revisor:\n{spec.review_notes}\n\n"
        'Responda apenas em JSON: {"perguntas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("perguntas", [])
