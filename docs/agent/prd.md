# PRD — AQuA-QE UI Designer

> Estrutura conforme `../standards/prd_standard.md`.

## Contexto e problema

A UX Specification (agente irmão AQuA-QE UX Designer) já descreve **como o usuário navega**
para completar uma tarefa — mas não descreve **como a interface se apresenta visualmente**:
quais componentes de um design system real cabem em cada tela, quais estados de interação
esses componentes precisam suportar, e quais notas de responsividade/acessibilidade visual
devem ser verificadas. Sem essa camada, decisões de apresentação visual ficam implícitas até a
implementação, terceirizadas informalmente para quem constrói a interface — gerando
inconsistência visual entre telas do mesmo produto.

## Objetivo do produto

Gerar uma UI Specification a partir de uma UX Specification já pronta, cobrindo telas com
componentes recomendados de um catálogo fechado (Material Design 3), estados de interação,
sugestões de design tokens (sempre "a confirmar") e notas de layout responsivo — com
rastreabilidade total à fonte e revisão humana obrigatória antes de qualquer aceite. **Nunca
substitui a UX Specification** — consome seus fluxos de navegação/arquitetura da informação
como texto de entrada, nunca os regenera.

## Público-alvo / personas

- **UI/Visual Designer** — usa a UI Specification gerada como ponto de partida estruturado
  antes de abrir uma ferramenta de design visual real (Figma, fora de escopo desta fase).
- **UX Designer** — confere se a tradução de seus fluxos em telas/componentes preserva a
  intenção de navegação original.
- **Front-end Developer** — consulta componentes/estados/tokens sugeridos como um primeiro
  contrato visual antes da implementação real.

## Escopo (Fase 1 — este build)

- Ler a UX Specification de origem via um de quatro caminhos flexíveis e mutuamente exclusivos:
  arquivo local (`--arquivo`), texto/chat direto (`--texto`), ticket Jira (`--jira`, leitura) ou
  página Confluence (`--confluence`, leitura).
- Extrair título e contexto do problema a partir da UX Specification.
- Identificar as telas de navegação e, para cada uma, os componentes aplicáveis do catálogo
  fechado Material Design 3 — nunca um componente fora dele (GR-UI-1).
- Definir estados de interação (hover/focus/disabled/loading/error/success) por tela.
- Sugerir design tokens (cores/tipografia/espaçamento) — sempre como sugestão a confirmar
  (GR-UI-2), nunca a identidade visual definitiva do produto.
- Definir notas de layout responsivo citando as window size classes reais do Material Design 3.
- Gerar recomendações de acessibilidade visual fundamentadas em WCAG 2.2 — sempre "a
  verificar", nunca certificação (GR-UI-3).
- Validar a saída contra um checklist automático antes de apresentá-la.
- Revisar com um segundo LLM independente do gerador, combinado com uma checagem
  determinística do catálogo fechado (defesa em profundidade de GR-UI-1).
- Suportar ciclo de refinamento humano-no-loop (perguntas de esclarecimento → resposta humana
  → refino), com memória institucional de respostas de refinamento (RAG).
- Exportar o resultado em Markdown.
- Publicar o resultado como página no Confluence Cloud, sempre como irmã da página de origem e
  sempre atrás de confirmação humana explícita (`--publicar-confluence`/`--atualizar-confluence`,
  mutuamente exclusivos).

## Fora de escopo (Fase 1 — ver WHITEPAPER seção 11 para detalhe)

- **Integração real com Figma (leitura/escrita)** — não construída nesta fase; é a primeira
  integração não-textual da plataforma, deliberadamente adiada para uma issue futura.
- **Integração com Storybook** (publicar/ler componentes reais implementados) — issue futura.
- **Integração com GitHub** (abrir PR com os tokens/especificação) — issue futura.
- **Outros catálogos de design system** (Apple Human Interface Guidelines, Microsoft Fluent,
  IBM Carbon) — só Material Design 3 nesta fase; ver `WHITEPAPER.md`, seção 11.
- **Geração/edição de fluxos de navegação ou arquitetura da informação** — permanece
  exclusivamente do agente irmão AQuA-QE UX Designer; este agente só consome esse texto.
- Escrita em Jira (o agente só lê essa fonte, mesmo princípio dos agentes irmãos).
- RAG/memória de projeto ou longo prazo (além da memória institucional de refinamento, já implementada).

## Requisitos funcionais

1. Ler a UX Specification de origem por um dos quatro caminhos flexíveis (arquivo/texto/Jira/Confluence).
2. Extrair título e contexto do problema a partir da fonte.
3. Identificar telas e os componentes Material Design 3 aplicáveis a cada uma, rastreáveis à fonte.
4. Definir estados de interação por tela, só para telas com componentes já identificados.
5. Sugerir design tokens (cores/tipografia/espaçamento), sempre rotulados como sugestão.
6. Definir notas de layout responsivo citando as window size classes reais do Material Design 3.
7. Gerar recomendações de acessibilidade visual fundamentadas em WCAG 2.2.
8. Validar a saída contra um checklist automático (ao menos 1 tela com componentes e estados) antes de apresentá-la.
9. Revisar com um segundo LLM independente do gerador, mais uma checagem determinística do catálogo fechado.
10. Quando a revisão reprovar, gerar perguntas de esclarecimento e refinar com as respostas humanas.
11. Exportar o resultado validado em Markdown.
12. Publicar no Confluence como página irmã da UX Specification de origem, sempre atrás de confirmação humana.

## Requisitos não funcionais

- **Rastreabilidade** — toda tela/componente gerado deve ser rastreável à UX Specification de origem.
- **Catálogo fechado** — nenhum componente citado pode estar fora do Material Design 3 (GR-UI-1).
- **Nenhuma aprovação automática** — toda saída é um rascunho validado, sujeito a revisão humana obrigatória.
- **Nunca afirmar certeza não verificada** — design tokens são sempre sugestão; recomendações de acessibilidade são sempre "a verificar", nunca conformidade certificada.
- **Consistência de formato** — toda saída segue o template em `../../knowledge/templates/ui_specification.md`.

## Métricas de sucesso

- Taxa de aceitação sem retrabalho — % de UI Specifications geradas aceitas sem edição substancial.
- Cobertura de rastreabilidade — % de telas com `source_reference` preenchido a partir da fonte real.
- Taxa de componentes fora do catálogo descartados antes de chegar à saída (indicador indireto de disciplina de GR-UI-1 sendo exercida, não de falha).

## Riscos e premissas

- Premissa: a UX Specification de origem contém informação suficiente para inferir telas e componentes plausíveis na maioria dos casos; quando não contém, o agente deve refletir isso via `pending_clarification`, nunca inventar telas/componentes.
- Risco: UX Specifications muito abstratas (poucos fluxos/seções de IA) podem limitar a qualidade das telas identificadas.
- Risco: sem integração real com Figma (issue futura), a UI Specification desta fase é só textual — útil para alinhamento estrutural, mas não substitui um wireframe/protótipo visual real antes da implementação.
