from ..models import UISpecification


def validate_ui_specification(spec: UISpecification) -> list[str]:
    """Valida a UI Specification contra o checklist automático e retorna os motivos de reprovação (lista vazia = aprovado no checklist)."""
    motivos = []
    if not spec.title:
        motivos.append("título ausente")
    if not spec.context_problem:
        motivos.append("contexto do problema ausente")
    if not spec.screens:
        motivos.append("nenhuma tela identificada")
    else:
        for tela in spec.screens:
            if not tela.components:
                motivos.append(f"tela '{tela.name}' sem componentes do Material Design 3 identificados")
            elif not tela.states:
                motivos.append(f"tela '{tela.name}' sem estados de componente definidos")
    if not (
        spec.design_tokens.colors or spec.design_tokens.typography or spec.design_tokens.spacing
    ):
        motivos.append("nenhuma sugestão de design tokens (cores/tipografia/espaçamento)")
    if not spec.responsive_notes:
        motivos.append("notas de layout responsivo ausentes")
    if not spec.accessibility_recommendations:
        motivos.append("nenhuma recomendação de acessibilidade visual")
    return motivos
