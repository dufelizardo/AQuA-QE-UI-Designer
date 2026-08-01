from ..models import UIScreen
from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você gera recomendações de acessibilidade visual fundamentadas em WCAG 2.2 para as telas "
    "e componentes de uma UI Specification. Cada recomendação deve citar um critério WCAG 2.2 "
    "específico e ser redigida sempre como algo 'a verificar' pela equipe de desenvolvimento — "
    "nunca como afirmação de conformidade (GR-UI-3). Nunca certifique que algo 'está em "
    "conformidade'. Cada recomendação deve ser uma única string de texto, nunca um objeto/"
    "dicionário com campos separados."
)


def review_accessibility_visual(screens: list[UIScreen]) -> list[str]:
    """Gera recomendações de acessibilidade visual fundamentadas em WCAG 2.2 sobre as telas e
    componentes identificados — sempre 'a verificar', nunca certificação de conformidade (GR-UI-3)."""
    if not screens:
        return []
    telas = [
        {"nome": tela.name, "componentes": tela.components, "estados": tela.states}
        for tela in screens
    ]
    prompt = f"Telas:\n{telas}\n\nResponda apenas em JSON: {{\"recomendacoes\": [\"...\"]}}"
    dados = complete_json(prompt, system=_SYSTEM)
    return lista_de_strings(dados.get("recomendacoes", []), campos_prioritarios=("criterio_wcag",))
