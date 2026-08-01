from aqua_qe_ui_designer.skills import (
    get_confluence_publish_location as get_confluence_publish_location_module,
)
from aqua_qe_ui_designer.skills.get_confluence_publish_location import (
    get_confluence_publish_location,
)


def test_get_confluence_publish_location_extrai_id_da_url(monkeypatch):
    def fake_get_page_parent_context(page_id):
        assert page_id == "1179649"
        return "AQuAQE", "1212417"

    monkeypatch.setattr(
        get_confluence_publish_location_module,
        "get_page_parent_context",
        fake_get_page_parent_context,
    )

    space_key, ancestral = get_confluence_publish_location(
        "https://example.atlassian.net/wiki/spaces/AQuAQE/pages/1179649/PRD"
    )

    assert space_key == "AQuAQE"
    assert ancestral == "1212417"


def test_get_confluence_publish_location_aceita_id_puro(monkeypatch):
    monkeypatch.setattr(
        get_confluence_publish_location_module,
        "get_page_parent_context",
        lambda page_id: ("AQuAQE", None),
    )

    space_key, ancestral = get_confluence_publish_location("1179649")

    assert space_key == "AQuAQE"
    assert ancestral is None
