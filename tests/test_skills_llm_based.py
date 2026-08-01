from aqua_qe_ui_designer.models import (
    ComponentSpec,
    DesignTokensSuggestion,
    PrioritizedRecommendation,
    StateSpec,
    UIScreen,
    UISpecification,
)
from aqua_qe_ui_designer.skills import define_component_states as define_component_states_module
from aqua_qe_ui_designer.skills import define_responsive_layout as define_responsive_layout_module
from aqua_qe_ui_designer.skills import (
    draft_empty_and_error_states as draft_empty_and_error_states_module,
)
from aqua_qe_ui_designer.skills import draft_interface_messages as draft_interface_messages_module
from aqua_qe_ui_designer.skills import extract_ui_context as extract_ui_context_module
from aqua_qe_ui_designer.skills import (
    generate_ui_clarifying_questions as generate_ui_clarifying_questions_module,
)
from aqua_qe_ui_designer.skills import (
    identify_screens_and_components as identify_screens_and_components_module,
)
from aqua_qe_ui_designer.skills import refine_ui_specification as refine_ui_specification_module
from aqua_qe_ui_designer.skills import (
    review_accessibility_visual as review_accessibility_visual_module,
)
from aqua_qe_ui_designer.skills import review_ui_specification as review_ui_specification_module
from aqua_qe_ui_designer.skills import suggest_design_tokens as suggest_design_tokens_module
from aqua_qe_ui_designer.skills import (
    synthesize_recommendations as synthesize_recommendations_module,
)


def _spec(**overrides) -> UISpecification:
    base = {
        "id": "UI-001",
        "title": "titulo",
        "context_problem": "contexto",
        "source_reference": "fonte",
    }
    base.update(overrides)
    return UISpecification(**base)


# --- extract_ui_context -----------------------------------------------------------------


def test_extract_ui_context_maps_json_to_fields(monkeypatch):
    monkeypatch.setattr(
        extract_ui_context_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "titulo": "Agendamento de Consulta",
            "contexto": "contexto extraido",
        },
    )

    contexto = extract_ui_context_module.extract_ui_context("uxs")

    assert contexto["title"] == "Agendamento de Consulta"
    assert contexto["context_problem"] == "contexto extraido"


def test_extract_ui_context_defaults_to_empty_when_absent(monkeypatch):
    monkeypatch.setattr(
        extract_ui_context_module, "complete_json", lambda prompt, system="", model=None: {}
    )

    contexto = extract_ui_context_module.extract_ui_context("uxs")

    assert contexto["title"] == ""
    assert contexto["context_problem"] == ""


# --- identify_screens_and_components ----------------------------------------------------


def test_identify_screens_and_components_maps_json_to_screens(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela de Agendamento",
                    "componentes": [
                        {"nome": "Cards"},
                        {
                            "nome": "Buttons",
                            "variante": "Filled",
                            "tamanho": "Large",
                            "icone": "add",
                            "notas": "ação principal",
                        },
                    ],
                    "hierarquia": ["Título", "Descrição", "Botão principal"],
                    "trecho_fonte": "trecho 1",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components(
        "uxs", {"context_problem": "c"}
    )

    assert len(telas) == 1
    assert telas[0].name == "Tela de Agendamento"
    assert telas[0].components[0] == ComponentSpec(name="Cards")
    assert telas[0].components[1] == ComponentSpec(
        name="Buttons", variant="Filled", size="Large", icon="add", notes="ação principal"
    )
    assert telas[0].hierarchy == ["Título", "Descrição", "Botão principal"]
    assert telas[0].source_reference == "trecho 1"


def test_identify_screens_and_components_descarta_componente_fora_do_catalogo(monkeypatch):
    """GR-UI-1, o guardrail mais importante deste agente: um componente fora do catálogo
    fechado do Material Design 3 nunca é repassado adiante."""
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": [
                        {"nome": "Cards"},
                        {"nome": "Componente Inventado Que Nao Existe"},
                    ],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert [componente.name for componente in telas[0].components] == ["Cards"]


def test_identify_screens_and_components_converte_componente_string_simples(monkeypatch):
    """Postura defensiva: o LLM pode devolver uma lista de strings simples em vez de objetos."""
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": ["Cards", "Buttons"],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert [componente.name for componente in telas[0].components] == ["Cards", "Buttons"]
    assert telas[0].components[0].variant == ""


def test_identify_screens_and_components_icone_invalido_vira_vazio_sem_descartar_componente(
    monkeypatch,
):
    """GR-UI-7: um ícone fora do catálogo fechado Material Symbols volta para "" — mas, ao
    contrário de um componente fora do catálogo Material Design 3 (GR-UI-1), nunca descarta o
    componente inteiro."""
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": [{"nome": "Cards", "icone": "icone_que_nao_existe"}],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert len(telas[0].components) == 1
    assert telas[0].components[0].name == "Cards"
    assert telas[0].components[0].icon == ""


def test_identify_screens_and_components_aceita_icone_valido(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": [{"nome": "Cards", "icone": "calendar_today"}],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas[0].components[0].icon == "calendar_today"


def test_identify_screens_and_components_ignora_tela_que_nao_e_objeto(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {"telas": ["texto solto sem estrutura"]},
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas == []


def test_identify_screens_and_components_campo_nao_string_e_convertido(monkeypatch):
    """Postura defensiva: um campo simples (ex.: variante) pode chegar como objeto/lista em vez
    de string — mesma defesa aplicada a todo campo de texto pedido ao LLM."""
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": [
                        {"nome": "Buttons", "variante": {"estilo": "Filled"}}
                    ],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas[0].components[0].variant == "Filled"


def test_identify_screens_and_components_ignora_componente_sem_nome_no_catalogo(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela", "componentes": [{}], "trecho_fonte": "f"}]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas[0].components == []


def test_identify_screens_and_components_inclui_catalogos_no_prompt(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"telas": []}

    monkeypatch.setattr(identify_screens_and_components_module, "complete_json", fake_complete_json)

    identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert "Search Bar" in captured["prompt"]
    assert "calendar_today" in captured["prompt"]


# --- define_component_states -------------------------------------------------------------


def test_define_component_states_maps_json_to_screen_states(monkeypatch):
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "estados": [
                        {"estado": "hover"},
                        {
                            "estado": "loading",
                            "contexto": "enquanto consulta horários disponíveis",
                        },
                    ],
                }
            ]
        },
    )

    telas = [UIScreen(name="Tela", components=[ComponentSpec(name="Cards")])]
    resultado = define_component_states_module.define_component_states(telas)

    assert resultado[0].states[0] == StateSpec(name="hover")
    assert resultado[0].states[1] == StateSpec(
        name="loading", context="enquanto consulta horários disponíveis"
    )


def test_define_component_states_converte_estado_string_simples(monkeypatch):
    """Postura defensiva: o LLM pode devolver uma lista de strings simples em vez de objetos."""
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela", "estados": ["hover", "disabled"]}]
        },
    )

    telas = [UIScreen(name="Tela", components=[ComponentSpec(name="Cards")])]
    resultado = define_component_states_module.define_component_states(telas)

    assert [estado.name for estado in resultado[0].states] == ["hover", "disabled"]
    assert resultado[0].states[0].context == ""


def test_define_component_states_pula_chamada_quando_nenhuma_tela_tem_componentes(monkeypatch):
    chamou = {"valor": False}

    def fake_complete_json(prompt, system="", model=None):
        chamou["valor"] = True
        return {"telas": []}

    monkeypatch.setattr(define_component_states_module, "complete_json", fake_complete_json)

    telas = [UIScreen(name="Tela", components=[])]
    resultado = define_component_states_module.define_component_states(telas)

    assert chamou["valor"] is False
    assert resultado[0].states == []


def test_define_component_states_nao_afeta_tela_sem_componentes(monkeypatch):
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela com componentes", "estados": [{"estado": "hover"}]}]
        },
    )

    telas = [
        UIScreen(name="Tela com componentes", components=[ComponentSpec(name="Cards")]),
        UIScreen(name="Tela vazia", components=[]),
    ]
    resultado = define_component_states_module.define_component_states(telas)

    assert resultado[0].states == [StateSpec(name="hover")]
    assert resultado[1].states == []


def test_define_component_states_contexto_nao_string_e_convertido(monkeypatch):
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "estados": [
                        {"estado": "loading", "contexto": {"detalhe": "ao consultar horários"}}
                    ],
                }
            ]
        },
    )

    telas = [UIScreen(name="Tela", components=[ComponentSpec(name="Cards")])]
    resultado = define_component_states_module.define_component_states(telas)

    assert resultado[0].states[0].context == "ao consultar horários"


def test_define_component_states_ignora_estado_sem_nome(monkeypatch):
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela", "estados": [{"contexto": "sem nome de estado"}, {"estado": "hover"}]}]
        },
    )

    telas = [UIScreen(name="Tela", components=[ComponentSpec(name="Cards")])]
    resultado = define_component_states_module.define_component_states(telas)

    assert [estado.name for estado in resultado[0].states] == ["hover"]


def test_define_component_states_inclui_trecho_fonte_no_prompt_para_fundamentar_contexto(
    monkeypatch,
):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"telas": []}

    monkeypatch.setattr(define_component_states_module, "complete_json", fake_complete_json)

    telas = [
        UIScreen(
            name="Tela",
            components=[ComponentSpec(name="Cards")],
            source_reference="o sistema consulta os horários disponíveis antes de exibir",
        )
    ]
    define_component_states_module.define_component_states(telas)

    assert "consulta os horários disponíveis" in captured["prompt"]


# --- suggest_design_tokens ----------------------------------------------------------------


def test_suggest_design_tokens_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        suggest_design_tokens_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "cores": ["primary: azul"],
            "tipografia": ["title-large"],
            "espacamento": ["16dp"],
        },
    )

    tokens = suggest_design_tokens_module.suggest_design_tokens("uxs", {"context_problem": "c"})

    assert tokens.colors == ["primary: azul"]
    assert tokens.typography == ["title-large"]
    assert tokens.spacing == ["16dp"]


def test_suggest_design_tokens_converte_item_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        suggest_design_tokens_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "cores": [{"nome": "primary", "descricao": "azul"}],
            "tipografia": [],
            "espacamento": [],
        },
    )

    tokens = suggest_design_tokens_module.suggest_design_tokens("uxs", {})

    assert tokens.colors == ["primary: azul"]


# --- define_responsive_layout -------------------------------------------------------------


def test_define_responsive_layout_returns_string_unchanged(monkeypatch):
    monkeypatch.setattr(
        define_responsive_layout_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "notas_responsivas": "Usar window size class compact/medium/expanded"
        },
    )

    resultado = define_responsive_layout_module.define_responsive_layout(
        "uxs", {"context_problem": "c"}
    )

    assert resultado == "Usar window size class compact/medium/expanded"


def test_define_responsive_layout_converte_lista_em_string(monkeypatch):
    monkeypatch.setattr(
        define_responsive_layout_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "notas_responsivas": ["compact: navegação em pilha única", "expanded: navegação lateral"]
        },
    )

    resultado = define_responsive_layout_module.define_responsive_layout("uxs", {})

    assert resultado == "compact: navegação em pilha única\nexpanded: navegação lateral"


# --- review_accessibility_visual ----------------------------------------------------------


def test_review_accessibility_visual_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        review_accessibility_visual_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "recomendacoes": ["verificar contraste (WCAG 1.4.3)"]
        },
    )

    telas = [
        UIScreen(
            name="Tela",
            components=[ComponentSpec(name="Cards")],
            states=[StateSpec(name="hover")],
        )
    ]
    resultado = review_accessibility_visual_module.review_accessibility_visual(telas)

    assert resultado == ["verificar contraste (WCAG 1.4.3)"]


def test_review_accessibility_visual_returns_empty_without_calling_llm_when_no_screens(
    monkeypatch,
):
    chamou = {"valor": False}

    def fake_complete_json(prompt, system="", model=None):
        chamou["valor"] = True
        return {"recomendacoes": []}

    monkeypatch.setattr(review_accessibility_visual_module, "complete_json", fake_complete_json)

    resultado = review_accessibility_visual_module.review_accessibility_visual([])

    assert resultado == []
    assert chamou["valor"] is False


def test_review_accessibility_visual_converte_recomendacao_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        review_accessibility_visual_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "recomendacoes": [
                {
                    "criterio_wcag": "2.4.3 Ordem de Foco",
                    "acao": "verificar a ordem de tabulação dos cards",
                }
            ]
        },
    )

    telas = [
        UIScreen(
            name="Tela",
            components=[ComponentSpec(name="Cards")],
            states=[StateSpec(name="focus")],
        )
    ]
    resultado = review_accessibility_visual_module.review_accessibility_visual(telas)

    assert resultado == [
        "2.4.3 Ordem de Foco: verificar a ordem de tabulação dos cards"
    ]


def test_review_accessibility_visual_serializa_nomes_no_prompt_em_vez_do_objeto(monkeypatch):
    """Sem essa serialização, o prompt mostraria o repr Python de ComponentSpec/StateSpec em
    vez de nomes legíveis para o LLM revisor."""
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"recomendacoes": []}

    monkeypatch.setattr(review_accessibility_visual_module, "complete_json", fake_complete_json)

    telas = [
        UIScreen(
            name="Tela",
            components=[ComponentSpec(name="Cards", variant="Filled")],
            states=[StateSpec(name="hover")],
        )
    ]
    review_accessibility_visual_module.review_accessibility_visual(telas)

    assert "ComponentSpec" not in captured["prompt"]
    assert "StateSpec" not in captured["prompt"]
    assert "Cards" in captured["prompt"]


# --- generate_ui_clarifying_questions -------------------------------------------------------


def test_generate_ui_clarifying_questions_returns_empty_without_review_notes():
    assert (
        generate_ui_clarifying_questions_module.generate_ui_clarifying_questions(_spec()) == []
    )


def test_generate_ui_clarifying_questions_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        generate_ui_clarifying_questions_module,
        "complete_json",
        lambda prompt, system="", model=None: {"perguntas": ["Quais telas fazem parte deste fluxo?"]},
    )

    spec = _spec(review_notes=["nenhuma tela identificada"])
    perguntas = generate_ui_clarifying_questions_module.generate_ui_clarifying_questions(spec)

    assert perguntas == ["Quais telas fazem parte deste fluxo?"]


# --- draft_empty_and_error_states -----------------------------------------------------------


def test_draft_empty_and_error_states_maps_json_to_tuple_of_lists(monkeypatch):
    monkeypatch.setattr(
        draft_empty_and_error_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "estados_vazios": ["Nenhum horário disponível no momento."],
            "estados_de_erro": ["Não foi possível carregar os horários. Tente novamente."],
        },
    )

    vazios, erros = draft_empty_and_error_states_module.draft_empty_and_error_states(
        "uxs", "Tela de Agendamento", {"context_problem": "c"}
    )

    assert vazios == ["Nenhum horário disponível no momento."]
    assert erros == ["Não foi possível carregar os horários. Tente novamente."]


def test_draft_empty_and_error_states_defaults_to_empty_lists_when_absent(monkeypatch):
    monkeypatch.setattr(
        draft_empty_and_error_states_module, "complete_json", lambda prompt, system="", model=None: {}
    )

    vazios, erros = draft_empty_and_error_states_module.draft_empty_and_error_states(
        "uxs", "Tela", {}
    )

    assert vazios == []
    assert erros == []


def test_draft_empty_and_error_states_converte_item_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        draft_empty_and_error_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "estados_vazios": [{"nome": "Nenhum horário disponível"}],
            "estados_de_erro": [],
        },
    )

    vazios, _ = draft_empty_and_error_states_module.draft_empty_and_error_states(
        "uxs", "Tela", {}
    )

    assert vazios == ["Nenhum horário disponível"]


def test_draft_empty_and_error_states_inclui_nome_da_tela_no_prompt(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"estados_vazios": [], "estados_de_erro": []}

    monkeypatch.setattr(draft_empty_and_error_states_module, "complete_json", fake_complete_json)

    draft_empty_and_error_states_module.draft_empty_and_error_states(
        "uxs", "Tela de Agendamento", {}
    )

    assert "Tela de Agendamento" in captured["prompt"]


# --- draft_interface_messages ----------------------------------------------------------------


def test_draft_interface_messages_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        draft_interface_messages_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "mensagens": ["Deseja realmente cancelar o agendamento?"]
        },
    )

    resultado = draft_interface_messages_module.draft_interface_messages(
        "uxs", {"context_problem": "c"}
    )

    assert resultado == ["Deseja realmente cancelar o agendamento?"]


def test_draft_interface_messages_defaults_to_empty_list_when_absent(monkeypatch):
    monkeypatch.setattr(
        draft_interface_messages_module, "complete_json", lambda prompt, system="", model=None: {}
    )

    resultado = draft_interface_messages_module.draft_interface_messages("uxs", {})

    assert resultado == []


def test_draft_interface_messages_converte_item_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        draft_interface_messages_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "mensagens": [{"nome": "Erro de conexão genérico"}]
        },
    )

    resultado = draft_interface_messages_module.draft_interface_messages("uxs", {})

    assert resultado == ["Erro de conexão genérico"]


# --- refine_ui_specification ----------------------------------------------------------------


def test_refine_ui_specification_rewrites_fields_from_answers(monkeypatch):
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "titulo": "titulo refinado",
            "contexto": "contexto",
            "telas": [{"nome": "Tela", "componentes": ["Cards"], "estados": ["hover"]}],
            "cores": ["primary: azul"],
            "tipografia": ["title-large"],
            "espacamento": ["16dp"],
            "notas_responsivas": "compact/medium/expanded",
            "acessibilidade": ["verificar foco"],
        },
    )

    spec = _spec(title="titulo antigo")
    resultado = refine_ui_specification_module.refine_ui_specification(
        spec, [{"pergunta": "qual o titulo?", "resposta": "titulo refinado"}]
    )

    assert resultado.title == "titulo refinado"
    assert resultado.screens[0].name == "Tela"
    assert resultado.screens[0].components == [ComponentSpec(name="Cards")]
    assert resultado.screens[0].states == [StateSpec(name="hover")]
    assert resultado.design_tokens.colors == ["primary: azul"]
    assert resultado.responsive_notes == "compact/medium/expanded"
    assert resultado.accessibility_recommendations == ["verificar foco"]


def test_refine_ui_specification_descarta_componente_fora_do_catalogo(monkeypatch):
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": ["Cards", "Componente Inventado"],
                    "estados": ["hover"],
                }
            ]
        },
    )

    spec = _spec()
    resultado = refine_ui_specification_module.refine_ui_specification(spec, [])

    assert resultado.screens[0].components == [ComponentSpec(name="Cards")]


def test_refine_ui_specification_preserva_campos_sem_resposta_relacionada(monkeypatch):
    """Sem telas/design tokens na resposta do LLM, mantém os valores atuais em vez de apagá-los."""
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {"titulo": "novo titulo"},
    )

    spec = _spec(
        title="titulo antigo",
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
                source_reference="f",
            )
        ],
        design_tokens=DesignTokensSuggestion(colors=["primary: azul"]),
        responsive_notes="compact/medium/expanded",
        accessibility_recommendations=["verificar contraste"],
    )

    resultado = refine_ui_specification_module.refine_ui_specification(spec, [])

    assert resultado.title == "novo titulo"
    assert resultado.screens[0].name == "Tela"
    assert resultado.design_tokens.colors == ["primary: azul"]
    assert resultado.responsive_notes == "compact/medium/expanded"
    assert resultado.accessibility_recommendations == ["verificar contraste"]


def test_refine_ui_specification_ignora_tela_que_nao_e_objeto(monkeypatch):
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                "texto solto sem estrutura",
                {"nome": "Tela", "componentes": ["Cards"], "estados": ["hover"]},
            ]
        },
    )

    spec = _spec()
    resultado = refine_ui_specification_module.refine_ui_specification(spec, [])

    assert len(resultado.screens) == 1
    assert resultado.screens[0].name == "Tela"


def test_refine_ui_specification_preserva_hierarquia_e_estados_vazios_e_de_erro_da_tela_atual(
    monkeypatch,
):
    """O ciclo de refino não reaborda hierarquia/empty states/error states — preserva o que já
    existia na tela de mesmo nome em vez de apagar esse detalhe."""
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela", "componentes": ["Cards"], "estados": ["hover"]}]
        },
    )

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
                hierarchy=["Título", "Botão principal"],
                empty_states=["Nenhum item encontrado."],
                error_states=["Não foi possível carregar."],
                source_reference="f",
            )
        ]
    )

    resultado = refine_ui_specification_module.refine_ui_specification(spec, [])

    assert resultado.screens[0].hierarchy == ["Título", "Botão principal"]
    assert resultado.screens[0].empty_states == ["Nenhum item encontrado."]
    assert resultado.screens[0].error_states == ["Não foi possível carregar."]


# --- synthesize_recommendations --------------------------------------------------------------


def test_synthesize_recommendations_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": [
                {"prioridade": "Alta", "texto": "verificar contraste (WCAG 1.4.3)"},
                {"prioridade": "Baixa", "texto": "definir estado de erro do campo"},
            ]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste (WCAG 1.4.3)"], ["definir estado de erro do campo"]
    )

    assert resultado == [
        PrioritizedRecommendation(priority="Alta", text="verificar contraste (WCAG 1.4.3)"),
        PrioritizedRecommendation(priority="Baixa", text="definir estado de erro do campo"),
    ]


def test_synthesize_recommendations_returns_empty_without_calling_llm_when_both_empty(monkeypatch):
    chamou = {"valor": False}

    def fake_complete_json(prompt, system="", model=None):
        chamou["valor"] = True
        return {"sintese": []}

    monkeypatch.setattr(synthesize_recommendations_module, "complete_json", fake_complete_json)

    resultado = synthesize_recommendations_module.synthesize_recommendations([], [])

    assert resultado == []
    assert chamou["valor"] is False


def test_synthesize_recommendations_converte_item_objeto_em_string(monkeypatch):
    """Postura defensiva: o campo `texto` pode chegar como um objeto aninhado em vez de string
    simples — mesma defesa já aplicada em toda skill que pede um campo de texto ao LLM."""
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": [
                {
                    "prioridade": "Alta",
                    "texto": {"resumo": "verificar contraste (WCAG 1.4.3)"},
                }
            ]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste (WCAG 1.4.3)"], []
    )

    assert resultado == [
        PrioritizedRecommendation(priority="Alta", text="verificar contraste (WCAG 1.4.3)")
    ]


def test_synthesize_recommendations_prioridade_invalida_vira_media(monkeypatch):
    """Nunca inventa um quarto nível de prioridade — normaliza para 'Média'."""
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": [{"prioridade": "Urgentíssima", "texto": "verificar contraste"}]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste"], []
    )

    assert resultado == [PrioritizedRecommendation(priority="Média", text="verificar contraste")]


def test_synthesize_recommendations_ignora_item_sem_texto(monkeypatch):
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": [
                {"prioridade": "Alta"},
                {"prioridade": "Baixa", "texto": "verificar contraste"},
            ]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste"], []
    )

    assert resultado == [PrioritizedRecommendation(priority="Baixa", text="verificar contraste")]


def test_synthesize_recommendations_item_string_simples_vira_media(monkeypatch):
    """Postura defensiva: uma string simples em vez de objeto vira prioridade 'Média'."""
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {"sintese": ["verificar contraste"]},
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste"], []
    )

    assert resultado == [PrioritizedRecommendation(priority="Média", text="verificar contraste")]


# --- review_ui_specification (reviewer) --------------------------------------------------------


def test_review_ui_specification_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(review_ui_specification_module, "complete_json", fake_complete_json)

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
            )
        ],
        accessibility_recommendations=["verificar contraste"],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"


def test_review_ui_specification_inclui_catalogo_real_no_prompt(monkeypatch):
    """Regressão (achado ao vivo, Groq/llama-3.3-70b-versatile): o revisor LLM alucinou que
    'Search Bar' e 'Progress Indicators' não existiam no catálogo Material Design 3 — ambos
    existem, mas o prompt nunca enviava o catálogo real, então o modelo julgava pelo próprio
    conhecimento (errado) em vez da lista de verdade desta plataforma. O prompt agora precisa
    conter o catálogo literal."""
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(review_ui_specification_module, "complete_json", fake_complete_json)

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Search Bar")],
                states=[StateSpec(name="hover")],
            )
        ],
        accessibility_recommendations=["verificar contraste"],
    )
    review_ui_specification_module.review_ui_specification(spec)

    assert "Search Bar" in captured["prompt"]
    assert "Progress Indicators" in captured["prompt"]


def test_review_ui_specification_serializa_variante_tamanho_icone_e_contexto_no_prompt(
    monkeypatch,
):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(review_ui_specification_module, "complete_json", fake_complete_json)

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[
                    ComponentSpec(name="Buttons", variant="Filled", size="Large", icon="add")
                ],
                states=[
                    StateSpec(name="loading", context="enquanto consulta horários disponíveis")
                ],
            )
        ],
        accessibility_recommendations=["verificar contraste"],
    )
    review_ui_specification_module.review_ui_specification(spec)

    assert "Filled" in captured["prompt"]
    assert "enquanto consulta horários disponíveis" in captured["prompt"]


def test_review_ui_specification_reprova_componente_fora_do_catalogo_mesmo_se_llm_aprovar(
    monkeypatch,
):
    """GR-UI-1: checagem determinística nunca deixa passar um componente fora do catálogo,
    mesmo que o LLM revisor não perceba e aprove."""
    monkeypatch.setattr(
        review_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {"aprovado": True, "problemas": []},
    )

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards"), ComponentSpec(name="Componente Fantasma")],
                states=[StateSpec(name="hover")],
            )
        ],
        accessibility_recommendations=["verificar contraste"],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert resultado["aprovado"] is False
    assert any("Componente Fantasma" in problema for problema in resultado["problemas"])
    assert any("GR-UI-1" in problema for problema in resultado["problemas"])


def test_review_ui_specification_reprova_componente_sem_estados(monkeypatch):
    monkeypatch.setattr(
        review_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {"aprovado": True, "problemas": []},
    )

    spec = _spec(
        screens=[UIScreen(name="Tela", components=[ComponentSpec(name="Cards")], states=[])],
        accessibility_recommendations=["verificar contraste"],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert resultado["aprovado"] is False
    assert any("sem estados de interação definidos" in problema for problema in resultado["problemas"])


def test_review_ui_specification_reprova_sem_recomendacao_de_acessibilidade(monkeypatch):
    monkeypatch.setattr(
        review_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {"aprovado": True, "problemas": []},
    )

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
            )
        ],
        accessibility_recommendations=[],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert resultado["aprovado"] is False
    assert any("nenhuma recomendação de acessibilidade" in problema for problema in resultado["problemas"])


def test_review_ui_specification_converte_problema_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        review_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "aprovado": False,
            "problemas": [
                {
                    "detalhes": "componente Cards sem estado de erro definido",
                }
            ],
        },
    )

    spec = _spec(
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
            )
        ],
        accessibility_recommendations=["verificar contraste"],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert "componente Cards sem estado de erro definido" in resultado["problemas"]
