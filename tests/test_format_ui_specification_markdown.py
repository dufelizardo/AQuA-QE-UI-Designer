from aqua_qe_ui_designer.models import (
    ComponentSpec,
    DesignTokensSuggestion,
    PrioritizedRecommendation,
    StateSpec,
    UIScreen,
    UISpecification,
)
from aqua_qe_ui_designer.skills.format_ui_specification_markdown import (
    format_ui_specification_markdown,
)


def test_format_ui_specification_markdown_includes_all_fields():
    spec = UISpecification(
        id="UI-001",
        title="Agendamento de Consulta",
        context_problem="Paciente precisa agendar uma consulta pelo app",
        screens=[
            UIScreen(
                name="Tela de Agendamento",
                components=[
                    ComponentSpec(name="Cards"),
                    ComponentSpec(
                        name="Buttons",
                        variant="Filled",
                        size="Large",
                        icon="add",
                        notes="ação principal",
                    ),
                ],
                states=[
                    StateSpec(name="hover"),
                    StateSpec(name="loading", context="enquanto consulta horários disponíveis"),
                ],
                hierarchy=["Título", "Descrição", "Botão principal"],
                empty_states=["Nenhum horário disponível no momento."],
                error_states=["Não foi possível carregar os horários. Tente novamente."],
                source_reference="trecho 1",
            )
        ],
        design_tokens=DesignTokensSuggestion(
            colors=["primary: azul, para ações principais"],
            typography=["title-large"],
            spacing=["16dp"],
        ),
        responsive_notes="Usar window size class compact em telas menores",
        accessibility_recommendations=["verificar contraste (WCAG 1.4.3)"],
        source_reference="texto fonte completo",
        uxs_reference="https://example.atlassian.net/wiki/pages/1179649/UXS",
        figma_file_reference="",
        review_notes=["Tela sem estados de erro definidos"],
        recommendations_synthesis=[
            PrioritizedRecommendation(
                priority="Alta", text="priorizar contraste e estados de erro"
            )
        ],
        interface_messages=["Deseja realmente cancelar o agendamento?"],
        navigation_sequence=["Tela de Agendamento"],
        icons=["calendar_today", "add"],
        motion_notes="Transições seguem o Material Motion do Material Design 3.",
    )

    resultado = format_ui_specification_markdown(spec)

    assert "# Agendamento de Consulta" in resultado
    assert "**ID**: UI-001" in resultado
    assert "**Status**: pending_clarification" in resultado
    assert "Paciente precisa agendar uma consulta pelo app" in resultado
    assert "**UX Specification de origem**: https://example.atlassian.net/wiki/pages/1179649/UXS" in resultado
    assert "GR-UI-4" in resultado
    assert "### Tela de Agendamento" in resultado
    assert "- Cards" in resultado
    assert "- Buttons (Filled, Large) — ícone: add; nota: ação principal" in resultado
    assert "1. Título" in resultado
    assert "2. Descrição" in resultado
    assert "3. Botão principal" in resultado
    assert "- **Tela de Agendamento**: hover, loading — enquanto consulta horários disponíveis" in resultado
    assert "Nenhum horário disponível no momento." in resultado
    assert "Não foi possível carregar os horários. Tente novamente." in resultado
    assert "GR-UI-6" in resultado
    assert "primary: azul, para ações principais" in resultado
    assert "sugestão a confirmar" in resultado
    assert "Usar window size class compact em telas menores" in resultado
    assert "- verificar contraste (WCAG 1.4.3)" in resultado
    assert "| Prioridade | Recomendação |" in resultado
    assert "| Alta | priorizar contraste e estados de erro |" in resultado
    assert "Tela de Agendamento" in resultado.split("## 9. Navegação")[1]
    assert "Deseja realmente cancelar o agendamento?" in resultado
    assert "- calendar_today" in resultado
    assert "- add" in resultado
    assert "Transições seguem o Material Motion do Material Design 3." in resultado
    assert "GR-UI-8" in resultado
    assert "| Tela: Tela de Agendamento | trecho 1 |" in resultado
    assert "| UX Specification de origem | https://example.atlassian.net/wiki/pages/1179649/UXS |" in resultado


def test_format_ui_specification_markdown_navegacao_renderiza_cadeia_de_setas():
    spec = UISpecification(
        id="UI-002",
        title="t",
        context_problem="c",
        navigation_sequence=["Tela A", "Tela B", "Tela C"],
    )

    resultado = format_ui_specification_markdown(spec)

    assert "Tela A → Tela B → Tela C" in resultado


def test_format_ui_specification_markdown_recomendacoes_ordenadas_alta_media_baixa():
    spec = UISpecification(
        id="UI-003",
        title="t",
        context_problem="c",
        recommendations_synthesis=[
            PrioritizedRecommendation(priority="Baixa", text="item baixo"),
            PrioritizedRecommendation(priority="Alta", text="item alto"),
            PrioritizedRecommendation(priority="Média", text="item médio"),
        ],
    )

    resultado = format_ui_specification_markdown(spec)
    tabela = resultado.split("## 8. Recomendações")[1].split("## 9.")[0]

    posicao_alta = tabela.index("item alto")
    posicao_media = tabela.index("item médio")
    posicao_baixa = tabela.index("item baixo")
    assert posicao_alta < posicao_media < posicao_baixa


def test_format_ui_specification_markdown_omits_empty_sections_gracefully():
    spec = UISpecification(id="UI-004", title="t", context_problem="c")

    resultado = format_ui_specification_markdown(spec)

    assert "(nenhuma)" in resultado
    assert "(nenhum)" in resultado
    assert "(nenhuma nota)" in resultado
    assert "**UX Specification de origem**: (não informado)" in resultado
    assert "fora de escopo nesta fase" in resultado


def test_format_ui_specification_markdown_tela_sem_componentes_e_sem_hierarquia():
    spec = UISpecification(
        id="UI-005",
        title="t",
        context_problem="c",
        screens=[UIScreen(name="Tela vazia")],
    )

    resultado = format_ui_specification_markdown(spec)

    assert "(nenhum identificado)" in resultado
    assert "(não definida)" in resultado


def test_format_ui_specification_markdown_rastreabilidade_achata_trecho_multilinha():
    trecho_multilinha = "Linha um.\nLinha dois.\nLinha três."
    spec = UISpecification(
        id="UI-006",
        title="t",
        context_problem="c",
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
                source_reference=trecho_multilinha,
            )
        ],
    )

    resultado = format_ui_specification_markdown(spec)

    assert "| Tela: Tela | Linha um. Linha dois. Linha três. |" in resultado
    linha_tabela = next(
        linha for linha in resultado.splitlines() if linha.startswith("| Tela: Tela")
    )
    assert "\n" not in linha_tabela


def test_format_ui_specification_markdown_rastreabilidade_trunca_trecho_longo():
    trecho_longo = "x" * 500
    spec = UISpecification(
        id="UI-007",
        title="t",
        context_problem="c",
        screens=[
            UIScreen(
                name="Tela",
                components=[ComponentSpec(name="Cards")],
                states=[StateSpec(name="hover")],
                source_reference=trecho_longo,
            )
        ],
    )

    resultado = format_ui_specification_markdown(spec)

    assert f"| Tela: Tela | {'x' * 200}… |" in resultado


def test_format_ui_specification_markdown_shows_figma_reference_when_present():
    spec = UISpecification(
        id="UI-008", title="t", context_problem="c", figma_file_reference="https://figma.com/file/abc"
    )

    resultado = format_ui_specification_markdown(spec)

    assert "**Arquivo Figma de referência**: https://figma.com/file/abc" in resultado
