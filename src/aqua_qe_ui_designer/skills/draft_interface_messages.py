from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você redige rascunhos de mensagens globais da interface de uma UI Specification (ex.: o "
    "texto de um diálogo de confirmação de cancelamento, uma mensagem genérica de erro de "
    "conexão). Deixe sempre explícito, no seu próprio critério de geração, que este texto é um "
    "RASCUNHO A CONFIRMAR com o time de conteúdo/produto — nunca afirme que é a copy final e já "
    "aprovada (GR-UI-6, mesmo tratamento de GR-UI-2 para design tokens). Baseie-se apenas em "
    "situações plausíveis a partir do que a UX Specification realmente descreve; nunca invente "
    "uma mensagem sem relação com o fluxo descrito. Cada item deve ser uma única string de "
    "texto, nunca um objeto/dicionário com campos separados. Responda sempre em português."
)


def draft_interface_messages(texto_uxs: str, contexto: dict) -> list[str]:
    """Gera rascunhos de mensagens globais da interface (a confirmar com o time de conteúdo/
    produto, GR-UI-6), grounded no que a UX Specification realmente descreve."""
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        "Responda apenas em JSON, com cada item marcado como rascunho a confirmar: "
        '{"mensagens": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return lista_de_strings(dados.get("mensagens", []))
