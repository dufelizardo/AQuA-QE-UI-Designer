from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você redige rascunhos de copy para os estados vazio (empty state) e de erro (error state) "
    "de uma tela de uma UI Specification. Deixe sempre explícito, no seu próprio critério de "
    "geração, que este texto é um RASCUNHO A CONFIRMAR com o time de conteúdo/produto — nunca "
    "afirme que é a copy final e já aprovada (GR-UI-6, mesmo tratamento de GR-UI-2 para design "
    "tokens). Baseie-se apenas em cenários de falha/vazio plausíveis a partir do propósito real "
    "da tela descrito na UX Specification (ex.: 'nenhum horário disponível' faz sentido para "
    "uma tela que lista horários de agendamento) — nunca fabrique um cenário genérico sem "
    "relação com o que a tela realmente faz. Cada item deve ser uma única string de texto, "
    "nunca um objeto/dicionário com campos separados. Responda sempre em português."
)


def draft_empty_and_error_states(
    texto_uxs: str, tela_nome: str, contexto: dict
) -> tuple[list[str], list[str]]:
    """Gera rascunhos de copy (a confirmar com o time de conteúdo/produto, GR-UI-6) para os
    estados vazio e de erro de uma tela, grounded nos cenários de falha/vazio plausíveis a
    partir do propósito real da tela na UX Specification."""
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"Tela: {tela_nome}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        "Responda apenas em JSON, com cada item marcado como rascunho a confirmar: "
        '{"estados_vazios": ["..."], "estados_de_erro": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return (
        lista_de_strings(dados.get("estados_vazios", [])),
        lista_de_strings(dados.get("estados_de_erro", [])),
    )
