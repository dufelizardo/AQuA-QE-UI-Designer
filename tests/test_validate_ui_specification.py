from aqua_qe_ui_designer.models import (
    ComponentSpec,
    DesignTokensSuggestion,
    StateSpec,
    UIScreen,
    UISpecification,
)
from aqua_qe_ui_designer.skills.validate_ui_specification import validate_ui_specification


def _spec_completa(**overrides) -> UISpecification:
    base = {
        "id": "UI-001",
        "title": "titulo",
        "context_problem": "contexto",
        "screens": [
            UIScreen(
                name="Agendamento",
                components=[ComponentSpec(name="Cards"), ComponentSpec(name="Buttons")],
                states=[StateSpec(name="hover"), StateSpec(name="disabled")],
                source_reference="fonte",
            )
        ],
        "design_tokens": DesignTokensSuggestion(colors=["primary: azul"]),
        "responsive_notes": "compact/medium/expanded",
        "accessibility_recommendations": ["verificar contraste (WCAG 1.4.3)"],
    }
    base.update(overrides)
    return UISpecification(**base)


def test_valid_ui_specification_passes():
    assert validate_ui_specification(_spec_completa()) == []


def test_missing_title_fails():
    assert "título ausente" in validate_ui_specification(_spec_completa(title=""))


def test_missing_context_fails():
    assert "contexto do problema ausente" in validate_ui_specification(
        _spec_completa(context_problem="")
    )


def test_no_screens_fails():
    motivos = validate_ui_specification(_spec_completa(screens=[]))
    assert "nenhuma tela identificada" in motivos


def test_screen_without_components_fails():
    motivos = validate_ui_specification(
        _spec_completa(screens=[UIScreen(name="Agendamento", components=[], states=[])])
    )
    assert "tela 'Agendamento' sem componentes do Material Design 3 identificados" in motivos


def test_screen_with_components_but_no_states_fails():
    motivos = validate_ui_specification(
        _spec_completa(
            screens=[UIScreen(name="Agendamento", components=[ComponentSpec(name="Cards")], states=[])]
        )
    )
    assert "tela 'Agendamento' sem estados de componente definidos" in motivos


def test_no_design_tokens_fails():
    motivos = validate_ui_specification(
        _spec_completa(design_tokens=DesignTokensSuggestion())
    )
    assert "nenhuma sugestão de design tokens (cores/tipografia/espaçamento)" in motivos


def test_missing_responsive_notes_fails():
    motivos = validate_ui_specification(_spec_completa(responsive_notes=""))
    assert "notas de layout responsivo ausentes" in motivos


def test_no_accessibility_recommendations_fails():
    motivos = validate_ui_specification(_spec_completa(accessibility_recommendations=[]))
    assert "nenhuma recomendação de acessibilidade visual" in motivos


def test_multiplos_motivos_acumulam_em_vez_de_parar_no_primeiro():
    motivos = validate_ui_specification(
        _spec_completa(title="", accessibility_recommendations=[])
    )
    assert "título ausente" in motivos
    assert "nenhuma recomendação de acessibilidade visual" in motivos
