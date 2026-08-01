from aqua_qe_ui_designer.skills import update_confluence_page as update_confluence_page_module
from aqua_qe_ui_designer.skills.update_confluence_page import update_confluence_page


def test_update_confluence_page_extrai_id_da_url(monkeypatch):
    chamadas = {}

    def fake_update_page(page_id, texto):
        chamadas["page_id"] = page_id
        chamadas["texto"] = texto

    monkeypatch.setattr(update_confluence_page_module, "update_page", fake_update_page)

    update_confluence_page(
        "https://example.atlassian.net/wiki/spaces/AQuAQE/pages/999999/UXS", "# texto"
    )

    assert chamadas["page_id"] == "999999"
    assert chamadas["texto"] == "# texto"


def test_update_confluence_page_aceita_id_puro(monkeypatch):
    chamadas = {}
    monkeypatch.setattr(
        update_confluence_page_module,
        "update_page",
        lambda page_id, texto: chamadas.update(page_id=page_id),
    )

    update_confluence_page("999999", "# texto")

    assert chamadas["page_id"] == "999999"
