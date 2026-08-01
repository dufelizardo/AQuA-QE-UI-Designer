import httpx

from aqua_qe_ui_designer.services import confluence_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_storage_para_texto_strips_tags_and_decodes_entities():
    html = "<h1>T&iacute;tulo</h1><p>Primeiro par&aacute;grafo.</p><ul><li>Item 1</li></ul>"

    resultado = confluence_service._storage_para_texto(html)

    assert "Título" in resultado
    assert "Primeiro parágrafo." in resultado
    assert "Item 1" in resultado


def test_get_page_text_extracts_title_and_body(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {
        "title": "Meu PRD",
        "body": {"storage": {"value": "<p>Conteúdo da página.</p>"}},
    }

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/wiki/rest/api/content/163841"
        assert auth == ("user@example.com", "token")
        assert params == {"expand": "body.storage"}
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    resultado = confluence_service.get_page_text("163841")

    assert "Meu PRD" in resultado
    assert "Conteúdo da página." in resultado


def test_get_page_parent_context_returns_space_and_immediate_ancestor(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {
        "space": {"key": "AQuAQE"},
        "ancestors": [{"id": "950440"}, {"id": "1212417"}],
    }

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/wiki/rest/api/content/1179649"
        assert params == {"expand": "space,ancestors"}
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    space_key, ancestral = confluence_service.get_page_parent_context("1179649")

    assert space_key == "AQuAQE"
    assert ancestral == "1212417"


def test_get_page_parent_context_returns_none_when_page_has_no_ancestors(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {"space": {"key": "AQuAQE"}, "ancestors": []}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResponse(payload))

    _, ancestral = confluence_service.get_page_parent_context("1179649")

    assert ancestral is None


def test_texto_para_storage_converte_headings_e_listas():
    texto = "# Título\n\n## Seção\n\n### Subseção\n\n- item 1\n- item 2\n\nParágrafo solto."

    resultado = confluence_service._texto_para_storage(texto)

    assert "<h1>Título</h1>" in resultado
    assert "<h2>Seção</h2>" in resultado
    assert "<h3>Subseção</h3>" in resultado
    assert "<ul><li>item 1</li><li>item 2</li></ul>" in resultado
    assert "<p>Parágrafo solto.</p>" in resultado


def test_texto_para_storage_converte_negrito_markdown():
    resultado = confluence_service._texto_para_storage("- **Termo**: definição do termo")

    assert resultado == "<ul><li><strong>Termo</strong>: definição do termo</li></ul>"


def test_texto_para_storage_agrupa_lista_numerada_em_ol():
    resultado = confluence_service._texto_para_storage("1. primeiro passo\n2. segundo passo")

    assert resultado == "<ol><li>primeiro passo</li><li>segundo passo</li></ol>"


def test_texto_para_storage_nao_mistura_ul_e_ol_na_mesma_lista():
    resultado = confluence_service._texto_para_storage("- item solto\n1. passo 1\n2. passo 2")

    assert resultado == (
        "<ul><li>item solto</li></ul><ol><li>passo 1</li><li>passo 2</li></ol>"
    )


def test_texto_para_storage_converte_tabela_markdown():
    texto = (
        "## Componentes\n\n"
        "| Componente | Responsabilidade |\n"
        "|---|---|\n"
        "| API Gateway | Rotear requisições |\n"
        "| Serviço de Agendamento | Gerenciar consultas |\n\n"
        "Texto depois da tabela"
    )

    resultado = confluence_service._texto_para_storage(texto)

    assert resultado == (
        "<h2>Componentes</h2>"
        "<table><tbody>"
        "<tr><th>Componente</th><th>Responsabilidade</th></tr>"
        "<tr><td>API Gateway</td><td>Rotear requisições</td></tr>"
        "<tr><td>Serviço de Agendamento</td><td>Gerenciar consultas</td></tr>"
        "</tbody></table>"
        "<p>Texto depois da tabela</p>"
    )


def test_texto_para_storage_tabela_sem_conteudo_depois_fecha_corretamente():
    texto = "| a | b |\n|---|---|\n| 1 | 2 |"

    resultado = confluence_service._texto_para_storage(texto)

    assert resultado == "<table><tbody><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></tbody></table>"


def test_create_page_posts_body_with_ancestor_and_returns_id(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    def fake_post(url, auth=None, json=None, timeout=None):
        assert url == "https://example.atlassian.net/wiki/rest/api/content"
        assert json["space"] == {"key": "AQuAQE"}
        assert json["title"] == "UXS - Mais Saúde Pública"
        assert json["ancestors"] == [{"id": "1212417"}]
        return _FakeResponse({"id": "999999"})

    monkeypatch.setattr(httpx, "post", fake_post)

    page_id = confluence_service.create_page(
        "AQuAQE", "UXS - Mais Saúde Pública", "# Título\n\ncontexto", "1212417"
    )

    assert page_id == "999999"


def test_create_page_sem_parent_nao_envia_ancestors(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    def fake_post(url, auth=None, json=None, timeout=None):
        assert "ancestors" not in json
        return _FakeResponse({"id": "1"})

    monkeypatch.setattr(httpx, "post", fake_post)

    confluence_service.create_page("AQuAQE", "t", "texto")


def test_update_page_busca_versao_atual_e_incrementa(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    chamadas = {"put_json": None}

    def fake_get(url, auth=None, params=None, timeout=None):
        assert params == {"expand": "version"}
        return _FakeResponse({"title": "UXS - Mais Saúde Pública", "version": {"number": 3}})

    def fake_put(url, auth=None, json=None, timeout=None):
        chamadas["put_json"] = json
        return _FakeResponse({})

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(httpx, "put", fake_put)

    confluence_service.update_page("999999", "# Título\n\nnovo conteúdo")

    assert chamadas["put_json"]["version"]["number"] == 4
    assert chamadas["put_json"]["title"] == "UXS - Mais Saúde Pública"
