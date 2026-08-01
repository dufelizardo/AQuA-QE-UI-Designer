# Template — UI Specification (UIS)

> Estrutura padrão, sem conteúdo de domínio. Ver `../../docs/agent/output_schema.md` para o
> schema de dados exato gerado pelo agente (`UISpecification`, `UIScreen`,
> `DesignTokensSuggestion`).

## 1. Objetivo

`<a tarefa/problema que motiva esta especificação visual, herdado da UX Specification de origem — gerado por extract_ui_context>`

## 2. Escopo

`<referência (URL/ID) da UX Specification de origem — não um resumo do texto completo, só a referência>`

`<referência de arquivo Figma — sempre "fora de escopo nesta fase" neste build (GR-UI-4); campo existe no schema para não exigir mudança de schema quando a integração real com Figma for adicionada em uma issue futura>`

## 3. Telas e Componentes

`<lista de UIScreen — nome, componentes recomendados do catálogo fechado Material Design 3, origem rastreável — gerado por identify_screens_and_components (GR-UI-1: nenhum componente fora do catálogo)>`

## 4. Estados dos Componentes

`<estados de interação (hover/focus/disabled/loading/error/success) por tela — gerado por define_component_states, só para telas com componentes já identificados>`

## 5. Design Tokens (Sugestão)

> Sempre rotulado como sugestão a confirmar com o time de Design — nunca a identidade visual
> definitiva do produto, a menos que a UX Specification/PRD de origem já a especifique
> explicitamente (GR-UI-2).

`<cores, tipografia e espaçamento sugeridos — gerado por suggest_design_tokens, citando papéis semânticos reais do Material Design 3 e a nomenclatura do W3C Design Tokens>`

## 6. Layout Responsivo

`<notas de layout responsivo citando as window size classes reais do Material Design 3 (compact/medium/expanded) — gerado por define_responsive_layout, nunca um breakpoint numérico inventado>`

## 7. Recomendações de Acessibilidade Visual

`<lista de recomendações fundamentadas em WCAG 2.2, sempre "a verificar", nunca certificação de conformidade — gerado por review_accessibility_visual (GR-UI-3)>`

## 8. Recomendações

`<síntese priorizada (3-5 itens), gerada por synthesize_recommendations combinando as recomendações de acessibilidade (seção 7) e as observações da revisão (Material Design 3 + WCAG 2.2) — nunca inclui um item que não esteja em uma das duas, é uma reordenação/resumo do que já existe, não conteúdo novo>`

## Rastreabilidade

`<tabela de/para: a UX Specification de origem e cada tela identificada, ligados ao trecho de origem que os fundamenta — não um dump do texto completo da fonte, ver GR-UI-5>`

## Relação com a hierarquia de artefatos

```
PRD (Product Manager)
      │
      ▼
Épico / User Story (Product Owner)
      │
      ▼
UX Specification (UX Designer) — fluxos de navegação, arquitetura da informação, acessibilidade
      │
      ▼
UI Specification (UI Designer) — este documento: telas, componentes Material Design 3,
estados, design tokens (sugestão), layout responsivo, acessibilidade visual
      │
      ▼
Figma real (leitura/escrita) / Storybook / GitHub — fora de escopo desta fase (issues futuras)
```

A UI Specification não substitui a UX Specification — é a ponte entre "como o usuário
navega" (fluxo de navegação, nível de interação) e "como a interface se apresenta
visualmente" (componentes de um catálogo de design system real, estados, tokens sugeridos,
responsividade). Este build é deliberadamente só textual — sem Figma/Storybook/GitHub reais
— ver `WHITEPAPER.md`, seção 11, para o que fica para issues futuras.
