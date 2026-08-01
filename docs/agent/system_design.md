# System Design

> Estrutura conforme `../standards/system_design_standard.md`.

## Visão geral da arquitetura

O agente é um pipeline de skills orquestrado sequencialmente, com dois pontos de checagem
antes de qualquer saída ser considerada válida: validação automática (checklist estrutural) e
revisão humana obrigatória — mesmo padrão de PM/PO/SA/UX Designer. A revisão por LLM é reforçada
por uma checagem determinística (Python puro) do catálogo fechado Material Design 3, defesa em
profundidade do guardrail mais crítico (GR-UI-1). Não há aprovação automática (ver
`guardrails.md`).

```
Entrada (UX Specification via arquivo/texto/Jira/Confluence — uma fonte, mutuamente exclusiva)
   → read_text_file / read_jira_issue / read_confluence_page / parse_chat_transcript+format_chat_transcript
   → extract_ui_context (título + contexto do problema)
   → identify_screens_and_components (telas + componentes do catálogo fechado Material Design 3)
   → define_component_states (estados de interação por tela)
   → suggest_design_tokens (cores/tipografia/espaçamento — sempre sugestão)
   → define_responsive_layout (window size classes Material Design 3)
   → review_accessibility_visual (recomendações WCAG 2.2)
   → validate_ui_specification (checklist automático)
   → review_ui_specification (checagem determinística do catálogo + LLM revisor independente — phi4)
   → [se reprovado] generate_ui_clarifying_questions → resposta humana → refine_ui_specification → revalidar
   → synthesize_recommendations (síntese priorizada de acessibilidade + revisão)
   → aceite humano explícito
   → format_ui_specification_markdown (export local)
   → [opcional] get_confluence_publish_location → create_confluence_page (nova) OU update_confluence_page (existente)
```

## Componentes

- **Orquestrador** — ponto de entrada único (`handle_request`), decide a sequência de skills
  (ordem fixa do `agent_manifest.yaml`). Implementado em
  `../../src/aqua_qe_ui_designer/orchestrator/ui_designer.py`.
- **Workflow** — orquestração da sequência de skills (`generate_ui_specification`,
  `finalize_ui_specification`), implementado em `../../src/aqua_qe_ui_designer/workflow/`.
- **Skills** — funções descritas em `skills.md`, implementadas em
  `../../src/aqua_qe_ui_designer/skills/`. Inclui o módulo compartilhado `_normalizacao.py`
  (normalização defensiva de respostas do LLM) e `_material_design_3_catalog.py` (catálogo
  fechado consultado por mais de uma skill).
- **Modelos de dados** — `UISpecification`, `UIScreen`, `DesignTokensSuggestion`, `ChatMessage`,
  enum `ArtifactStatus`, implementados em `../../src/aqua_qe_ui_designer/models/`, conforme
  `output_schema.md`.
- **Fontes de conhecimento** — `knowledge/methodology/` (catálogo Material Design 3, WCAG 2.2,
  vocabulário núcleo W3C Design Tokens), consumido diretamente no prompt de cada skill (sem RAG
  nesta fase — o volume cabe direto no contexto).
- **Interfaces externas** — entrada: arquivo local, texto/chat, ticket Jira (leitura) ou página
  Confluence (leitura); saída: arquivo Markdown exportado (`format_ui_specification_markdown`)
  e, opcionalmente, uma página no Confluence (`create_confluence_page`), sempre irmã da página
  de origem e sempre atrás de confirmação humana.

## Fluxo de dados

1. A entrada é lida por uma das quatro skills de leitura (mutuamente exclusivas no CLI), sem
   escrita em nenhuma delas nesta etapa.
2. `extract_ui_context` identifica título e contexto do problema.
3. `identify_screens_and_components` identifica as telas e os componentes Material Design 3
   aplicáveis, descartando qualquer um fora do catálogo (GR-UI-1).
4. `define_component_states` define estados de interação por tela.
5. `suggest_design_tokens` sugere candidatos de design tokens, sempre rotulados como sugestão.
6. `define_responsive_layout` gera notas de layout responsivo citando as window size classes reais.
7. `review_accessibility_visual` gera recomendações WCAG 2.2 sobre as telas/componentes.
8. `validate_ui_specification` aplica o checklist automático; se reprovar, a UI Specification
   fica `pending_clarification`.
9. Se aprovado no checklist, `review_ui_specification` roda a checagem determinística do
   catálogo fechado e, em seguida, o LLM revisor independente avalia o conjunto.
10. Se a revisão reprovar, o ciclo de refinamento humano-no-loop (mesmo padrão de PM/PO/SA/UX
    Designer) entra em ação.
11. A aprovação final é sempre um ato humano, fora da responsabilidade do agente — só então a
    UI Specification é exportada.

## Modos de operação

Um único fluxo nesta fase — gerar a UI Specification a partir de uma UX Specification já
pronta. Sem distinção "unitário/lote" — mesma razão de design do Solution Architect/UX
Designer (só existe um artefato nesta fase).

## Restrições técnicas

- Dois LLMs locais via Ollama por padrão (`OLLAMA_MODEL` gerador, `OLLAMA_REVIEW_MODEL`
  revisor) — mesma convenção de PM/PO/SA/UX Designer.
- **Piloto de provedor de LLM em nuvem** — `LLM_PROVIDER=ollama|nvidia|cerebras|google|groq`,
  padrão `ollama`. Portado desde a Fase 1 (diferente de PM/PO/SA/UX Designer, que o adicionaram
  depois de necessidade real comprovada) — a infraestrutura já é bem conhecida da plataforma, e
  o custo de portá-la desde o início é baixo.
- Sem RAG/embeddings sobre `knowledge/methodology/` nesta fase — pequeno o suficiente para
  caber direto no prompt de cada skill. Há, porém, embedding/RAG para um propósito específico:
  memória institucional de respostas de refinamento (`embedding_service`/`rag_service`, Qdrant
  embarcado — ver `memory.md`).
- Jira é só leitura, sem escrita — mesmo princípio de "nenhum serviço construído sem consumidor
  real" já aplicado em PM/PO/SA/UX Designer. Confluence tem escrita gated (publicar/atualizar),
  sempre atrás de confirmação humana e sempre como página irmã da fonte.
- **Nenhuma integração com Figma, Storybook ou GitHub nesta fase** — `figma_file_reference`
  existe no schema, mas fica sempre vazio; nenhum `figma_service.py`/`storybook_service.py`/
  `github_service.py` é criado neste build (ver `WHITEPAPER.md`, seção 11).

## Observabilidade

Cada execução deve registrar: fonte de entrada (UX Specification), telas/componentes/estados
identificados, resultado do checklist automático e da revisão (incluindo a checagem
determinística do catálogo), e se houve ciclo de refinamento — necessário para auditar
rastreabilidade (ver `guardrails.md`) e para os casos de teste de `evaluation.md`.
