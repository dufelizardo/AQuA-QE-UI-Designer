from aqua_qe_ui_designer.models import UISpecification
from aqua_qe_ui_designer.orchestrator import ui_designer as module


def test_handle_request_delegates_to_workflow(monkeypatch):
    esperado = UISpecification(id="UI-001", title="t", context_problem="c")
    captured = {}

    def fake_generate(texto_uxs, uxs_reference):
        captured["texto_uxs"] = texto_uxs
        captured["uxs_reference"] = uxs_reference
        return esperado

    monkeypatch.setattr(module, "generate_ui_specification", fake_generate)

    resultado = module.handle_request("uxs", "url-uxs")

    assert resultado is esperado
    assert captured == {"texto_uxs": "uxs", "uxs_reference": "url-uxs"}


def test_handle_request_default_reference_is_empty_string(monkeypatch):
    esperado = UISpecification(id="UI-001", title="t", context_problem="c")
    captured = {}

    def fake_generate(texto_uxs, uxs_reference):
        captured["uxs_reference"] = uxs_reference
        return esperado

    monkeypatch.setattr(module, "generate_ui_specification", fake_generate)

    module.handle_request("uxs")

    assert captured["uxs_reference"] == ""
