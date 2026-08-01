from ..models import DesignTokensSuggestion
from ..services.llm_service import complete_json
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você sugere candidatos de design tokens (cores, tipografia, espaçamento) para uma UI "
    "Specification, sempre rotulados como SUGESTÃO A CONFIRMAR com o time de Design — nunca "
    "afirme que são a identidade visual real e já estabelecida do produto, a menos que a UX "
    "Specification/PRD de origem já a especifique explicitamente (GR-UI-2). Baseie-se apenas "
    "no que a fonte descreve; prefira citar o que já é real/conhecido a inventar uma "
    "identidade visual nova (GR-UI-5). Cada token deve ser uma única string de texto (ex.: "
    "'primary: tom de azul, para ações principais'), nunca um objeto/dicionário com campos "
    "separados."
)


def suggest_design_tokens(texto_uxs: str, contexto: dict) -> DesignTokensSuggestion:
    """Sugere candidatos de design tokens (cores/tipografia/espaçamento) — sempre como
    sugestão a confirmar, nunca como identidade visual definitiva do produto (GR-UI-2)."""
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        'Responda apenas em JSON: {"cores": ["..."], "tipografia": ["..."], "espacamento": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    campos = ("nome",)
    return DesignTokensSuggestion(
        colors=lista_de_strings(dados.get("cores", []), campos_prioritarios=campos),
        typography=lista_de_strings(dados.get("tipografia", []), campos_prioritarios=campos),
        spacing=lista_de_strings(dados.get("espacamento", []), campos_prioritarios=campos),
    )
