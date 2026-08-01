from aqua_qe_ui_designer.models import (
    ArtifactStatus,
    ChatMessage,
    ComponentSpec,
    DesignTokensSuggestion,
    PrioritizedRecommendation,
    StateSpec,
    UIScreen,
    UISpecification,
)


def test_component_spec_defaults():
    componente = ComponentSpec(name="Cards")
    assert componente.variant == ""
    assert componente.size == ""
    assert componente.icon == ""
    assert componente.notes == ""


def test_component_spec_full_payload():
    componente = ComponentSpec(
        name="Buttons", variant="Filled", size="Large", icon="add", notes="ação principal"
    )
    assert componente.name == "Buttons"
    assert componente.variant == "Filled"
    assert componente.size == "Large"
    assert componente.icon == "add"
    assert componente.notes == "ação principal"


def test_state_spec_defaults():
    estado = StateSpec(name="hover")
    assert estado.context == ""


def test_state_spec_with_context():
    estado = StateSpec(name="loading", context="enquanto consulta horários disponíveis")
    assert estado.name == "loading"
    assert estado.context == "enquanto consulta horários disponíveis"


def test_prioritized_recommendation_fields():
    recomendacao = PrioritizedRecommendation(priority="Alta", text="verificar contraste")
    assert recomendacao.priority == "Alta"
    assert recomendacao.text == "verificar contraste"


def test_ui_screen_defaults():
    tela = UIScreen(name="Agendamento")
    assert tela.components == []
    assert tela.states == []
    assert tela.hierarchy == []
    assert tela.empty_states == []
    assert tela.error_states == []
    assert tela.source_reference == ""


def test_ui_screen_full_payload():
    tela = UIScreen(
        name="Agendamento",
        components=[ComponentSpec(name="Cards"), ComponentSpec(name="Buttons", variant="Filled")],
        states=[StateSpec(name="hover"), StateSpec(name="loading", context="ao consultar")],
        hierarchy=["Título", "Descrição", "Botão principal"],
        empty_states=["Nenhum horário disponível no momento."],
        error_states=["Não foi possível carregar os horários. Tente novamente."],
        source_reference="fonte",
    )
    assert tela.components[0].name == "Cards"
    assert tela.components[1].variant == "Filled"
    assert tela.states[1].context == "ao consultar"
    assert tela.hierarchy == ["Título", "Descrição", "Botão principal"]
    assert tela.empty_states == ["Nenhum horário disponível no momento."]
    assert tela.error_states == ["Não foi possível carregar os horários. Tente novamente."]


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
    assert spec.interface_messages == []
    assert spec.navigation_sequence == []
    assert spec.icons == []
    assert spec.motion_notes == ""


def test_ui_specification_accepts_full_payload():
    spec = UISpecification(
        id="UI-001",
        title="t",
        context_problem="c",
        screens=[
            UIScreen(
                name="Agendamento",
                components=[ComponentSpec(name="Cards"), ComponentSpec(name="Buttons")],
                states=[StateSpec(name="hover"), StateSpec(name="disabled")],
                hierarchy=["Título", "Botão principal"],
                empty_states=["Nenhum agendamento encontrado."],
                error_states=["Não foi possível salvar o agendamento."],
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
        recommendations_synthesis=[
            PrioritizedRecommendation(priority="Alta", text="priorizar contraste")
        ],
        interface_messages=["Deseja realmente cancelar o agendamento?"],
        navigation_sequence=["Agendamento"],
        icons=["calendar_today"],
        motion_notes="Transições seguem o Material Motion.",
    )
    assert spec.screens[0].name == "Agendamento"
    assert spec.screens[0].components[0].name == "Cards"
    assert spec.screens[0].hierarchy == ["Título", "Botão principal"]
    assert spec.design_tokens.colors == ["primary: azul"]
    assert spec.status == ArtifactStatus.DRAFT_VALIDATED
    assert spec.uxs_reference == "https://example.atlassian.net/wiki/pages/1"
    assert spec.figma_file_reference == ""
    assert spec.recommendations_synthesis == [
        PrioritizedRecommendation(priority="Alta", text="priorizar contraste")
    ]
    assert spec.interface_messages == ["Deseja realmente cancelar o agendamento?"]
    assert spec.navigation_sequence == ["Agendamento"]
    assert spec.icons == ["calendar_today"]
    assert spec.motion_notes == "Transições seguem o Material Motion."
