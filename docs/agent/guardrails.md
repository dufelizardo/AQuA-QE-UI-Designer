# Guardrails

> Estrutura conforme a seção "Guardrails" de `../standards/ai_spec_standard.md`. Os guardrails abaixo têm prioridade igual — nenhum é subordinado aos outros.

## GR-UI-1 — Nunca citar um componente/padrão fora do catálogo fechado Material Design 3 (o mais crítico)

`identify_screens_and_components` e `refine_ui_specification` só podem citar um componente
que exista literalmente em `../../knowledge/methodology/material_design_3.md`
(`COMPONENTES_MD3` em código, `../../src/aqua_qe_ui_designer/skills/_material_design_3_catalog.py`).
Qualquer nome fora dessa lista é descartado silenciosamente antes de chegar a
`UIScreen.components` — nunca repassado adiante como se fosse válido. `review_ui_specification`
verifica isso de novo, de forma determinística (Python puro, não delegado só ao LLM revisor),
como defesa em profundidade contra um componente inválido reintroduzido por um refino
posterior. Mesmo princípio de catálogo fechado já aplicado em `identify_architecture_pattern`
no agente irmão AQuA-QE Solution Architect.

## GR-UI-2 — Design tokens sugeridos nunca são a identidade visual definitiva do produto

`suggest_design_tokens` sempre rotula sua saída como **sugestão a confirmar** com o time de
Design — nunca como a paleta/tipografia/espaçamento já estabelecidos do produto, a menos que
a UX Specification ou o PRD de origem já os especifiquem explicitamente. O agente não tem
acesso a nenhum design system real existente nesta fase (ver GR-UI-5) — inventar uma
identidade visual "definitiva" seria uma afirmação não sustentada pela fonte.

## GR-UI-3 — Nunca certificar conformidade de acessibilidade

`review_accessibility_visual` sempre apresenta suas recomendações fundamentadas em WCAG 2.2
como algo **a verificar**, nunca como uma certificação ("esta tela está em conformidade com
WCAG 2.2 AA"). O agente não tem como validar conformidade real (isso exige ferramentas de
auditoria/testes com usuários reais) — só pode apontar onde a estrutura visual sugere risco
de não conformidade. Mesmo princípio de GR-UX-2 no agente irmão AQuA-QE UX Designer.

## GR-UI-4 — Nunca fabricar um render visual real

Nenhuma skill deste agente produz ou descreve um resultado como se fosse um render visual
real já produzido (ex.: "veja como ficará esta tela") — este build é puramente textual, sem
nenhuma integração com uma ferramenta de design visual real (Figma). O campo
`UISpecification.figma_file_reference` existe no schema desde já (para não exigir mudança de
schema quando essa integração for construída), mas fica sempre vazio nesta fase — nunca
preenchido com um link fabricado. `format_ui_specification_markdown` marca essa seção
explicitamente como fora de escopo, nunca a omite silenciosamente.

## GR-UI-5 — Preferir o que já é real/conhecido a inventar identidade de produto

Este build não lê nenhum design system real existente nem nenhuma integração externa de
leitura visual — `identify_screens_and_components` e `suggest_design_tokens` devem se ater ao
que a UX Specification/PRD de origem realmente descreve, preferindo sempre uma referência real
já citada na fonte (ou um papel/convenção genuína do Material Design 3/W3C Design Tokens) a
uma suposição sobre a identidade do produto. `define_responsive_layout` nunca inventa um
número de breakpoint fora das window size classes reais do Material Design 3
(compact/medium/expanded).

## GR-UI-6 — Rascunhos de copy nunca são texto final

`draft_empty_and_error_states` (estados vazio/erro por tela) e `draft_interface_messages`
(mensagens globais da interface, ex.: um diálogo de confirmação de cancelamento) sempre
produzem copy explicitamente rotulada como **rascunho a confirmar** com o time de
conteúdo/produto — nunca afirmada como texto final e já aprovado para envio direto ao usuário.
Mesmo tratamento já aplicado a design tokens em GR-UI-2.

## GR-UI-7 — Nunca citar um ícone fora do catálogo fechado Material Symbols

`ComponentSpec.icon` só pode existir fora de `""` se vier literalmente de
`../../knowledge/methodology/material_symbols.md`
(`ICONES_MATERIAL_SYMBOLS` em código, `../../src/aqua_qe_ui_designer/skills/_material_symbols_catalog.py`).
`identify_screens_and_components` descarta qualquer ícone fora do catálogo de volta para
`""` — mesma disciplina de catálogo fechado do GR-UI-1, agora para ícones em vez de
componentes, com uma diferença deliberada: um ícone inválido nunca invalida o componente
inteiro (só o campo `icon` some), porque um ícone é um detalhe de configuração do componente,
não a sua identidade.

## GR-UI-8 — `navigation_sequence` nunca deriva uma lógica de fluxo nova

`UISpecification.navigation_sequence` é sempre construído em Python puro, sem chamada a
nenhum LLM, diretamente a partir das telas que este agente já identificou
(`[tela.name for tela in screens]`) — nunca uma re-derivação independente de fluxo de
navegação/arquitetura da informação, o que duplicaria o artefato próprio do agente irmão
AQuA-QE UX Designer (o User Flow da UX Specification de origem). Mesmo princípio de "nunca
duplicar o artefato de um agente irmão" já aplicado entre Personas/Jornadas do Product Manager
e do UX Designer.

## Guardrail transversal — Sem aprovação automática

Independentemente dos guardrails acima serem satisfeitos, o agente nunca marca uma UI
Specification como "aprovada" — apenas como **rascunho validado** (`draft_validated`). A
aprovação final é sempre um ato humano, nunca delegado ao LLM revisor nem ao checklist
automático (mesmo princípio já aplicado em todos os agentes irmãos). O mesmo vale para
escritas externas: publicar uma página no Confluence sempre exige confirmação humana
explícita no CLI, e a página publicada é sempre irmã da página de origem da UX Specification
— nunca em local arbitrário.

## Aplicação

Estes guardrails são a origem das regras formais e verificáveis em `rules.md`, e devem ser
reforçados explicitamente no prompt de sistema de cada skill (ver `prompt.md`).
