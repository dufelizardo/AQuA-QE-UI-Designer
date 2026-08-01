from aqua_qe_ui_designer.models import DesignTokensSuggestion, UIScreen, UISpecification
from aqua_qe_ui_designer.skills import define_component_states as define_component_states_module
from aqua_qe_ui_designer.skills import define_responsive_layout as define_responsive_layout_module
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
                    "componentes": ["Cards", "Buttons"],
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
    assert telas[0].components == ["Cards", "Buttons"]
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
                    "componentes": ["Cards", "Componente Inventado Que Nao Existe"],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas[0].components == ["Cards"]


def test_identify_screens_and_components_converte_componente_objeto_em_string(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [
                {
                    "nome": "Tela",
                    "componentes": [{"nome": "Cards"}, {"nome": "Buttons"}],
                    "trecho_fonte": "f",
                }
            ]
        },
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas[0].components == ["Cards", "Buttons"]


def test_identify_screens_and_components_ignora_tela_que_nao_e_objeto(monkeypatch):
    monkeypatch.setattr(
        identify_screens_and_components_module,
        "complete_json",
        lambda prompt, system="", model=None: {"telas": ["texto solto sem estrutura"]},
    )

    telas = identify_screens_and_components_module.identify_screens_and_components("uxs", {})

    assert telas == []


# --- define_component_states -------------------------------------------------------------


def test_define_component_states_maps_json_to_screen_states(monkeypatch):
    monkeypatch.setattr(
        define_component_states_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "telas": [{"nome": "Tela", "estados": ["hover", "disabled"]}]
        },
    )

    telas = [UIScreen(name="Tela", components=["Cards"])]
    resultado = define_component_states_module.define_component_states(telas)

    assert resultado[0].states == ["hover", "disabled"]


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
            "telas": [{"nome": "Tela com componentes", "estados": ["hover"]}]
        },
    )

    telas = [
        UIScreen(name="Tela com componentes", components=["Cards"]),
        UIScreen(name="Tela vazia", components=[]),
    ]
    resultado = define_component_states_module.define_component_states(telas)

    assert resultado[0].states == ["hover"]
    assert resultado[1].states == []


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

    telas = [UIScreen(name="Tela", components=["Cards"], states=["hover"])]
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

    telas = [UIScreen(name="Tela", components=["Cards"], states=["focus"])]
    resultado = review_accessibility_visual_module.review_accessibility_visual(telas)

    assert resultado == [
        "2.4.3 Ordem de Foco: verificar a ordem de tabulação dos cards"
    ]


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
    assert resultado.screens[0].components == ["Cards"]
    assert resultado.screens[0].states == ["hover"]
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

    assert resultado.screens[0].components == ["Cards"]


def test_refine_ui_specification_preserva_campos_sem_resposta_relacionada(monkeypatch):
    """Sem telas/design tokens na resposta do LLM, mantém os valores atuais em vez de apagá-los."""
    monkeypatch.setattr(
        refine_ui_specification_module,
        "complete_json",
        lambda prompt, system="", model=None: {"titulo": "novo titulo"},
    )

    spec = _spec(
        title="titulo antigo",
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"], source_reference="f")],
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


# --- synthesize_recommendations --------------------------------------------------------------


def test_synthesize_recommendations_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": ["verificar contraste (WCAG 1.4.3)", "definir estado de erro do campo"]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste (WCAG 1.4.3)"], ["definir estado de erro do campo"]
    )

    assert resultado == ["verificar contraste (WCAG 1.4.3)", "definir estado de erro do campo"]


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
    monkeypatch.setattr(
        synthesize_recommendations_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "sintese": [{"recomendacao": "verificar contraste (WCAG 1.4.3)"}]
        },
    )

    resultado = synthesize_recommendations_module.synthesize_recommendations(
        ["verificar contraste (WCAG 1.4.3)"], []
    )

    assert resultado == ["verificar contraste (WCAG 1.4.3)"]


# --- review_ui_specification (reviewer) --------------------------------------------------------


def test_review_ui_specification_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(review_ui_specification_module, "complete_json", fake_complete_json)

    spec = _spec(
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"])],
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
        screens=[UIScreen(name="Tela", components=["Search Bar"], states=["hover"])],
        accessibility_recommendations=["verificar contraste"],
    )
    review_ui_specification_module.review_ui_specification(spec)

    assert "Search Bar" in captured["prompt"]
    assert "Progress Indicators" in captured["prompt"]


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
            UIScreen(name="Tela", components=["Cards", "Componente Fantasma"], states=["hover"])
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
        screens=[UIScreen(name="Tela", components=["Cards"], states=[])],
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
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"])],
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
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"])],
        accessibility_recommendations=["verificar contraste"],
    )
    resultado = review_ui_specification_module.review_ui_specification(spec)

    assert "componente Cards sem estado de erro definido" in resultado["problemas"]
