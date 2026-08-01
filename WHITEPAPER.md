# AQuA-QE UI Designer — Whitepaper

## 1. Resumo executivo

O AQuA-QE UI Designer é o quinto agente da plataforma AQuA-QE, especializado em traduzir uma
UX Specification já pronta (do agente irmão AQuA-QE UX Designer) numa especificação visual
estruturada: telas com componentes recomendados de um catálogo de design system real (Material
Design 3), estados de interação, sugestões de design tokens e notas de layout responsivo. Ele
responde a uma pergunta que nenhum dos quatro agentes irmãos responde: **como a interface
efetivamente se apresenta visualmente para suportar os fluxos de navegação já definidos?**

Este documento descreve a Fase 1 do agente — deliberadamente restrita ao núcleo textual:
nenhuma integração com Figma, Storybook ou GitHub ainda (issues futuras separadas), e um único
catálogo de design system (Material Design 3), não múltiplos.

**Status no momento deste documento**: a spec formal (`docs/agent/`) e a implementação
(`src/`, `run.py`, `tests/`, totalmente mockados) estão prontas para este núcleo (Fase 1).

## 2. Fundamentação metodológica

Nenhum critério de qualidade deste agente foi inventado. Cada um é documentado em
`knowledge/methodology/` e referenciado diretamente pelas skills e guardrails do agente:

- **Catálogo Material Design 3** (`material_design_3.md`) — fundamenta `identify_screens_and_components` (catálogo fechado de componentes, GR-UI-1), `suggest_design_tokens` (papéis de cor/tipografia) e `define_responsive_layout` (window size classes).
- **WCAG 2.2** (`wcag.md`) — fundamenta as recomendações de acessibilidade visual (`review_accessibility_visual`).
- **W3C Design Tokens Community Group** (`design_tokens_w3c.md`) — fundamenta a nomenclatura/forma dos design tokens sugeridos (`suggest_design_tokens`), nunca a paleta/identidade em si.

## 3. Princípios de design (guardrails)

O mesmo princípio central dos quatro agentes irmãos se aplica aqui: quando a revisão aponta um
problema, o agente não tenta se autocorrigir adivinhando a resposta certa — ele interrompe e
pergunta a um humano. Ver `docs/agent/guardrails.md` para o detalhe formal (GR-UI-1 a GR-UI-5).

O guardrail mais importante e mais específico deste agente é **GR-UI-1 — nunca citar um
componente fora do catálogo fechado Material Design 3**: mesmo espírito de GR-SA-1
(`identify_architecture_pattern`) no Solution Architect, mas reforçado aqui por uma dupla
camada de defesa — a skill de identificação descarta qualquer componente inválido antes de
retornar, e `review_ui_specification` verifica isso de novo, de forma determinística (Python
puro), mesmo que um refino posterior reintroduza um componente inválido e o LLM revisor não
perceba.

Igualmente importante é **GR-UI-2 — design tokens sugeridos nunca são a identidade visual
definitiva do produto**: o agente não tem acesso a nenhum design system real do produto nesta
fase; toda sugestão de cor/tipografia/espaçamento é rotulada como candidata a confirmar com o
time de Design.

## 4. Arquitetura

```
UX Specification (arquivo/texto/Jira/Confluence)
  → CLI (run.py) → orchestrator/ui_designer.py → workflow/generate_ui_specification.py → skills/* → models/* → services/*
```

Um pipeline de skills orquestrado sequencialmente, com dois pontos de checagem antes de
qualquer saída ser considerada válida: validação automática (checklist estrutural, Python
puro) e revisão humana obrigatória. A revisão por LLM é reforçada por uma checagem
determinística do catálogo fechado. Ver `docs/agent/system_design.md` para o fluxo de dados
completo.

## 5. As skills

Skills sem LLM (Python puro, determinística):

- `read_text_file`, `parse_chat_transcript`, `format_chat_transcript` — leitura/normalização de entrada.
- `validate_ui_specification` — checklist estrutural, retorna motivos específicos de reprovação (não `bool`).
- `format_ui_specification_markdown` — formata a UI Specification em Markdown.
- `record_refinement_answer`/`suggest_refinement_answer` — memória institucional de refinamento (RAG).

Skills com LLM gerador (`OLLAMA_MODEL`, padrão `mistral`):

- `extract_ui_context`, `identify_screens_and_components`, `define_component_states`, `suggest_design_tokens`, `define_responsive_layout`, `review_accessibility_visual`, `generate_ui_clarifying_questions`, `refine_ui_specification`, `synthesize_recommendations`.

Skills com LLM revisor independente (`OLLAMA_REVIEW_MODEL`, padrão `phi4` — deliberadamente um
modelo diferente do gerador, para mitigar *self-preference bias*), combinado com checagem
determinística:

- `review_ui_specification` — verifica o catálogo fechado (Python puro) e, em seguida, avalia com o LLM revisor.

Skills de I/O externo:

- `read_jira_issue` (leitura, Jira Cloud REST API), `read_confluence_page` (leitura, Confluence Cloud REST API), `get_confluence_publish_location`/`create_confluence_page`/`update_confluence_page` (escrita gated no Confluence).

Detalhamento completo de entrada/saída/erros de cada skill em `docs/agent/skills.md`.

## 6. O ciclo de refinamento interativo (herdado de PM/PO/SA/UX Designer)

1. Uma UI Specification chega reprovada com `review_notes` preenchido de uma de duas formas:
   `validate_ui_specification` reprova o checklist automático e grava os motivos específicos —
   sem gastar uma chamada de LLM revisor; ou, se o checklist passa, `review_ui_specification`
   reprova com apontamentos concretos (incluindo, de forma determinística, qualquer componente
   fora do catálogo).
2. `generate_ui_clarifying_questions` transforma cada apontamento em uma pergunta objetiva e
   acionável.
3. O CLI (`run.py --refinar`) apresenta as perguntas no terminal, sugerindo (via memória
   institucional RAG) a resposta mais parecida já dada antes; **um humano real responde**.
4. `refine_ui_specification` reescreve os campos afetados usando as respostas como contexto
   real — preservando o texto/nível de detalhe dos campos que as respostas não abordam, e
   continuando a filtrar qualquer componente fora do catálogo fechado.

## 7. O handoff no ecossistema AQuA-QE

```
Product Manager
      │
      ▼
     PRD
      │
   ┌──┴──┐
   ▼     ▼
  PO    UX Designer
   │     │
   ▼     ▼
Backlog  UX Specification
              │
              ▼
         UI Designer
              │
              ▼
       UI Specification
```

O UI Designer consome a UX Specification (fluxos de navegação, arquitetura da informação,
acessibilidade textual) e produz um único artefato novo, a UI Specification — telas,
componentes de um catálogo real, estados, tokens sugeridos e layout responsivo. Não há hoje
uma integração formal de volta ao Solution Architect ou a qualquer outro agente irmão; é uma
extensão natural a considerar quando houver demanda real.

## 8. Modos de operação

Um único fluxo nesta fase — gerar a UI Specification a partir de uma UX Specification já
pronta. Sem `--modo` (mesma razão de design do Solution Architect: só existe um artefato
nesta fase). Entrada por fonte única e flexível (`--arquivo`/`--texto`/`--jira`/`--confluence`,
mutuamente exclusivos) — padrão do Solution Architect, não o padrão dual-obrigatório do UX
Designer, porque este agente só precisa de um único documento de entrada.

## 9. Stack técnico

- **LLM via Ollama (padrão) ou provedor em nuvem** — `mistral`/`phi4` localmente por padrão;
  `LLM_PROVIDER=nvidia|cerebras|google|groq` disponível como piloto desde a Fase 1 (diferente
  dos agentes irmãos, que o adicionaram depois de necessidade real comprovada — aqui a
  infraestrutura já é bem conhecida da plataforma, então o custo de portá-la desde o início é
  baixo).
- **`uv`** para dependências — projeto standalone (repositório próprio, fora do monorepo que o
  originou).
- **Sem RAG sobre `knowledge/methodology/` nesta fase** — só 3 arquivos, pequeno o suficiente
  para caber direto no prompt de cada skill. Há, porém, embedding/RAG para um propósito
  específico: memória institucional de respostas de refinamento (`embedding_service`/
  `rag_service`, Qdrant embarcado — ver seção 6/`docs/agent/memory.md`).

## 10. Qualidade e cobertura de testes

Suíte de testes totalmente mockada (nenhuma chamada real a Ollama/Jira/Confluence/Qdrant),
avaliação em três camadas (checklist automático, checagem determinística do catálogo fechado +
LLM-como-juiz, revisão humana — ver `docs/agent/evaluation.md`). Ver o relatório de cobertura
gerado por `uv run pytest` para os números atuais.

## 11. O que ainda falta (deliberadamente adiado, não esquecido)

- **Integração real com Figma (leitura/escrita)** — a primeira integração não-textual da
  plataforma, deliberadamente adiada para uma issue futura separada. `figma_service.py` não
  existe neste build; `UISpecification.figma_file_reference` existe no schema, mas fica sempre
  vazio.
- **Integração com Storybook** (publicar/ler componentes reais implementados) — issue futura
  separada, sem `storybook_service.py` neste build.
- **Integração com GitHub** (abrir PR com tokens/especificação) — issue futura separada, sem
  `github_service.py` nem flags como `--abrir-pr-github` neste build.
- **Outros catálogos de design system** (Apple Human Interface Guidelines, Microsoft Fluent,
  IBM Carbon) — só Material Design 3 nesta fase.
- **Validação real ao vivo de qualquer coisa além do pipeline textual central** — a suíte de
  testes é inteiramente mockada; uma rodada ao vivo completa (Ollama/provedor em nuvem real)
  ainda não foi documentada para este agente especificamente.

## 12. Como executar

```bash
uv sync
uv run pytest
uv run python run.py --arquivo ux-spec.md --saida ui-spec.md
```

Ver `README.md`/`README.pt.md` para o setup completo (Ollama, `.env`) e `run.py --help` para
todas as opções (`--refinar`, `--publicar-confluence`, `--atualizar-confluence`).

## 13. Conclusão

O AQuA-QE UI Designer fecha uma lacuna real da plataforma — a camada de apresentação visual
entre "como o usuário navega" (UX Specification) e "como construir tecnicamente" (Solution
Design), sem duplicar responsabilidades já cobertas pelos agentes irmãos. Sua Fase 1 é
deliberadamente restrita ao núcleo textual, seguindo o mesmo princípio que já rege toda a
plataforma: entregar o que cabe no padrão estabelecido (rastreabilidade, catálogo fechado,
validação, revisão humana) primeiro, e documentar honestamente o que foi adiado — Figma,
Storybook e GitHub ficam para issues futuras, não construídos especulativamente aqui.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
