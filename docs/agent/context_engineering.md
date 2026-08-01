# Context Engineering

> Estrutura conforme `../standards/context_engineering_standard.md`.

## Fontes de contexto (Fase 1)

- **`knowledge/methodology/`** — sempre disponível; base para o catálogo fechado Material
  Design 3 (componentes, papéis de cor, escala tipográfica, window size classes), WCAG 2.2 e o
  vocabulário núcleo do W3C Design Tokens. Pequeno o suficiente para caber direto no prompt de
  cada skill — sem RAG nesta fase.
- **`knowledge/templates/`** — estrutura de saída (`ui_specification.md`).
- **UX Specification de origem** — o texto completo é passado a toda skill de geração; é a
  única fonte de verdade sobre telas/fluxos, nunca regerada aqui (ver `agent_design.md`, item 2).
- **Saída de skills anteriores na mesma execução** — ex.: `extract_ui_context` alimenta
  `identify_screens_and_components`, que por sua vez alimenta `define_component_states` e
  `review_accessibility_visual`.

## Fora desta fase

- **`knowledge/domain/`** e `retrieve_chunks` (RAG sobre `knowledge/methodology/`) — deferidos
  até o volume de conhecimento exceder o que cabe direto no prompt.
- **Leitura de um design system real do produto** (via Figma) — issue futura; nesta fase o
  único catálogo de referência é o Material Design 3 documentado em `knowledge/methodology/`.
- **Memória de projeto/longo prazo** — ver `memory.md`.

## Orçamento de tokens

Prioridade de alocação: (1) instruções fixas de persona/regras (`prompt.md`), (2) UX
Specification sendo processada, (3) conhecimento de metodologia relevante à skill em execução
(ex.: só o catálogo de componentes para `identify_screens_and_components`, só WCAG 2.2 para
`review_accessibility_visual`, não todo `knowledge/methodology/`), (4) formato de saída
esperado.

## Ordenação no prompt final

1. Persona e objetivos.
2. Regras/guardrails.
3. Conhecimento de metodologia relevante à skill (catálogo Material Design 3, WCAG 2.2, ou W3C Design Tokens).
4. UX Specification a processar.
5. Formato de saída esperado.

## Atualização/invalidação

Conhecimento de `knowledge/` é reconsultado a cada execução (não cacheado entre sessões
diferentes).
