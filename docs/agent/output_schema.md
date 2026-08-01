# Output Schema

> Estrutura de dados retornada por `generate_ui_specification` e exportada por
> `format_ui_specification_markdown`, alinhada a `../../knowledge/templates/ui_specification.md`.
> Implementada como dataclasses reais em `../../src/aqua_qe_ui_designer/models/`
> (`UISpecification`, `UIScreen`, `ComponentSpec`, `StateSpec`, `DesignTokensSuggestion`,
> `PrioritizedRecommendation`) — o JSON abaixo é a representação conceitual.

## Schema da UI Specification

```
{
  "id": "<string, ex.: UI-001>",
  "title": "<string — extraído por extract_ui_context>",
  "context_problem": "<string — resumo do problema/tarefa, extraído da UX Specification de origem>",
  "screens": [
    {
      "name": "<nome da tela, ex.: Tela de Agendamento>",
      "components": [
        {
          "name": "<nome exato de um componente do catálogo fechado Material Design 3 — nunca um nome fora dele, GR-UI-1>",
          "variant": "<vocabulário real de variante/estilo Material Design 3, ex.: 'Filled'/'Outlined'/'Text' para Buttons, 'Small'/'Center Aligned' para Top App Bar — nunca inventado; '' se não houver variante real aplicável>",
          "size": "<tamanho real, quando aplicável; '' se não houver>",
          "icon": "<nome exato de um ícone do catálogo fechado Material Symbols — nunca um nome fora dele, GR-UI-7; um ícone inválido volta para '' sem invalidar o componente>",
          "notes": "<nota curta de configuração, ex.: 'Placeholder: Pesquisar cidadão' — não é copy final de UI>"
        }
      ],
      "states": [
        {
          "name": "<estado de interação relevante, ex.: hover, focus, disabled, loading, error, success>",
          "context": "<contexto real do estado, quando a UX Specification descreve um ponto assíncrono/de espera específico, ex.: 'enquanto consulta horários disponíveis'; '' se a fonte não descrever nada específico>"
        }
      ],
      "hierarchy": ["<elemento da tela em ordem de hierarquia visual, nível 1→N implícito na ordem da lista, ex.: 'Título', 'Descrição', 'Botão principal', 'Links auxiliares'>"],
      "empty_states": ["<rascunho de copy a confirmar para o estado vazio da tela — GR-UI-6>"],
      "error_states": ["<rascunho de copy a confirmar para o estado de erro da tela — GR-UI-6>"],
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
  "recommendations_synthesis": [
    {
      "priority": "Alta | Média | Baixa — nunca um quarto nível inventado; um valor do LLM fora desses três é normalizado para 'Média'",
      "text": "<texto da recomendação, gerado por synthesize_recommendations, combinando accessibility_recommendations e review_notes — nunca um item que não esteja em uma das duas>"
    }
  ],
  "interface_messages": ["<mensagem global da interface (ex.: texto de um diálogo de confirmação, mensagem genérica de erro de conexão) — rascunho de copy a confirmar, gerado por draft_interface_messages, GR-UI-6>"],
  "navigation_sequence": ["<nome de tela, na ordem em que aparece em screens — construído em Python puro, [tela.name for tela in screens], nunca uma nova derivação de fluxo/navegação, GR-UI-8>"],
  "icons": ["<ícone Material Symbols não vazio usado em algum componente de alguma tela, deduplicado preservando a primeira ocorrência — construído em Python puro, sem chamada nova ao LLM>"],
  "motion_notes": "<nota fixa referenciando o Material Motion do Material Design 3 — constante estática atribuída pelo workflow, não gerada por LLM>"
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
