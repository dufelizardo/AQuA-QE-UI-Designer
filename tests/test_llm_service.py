import pytest

from aqua_qe_ui_designer.services import llm_service


def test_generator_model_default_is_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    assert llm_service.generator_model() == "mistral"


def test_reviewer_model_default_is_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OLLAMA_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "phi4"


def test_generator_model_respects_explicit_ollama_env(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_generator_model_uses_nvidia_default_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)

    assert llm_service.generator_model() == "deepseek-ai/deepseek-v4-pro"


def test_reviewer_model_uses_nvidia_default_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.delenv("NVIDIA_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "meta/llama-3.3-70b-instruct"


def test_generator_model_respects_explicit_nvidia_model_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_generator_model_uses_cerebras_default_when_provider_is_cerebras(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cerebras")
    monkeypatch.delenv("CEREBRAS_MODEL", raising=False)

    assert llm_service.generator_model() == "gpt-oss-120b"


def test_reviewer_model_uses_cerebras_default_when_provider_is_cerebras(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cerebras")
    monkeypatch.delenv("CEREBRAS_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "zai-glm-4.7"


def test_generator_model_respects_explicit_cerebras_model_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cerebras")
    monkeypatch.setenv("CEREBRAS_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_generator_model_uses_google_default_when_provider_is_google(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.delenv("GOOGLE_MODEL", raising=False)

    assert llm_service.generator_model() == "gemini-3.1-flash-lite"


def test_reviewer_model_uses_google_default_when_provider_is_google(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.delenv("GOOGLE_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "gemini-2.5-flash-lite"


def test_generator_model_respects_explicit_google_model_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.setenv("GOOGLE_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_generator_model_uses_groq_default_when_provider_is_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_MODEL", raising=False)

    assert llm_service.generator_model() == "llama-3.3-70b-versatile"


def test_reviewer_model_uses_groq_default_when_provider_is_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "openai/gpt-oss-120b"


def test_generator_model_respects_explicit_groq_model_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_complete_json_dispatches_to_ollama_by_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["model"] = model
            captured["messages"] = messages
            captured["kwargs"] = kwargs
            return {"message": {"content": '{"ok": true}'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    resultado = llm_service.complete_json("pergunta", system="sistema")

    assert resultado == {"ok": True}
    assert captured["model"] == "mistral"
    assert captured["kwargs"] == {"format": "json"}
    assert captured["messages"] == [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pergunta"},
    ]


def test_complete_dispatches_to_ollama_without_json_format(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["kwargs"] = kwargs
            return {"message": {"content": "resposta em texto"}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    resultado = llm_service.complete("pergunta")

    assert resultado == "resposta em texto"
    assert captured["kwargs"] == {}


def test_complete_json_dispatches_to_nvidia_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"ok": True}
    assert captured["model"] == "deepseek-ai/deepseek-v4-pro"
    assert captured["kwargs"] == {"response_format": {"type": "json_object"}}


def test_complete_json_dispatches_to_cerebras_when_provider_is_cerebras(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cerebras")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeCerebrasClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_cerebras_client", lambda: FakeCerebrasClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"ok": True}
    assert captured["model"] == "gpt-oss-120b"
    assert captured["kwargs"] == {"response_format": {"type": "json_object"}}


def test_complete_json_dispatches_to_google_when_provider_is_google(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeGoogleClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_google_client", lambda: FakeGoogleClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"ok": True}
    assert captured["model"] == "gemini-3.1-flash-lite"
    assert captured["kwargs"] == {"max_tokens": 8192, "response_format": {"type": "json_object"}}


def test_complete_json_dispatches_to_groq_when_provider_is_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeGroqClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_groq_client", lambda: FakeGroqClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"ok": True}
    assert captured["model"] == "llama-3.3-70b-versatile"
    assert captured["kwargs"] == {"response_format": {"type": "json_object"}}


def test_complete_json_uses_deepseek_reasoning_params_when_explicitly_selected(monkeypatch):
    """deepseek-ai/deepseek-v4-flash não é o default (saturou por capacidade no piloto do PM),
    mas continua com params dedicados em _NVIDIA_MODEL_PARAMS caso seja selecionado manualmente."""
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    resultado = llm_service.complete_json("pergunta", model="deepseek-ai/deepseek-v4-flash")

    assert resultado == {"ok": True}
    assert captured["model"] == "deepseek-ai/deepseek-v4-flash"
    assert captured["kwargs"] == {
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
        "response_format": {"type": "json_object"},
    }


def test_nvidia_unrecognized_model_falls_back_to_no_extra_params(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = "resposta em texto"

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    llm_service.complete("pergunta", model="algum/modelo-desconhecido")

    assert captured["kwargs"] == {}


def test_complete_json_raises_on_invalid_json_regardless_of_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            return {"message": {"content": "isto não é json"}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    with pytest.raises(ValueError):
        llm_service.complete_json("pergunta")


def test_complete_json_rejects_non_dict_json(monkeypatch):
    """Regressão: um agente irmão desta plataforma quebrou ao vivo quando o LLM devolveu uma
    lista JSON em vez de um objeto — complete_json deve rejeitar isso explicitamente."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            return {"message": {"content": "[1, 2, 3]"}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    with pytest.raises(ValueError):
        llm_service.complete_json("pergunta")


def test_complete_json_tolera_chaves_extras_apos_json_valido(monkeypatch):
    """Achado ao vivo: o Gemini às vezes devolve um objeto JSON válido seguido de chaves de
    fechamento sobrando, mesmo com response_format=json_object. complete_json deve aceitar o
    primeiro objeto válido e ignorar o lixo depois, em vez de rejeitar a resposta inteira."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            return {"message": {"content": '{"titulo": "Exemplo"}\n}\n}'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"titulo": "Exemplo"}


def test_complete_json_ainda_rejeita_json_truncado(monkeypatch):
    """Regressão: JSON genuinamente incompleto (não apenas com lixo depois) continua
    levantando ValueError — a tolerância é só para conteúdo extra após um objeto completo."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            return {"message": {"content": '{"titulo": "Exemplo", "itens": ["a", "b"'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    with pytest.raises(ValueError):
        llm_service.complete_json("pergunta")


def test_explicit_model_argument_overrides_generator_model(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["model"] = model
            return {"message": {"content": '{"ok": true}'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    llm_service.complete_json("pergunta", model="modelo-especifico")

    assert captured["model"] == "modelo-especifico"
