# Rules

> Estrutura conforme `../standards/rules_standard.md`. Cada regra deriva de um guardrail (`guardrails.md`).

## RULE-UI-1

- **Descrição**: nenhum componente citado em `UIScreen.components` pode estar fora do catálogo fechado Material Design 3.
- **Gatilho**: `identify_screens_and_components`, `refine_ui_specification`, `review_ui_specification`.
- **Ação esperada**: componente fora do catálogo é descartado antes de ser retornado; `review_ui_specification` reprova deterministicamente (Python puro) se algum ainda assim aparecer.
- **Severidade**: bloqueante.
- **Origem**: GR-UI-1.

## RULE-UI-2

- **Descrição**: design tokens sugeridos nunca são apresentados como a identidade visual definitiva do produto.
- **Gatilho**: `suggest_design_tokens`, `refine_ui_specification`.
- **Ação esperada**: toda saída de design tokens é rotulada "sugestão a confirmar" em `format_ui_specification_markdown`, salvo quando a fonte já especifica a identidade explicitamente.
- **Severidade**: bloqueante.
- **Origem**: GR-UI-2.

## RULE-UI-3

- **Descrição**: recomendações de acessibilidade visual nunca são apresentadas como conformidade confirmada.
- **Gatilho**: `review_accessibility_visual`.
- **Ação esperada**: toda recomendação usa fraseado de "verificar"/"recomenda-se", nunca "está em conformidade".
- **Severidade**: bloqueante.
- **Origem**: GR-UI-3.

## RULE-UI-4

- **Descrição**: nenhuma skill descreve ou fabrica um render visual real da UI Specification.
- **Gatilho**: qualquer skill de geração; `format_ui_specification_markdown`.
- **Ação esperada**: `figma_file_reference` permanece vazio nesta fase; a seção correspondente do export é explicitamente marcada como fora de escopo, nunca omitida silenciosamente nem preenchida com um link fabricado.
- **Severidade**: bloqueante.
- **Origem**: GR-UI-4.

## RULE-UI-5

- **Descrição**: telas, componentes e design tokens só podem ser derivados do que a UX Specification/PRD de origem realmente descreve (ou de uma referência real do Material Design 3/W3C Design Tokens) — nunca de uma suposição sobre a identidade do produto.
- **Gatilho**: `identify_screens_and_components`, `suggest_design_tokens`, `define_responsive_layout`.
- **Ação esperada**: se a origem não for identificável, o campo fica vazio/a lista fica menor — nunca preenchido por suposição; breakpoints sempre citam compact/medium/expanded, nunca um número inventado.
- **Severidade**: bloqueante.
- **Origem**: GR-UI-5.

## RULE-UI-6

- **Descrição**: nenhum artefato é marcado como "aprovado" pelo agente — apenas como "rascunho validado", independentemente de `finalize_ui_specification` aprovar no checklist automático e na revisão.
- **Gatilho**: `validate_ui_specification`/`review_ui_specification` retornam aprovação.
- **Ação esperada**: rotular como rascunho validado (ver `output_schema.md`) e aguardar aceite humano explícito no CLI antes de qualquer exportação.
- **Severidade**: bloqueante.
- **Origem**: guardrail transversal "Sem aprovação automática" (`guardrails.md`).

## RULE-UI-7

- **Descrição**: publicar ou atualizar uma página no Confluence nunca acontece automaticamente; a página publicada (nova) é sempre irmã da página de origem da UX Specification, e atualizar exige a página existente ser informada explicitamente pelo usuário (nunca inferida).
- **Gatilho**: `create_confluence_page` ou `update_confluence_page` seria chamada.
- **Ação esperada**: o CLI (`run.py`) sempre pergunta confirmação explícita antes de publicar/atualizar (`--publicar-confluence`/`--atualizar-confluence`, mutuamente exclusivos); `get_confluence_publish_location` deriva espaço/ancestral da página de origem, nunca de configuração manual solta.
- **Severidade**: bloqueante.
- **Origem**: mesmo espírito do guardrail transversal "Sem aprovação automática", estendido às escritas no Confluence (mesma regra já aplicada no Solution Architect/UX Designer).

## Resolução de conflitos

Todas as regras acima são bloqueantes — não há, nesta fase, regra de severidade
"recomendação". Mesma disciplina já adotada pelo AQuA-QE UX Designer: escopo restrito, menos
graus de liberdade, menos espaço para julgamento parcial.
