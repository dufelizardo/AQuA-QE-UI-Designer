# Output Schema

> Estrutura de dados retornada por `generate_ui_specification` e exportada por
> `format_ui_specification_markdown`, alinhada a `../../knowledge/templates/ui_specification.md`.
> Implementada como dataclasses reais em `../../src/aqua_qe_ui_designer/models/`
> (`UISpecification`, `UIScreen`, `DesignTokensSuggestion`) — o JSON abaixo é a representação
> conceitual.

## Schema da UI Specification

```
{
  "id": "<string, ex.: UI-001>",
  "title": "<string — extraído por extract_ui_context>",
  "context_problem": "<string — resumo do problema/tarefa, extraído da UX Specification de origem>",
  "screens": [
    {
      "name": "<nome da tela, ex.: Tela de Agendamento>",
      "components": ["<nome exato de um componente do catálogo fechado Material Design 3 — nunca um nome fora dele, GR-UI-1>"],
      "states": ["<estado de interação relevante, ex.: hover, focus, disabled, loading, error, success>"],
      "source_reference": "<trecho da UX Specification de origem>"
    }
  ],
  "design_tokens": {
    "colors": ["<sugestão de cor citando um papel semântico do Material Design 3 — sempre rotulada como sugestão a confirmar, GR-UI-2>"],
    "typography": ["<sugestão de tipografia citando um papel da escala Material Design 3>"],
    "spacing": ["<sugestão de espaçamento, incremento consistente>"]
  },
  "responsive_notes": "<notas de layout responsivo citando as window size classes reais do Material Design 3 (compact/medium/expanded) — nunca um breakpoint inventado>",
  "accessibility_recommendations": [
    "<recomendação fundamentada em WCAG 2.2, sempre como 'a verificar', nunca certificação — GR-UI-3>"
  ],
  "source_reference": "<texto de origem completo (UX Specification), para rastreabilidade — GR-UI-5>",
  "uxs_reference": "<URL/ID/chave informado pelo usuário como origem da UX Specification>",
  "figma_file_reference": "<sempre vazio nesta fase — GR-UI-4; campo já existe no schema para não exigir mudança quando a integração real com Figma for adicionada em issue futura>",
  "status": "draft_validated | pending_clarification | accepted",
  "review_notes": ["<motivo de reprovação do checklist (validate_ui_specification) OU apontamento do revisor (review_ui_specification), se houver>"],
  "recommendations_synthesis": ["<síntese priorizada gerada por synthesize_recommendations, combinando accessibility_recommendations e review_notes — nunca um item que não esteja em uma das duas>"]
}
```

## Valores válidos de `status`

- **`draft_validated`** — passou no checklist automático (`validation_checklist.md`) e na
  revisão por LLM (`review_ui_specification`); ainda não tem aceitação humana (ver RULE-UI-6
  em `rules.md`).
- **`pending_clarification`** — o agente interrompeu por ambiguidade/incompletude na fonte, ou
  o revisor reprovou a UI Specification (incluindo a checagem determinística do catálogo
  fechado, GR-UI-1); use o par `generate_ui_clarifying_questions`/`refine_ui_specification`
  para endereçar os apontamentos.
- **`accepted`** — setado **apenas** pelo CLI (`run.py`), nunca pela lógica automática do
  agente, após confirmação explícita do usuário.

## Formato de exportação (`format_ui_specification_markdown`)

A saída em Markdown segue diretamente a estrutura de
`../../knowledge/templates/ui_specification.md`, preenchida a partir deste schema.
