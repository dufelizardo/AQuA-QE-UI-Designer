# Acceptance Patterns

> Padrões estruturais que distinguem uma saída aceitável de uma inaceitável, conforme
> `validation_checklist.md` e `guardrails.md`. Exemplos concretos de domínio (few-shot)
> ficariam em `knowledge/examples/` — ainda não criado nesta fase.

## Padrão aceitável

Uma UI Specification é aceitável quando:

- Todo componente citado em `UIScreen.components` existe literalmente no catálogo fechado
  Material Design 3 (GR-UI-1).
- Toda tela com componentes identificados tem ao menos um estado de interação definido.
- Todo design token sugerido é rotulado como sugestão a confirmar, nunca a identidade visual
  definitiva do produto, salvo quando a fonte já a especifica (GR-UI-2).
- Toda recomendação de acessibilidade visual referencia um critério WCAG 2.2 específico e usa
  linguagem de recomendação, nunca certificação (GR-UI-3).
- Nenhuma alegação de render visual real aparece na saída; `figma_file_reference` permanece
  vazio nesta fase (GR-UI-4).
- Telas e componentes refletem o que a UX Specification de origem realmente descreve, nunca
  uma suposição sobre a identidade do produto (GR-UI-5).
- O campo `status` reflete corretamente o resultado da validação (`draft_validated` ou
  `pending_clarification`).

## Padrão inaceitável

Uma saída é inaceitável quando apresenta qualquer um dos sinais abaixo:

- **Componente fora do catálogo** — um nome de componente que não existe em
  `knowledge/methodology/material_design_3.md` (viola GR-UI-1).
- **Design token apresentado como identidade definitiva** — "a cor primária do produto é X"
  como fato, sem que a fonte já o especifique (viola GR-UI-2).
- **Certificação de acessibilidade** — "esta tela está em conformidade com WCAG 2.2 AA"
  apresentado como fato (viola GR-UI-3).
- **Render visual fabricado** — "veja como esta tela vai ficar" sem nenhuma integração visual
  real por trás (viola GR-UI-4).
- **Tela/componente inventado sem base na UX Specification** — um elemento sem qualquer menção
  ou inferência razoável a partir da fonte (viola GR-UI-5).
- **UI Specification marcada como aprovada** pelo próprio agente, sem passar por revisão
  humana (viola RULE-UI-6).

## Como usar este documento

Ao avaliar (`evaluation.md`) ou revisar manualmente uma saída do agente, comparar contra os
dois padrões acima antes de aceitar a UI Specification como rascunho válido.
