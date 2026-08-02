# AQuA-QE UI Designer

Agente que gera **UI Specifications** — telas com componentes recomendados de um catálogo
fechado de design system (Material Design 3), estados de componente, sugestões de design
tokens, notas de layout responsivo e recomendações de acessibilidade visual — a partir de uma
UX Specification já pronta do agente irmão [AQuA-QE UX Designer](https://github.com/dufelizardo/AQuA-QE-UX-Designer).
Com rastreabilidade obrigatória à fonte, validação automática e revisão humana no centro do
ciclo. Ver `WHITEPAPER.md` para a visão completa.

**Qual problema resolve**: transforma uma UX Specification aceita em detalhe de tela/componente
pronto para implementação, em vez de um arquivo Figma em branco.
**Quem usa**: UI designers e desenvolvedores front-end que precisam de um ponto de partida
fundamentado para o design visual (componentes, estados, tokens, notas responsivas/acessibilidade).
**Qual o benefício**: componentes só de um catálogo real e fechado (Material Design 3, nunca
inventado), design tokens sempre rotulados "sugestão a confirmar", copy de rascunho sempre
rotulada como tal — um ponto de partida defensável, nunca uma suposição apresentada como definitiva.
**Como funciona (alto nível)**: UX Specification → telas/componentes/estados/tokens/responsivo/
acessibilidade → valida → revisa (checagem determinística do catálogo + um LLM independente) →
[refina] → aceite humano.

**Status**: Fase 1 (núcleo) implementada — sem integração com Figma/Storybook/GitHub ainda
(issues futuras separadas), seguindo o mesmo padrão gerar→validar→revisar→aceite humano já
usado nos quatro agentes irmãos.

Este projeto tem repositório git próprio, independente do monorepo raiz (conforme a convenção
"todo projeto novo recebe repositório separado" — ver `CLAUDE.md` raiz do workspace).

## O que este agente faz

- Lê uma UX Specification por uma de quatro fontes flexíveis e mutuamente exclusivas: arquivo
  local, texto/chat direto, ticket Jira (apenas leitura) ou página Confluence (apenas leitura).
- Identifica as telas descritas na UX Specification e, para cada uma, os componentes
  aplicáveis do catálogo fechado Material Design 3 — nunca um componente fora desse catálogo.
- Define estados de interação relevantes (hover/focus/disabled/loading/error/success) por tela.
- Sugere design tokens (cores/tipografia/espaçamento) — sempre rotulados "sugestão a
  confirmar", nunca afirmados como a identidade visual real já estabelecida do produto.
- Define notas de layout responsivo citando as window size classes reais do Material Design 3
  (compact/medium/expanded) — nunca breakpoints inventados.
- Gera recomendações de acessibilidade visual fundamentadas em WCAG 2.2 — sempre "a
  verificar", nunca certificação de conformidade.
- Roda um ciclo de refinamento humano-no-loop quando a revisão reprova, com memória
  institucional de respostas de refinamento (RAG).
- Exporta o resultado em Markdown e, opcionalmente, publica como página irmã da UX
  Specification de origem no Confluence ou atualiza uma página já existente.

## O que este agente **não** faz (por design, nesta fase)

- **Nunca gera fluxos de navegação ou arquitetura da informação** — permanece
  responsabilidade exclusiva do UX Designer; este agente só consome esse texto como entrada.
- **Nunca integra com Figma, Storybook ou GitHub** — exigem integrações que a plataforma ainda
  não tem. Planejadas como issues futuras separadas. `UISpecification.figma_file_reference` já
  existe no schema (para não precisar mudar depois), mas fica sempre vazio neste build.
- **Nunca certifica conformidade de acessibilidade nem alega ter produzido um render visual
  real** — o agente não tem acesso a nenhuma ferramenta de design real nem de auditoria.
- Nunca gera PRD, Épicos/Stories, arquitetura técnica ou uma UX Specification (permanecem
  responsabilidade dos outros quatro agentes irmãos).

## Arquitetura (resumo — detalhe completo em `docs/agent/system_design.md`)

- **`src/aqua_qe_ui_designer/models/`** — `UISpecification`, `UIScreen`, `DesignTokensSuggestion`, `ChatMessage`, enum `ArtifactStatus`.
- **`src/aqua_qe_ui_designer/skills/`** — funções de responsabilidade única (ver `docs/agent/skills.md`), mais dois auxiliares internos compartilhados: `_normalizacao.py` (normalização defensiva de respostas do LLM que deveriam ser uma string/lista de strings simples) e `_material_design_3_catalog.py` (o catálogo fechado de componentes).
- **`src/aqua_qe_ui_designer/workflow/`** — orquestração da sequência de skills.
- **`src/aqua_qe_ui_designer/orchestrator/`** — ponto de entrada único (`handle_request`).
- **`src/aqua_qe_ui_designer/services/`** — `llm_service` (Ollama por padrão, mais um toggle de provedor em nuvem — `LLM_PROVIDER=nvidia|cerebras|google|groq`), `jira_service` (apenas leitura), `confluence_service` (leitura + escrita gated), `embedding_service`/`rag_service` (Ollama `bge-m3` + Qdrant embarcado — memória institucional de refinamento).

## Configuração

1. Instale [Python 3.12+](https://www.python.org/) e [uv](https://docs.astral.sh/uv/).
2. Instale o [Ollama](https://ollama.com) e baixe os três modelos locais usados por este agente:
   ```bash
   ollama pull mistral   # geração
   ollama pull phi4      # revisão independente
   ollama pull bge-m3    # embeddings (memória institucional de refinamento)
   ```
3. Instale as dependências:
   ```bash
   uv sync
   ```
4. Copie `.env.example` para `.env` e preencha os valores necessários (o Ollama funciona com os padrões; credenciais de Jira/Confluence são necessárias para `--jira`/`--confluence`/`--publicar-confluence`):
   ```bash
   cp .env.example .env
   ```

## Uso

```bash
uv run python run.py --arquivo ux-spec.md --saida ui-spec.md
uv run python run.py --confluence <url-da-ux-spec> --refinar --saida ui-spec.md
uv run python run.py --help
```

## Status detalhado

`docs/agent/` (PRD, System Design, Agent Design, Rules, Guardrails, Persona, Objectives,
Skills, Evaluation, Memory) e `docs/standards/` estão completos. `knowledge/methodology/` tem
os três documentos reais que fundamentam os critérios de qualidade (o catálogo de
componentes/cores/tipografia/window size classes do Material Design 3, WCAG 2.2 e o
vocabulário núcleo do W3C Design Tokens) — nenhum critério foi inventado à parte deles.
`knowledge/templates/ui_specification.md` define o formato de exportação.

`src/` (models/skills/workflow/orchestrator/services), `run.py` (CLI) e `tests/` estão
implementados e totalmente mockados (nenhuma chamada real a Ollama/Jira/Confluence/Qdrant).
Ver `WHITEPAPER.md`, seção 11, para o que fica deliberadamente fora desta fase (integrações
com Figma/Storybook/GitHub, catálogos de design system adicionais, validação real ao vivo).

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
