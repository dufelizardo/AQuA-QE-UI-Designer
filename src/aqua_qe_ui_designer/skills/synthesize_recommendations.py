from ..models import PrioritizedRecommendation
from ..services.llm_service import complete_json
from ._normalizacao import item_para_string, lista_de_dicts

_PRIORIDADES_VALIDAS = ("Alta", "Média", "Baixa")
_PRIORIDADE_PADRAO = "Média"

_SYSTEM = (
    "Você sintetiza e prioriza recomendações para o time de desenvolvimento/design "
    "considerar antes da implementação, a partir de duas listas já existentes: "
    "recomendações de acessibilidade visual (fundamentadas em WCAG 2.2) e observações da "
    "revisão de UI (Material Design 3 + WCAG 2.2). Aponte as 3 a 5 questões mais críticas, "
    "combinando as duas listas por ordem de importância — nunca invente uma recomendação "
    "nova que não esteja em nenhuma das duas listas informadas; você só reordena/resume o "
    "que já existe, nunca cria conteúdo além disso. Para cada item, atribua uma prioridade "
    "'Alta', 'Média' ou 'Baixa' — nunca um quarto nível de prioridade. Cada item deve ser um "
    'objeto {"prioridade": "Alta"|"Média"|"Baixa", "texto": "..."}, nunca só uma string solta. '
    "Responda sempre em português."
)


def _campo_texto(item: dict, chave: str) -> str:
    valor = item.get(chave, "")
    if isinstance(valor, str):
        return valor
    return item_para_string(valor) if valor else ""


def synthesize_recommendations(
    accessibility_recommendations: list[str], review_notes: list[str]
) -> list[PrioritizedRecommendation]:
    """Sintetiza/prioriza as recomendações de acessibilidade e as observações da revisão já
    existentes, sem inventar itens novos — cada item recebe uma prioridade 'Alta'/'Média'/
    'Baixa', nunca um quarto nível inventado (a resposta do LLM que não bater com nenhuma das
    três é normalizada para 'Média')."""
    if not accessibility_recommendations and not review_notes:
        return []
    prompt = (
        f"Recomendações de acessibilidade visual:\n{accessibility_recommendations}\n\n"
        f"Observações da revisão de UI:\n{review_notes}\n\n"
        'Responda apenas em JSON: {"sintese": [{"prioridade": "...", "texto": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    recomendacoes = []
    for item in lista_de_dicts(dados.get("sintese", []), "texto"):
        texto = _campo_texto(item, "texto")
        if not texto:
            continue
        prioridade = _campo_texto(item, "prioridade")
        if prioridade not in _PRIORIDADES_VALIDAS:
            prioridade = _PRIORIDADE_PADRAO
        recomendacoes.append(PrioritizedRecommendation(priority=prioridade, text=texto))
    return recomendacoes
