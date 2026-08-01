from ..models import UISpecification
from ..services.llm_service import complete_json, reviewer_model
from ._material_design_3_catalog import COMPONENTES_MD3
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você é um revisor de UI Specifications, independente de quem as gerou. O catálogo fechado "
    "de componentes Material Design 3 desta plataforma será informado literalmente no prompt — "
    "use exatamente essa lista para julgar se um componente existe no catálogo, nunca o seu "
    "próprio conhecimento geral sobre o Material Design 3 (o catálogo desta plataforma pode "
    "usar nomes/singular-plural diferentes do site oficial; a lista informada é sempre a fonte "
    "de verdade). Verifique também se todo componente identificado tem estados de interação "
    "definidos (no nível de tela é aceitável nesta fase — não exija estados por componente "
    "individual), e se toda tela tem ao menos uma recomendação de acessibilidade associada ao "
    "conjunto. Aponte problemas reais; nunca aprove algo com justificativa vaga. Cada problema "
    "apontado deve ser uma única string de texto, nunca um objeto/dicionário com campos "
    "separados."
)


def _checagens_deterministicas(spec: UISpecification) -> list[str]:
    """Checagem determinística (Python puro) das duas regras mais críticas antes de perguntar
    ao LLM — garante GR-UI-1 mesmo se o revisor (LLM) deixar passar um componente inválido
    reintroduzido por um refino posterior, e mesmo se a chamada ao LLM revisor falhar em
    perceber a ausência de estados."""
    problemas = []
    for tela in spec.screens:
        for componente in tela.components:
            if componente not in COMPONENTES_MD3:
                problemas.append(
                    f"Tela '{tela.name}': componente '{componente}' fora do catálogo fechado "
                    "Material Design 3 (GR-UI-1)"
                )
        if tela.components and not tela.states:
            problemas.append(
                f"Tela '{tela.name}': componente(s) identificado(s) sem estados de interação definidos"
            )
    if spec.screens and not spec.accessibility_recommendations:
        problemas.append("nenhuma recomendação de acessibilidade associada às telas identificadas")
    return problemas


def review_ui_specification(spec: UISpecification) -> dict:
    """Revisa a UI Specification com um LLM diferente do gerador, combinado com uma checagem
    determinística do catálogo fechado Material Design 3 (GR-UI-1) — sempre um modelo
    diferente do gerador, para mitigar self-preference bias."""
    problemas_deterministicos = _checagens_deterministicas(spec)

    modelo = reviewer_model()
    telas = [
        {"nome": tela.name, "componentes": tela.components, "estados": tela.states}
        for tela in spec.screens
    ]
    catalogo = ", ".join(COMPONENTES_MD3)
    prompt = (
        f"Catálogo fechado de componentes Material Design 3 (fonte de verdade — use exatamente "
        f"esta lista, não o seu conhecimento geral): {catalogo}\n\n"
        f"Título: {spec.title}\n"
        f"Contexto: {spec.context_problem}\n"
        f"Telas: {telas}\n"
        f"Design tokens sugeridos: cores={spec.design_tokens.colors}, "
        f"tipografia={spec.design_tokens.typography}, espaçamento={spec.design_tokens.spacing}\n"
        f"Notas de layout responsivo: {spec.responsive_notes}\n"
        f"Recomendações de acessibilidade: {spec.accessibility_recommendations}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    problemas_llm = lista_de_strings(dados.get("problemas", []))
    aprovado = bool(dados.get("aprovado", False)) and not problemas_deterministicos

    return {
        "aprovado": aprovado,
        "problemas": problemas_deterministicos + problemas_llm,
    }
