from aqua_qe_ui_designer.models import (
    ArtifactStatus,
    DesignTokensSuggestion,
    UIScreen,
    UISpecification,
)
from aqua_qe_ui_designer.workflow import generate_ui_specification as workflow_module


def _stub_geracao(monkeypatch, com_componentes=True, com_acessibilidade=True):
    monkeypatch.setattr(
        workflow_module,
        "extract_ui_context",
        lambda texto_uxs: {"title": "titulo", "context_problem": "contexto"},
    )
    telas = (
        [UIScreen(name="Tela", components=["Cards"], source_reference="f")]
        if com_componentes
        else [UIScreen(name="Tela", components=[], source_reference="f")]
    )
    monkeypatch.setattr(
        workflow_module, "identify_screens_and_components", lambda texto_uxs, contexto: telas
    )

    def fake_define_component_states(screens):
        for tela in screens:
            if tela.components:
                tela.states = ["hover", "disabled"]
        return screens

    monkeypatch.setattr(workflow_module, "define_component_states", fake_define_component_states)
    monkeypatch.setattr(
        workflow_module,
        "suggest_design_tokens",
        lambda texto_uxs, contexto: DesignTokensSuggestion(colors=["primary: azul"]),
    )
    monkeypatch.setattr(
        workflow_module,
        "define_responsive_layout",
        lambda texto_uxs, contexto: "compact/medium/expanded",
    )
    monkeypatch.setattr(
        workflow_module,
        "review_accessibility_visual",
        lambda screens: (["verificar contraste"] if com_acessibilidade else []),
    )


def test_generate_ui_specification_happy_path_marks_draft_validated_when_review_approves(
    monkeypatch,
):
    _stub_geracao(monkeypatch)
    monkeypatch.setattr(
        workflow_module,
        "review_ui_specification",
        lambda spec: {"aprovado": True, "problemas": []},
    )

    spec = workflow_module.generate_ui_specification(
        "uxs", uxs_reference="https://example.atlassian.net/wiki/pages/1"
    )

    assert spec.status == ArtifactStatus.DRAFT_VALIDATED
    assert spec.title == "titulo"
    assert spec.screens[0].name == "Tela"
    assert spec.screens[0].states == ["hover", "disabled"]
    assert spec.design_tokens.colors == ["primary: azul"]
    assert spec.responsive_notes == "compact/medium/expanded"
    assert spec.accessibility_recommendations == ["verificar contraste"]
    assert spec.review_notes == []
    assert spec.uxs_reference == "https://example.atlassian.net/wiki/pages/1"


def test_generate_ui_specification_review_rejection_marks_pending_clarification(monkeypatch):
    _stub_geracao(monkeypatch)
    monkeypatch.setattr(
        workflow_module,
        "review_ui_specification",
        lambda spec: {"aprovado": False, "problemas": ["componente sem estados"]},
    )

    spec = workflow_module.generate_ui_specification("uxs")

    assert spec.status == ArtifactStatus.PENDING_CLARIFICATION
    assert spec.review_notes == ["componente sem estados"]


def test_generate_ui_specification_validate_failure_skips_review(monkeypatch):
    """Sem componentes nem acessibilidade, validate_ui_specification reprova antes de chamar o revisor."""
    _stub_geracao(monkeypatch, com_componentes=False, com_acessibilidade=False)
    chamou_review = {"valor": False}

    def fake_review(spec):
        chamou_review["valor"] = True
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(workflow_module, "review_ui_specification", fake_review)

    spec = workflow_module.generate_ui_specification("uxs")

    assert spec.status == ArtifactStatus.PENDING_CLARIFICATION
    assert chamou_review["valor"] is False
    assert any("sem componentes" in nota for nota in spec.review_notes)
    assert "nenhuma recomendação de acessibilidade visual" in spec.review_notes


def _spec_completa() -> UISpecification:
    return UISpecification(
        id="UI-001",
        title="t",
        context_problem="c",
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"], source_reference="f")],
        design_tokens=DesignTokensSuggestion(colors=["primary: azul"]),
        responsive_notes="compact/medium/expanded",
        accessibility_recommendations=["verificar contraste"],
    )


def test_finalize_ui_specification_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(
        workflow_module, "validate_ui_specification", lambda spec: ["título ausente"]
    )

    spec = UISpecification(id="UI-001", title="", context_problem="")
    resultado = workflow_module.finalize_ui_specification(spec)

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["título ausente"]


def test_finalize_ui_specification_marca_draft_validated_quando_tudo_aprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_ui_specification", lambda spec: [])
    monkeypatch.setattr(
        workflow_module,
        "review_ui_specification",
        lambda spec: {"aprovado": True, "problemas": []},
    )

    resultado = workflow_module.finalize_ui_specification(_spec_completa())

    assert resultado.status == ArtifactStatus.DRAFT_VALIDATED


def test_finalize_ui_specification_sempre_recalcula_sintese(monkeypatch):
    """A síntese é sempre recomputada ao final, mesmo quando a validação reprova."""
    monkeypatch.setattr(
        workflow_module, "validate_ui_specification", lambda spec: ["nenhuma tela identificada"]
    )
    chamou_sintese = {"valor": False}

    def fake_sintese(accessibility_recommendations, review_notes):
        chamou_sintese["valor"] = True
        return ["síntese calculada"]

    monkeypatch.setattr(workflow_module, "synthesize_recommendations", fake_sintese)

    resultado = workflow_module.finalize_ui_specification(
        UISpecification(id="UI-001", title="t", context_problem="c")
    )

    assert chamou_sintese["valor"] is True
    assert resultado.recommendations_synthesis == ["síntese calculada"]


def test_refine_and_finalize_ui_specification_revalida_e_revisa_apos_o_refino(monkeypatch):
    """Regressão (mesmo bug real já corrigido nos agentes irmãos): refinar sem revalidar deixaria status/review_notes obsoletos para sempre."""
    spec = UISpecification(
        id="UI-001",
        title="t",
        context_problem="c",
        review_notes=["nenhuma tela identificada"],
    )
    monkeypatch.setattr(
        workflow_module,
        "_refinar_campos",
        lambda spec, respostas: _spec_completa(),
    )
    monkeypatch.setattr(workflow_module, "validate_ui_specification", lambda spec: [])
    monkeypatch.setattr(
        workflow_module,
        "review_ui_specification",
        lambda spec: {"aprovado": True, "problemas": []},
    )

    resultado = workflow_module.refine_and_finalize_ui_specification(
        spec, [{"pergunta": "p", "resposta": "r"}]
    )

    assert resultado.status == ArtifactStatus.DRAFT_VALIDATED
    assert resultado.review_notes == []
