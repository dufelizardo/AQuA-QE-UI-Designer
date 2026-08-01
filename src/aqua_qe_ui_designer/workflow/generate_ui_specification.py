from ..models import ArtifactStatus, UISpecification
from ..skills.define_component_states import define_component_states
from ..skills.define_responsive_layout import define_responsive_layout
from ..skills.draft_empty_and_error_states import draft_empty_and_error_states
from ..skills.draft_interface_messages import draft_interface_messages
from ..skills.extract_ui_context import extract_ui_context
from ..skills.identify_screens_and_components import identify_screens_and_components
from ..skills.refine_ui_specification import refine_ui_specification as _refinar_campos
from ..skills.review_accessibility_visual import review_accessibility_visual
from ..skills.review_ui_specification import review_ui_specification
from ..skills.suggest_design_tokens import suggest_design_tokens
from ..skills.synthesize_recommendations import synthesize_recommendations
from ..skills.validate_ui_specification import validate_ui_specification

_MOTION_NOTES = (
    "Transições seguem o Material Motion do Material Design 3 — padrões de entrada/saída "
    "padrão; detalhamento de animações específicas fica fora de escopo nesta fase."
)


def finalize_ui_specification(spec: UISpecification) -> UISpecification:
    """Aplica o checklist automático e a revisão por LLM, decidindo o status final da UI Specification."""
    motivos_checklist = validate_ui_specification(spec)
    if motivos_checklist:
        spec.status = ArtifactStatus.PENDING_CLARIFICATION
        spec.review_notes = motivos_checklist
    else:
        revisao = review_ui_specification(spec)
        spec.review_notes = revisao["problemas"]
        spec.status = (
            ArtifactStatus.DRAFT_VALIDATED
            if revisao["aprovado"]
            else ArtifactStatus.PENDING_CLARIFICATION
        )

    spec.recommendations_synthesis = synthesize_recommendations(
        spec.accessibility_recommendations, spec.review_notes
    )
    return spec


def refine_and_finalize_ui_specification(
    spec: UISpecification, respostas: list[dict]
) -> UISpecification:
    """Reescreve a UI Specification com as respostas do usuário e reaplica validate/review, atualizando status e review_notes."""
    spec_refinada = _refinar_campos(spec, respostas)
    return finalize_ui_specification(spec_refinada)


def generate_ui_specification(texto_uxs: str, uxs_reference: str = "") -> UISpecification:
    """Gera a UI Specification a partir do texto da UX Specification de origem, orquestrando a
    sequência padrão de skills.

    `uxs_reference` é a URL/ID da UX Specification de origem informada pelo usuário (não o
    texto lido) — usada apenas para a seção 2 (Escopo) do export em Markdown, nunca para
    leitura.
    """
    contexto = extract_ui_context(texto_uxs)
    telas = identify_screens_and_components(texto_uxs, contexto)
    telas = define_component_states(telas)
    tokens = suggest_design_tokens(texto_uxs, contexto)
    notas_responsivas = define_responsive_layout(texto_uxs, contexto)
    recomendacoes_acessibilidade = review_accessibility_visual(telas)

    for tela in telas:
        tela.empty_states, tela.error_states = draft_empty_and_error_states(
            texto_uxs, tela.name, contexto
        )
    mensagens_interface = draft_interface_messages(texto_uxs, contexto)

    # Pura Python, sem chamada nova ao LLM — nunca uma re-derivação independente de fluxo/
    # navegação, que duplicaria o artefato próprio da UX Specification (GR-UI-8).
    sequencia_navegacao = [tela.name for tela in telas]

    # Pura Python, sem chamada nova ao LLM — dedup preservando a primeira ocorrência.
    icones = list(
        dict.fromkeys(
            componente.icon
            for tela in telas
            for componente in tela.components
            if componente.icon
        )
    )

    spec = UISpecification(
        id="UI-001",
        title=contexto["title"],
        context_problem=contexto["context_problem"],
        screens=telas,
        design_tokens=tokens,
        responsive_notes=notas_responsivas,
        accessibility_recommendations=recomendacoes_acessibilidade,
        source_reference=texto_uxs,
        uxs_reference=uxs_reference,
        interface_messages=mensagens_interface,
        navigation_sequence=sequencia_navegacao,
        icons=icones,
        motion_notes=_MOTION_NOTES,
    )
    return finalize_ui_specification(spec)
