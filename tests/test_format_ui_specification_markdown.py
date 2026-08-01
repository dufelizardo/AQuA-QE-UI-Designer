from aqua_qe_ui_designer.models import DesignTokensSuggestion, UIScreen, UISpecification
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
                components=["Cards", "Buttons"],
                states=["hover", "disabled"],
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
        recommendations_synthesis=["priorizar contraste e estados de erro"],
    )

    resultado = format_ui_specification_markdown(spec)

    assert "# Agendamento de Consulta" in resultado
    assert "**ID**: UI-001" in resultado
    assert "**Status**: pending_clarification" in resultado
    assert "Paciente precisa agendar uma consulta pelo app" in resultado
    assert "**UX Specification de origem**: https://example.atlassian.net/wiki/pages/1179649/UXS" in resultado
    assert "GR-UI-4" in resultado
    assert "### Tela de Agendamento" in resultado
    assert "Componentes (Material Design 3): Cards, Buttons" in resultado
    assert "- **Tela de Agendamento**: hover, disabled" in resultado
    assert "primary: azul, para ações principais" in resultado
    assert "sugestão a confirmar" in resultado
    assert "Usar window size class compact em telas menores" in resultado
    assert "- verificar contraste (WCAG 1.4.3)" in resultado
    assert "- priorizar contraste e estados de erro" in resultado
    assert "| Tela: Tela de Agendamento | trecho 1 |" in resultado
    assert "| UX Specification de origem | https://example.atlassian.net/wiki/pages/1179649/UXS |" in resultado


def test_format_ui_specification_markdown_omits_empty_sections_gracefully():
    spec = UISpecification(id="UI-002", title="t", context_problem="c")

    resultado = format_ui_specification_markdown(spec)

    assert "(nenhuma)" in resultado
    assert "(nenhum)" in resultado
    assert "(nenhuma nota)" in resultado
    assert "**UX Specification de origem**: (não informado)" in resultado
    assert "fora de escopo nesta fase" in resultado


def test_format_ui_specification_markdown_rastreabilidade_achata_trecho_multilinha():
    trecho_multilinha = "Linha um.\nLinha dois.\nLinha três."
    spec = UISpecification(
        id="UI-003",
        title="t",
        context_problem="c",
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"], source_reference=trecho_multilinha)],
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
        id="UI-004",
        title="t",
        context_problem="c",
        screens=[UIScreen(name="Tela", components=["Cards"], states=["hover"], source_reference=trecho_longo)],
    )

    resultado = format_ui_specification_markdown(spec)

    assert f"| Tela: Tela | {'x' * 200}… |" in resultado


def test_format_ui_specification_markdown_shows_figma_reference_when_present():
    spec = UISpecification(
        id="UI-005", title="t", context_problem="c", figma_file_reference="https://figma.com/file/abc"
    )

    resultado = format_ui_specification_markdown(spec)

    assert "**Arquivo Figma de referência**: https://figma.com/file/abc" in resultado
