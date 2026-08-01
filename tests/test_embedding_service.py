import ollama

from aqua_qe_ui_designer.services import embedding_service


def test_embed_uses_default_model_and_host(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, host):
            captured["host"] = host

        def embed(self, model, input):
            captured["model"] = model
            captured["input"] = input
            return {"embeddings": [[0.1, 0.2]]}

    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_EMBEDDING_MODEL", raising=False)
    monkeypatch.setattr(ollama, "Client", FakeClient)

    resultado = embedding_service.embed(["texto"])

    assert resultado == [[0.1, 0.2]]
    assert captured["host"] == "http://localhost:11434"
    assert captured["model"] == "bge-m3"
    assert captured["input"] == ["texto"]


def test_embed_respects_env_overrides(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, host):
            captured["host"] = host

        def embed(self, model, input):
            captured["model"] = model
            return {"embeddings": []}

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:1234")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "outro-modelo")
    monkeypatch.setattr(ollama, "Client", FakeClient)

    embedding_service.embed(["a"])

    assert captured["host"] == "http://custom:1234"
    assert captured["model"] == "outro-modelo"
