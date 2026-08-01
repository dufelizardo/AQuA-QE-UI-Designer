from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você sintetiza e prioriza recomendações para o time de desenvolvimento/design "
    "considerar antes da implementação, a partir de duas listas já existentes: "
    "recomendações de acessibilidade visual (fundamentadas em WCAG 2.2) e observações da "
    "revisão de UI (Material Design 3 + WCAG 2.2). Aponte as 3 a 5 questões mais críticas, "
    "combinando as duas listas por ordem de importância — nunca invente uma recomendação "
    "nova que não esteja em nenhuma das duas listas informadas; você só reordena/resume o "
    "que já existe, nunca cria conteúdo além disso. Cada item da síntese deve ser uma única "
    "string de texto, nunca um objeto/dicionário com campos separados. Responda sempre em "
    "português."
)


def synthesize_recommendations(
    accessibility_recommendations: list[str], review_notes: list[str]
) -> list[str]:
    """Sintetiza/prioriza as recomendações de acessibilidade e as observações da revisão já
    existentes, sem inventar itens novos."""
    if not accessibility_recommendations and not review_notes:
        return []
    prompt = (
        f"Recomendações de acessibilidade visual:\n{accessibility_recommendations}\n\n"
        f"Observações da revisão de UI:\n{review_notes}\n\n"
        'Responda apenas em JSON: {"sintese": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return lista_de_strings(dados.get("sintese", []))
