# CLAUDE.md

Este arquivo orienta o Claude Code ao trabalhar neste repositório.

## O que é este projeto

Agente que gera UI Specifications (telas com componentes recomendados de um catálogo fechado
de design system — Material Design 3, estados de interação, sugestões de design tokens e notas
de layout responsivo) a partir de uma UX Specification já pronta do agente irmão AQuA-QE UX
Designer — com rastreabilidade obrigatória à fonte, validação automática e revisão humana no
centro do ciclo. Ver `WHITEPAPER.md` (também em inglês: `WHITEPAPER.en.md`) para a visão
completa, `docs/agent/` para a especificação completa e `docs/architecture/` para os diagramas (draw.io + SVG).

Este é um **repositório standalone**, próprio, independente de qualquer monorepo — não assuma
dependências herdadas de um workspace pai.

**Status atual**: Fase 1 (núcleo) implementada — `src/` tem models/skills/workflow/orchestrator/services
completos, `run.py` funcional, `tests/` totalmente mockados. Sem integração com
Figma/Storybook/GitHub ainda (issues futuras separadas).

## Comandos essenciais

```bash
# Instalar/sincronizar dependências
uv sync

# Rodar toda a suíte de testes (mockada, sem chamadas reais a Ollama/Jira/Confluence/Qdrant)
uv run pytest

# Rodar um teste único
uv run pytest tests/test_generate_ui_specification_workflow.py::test_nome_do_teste

# Gerar uma UI Specification a partir de um arquivo
uv run python run.py --arquivo ux-spec.md --saida ui-spec.md

# Ver todas as opções (--texto, --jira, --confluence, --refinar, --publicar-confluence, --atualizar-confluence)
uv run python run.py --help
```

Não há configuração própria de lint/type-check (`ruff`/`basedpyright`) neste `pyproject.toml`
— isso existe apenas na raiz do monorepo que originou este projeto, não neste repositório
standalone.

## Setup local

Ver a seção "Setup"/"Configuração" em `README.md`/`README.pt.md`: requer Python 3.12+, `uv`,
Ollama instalado com os modelos `mistral`, `phi4` e `bge-m3` baixados, e um `.env` preenchido a
partir de `.env.example`.

## Arquitetura (resumo — detalhe completo em `docs/agent/system_design.md` e `WHITEPAPER.md`)

```
Entrada (UX Specification via arquivo/texto/Jira/Confluence — uma fonte, mutuamente exclusiva)
  → CLI (run.py) → orchestrator/ui_designer.py → workflow/generate_ui_specification.py → skills/* → models/* → services/*
```

- `src/aqua_qe_ui_designer/models/` — `UISpecification`, `UIScreen`, `DesignTokensSuggestion`,
  `ChatMessage`, enum `ArtifactStatus`.
- `src/aqua_qe_ui_designer/skills/` — funções de responsabilidade única (ver
  `docs/agent/skills.md`), mais dois auxiliares internos (não skills públicas):
  `_normalizacao.py` (normalização defensiva de respostas do LLM que deveriam ser uma única
  string ou uma lista de strings simples, reutilizada por toda skill que pede isso a um LLM) e
  `_material_design_3_catalog.py` (`COMPONENTES_MD3`, o catálogo fechado consultado por mais de
  uma skill).
- `src/aqua_qe_ui_designer/workflow/generate_ui_specification.py` — `generate_ui_specification`,
  `finalize_ui_specification` (validate→review, sempre recomputa `recommendations_synthesis` ao
  final, mesmo se validate/review reprovarem), `refine_and_finalize_ui_specification`.
- `src/aqua_qe_ui_designer/orchestrator/ui_designer.py` — ponto de entrada único,
  `handle_request(texto_uxs, uxs_reference="")`.
- `src/aqua_qe_ui_designer/services/` — integrações externas: `llm_service` (Ollama por
  padrão, mais o toggle de provedor em nuvem `LLM_PROVIDER=ollama|nvidia|cerebras|google|groq`),
  `jira_service` (REST API + httpx, **apenas leitura**), `confluence_service` (REST API + httpx,
  **leitura e escrita**, reaproveitado verbatim do Solution Architect/UX Designer),
  `embedding_service`/`rag_service` (Ollama `bge-m3` + Qdrant embarcado — memória institucional
  de refinamento, ver abaixo).

## Convenções críticas

- **GR-UI-1, o guardrail mais importante deste agente**: nenhum componente citado em
  `UIScreen.components` pode existir fora do catálogo fechado Material Design 3
  (`knowledge/methodology/material_design_3.md` / `skills/_material_design_3_catalog.py`).
  `identify_screens_and_components` e `refine_ui_specification` descartam silenciosamente
  qualquer componente fora do catálogo antes de retornar; `review_ui_specification` verifica
  isso de novo, de forma **determinística** (Python puro, não delegado só ao LLM revisor) —
  defesa em profundidade contra um componente inválido reintroduzido por um refino posterior.
- **GR-UI-2**: `suggest_design_tokens` sempre rotula sua saída como sugestão a confirmar com o
  time de Design — nunca a identidade visual definitiva do produto, a menos que a UX
  Specification/PRD de origem já a especifique explicitamente.
- **GR-UI-3**: `review_accessibility_visual` sempre recomenda "verificar" um critério WCAG 2.2
  específico, nunca certifica conformidade como fato.
- **GR-UI-4**: nenhuma skill descreve ou fabrica um render visual real — `figma_file_reference`
  fica sempre vazio nesta fase; `format_ui_specification_markdown` marca essa seção
  explicitamente como fora de escopo.
- **GR-UI-5**: telas/componentes/design tokens só vêm do que a UX Specification/PRD de origem
  realmente descreve (ou de uma referência real do Material Design 3/W3C Design Tokens) — nunca
  de uma suposição sobre a identidade do produto; `define_responsive_layout` só cita as window
  size classes reais (compact/medium/expanded), nunca um breakpoint numérico inventado.
- **Sem aprovação automática**: nenhuma skill/workflow define `ArtifactStatus.ACCEPTED`. Esse
  status só é atribuído pelo CLI (`run.py`), após confirmação humana explícita no terminal.
- **Dois LLMs sempre diferentes**: `OLLAMA_MODEL` (padrão `mistral`) gera; `OLLAMA_REVIEW_MODEL`
  (padrão `phi4`) revisa. Deliberado — mitiga *self-preference bias*.
- **Piloto de provedor via toggle desde a Fase 1** (`LLM_PROVIDER=ollama|nvidia|cerebras|google|groq`,
  padrão `ollama`) — diferente dos agentes irmãos, que o adicionaram depois de necessidade real
  comprovada; aqui a infraestrutura já é bem conhecida da plataforma, então o custo de portá-la
  desde o início é baixo. `llm_service.generator_model()`/`reviewer_model()` resolvem o modelo
  certo conforme o provedor ativo; `complete`/`complete_json` mantêm assinatura inalterada.
  `complete_json` usa `json.JSONDecoder().raw_decode()` (tolera lixo após o JSON válido) e
  rejeita explicitamente qualquer JSON que não seja um objeto — bugs já corrigidos e
  documentados nos agentes irmãos, preservados aqui desde o início.
- **`_chat()` em `llm_service.py` usa despacho explícito `if/elif`** entre provedores — nunca
  um dict-de-callables/dict-de-funções, porque esse padrão captura os objetos de função no
  momento do import e quebra silenciosamente os testes baseados em `monkeypatch` (regressão já
  sofrida nesta plataforma).
- **Normalização defensiva de respostas do LLM é um módulo compartilhado desde o dia 1**
  (`skills/_normalizacao.py`) — toda skill que pede "uma lista de itens" ou "várias coisas como
  uma única string" a um LLM reutiliza `item_para_string`/`texto_ou_lista`/`lista_de_strings`
  em vez de reimplementar a defesa por arquivo. Esse exato bug (LLM devolvendo lista de
  objetos, dict aninhado, dict de item→'', ou uma string com repr de dict/list embutido) já
  apareceu repetidas vezes no agente irmão AQuA-QE UX Designer.
- **`refine_ui_specification` preserva o detalhe de campos não abordados pelas respostas do
  humano** — mesmo cuidado aplicado desde o início em todo agente desta plataforma, aprendido
  com um bug real corrigido em `refine_epic_metadata`/`refine_prd` no Product Owner.
- **`jira_service` é apenas leitura** — mesmo princípio dos agentes irmãos; não há hoje um caso
  de uso real de write-back no Jira a partir de uma UI Specification.
- **`confluence_service` tem escrita gated** — publicar (`--publicar-confluence`, cria página
  nova, sempre irmã da página de origem da UX Specification) ou atualizar
  (`--atualizar-confluence`, edita uma página existente informada) sempre exigem confirmação
  humana explícita no CLI, mutuamente exclusivos entre si.
- **Entrada de fonte única e flexível** (`--arquivo`/`--texto`/`--jira`/`--confluence`,
  mutuamente exclusivos) — padrão do Solution Architect, não o padrão dual-obrigatório do UX
  Designer, porque este agente só precisa de um único documento de entrada (a UX Specification
  já consolidada).
- **Este agente nunca gera fluxos de navegação ou arquitetura da informação** (papel exclusivo
  do AQuA-QE UX Designer), **nunca gera PRD** (Product Manager), **nunca gera Épicos/User
  Stories** (Product Owner), **nunca projeta arquitetura técnica** (Solution Architect).
  Consome a UX Specification já pronta e produz um único artefato novo, a UI Specification.
- **Nenhuma integração com Figma, Storybook ou GitHub neste build** — sem `figma_service.py`,
  `storybook_service.py`, `github_service.py`, sem flags `--publicar-figma`/`--abrir-pr-github`.
  Issues futuras separadas (ver `WHITEPAPER.md`, seção 11).
- **Memória institucional de respostas de refinamento** (`record_refinement_answer`/
  `suggest_refinement_answer`, `rag_service.py`): cada resposta que o humano dá num ciclo de
  refinamento é gravada numa collection Qdrant embarcada própria (`refinement_answer_memory`)
  via embedding local (`bge-m3`). No ciclo seguinte, se uma pergunta parecida aparecer (mesmo
  ou outro artefato/projeto), a resposta mais similar já dada é exibida como sugestão no
  terminal, com o score de similaridade — **nunca aplicada automaticamente**.
- **Testes sempre mockam** Ollama/Jira/Confluence/Qdrant — nenhum teste em `tests/` faz chamada
  real de rede.

## Onde procurar mais detalhe

- `docs/agent/` — PRD, System Design, Agent Design, Rules, Guardrails, Persona, Objectives,
  Skills, Evaluation, Memory (a spec formal completa do agente, escrita antes de qualquer
  código).
- `knowledge/methodology/` — os frameworks reais que fundamentam os critérios de qualidade
  (catálogo Material Design 3, WCAG 2.2, vocabulário núcleo do W3C Design Tokens) — nenhum
  critério do agente foi inventado à parte desses documentos.
- `docs/architecture/` — diagramas visuais (draw.io + SVG) dos mesmos fluxos: arquitetura em
  camadas, fluxo da UI Specification, GR-UI-1 (catálogo fechado Material Design 3, com defesa
  em profundidade), ciclo de refinamento humano-no-loop com memória RAG e o pipeline completo
  com o handoff a partir do UX Designer.
- `WHITEPAPER.md` / `WHITEPAPER.en.md` — visão consolidada, inclui o que foi deliberadamente
  deixado fora da Fase 1 (seção 11).
