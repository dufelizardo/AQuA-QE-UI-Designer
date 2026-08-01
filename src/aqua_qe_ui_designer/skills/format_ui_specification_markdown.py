from ..models import UISpecification


def _lista_md(itens: list[str]) -> str:
    return "\n".join(f"- {item}" for item in itens) if itens else "(nenhum)"


def _telas_e_componentes_md(spec: UISpecification) -> str:
    if not spec.screens:
        return "(nenhuma)"
    linhas = []
    for tela in spec.screens:
        componentes = ", ".join(tela.components) if tela.components else "(nenhum identificado)"
        linhas.append(f"### {tela.name}")
        linhas.append("")
        linhas.append(f"Componentes (Material Design 3): {componentes}")
        linhas.append("")
    return "\n".join(linhas).rstrip()


def _estados_md(spec: UISpecification) -> str:
    if not spec.screens:
        return "(nenhum)"
    linhas = []
    for tela in spec.screens:
        estados = ", ".join(tela.states) if tela.states else "(nenhum definido)"
        linhas.append(f"- **{tela.name}**: {estados}")
    return "\n".join(linhas)


def _design_tokens_md(spec: UISpecification) -> str:
    tokens = spec.design_tokens
    cores = ", ".join(tokens.colors) if tokens.colors else "(nenhuma)"
    tipografia = ", ".join(tokens.typography) if tokens.typography else "(nenhuma)"
    espacamento = ", ".join(tokens.spacing) if tokens.spacing else "(nenhum)"
    return (
        f"- **Cores** (sugestão a confirmar): {cores}\n"
        f"- **Tipografia** (sugestão a confirmar): {tipografia}\n"
        f"- **Espaçamento** (sugestão a confirmar): {espacamento}"
    )


_TRECHO_MAX_CARACTERES = 200


def _trecho_para_tabela(trecho: str) -> str:
    """Achata um trecho de origem para uma única linha e limita o tamanho, para nunca quebrar
    a sintaxe de tabela Markdown nem inflar a tabela com o texto completo da fonte — mesmo
    cuidado já aplicado no agente irmão AQuA-QE UX Designer."""
    texto = " ".join(trecho.split())
    if len(texto) > _TRECHO_MAX_CARACTERES:
        texto = texto[:_TRECHO_MAX_CARACTERES].rstrip() + "…"
    return texto or "(não informado)"


def _rastreabilidade_md(spec: UISpecification) -> str:
    """Tabela de/para: cada artefato gerado, ligado ao trecho da fonte que o originou (GR-UI-5)."""
    linhas = [
        "| Artefato | Trecho de origem |",
        "|---|---|",
        f"| UX Specification de origem | {spec.uxs_reference or '(não informado)'} |",
    ]
    for tela in spec.screens:
        linhas.append(f"| Tela: {tela.name} | {_trecho_para_tabela(tela.source_reference)} |")
    return "\n".join(linhas)


def format_ui_specification_markdown(spec: UISpecification) -> str:
    """Formata a UI Specification em Markdown, seguindo as seções de knowledge/templates/ui_specification.md."""
    return (
        f"# {spec.title or spec.id}\n\n"
        f"**ID**: {spec.id}\n"
        f"**Status**: {spec.status.value}\n\n"
        f"## 1. Objetivo\n{spec.context_problem}\n\n"
        "## 2. Escopo\n"
        f"- **UX Specification de origem**: {spec.uxs_reference or '(não informado)'}\n"
        "- **Arquivo Figma de referência**: "
        f"{spec.figma_file_reference or '(fora de escopo nesta fase — GR-UI-4, ver WHITEPAPER.md seção 11)'}\n\n"
        f"## 3. Telas e Componentes\n\n{_telas_e_componentes_md(spec)}\n\n"
        f"## 4. Estados dos Componentes\n\n{_estados_md(spec)}\n\n"
        "## 5. Design Tokens (Sugestão)\n\n"
        "> Sugestão a confirmar com o time de Design — nunca a identidade visual definitiva do "
        "produto, a menos que a UX Specification/PRD de origem já a especifique explicitamente "
        "(GR-UI-2).\n\n"
        f"{_design_tokens_md(spec)}\n\n"
        f"## 6. Layout Responsivo\n\n{spec.responsive_notes or '(nenhuma nota)'}\n\n"
        "## 7. Recomendações de Acessibilidade Visual\n\n"
        "> Fundamentadas em WCAG 2.2 — sempre 'a verificar', nunca certificação de conformidade "
        "(GR-UI-3).\n\n"
        f"{_lista_md(spec.accessibility_recommendations)}\n\n"
        "## 8. Recomendações\n\n"
        "> Síntese priorizada combinando as recomendações de acessibilidade (seção 7) e as "
        "observações da revisão (Material Design 3 + WCAG 2.2, seção de rastreabilidade abaixo) "
        "— nunca inclui um item que não esteja em uma das duas.\n\n"
        f"{_lista_md(spec.recommendations_synthesis)}\n\n"
        f"## Rastreabilidade\n\n{_rastreabilidade_md(spec)}\n"
    )
