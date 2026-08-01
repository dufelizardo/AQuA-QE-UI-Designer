from aqua_qe_ui_designer.models import (
    ArtifactStatus,
    ChatMessage,
    DesignTokensSuggestion,
    UIScreen,
    UISpecification,
)


def test_ui_screen_defaults():
    tela = UIScreen(name="Agendamento")
    assert tela.components == []
    assert tela.states == []
    assert tela.source_reference == ""


def test_design_tokens_suggestion_defaults():
    tokens = DesignTokensSuggestion()
    assert tokens.colors == []
    assert tokens.typography == []
    assert tokens.spacing == []


def test_chat_message_fields():
    mensagem = ChatMessage(speaker="Designer", text="olá")
    assert mensagem.speaker == "Designer"
    assert mensagem.text == "olá"


def test_ui_specification_defaults_to_pending_clarification():
    spec = UISpecification(id="UI-001", title="t", context_problem="c")
    assert spec.status == ArtifactStatus.PENDING_CLARIFICATION
    assert spec.screens == []
    assert isinstance(spec.design_tokens, DesignTokensSuggestion)
    assert spec.responsive_notes == ""
    assert spec.accessibility_recommendations == []
    assert spec.review_notes == []
    assert spec.source_reference == ""
    assert spec.uxs_reference == ""
    assert spec.figma_file_reference == ""
    assert spec.recommendations_synthesis == []


def test_ui_specification_accepts_full_payload():
    spec = UISpecification(
        id="UI-001",
        title="t",
        context_problem="c",
        screens=[
            UIScreen(
                name="Agendamento",
                components=["Cards", "Buttons"],
                states=["hover", "disabled"],
                source_reference="fonte",
            )
        ],
        design_tokens=DesignTokensSuggestion(
            colors=["primary: azul"], typography=["title-large"], spacing=["16dp"]
        ),
        responsive_notes="compact/medium/expanded",
        accessibility_recommendations=["verificar contraste"],
        source_reference="fonte completa",
        uxs_reference="https://example.atlassian.net/wiki/pages/1",
        figma_file_reference="",
        status=ArtifactStatus.DRAFT_VALIDATED,
        review_notes=["nota"],
        recommendations_synthesis=["priorizar contraste"],
    )
    assert spec.screens[0].name == "Agendamento"
    assert spec.design_tokens.colors == ["primary: azul"]
    assert spec.status == ArtifactStatus.DRAFT_VALIDATED
    assert spec.uxs_reference == "https://example.atlassian.net/wiki/pages/1"
    assert spec.figma_file_reference == ""
    assert spec.recommendations_synthesis == ["priorizar contraste"]
