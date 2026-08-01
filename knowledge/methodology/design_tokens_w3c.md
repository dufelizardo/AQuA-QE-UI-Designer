# W3C Design Tokens — Vocabulário Núcleo

> Fonte: W3C Design Tokens Community Group Report (Design Tokens Format Module,
> `design-tokens.github.io/community-group`). Referência real consultada por
> `suggest_design_tokens` para a *forma*/nomenclatura de um design token — não define a
> paleta/identidade visual de nenhum produto específico, que continua sempre uma sugestão a
> confirmar com o time de Design (GR-UI-2), nunca um valor definitivo inventado por este
> agente.

## O que é um design token

Um design token é um par nome/valor que representa uma decisão de design atômica e reutilizável
(uma cor, um tamanho de fonte, um espaçamento) — a mesma decisão referenciada por nome em
qualquer plataforma (web, mobile, design tool), em vez de um valor solto repetido em cada
lugar que o usa.

## Tipos de token do vocabulário núcleo

- **Color** — um valor de cor (ex.: um papel semântico do Material Design 3, como `primary`).
- **Dimension** — uma medida de comprimento (ex.: espaçamento, raio de borda), tipicamente em `px`/`rem`/`dp`.
- **Font Family** — a família tipográfica usada.
- **Font Weight** — o peso da fonte (ex.: `400`, `700`, ou um alias como `regular`/`bold`).
- **Duration** — uma duração de tempo (ex.: para uma transição/animação).
- **Cubic Bézier** — uma curva de easing para transições/animações.
- **Number** — um valor numérico sem unidade (ex.: um multiplicador de escala).
- **Stroke Style, Border, Transition, Shadow, Gradient, Typography** — tokens **compostos**,
  que agrupam vários tokens primitivos acima num único token nomeado (ex.: um token
  `Typography` compondo `font-family` + `font-weight` + tamanho).

## Convenção de nomenclatura usada por este agente

Este agente não define um design system novo — `suggest_design_tokens` sugere candidatos
seguindo a convenção `categoria.papel` (ex.: `color.primary`, `typography.headline-medium`,
`spacing.16`), sempre citando o papel semântico do Material Design 3
(`knowledge/methodology/material_design_3.md`) como a fonte do que aquele papel representa —
nunca um valor de design system genérico "de mercado" desconectado da fonte real (UX
Specification/PRD).

## Como este agente usa este documento

- `suggest_design_tokens` estrutura sua sugestão como tokens nomeados (não como uma lista solta
  de valores) — cada item sugerido é rotulado com o tipo de token que representa (cor,
  tipografia ou espaçamento) e o papel semântico correspondente do Material Design 3.
- Nenhuma skill deste agente declara um token como a especificação técnica final e
  implementável de um design system — a saída é sempre uma sugestão a confirmar (GR-UI-2),
  já que este build não lê nenhum design system real existente (ver GR-UI-5).
