# Evaluation

> Estrutura conforme `../standards/evaluation_standard.md`. Decisão de produto: avaliação
> combina checklist automático, revisão por um segundo LLM (mais checagem determinística do
> catálogo fechado) e revisão humana obrigatória (nenhum substitui o outro).

## Métricas

- **Taxa de aprovação automática** — % de UI Specifications geradas que passam no checklist
  (`validation_checklist.md`) sem interrupção por ambiguidade.
- **Taxa de aceitação sem retrabalho** — % de UI Specifications em `draft_validated` aceitas
  pelo time de design/desenvolvimento sem edição substancial.
- **Cobertura de rastreabilidade** — % de telas com `source_reference` preenchido a partir da
  fonte real, não vazio.
- **Taxa de conformidade ao catálogo fechado** — % de componentes citados que existem no
  catálogo Material Design 3 (deveria ser sempre 100%, já que `identify_screens_and_components`
  descarta o resto antes da saída — esta métrica audita se a checagem determinística de
  `review_ui_specification` nunca precisou intervir de fato).
- **Taxa de recomendações de acessibilidade fundamentadas** — % de recomendações que citam um
  critério WCAG 2.2 específico, não genérico.

## Casos de teste

- **Caminho feliz** — UX Specification clara, com fluxos/seções de IA detalhados; deve gerar
  uma UI Specification `draft_validated` sem interrupção.
- **UX Specification sem detalhe suficiente** — `identify_screens_and_components` deve
  identificar menos telas/componentes, ou `validate_ui_specification` deve reprovar, nunca
  inventar uma tela/componente para "completar" a especificação (GR-UI-5).
- **Componente fora do catálogo devolvido pelo LLM** — `identify_screens_and_components` deve
  descartá-lo silenciosamente antes de retornar; se ainda assim aparecer em `review_ui_specification`,
  a checagem determinística deve reprovar mesmo que o LLM revisor aprove (GR-UI-1).
- **Design token sugerido sem menção explícita da fonte** — `format_ui_specification_markdown`
  deve rotular a seção inteira como sugestão a confirmar (GR-UI-2).
- **Recomendação de acessibilidade sem critério WCAG citado** — deve ser sinalizada como
  genérica demais (GR-UI-3).
- **`review_notes` mencionando um render visual real** ("veja como ficará") — nunca deveria
  ocorrer; se ocorrer, é uma falha de prompt a corrigir imediatamente (GR-UI-4).

## Método de avaliação

1. **Checklist automático** (`validate_ui_specification`) — roda em toda execução, aplicando
   `validation_checklist.md`. Sem LLM.
2. **Checagem determinística do catálogo fechado** (dentro de `review_ui_specification`,
   Python puro) — roda antes de qualquer chamada ao LLM revisor, defesa em profundidade de
   GR-UI-1.
3. **LLM-como-juiz** (`review_ui_specification`) — roda após as duas checagens acima; usa um
   modelo diferente do gerador (`OLLAMA_REVIEW_MODEL`, padrão `phi4`, enquanto as skills de
   geração usam `mistral`) para evitar self-preference bias.
4. **Revisão humana obrigatória** — toda UI Specification `draft_validated` passa por aceite
   humano explícito antes de ser exportada; feedback da revisão alimenta a métrica de taxa de
   aceitação.

## Frequência

Casos de teste automatizados rodam a cada mudança em prompt, regras ou skills que possam
afetar comportamento (ver `prompt.md`, `rules.md`).

## Critério de aprovação de uma nova versão do agente

Uma nova versão do prompt/regras/skills só substitui a anterior se não piorar a taxa de
aceitação sem retrabalho nem a taxa de conformidade ao catálogo fechado nos casos de teste de
regressão.

## Registro de regressões

Toda falha encontrada em uso real (ex.: componente fora do catálogo aceito, design token
apresentado como identidade definitiva, recomendação de acessibilidade sem critério citado)
vira um novo caso de teste permanente nesta lista.
