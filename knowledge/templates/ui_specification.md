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

`<lista de UIScreen — nome, componentes recomendados do catálogo fechado Material Design 3 com variante/tamanho/ícone/notas quando fizerem sentido, origem rastreável — gerado por identify_screens_and_components (GR-UI-1: nenhum componente fora do catálogo; GR-UI-7: nenhum ícone fora do catálogo fechado Material Symbols)>`

`<subseção "Hierarquia Visual" por tela — ordem nível 1→N dos elementos da tela, gerada por identify_screens_and_components>`

`<subseções "Estados Vazios"/"Estados de Erro" por tela — rascunho de copy a confirmar com o time de conteúdo/produto, gerado por draft_empty_and_error_states (GR-UI-6)>`

## 4. Estados dos Componentes

`<estados de interação (hover/focus/disabled/loading/error/success) por tela, com o contexto real quando a UX Specification descreve um ponto assíncrono/de espera específico — gerado por define_component_states, só para telas com componentes já identificados>`

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

`<síntese priorizada (3-5 itens), em tabela Priority | Recomendação, ordenada Alta → Média → Baixa, gerada por synthesize_recommendations combinando as recomendações de acessibilidade (seção 7) e as observações da revisão (Material Design 3 + WCAG 2.2) — nunca inclui um item que não esteja em uma das duas, é uma reordenação/resumo do que já existe, não conteúdo novo>`

## 9. Navegação

`<sequência de telas já identificadas, renderizada como uma cadeia de setas (Tela A → Tela B → Tela C) — construída em Python puro a partir de screens, nunca uma nova derivação de fluxo/navegação (GR-UI-8, papel exclusivo da UX Specification de origem)>`

## 10. Mensagens da Interface

`<mensagens globais da interface (ex.: texto de um diálogo de confirmação, mensagem genérica de erro de conexão) — rascunho de copy a confirmar com o time de conteúdo/produto, gerado por draft_interface_messages (GR-UI-6)>`

## 11. Ícones

`<lista simples, deduplicada, de todo ícone Material Symbols usado nos componentes das telas — construída em Python puro, sem chamada nova ao LLM>`

## 12. Movimento

`<nota fixa referenciando o Material Motion do Material Design 3 — constante estática, não gerada por LLM, sem detalhamento de animações específicas nesta fase>`

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
