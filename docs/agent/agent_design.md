# Agent Design

> Estrutura conforme `../standards/system_design_standard.md` (este agente não duplica um
> `agent_design_standard.md` próprio — segue o mesmo formato usado pelos agentes irmãos, que
> referenciam a mesma seção). Decisões de design centrais do agente.

1. **Um único artefato nesta fase** — igual ao Solution Architect e ao UX Designer, o UI
   Designer gera só a UI Specification nesta fase. Simplifica o CLI (sem `--modo`) e o
   orquestrador (uma única sequência de skills).
2. **Fluxos de navegação e arquitetura da informação são consumidos, nunca gerados** — decisão
   de design mais importante do agente, espelhando GR-UX-4 no UX Designer para Personas/User
   Journeys. A UX Specification já produz ambos; regerá-los aqui criaria duas fontes
   divergentes do mesmo artefato. `extract_ui_context` só lê o texto da UX Specification como
   contexto.
3. **Catálogo fechado Material Design 3, não um "design genérico"** — `identify_screens_and_components`
   só pode citar um componente do catálogo em `knowledge/methodology/material_design_3.md`.
   Essa disciplina de catálogo fechado é o mesmo padrão já usado por
   `identify_architecture_pattern` no Solution Architect (GR-SA-1) — aqui é GR-UI-1, o
   guardrail mais importante deste agente.
4. **Design tokens são sempre sugestão, nunca identidade definitiva** — `suggest_design_tokens`
   nunca afirma ter acesso à paleta/tipografia real e já estabelecida do produto (GR-UI-2), o
   mesmo espírito de GR-M5 no Product Manager (métricas candidatas sempre rotuladas como
   sugestão, nunca fato).
5. **Acessibilidade visual é recomendação, nunca certificação** — `review_accessibility_visual`
   fundamenta suas recomendações em WCAG 2.2, mas nunca afirma "esta tela está em conformidade"
   como fato — sempre algo a verificar por um humano/ferramenta de auditoria real (GR-UI-3,
   mesmo espírito de GR-UX-2 no UX Designer).
6. **Figma/Storybook/GitHub ficam fora, não por serem menos importantes, mas por exigirem
   integrações que a plataforma ainda não tem** — decisão de **fase**, não permanente: nascem
   como issues futuras quando essas integrações forem construídas, mesmo princípio de "entregar
   o núcleo que cabe no padrão estabelecido primeiro" já usado pelo Solution Architect com Jira
   (só leitura) e pelo UX Designer com Figma (adiado para este próprio agente).
7. **Aprovar automaticamente vs. exigir revisão humana** — o agente **nunca** decide aprovação
   final. `validate_ui_specification` decide apenas se a UI Specification passa no checklist
   automático (nível "rascunho validado"); a aprovação de design/desenvolvimento permanece
   sempre humana.
8. **Revisão combina LLM e checagem determinística, não só um ou outro** — diferente dos
   agentes irmãos (revisão só por LLM), `review_ui_specification` roda uma checagem Python
   pura do catálogo fechado *antes* de perguntar ao LLM revisor, como defesa em profundidade de
   GR-UI-1 (o guardrail mais crítico) — mesmo se o refino posterior reintroduzir um componente
   inválido e o LLM revisor não perceber.
9. **Revisão e refinamento atuam sobre a UI Specification inteira, nunca tela por tela** —
   mesma razão de design do Solution Architect/UX Designer: não há aqui uma unidade
   intermediária cara o suficiente para justificar um checkpoint por tela.
10. **Entrada de fonte única e flexível, não dual como o UX Designer** — este agente segue o
    padrão do Solution Architect (`--arquivo`/`--texto`/`--jira`/`--confluence`, mutuamente
    exclusivos), porque, diferente do UX Designer (que sempre precisa de PRD **e** Story/Epic
    juntos), este agente só precisa de um único documento de entrada: a UX Specification já
    consolidada.
