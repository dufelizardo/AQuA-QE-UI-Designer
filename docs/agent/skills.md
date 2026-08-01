# Skills

> **Nota de fase**: este documento descreve as skills da Fase 1 (o núcleo — sem
> Figma/Storybook/GitHub, adiados para issues futuras), na ordem do `agent_manifest.yaml` —
> todas implementadas em `../../src/aqua_qe_ui_designer/skills/`, no formato definido em
> `../standards/skill_standard.md`. Tipos de entrada/saída referem-se às estruturas de
> `output_schema.md`, implementadas em `../../src/aqua_qe_ui_designer/models/`.
>
> `extract_ui_context`, `identify_screens_and_components`, `define_component_states`,
> `suggest_design_tokens`, `define_responsive_layout`, `review_accessibility_visual`,
> `generate_ui_clarifying_questions`, `refine_ui_specification` e `synthesize_recommendations`
> usam o LLM gerador (`../../src/aqua_qe_ui_designer/services/llm_service.py::generator_model()`;
> Ollama local por padrão, `OLLAMA_MODEL`/padrão `mistral` — ou um provedor em nuvem via
> `LLM_PROVIDER`, ver `system_design.md`). `validate_ui_specification` e
> `format_ui_specification_markdown` são Python puro, sem LLM. `review_ui_specification` usa o
> LLM revisor (`llm_service.py::reviewer_model()`; Ollama `OLLAMA_REVIEW_MODEL`/padrão `phi4`),
> sempre diferente do gerador, combinado com uma checagem determinística (Python puro) do
> catálogo fechado Material Design 3. `read_jira_issue`/`read_confluence_page` usam a API REST
> do Jira/Confluence Cloud — **apenas leitura**. `create_confluence_page`/`update_confluence_page`/
> `get_confluence_publish_location` **escrevem** no Confluence Cloud — sempre atrás de
> confirmação humana explícita no CLI (`run.py`), reaproveitando o padrão já provado no
> Solution Architect/UX Designer.

## read_text_file

- **Descrição**: lê um arquivo `.txt`/`.md` local (ex.: uma UX Specification exportada) e retorna seu conteúdo. Sem LLM.
- **Entrada**: `caminho: str`.
- **Saída**: `str`.
- **Efeitos colaterais**: leitura de arquivo local.
- **Erros esperados**: arquivo inexistente ou sem permissão de leitura.
- **Dependências**: nenhuma.

## parse_chat_transcript

- **Descrição**: separa uma transcrição de chat em mensagens por remetente. Puro Python (regex), sem LLM.
- **Entrada**: `texto: str`.
- **Saída**: `list[ChatMessage]`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: nenhum — texto sem remetente identificável vira uma única mensagem sem remetente.
- **Dependências**: nenhuma.

## format_chat_transcript

- **Descrição**: reconstrói uma transcrição normalizada ("Remetente: mensagem" por parágrafo) a partir das mensagens. Puro Python, determinístico.
- **Entrada**: `mensagens: list[ChatMessage]`.
- **Saída**: `str`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `parse_chat_transcript`.

## read_jira_issue

- **Descrição**: busca um ticket Jira e retorna como texto simples, convertendo do Atlassian Document Format. Apenas leitura — este agente nunca escreve de volta no Jira.
- **Entrada**: `issue_key: str` (ex.: `"AQUAQE-11"`).
- **Saída**: `str`.
- **Efeitos colaterais**: chamada HTTP `GET` ao Jira Cloud.
- **Erros esperados**: credencial ausente, ticket inexistente ou sem permissão.
- **Dependências**: nenhuma.

## read_confluence_page

- **Descrição**: busca uma página do Confluence Cloud (tipicamente a UX Specification publicada, aceita URL completa ou ID) e retorna título + corpo como texto simples. Apenas leitura.
- **Entrada**: `pagina: str` (URL completa ou ID).
- **Saída**: `str`.
- **Efeitos colaterais**: chamada HTTP `GET` ao Confluence Cloud.
- **Erros esperados**: credencial ausente, página inexistente ou sem permissão (HTTP 4xx).
- **Dependências**: nenhuma outra skill. Reaproveita `confluence_service.py`, portado do Solution Architect/UX Designer.

## get_confluence_publish_location

- **Descrição**: deriva o espaço/ancestral de publicação a partir da página de origem da UX Specification, para que a UI Specification seja publicada como página irmã — nunca de configuração manual solta (RULE-UI-7).
- **Entrada**: `pagina_origem: str` (URL/ID da UX Specification).
- **Saída**: `tuple[str, str | None]` (espaço, ID do ancestral).
- **Efeitos colaterais**: chamada HTTP `GET` ao Confluence Cloud.
- **Erros esperados**: página de origem sem página-mãe identificável.
- **Dependências**: consome a mesma fonte de `read_confluence_page`.

## create_confluence_page

- **Descrição**: cria a UI Specification como página nova no Confluence Cloud, sempre como irmã da página de origem. Só é chamada pelo CLI após confirmação humana explícita (RULE-UI-7).
- **Entrada**: `texto: str`, `titulo: str`, `space_key: str`, `parent_page_id: str | None`.
- **Saída**: `str` (URL da página criada).
- **Efeitos colaterais**: chamada HTTP `POST` ao Confluence Cloud — **escreve** em sistema externo.
- **Erros esperados**: credencial ausente, espaço/ancestral inválido.
- **Dependências**: consome `get_confluence_publish_location` e `format_ui_specification_markdown`.

## update_confluence_page

- **Descrição**: atualiza uma página da UI Specification já existente no Confluence Cloud (aceita URL completa ou apenas o ID), preservando título e incrementando a versão. Só é chamada pelo CLI após confirmação humana explícita (RULE-UI-7), e é mutuamente exclusiva com `create_confluence_page` numa mesma execução (`--atualizar-confluence`/`--publicar-confluence`).
- **Entrada**: `pagina: str`, `texto: str`.
- **Saída**: `None`.
- **Efeitos colaterais**: chamadas HTTP `GET`+`PUT` ao Confluence Cloud — **escreve** em sistema externo.
- **Erros esperados**: credencial ausente, página inexistente ou sem permissão.
- **Dependências**: consome `format_ui_specification_markdown`.

## extract_ui_context

- **Descrição**: extrai título e contexto do problema a partir do texto da UX Specification de origem. Nunca regenera fluxos de navegação/arquitetura da informação — só os lê como contexto.
- **Entrada**: `texto_uxs: str`.
- **Saída**: `dict` (`title`, `context_problem`).
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome a saída de `read_text_file`/`read_jira_issue`/`read_confluence_page`/`format_chat_transcript`.

## identify_screens_and_components

- **Descrição**: identifica as telas de navegação descritas na UX Specification e, para cada uma, os componentes do catálogo fechado Material Design 3 (`../../knowledge/methodology/material_design_3.md`) que se aplicam. Descarta qualquer componente fora do catálogo em vez de repassá-lo adiante (GR-UI-1, o guardrail mais importante deste agente).
- **Entrada**: `texto_uxs: str`, `contexto: dict` (de `extract_ui_context`).
- **Saída**: `list[UIScreen]` (`name`, `components: list[str]`, `source_reference`).
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido; UX Specification sem detalhe suficiente (retorna menos telas/componentes, nunca inventa — GR-UI-5).
- **Dependências**: consome a saída de `extract_ui_context`.

## define_component_states

- **Descrição**: define, para cada tela e os componentes já identificados nela, os estados de interação relevantes (hover/focus/disabled/loading/error/success). Só roda para telas com componentes já identificados.
- **Entrada**: `screens: list[UIScreen]`.
- **Saída**: `list[UIScreen]` (mesmas telas, com `states` preenchido).
- **Efeitos colaterais**: chamada ao LLM gerador (pulada se nenhuma tela tiver componentes).
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome a saída de `identify_screens_and_components`.

## suggest_design_tokens

- **Descrição**: sugere candidatos de design tokens (cores/tipografia/espaçamento), sempre citando papéis semânticos reais do Material Design 3 e a nomenclatura do W3C Design Tokens — sempre rotulado como sugestão a confirmar, nunca a identidade visual definitiva do produto (GR-UI-2).
- **Entrada**: `texto_uxs: str`, `contexto: dict`.
- **Saída**: `DesignTokensSuggestion` (`colors`, `typography`, `spacing`).
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome a saída de `extract_ui_context`.

## define_responsive_layout

- **Descrição**: gera notas de layout responsivo citando as window size classes reais do Material Design 3 (compact/medium/expanded) — nunca um breakpoint numérico inventado (GR-UI-5).
- **Entrada**: `texto_uxs: str`, `contexto: dict`.
- **Saída**: `str`.
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome a saída de `extract_ui_context`.

## review_accessibility_visual

- **Descrição**: gera recomendações de acessibilidade visual fundamentadas em WCAG 2.2 (`../../knowledge/methodology/wcag.md`) sobre as telas/componentes identificados — sempre como recomendação a verificar, nunca certificação de conformidade (GR-UI-3).
- **Entrada**: `screens: list[UIScreen]`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM gerador (pulada se não houver telas).
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome a saída de `identify_screens_and_components`/`define_component_states`.

## validate_ui_specification

- **Descrição**: valida a UI Specification contra o checklist automático (`validation_checklist.md`) e retorna os motivos específicos de reprovação — mesmo contrato `list[str]` já corrigido nos agentes irmãos (nunca `bool` sem motivo).
- **Entrada**: `spec: UISpecification`.
- **Saída**: `list[str]` — motivos de reprovação, acumulando todos; lista vazia = aprovado no checklist.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `identify_screens_and_components`/`define_component_states`/`suggest_design_tokens`/`define_responsive_layout`/`review_accessibility_visual`.

## review_ui_specification

- **Descrição**: revisa a UI Specification com um LLM diferente do gerador, combinado com uma checagem determinística (Python puro) que garante GR-UI-1 mesmo se o LLM revisor não perceber um componente inválido. Verifica também se todo componente identificado tem estados definidos e se há recomendação de acessibilidade associada às telas.
- **Entrada**: `spec: UISpecification`.
- **Saída**: `dict` (`aprovado: bool`, `problemas: list[str]`).
- **Efeitos colaterais**: chamada ao LLM revisor.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: roda depois de `validate_ui_specification` aprovar.

## generate_ui_clarifying_questions

- **Descrição**: transforma os apontamentos de `review_notes` em perguntas objetivas para o usuário.
- **Entrada**: `spec: UISpecification`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome `review_notes`, preenchido por `validate_ui_specification` ou `review_ui_specification`.

## refine_ui_specification

- **Descrição**: reescreve os campos afetados pelas respostas do usuário, preservando o texto/nível de detalhe dos campos que as respostas não abordam — mesmo cuidado já aplicado em `refine_solution_design`/`refine_ux_specification` nos agentes irmãos, aprendido com um bug real de obsolescência. Componentes citados continuam sempre filtrados pelo catálogo fechado (GR-UI-1).
- **Entrada**: `spec: UISpecification`, `respostas: list[dict]` (`{"pergunta": str, "resposta": str}`).
- **Saída**: `UISpecification`.
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: consome `generate_ui_clarifying_questions` + resposta humana coletada pelo CLI.

## synthesize_recommendations

- **Descrição**: sintetiza e prioriza as 3 a 5 questões mais críticas combinando as recomendações de acessibilidade visual (`review_accessibility_visual`) e as observações da revisão (`review_ui_specification`/`validate_ui_specification`) já existentes — nunca inventa um item novo que não esteja em uma das duas listas de entrada.
- **Entrada**: `accessibility_recommendations: list[str]`, `review_notes: list[str]`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM gerador.
- **Erros esperados**: resposta do LLM não é JSON válido.
- **Dependências**: roda em `finalize_ui_specification`, depois de `review_notes` estar definido.

## format_ui_specification_markdown

- **Descrição**: exporta a UI Specification em Markdown, seguindo as seções de `../../knowledge/templates/ui_specification.md`. A seção "Escopo" cita `uxs_reference` (link/chave, não o texto completo) e sempre marca `figma_file_reference` como fora de escopo nesta fase (GR-UI-4) quando vazio.
- **Entrada**: `spec: UISpecification`.
- **Saída**: `str`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída final de `refine_ui_specification` (ou a saída inicial, se aprovada sem refino).

## record_refinement_answer

- **Descrição**: grava uma resposta que o humano deu a uma pergunta de esclarecimento do ciclo de refinamento, para reaproveitamento futuro como sugestão editável — memória institucional entre ciclos (mesmo ou de outro artefato/projeto), nunca aplicada automaticamente.
- **Entrada**: `pergunta: str`, `resposta: str`, `tipo_artefato: str` (aqui sempre `"ui_specification"`).
- **Saída**: `None`.
- **Efeitos colaterais**: grava um ponto na collection Qdrant embarcada `refinement_answer_memory` (embedding via Ollama `bge-m3`).
- **Erros esperados**: nenhum tratado especificamente.
- **Dependências**: chamada pelo CLI (`run.py --refinar`) logo após cada resposta não vazia do humano.

## suggest_refinement_answer

- **Descrição**: busca a resposta de refinamento mais parecida já dada antes (memória institucional) para a pergunta atual, e a exibe como sugestão — sempre editável, nunca aplicada automaticamente.
- **Entrada**: `pergunta: str`.
- **Saída**: `dict | None`.
- **Efeitos colaterais**: consulta a collection Qdrant embarcada `refinement_answer_memory`.
- **Erros esperados**: nenhum tratado especificamente.
- **Dependências**: chamada pelo CLI (`run.py --refinar`) antes de cada `input()` de resposta.
