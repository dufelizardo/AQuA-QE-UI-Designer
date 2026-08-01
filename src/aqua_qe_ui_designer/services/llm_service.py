import json
import os

import ollama
from openai import OpenAI

_DEFAULT_MODEL = "mistral"
_DEFAULT_REVIEW_MODEL = "phi4"
_DEFAULT_NVIDIA_MODEL = "deepseek-ai/deepseek-v4-pro"
_DEFAULT_NVIDIA_REVIEW_MODEL = "meta/llama-3.3-70b-instruct"
_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
# Modelos e achados de instabilidade em uso real (503/404/timeout) já documentados nos
# agentes irmãos AQuA-QE Product Manager/Product Owner/Solution Architect/UX Designer —
# motivou avaliar Cerebras e Google AI Studio como provedores alternativos (ver
# LLM_PROVIDER=cerebras|google abaixo). Fallback documentado se deepseek-v4-pro saturar por
# capacidade: openai/gpt-oss-120b, status "Preview" nesta conta NVIDIA.

_DEFAULT_CEREBRAS_MODEL = "gpt-oss-120b"
_DEFAULT_CEREBRAS_REVIEW_MODEL = "zai-glm-4.7"
_CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"

# gemini-3.1-flash-lite (gerador) e gemini-2.5-flash-lite (revisor) — mesmos modelos já
# validados ao vivo com sucesso nos agentes irmãos (Solution Design/PRD real gerado de
# ponta a ponta sem erro). Rate limit baixo no tier gratuito (15 req/min) para lotes
# grandes — motivou avaliar Groq como quarto provedor.
_DEFAULT_GOOGLE_MODEL = "gemini-3.1-flash-lite"
_DEFAULT_GOOGLE_REVIEW_MODEL = "gemini-2.5-flash-lite"
_GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Sem isso, a resposta vem truncada em conteúdo real mais rico (achado ao vivo nos agentes
# irmãos) — o default de max_tokens da API do Google é pequeno demais para esse tipo de
# agente. Aplicado a qualquer modelo Google, não chaveado por modelo.
_GOOGLE_DEFAULT_PARAMS: dict = {"max_tokens": 8192}

# Groq confirmado pelo usuário com 30 req/min tanto no gerador quanto no revisor — folga
# maior que qualquer tier gratuito do Google testado, o mais estável em uso real desta
# plataforma até agora (validado ao vivo no Product Owner processando um PRD real em lote).
_DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
_DEFAULT_GROQ_REVIEW_MODEL = "openai/gpt-oss-120b"
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Parâmetros de sampling recomendados pela NVIDIA por modelo NIM (build.nvidia.com/playground)
# — chaveados por nome do modelo, não por papel (gerador/revisor), para continuar corretos se
# um dos dois for trocado via NVIDIA_MODEL/NVIDIA_REVIEW_MODEL. Modelo sem entrada aqui usa a
# chamada sem parâmetros extras (só model/messages/response_format).
_NVIDIA_MODEL_PARAMS: dict[str, dict] = {
    "deepseek-ai/deepseek-v4-flash": {
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
    },
}


def _nvidia_params(modelo: str) -> dict:
    return dict(_NVIDIA_MODEL_PARAMS.get(modelo, {}))


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "ollama")


def _ollama_client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def _nvidia_client() -> OpenAI:
    return OpenAI(base_url=_NVIDIA_BASE_URL, api_key=os.environ["NVIDIA_API_KEY"])


def _cerebras_client() -> OpenAI:
    return OpenAI(base_url=_CEREBRAS_BASE_URL, api_key=os.environ["CEREBRAS_API_KEY"])


def _google_client() -> OpenAI:
    return OpenAI(base_url=_GOOGLE_BASE_URL, api_key=os.environ["GOOGLE_API_KEY"])


def _groq_client() -> OpenAI:
    return OpenAI(base_url=_GROQ_BASE_URL, api_key=os.environ["GROQ_API_KEY"])


def generator_model() -> str:
    """Resolve o modelo gerador conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia|cerebras|google|groq)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_MODEL", _DEFAULT_NVIDIA_MODEL)
    if _provider() == "cerebras":
        return os.getenv("CEREBRAS_MODEL", _DEFAULT_CEREBRAS_MODEL)
    if _provider() == "google":
        return os.getenv("GOOGLE_MODEL", _DEFAULT_GOOGLE_MODEL)
    if _provider() == "groq":
        return os.getenv("GROQ_MODEL", _DEFAULT_GROQ_MODEL)
    return os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)


def reviewer_model() -> str:
    """Resolve o modelo revisor conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia|cerebras|google|groq)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_REVIEW_MODEL", _DEFAULT_NVIDIA_REVIEW_MODEL)
    if _provider() == "cerebras":
        return os.getenv("CEREBRAS_REVIEW_MODEL", _DEFAULT_CEREBRAS_REVIEW_MODEL)
    if _provider() == "google":
        return os.getenv("GOOGLE_REVIEW_MODEL", _DEFAULT_GOOGLE_REVIEW_MODEL)
    if _provider() == "groq":
        return os.getenv("GROQ_REVIEW_MODEL", _DEFAULT_GROQ_REVIEW_MODEL)
    return os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)


def _chat(modelo: str, messages: list[dict], json_mode: bool) -> str:
    provider = _provider()
    if provider in ("nvidia", "cerebras", "google", "groq"):
        if provider == "nvidia":
            kwargs = _nvidia_params(modelo)
        elif provider == "google":
            kwargs = dict(_GOOGLE_DEFAULT_PARAMS)
        else:
            kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if provider == "nvidia":
            cliente = _nvidia_client()
        elif provider == "cerebras":
            cliente = _cerebras_client()
        elif provider == "google":
            cliente = _google_client()
        else:
            cliente = _groq_client()
        resposta = cliente.chat.completions.create(model=modelo, messages=messages, **kwargs)
        return resposta.choices[0].message.content

    kwargs = {"format": "json"} if json_mode else {}
    resposta = _ollama_client().chat(model=modelo, messages=messages, **kwargs)
    return resposta["message"]["content"]


def complete(prompt: str, system: str = "", model: str | None = None) -> str:
    """Envia um prompt ao provedor de LLM ativo (Ollama ou provedor em nuvem) e retorna o texto de resposta."""
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    return _chat(modelo, messages, json_mode=False)


def complete_json(prompt: str, system: str = "", model: str | None = None) -> dict:
    """Envia um prompt ao provedor de LLM ativo e retorna a resposta já parseada como JSON.

    Usa `raw_decode` em vez de `json.loads` — aceita o primeiro objeto JSON válido e ignora
    qualquer lixo depois dele (mesmo achado ao vivo já documentado nos agentes irmãos).
    Rejeita explicitamente qualquer JSON que não seja um objeto (ex.: uma lista bruta), erro
    real já visto em outro agente irmão desta plataforma.
    """
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    conteudo = _chat(modelo, messages, json_mode=True)
    try:
        dados, _ = json.JSONDecoder().raw_decode(conteudo.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Resposta do LLM não é um JSON válido: {conteudo!r}") from exc
    if not isinstance(dados, dict):
        raise ValueError(f"Resposta do LLM não é um objeto JSON: {conteudo!r}")
    return dados
