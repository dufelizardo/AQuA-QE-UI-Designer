# Material Design 3 — Catálogo de Componentes, Papéis de Cor, Tipografia e Breakpoints

> Fonte: especificação pública do Material Design 3 (Google, `m3.material.io`). Referência
> real consultada por `identify_screens_and_components`, `define_component_states`,
> `suggest_design_tokens`, `define_responsive_layout` e `review_ui_specification` — o agente
> só recomenda um componente **desta lista**, nunca inventa um nome fora dela (GR-UI-1, o
> guardrail mais importante deste agente). Este documento resume/organiza a especificação
> pública em prosa própria; não reproduz blocos extensos verbatim do site oficial.

## Catálogo fechado de componentes

A lista abaixo é o catálogo fechado consultado por `src/aqua_qe_ui_designer/skills/_material_design_3_catalog.py`
(`COMPONENTES_MD3`). Qualquer componente citado pelo LLM fora desta lista é descartado antes
de chegar à `UIScreen.components` (GR-UI-1).

- **Top App Bar** — barra superior com título da tela e ações contextuais (voltar, buscar, mais opções).
- **Bottom App Bar** — barra inferior com ações de navegação/ações primárias em telas mobile.
- **Navigation Bar** — navegação principal por até 5 destinos, fixa na base da tela (mobile).
- **Navigation Rail** — navegação principal vertical e compacta, para telas médias.
- **Navigation Drawer** — painel de navegação lateral, expansível, para telas expandidas ou com muitos destinos.
- **Tabs** — navegação entre grupos de conteúdo relacionados dentro de uma mesma tela.
- **Buttons** — ações (filled, outlined, text, elevated, tonal) — a ação primária/secundária de uma tela.
- **FAB (Floating Action Button)** — a ação mais importante e frequente de uma tela, sempre visível.
- **Extended FAB** — variante do FAB com rótulo de texto, para a ação primária quando o ícone sozinho não é suficiente.
- **Icon Buttons** — ações compactas representadas só por ícone (favoritar, curtir, mais opções).
- **Segmented Buttons** — conjunto de opções mutuamente exclusivas ou múltiplas, lado a lado.
- **Cards** — contêiner que agrupa conteúdo e ações relacionadas (ex.: um item de lista rico, um resumo).
- **Chips** — elementos compactos para entrada, filtro, seleção ou ação rápida.
- **Lists** — apresentação vertical de itens (texto, ícone, ação) — navegação ou seleção de itens.
- **Text Fields** — entrada de texto do usuário (filled ou outlined), com rótulo/mensagem de apoio/erro.
- **Search Bar** — campo de busca, geralmente expansível para uma tela de resultados/sugestões.
- **Menus** — lista temporária de opções ancorada a um elemento (ex.: menu de contexto, dropdown).
- **Dialogs** — janela modal para uma decisão/confirmação pontual, interrompendo o fluxo principal.
- **Bottom Sheets** — painel que sobe da base da tela para uma ação/conteúdo complementar, sem trocar de tela.
- **Snackbar** — mensagem breve e não bloqueante de feedback sobre uma ação (com ação de desfazer opcional).
- **Tooltips** — texto de apoio contextual, exibido ao focar/pairar sobre um elemento.
- **Progress Indicators** — indicadores lineares ou circulares de carregamento/progresso.
- **Sliders** — seleção de um valor (ou intervalo) num intervalo contínuo/discreto.
- **Switches** — alternância entre dois estados (ligado/desligado) de uma configuração.
- **Checkboxes** — seleção múltipla independente de opções.
- **Radio Buttons** — seleção única entre um conjunto de opções mutuamente exclusivas.
- **Date Pickers** — seleção de uma data (ou intervalo de datas) via calendário ou entrada de texto.
- **Time Pickers** — seleção de um horário via mostrador ou entrada de texto.
- **Dividers** — linha fina que separa/agrupa conteúdo relacionado dentro de uma tela.
- **Badges** — indicador numérico ou de status sobre um ícone/elemento (ex.: contagem de notificações).
- **Carousel** — apresentação horizontal rolável de itens de mídia/conteúdo relacionado.

## Papéis de cor (color roles)

O Material Design 3 organiza cor por **papel semântico**, não por valor fixo — cada papel tem
uma variante "on-" para o conteúdo sobre ele (texto/ícone), garantindo contraste:

- **Primary / On Primary** — a cor de maior destaque; usada nos elementos mais proeminentes (ex.: FAB, botão principal).
- **Secondary / On Secondary** — destaque menos proeminente que primary, para reforçar seleções/filtros.
- **Tertiary / On Tertiary** — contraste/acento complementar, para chamar atenção sem competir com primary.
- **Error / On Error** — estados de erro (mensagens, ícones, bordas de campo inválido).
- **Surface / On Surface** — a cor de fundo de componentes (cards, sheets, menus) e o conteúdo sobre ela.
- **Surface Variant / On Surface Variant** — variação de superfície para diferenciar áreas (ex.: um campo desabilitado).
- **Outline** — bordas e divisores que precisam de contraste sem competir com o conteúdo.

`suggest_design_tokens` cita esses papéis (nunca um valor hexadecimal arbitrário sem relação
com eles) — sempre como sugestão a confirmar com o time de Design (GR-UI-2).

## Escala de tipografia (type scale)

Cinco papéis, cada um em três tamanhos (small/medium/large): **Display**, **Headline**,
**Title**, **Body**, **Label**. `suggest_design_tokens` cita o papel (ex.: "headline-medium
para o título da tela"), nunca um valor de `font-size` em pixels sem relação com a escala.

## Espaçamento (spacing)

O Material Design 3 não fixa uma escala numérica única e obrigatória — a diretriz é usar um
incremento consistente (tipicamente múltiplos de 4dp) para as margens e o espaçamento interno
de componentes. `suggest_design_tokens` sugere um incremento consistente como ponto de
partida (ex.: "16dp entre cards em uma lista"), sempre rotulado como sugestão a confirmar
(GR-UI-2) — nunca uma escala "oficial" inventada além do incremento base.

## Window size classes (breakpoints reais)

Referência real usada por `define_responsive_layout` — nunca um número de breakpoint
inventado sem relação com estas três classes:

- **Compact** — largura de janela até 599dp (a maioria dos smartphones em retrato). Navegação tipicamente em `Navigation Bar`.
- **Medium** — 600dp a 839dp (tablets em retrato, smartphones grandes em paisagem, janelas redimensionadas em desktop). Navegação tipicamente em `Navigation Rail`.
- **Expanded** — 840dp ou mais (tablets em paisagem, desktop). Navegação tipicamente em `Navigation Rail` ou `Navigation Drawer` permanente.

## Como este agente usa este documento

- `identify_screens_and_components` só pode citar um nome de componente que apareça na lista
  do catálogo acima (idêntico ao `COMPONENTES_MD3` em código) — qualquer outro nome é
  descartado (GR-UI-1).
- `suggest_design_tokens` cita papéis de cor/tipografia/espaçamento reais deste documento,
  nunca uma identidade visual fabricada (GR-UI-2).
- `define_responsive_layout` cita as três window size classes acima, nunca um número de
  breakpoint inventado (GR-UI-5).
