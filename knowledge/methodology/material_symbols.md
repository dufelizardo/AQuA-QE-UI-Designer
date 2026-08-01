# Material Symbols — Catálogo de Ícones

> Fonte: especificação pública do Material Symbols (Google, `fonts.google.com/icons`).
> Referência real consultada por `identify_screens_and_components` (campo
> `ComponentSpec.icon`) — o agente só recomenda um ícone **desta lista**, nunca inventa um nome
> fora dela (GR-UI-7, mesma disciplina de catálogo fechado do GR-UI-1, agora para ícones). Este
> documento resume/organiza a especificação pública em prosa própria, com uma curadoria dos
> ícones mais comuns em fluxos de produto — não reproduz o catálogo completo (milhares de
> ícones) nem nenhum asset visual do Google verbatim.

## Catálogo fechado de ícones

A lista abaixo é o catálogo fechado consultado por
`src/aqua_qe_ui_designer/skills/_material_symbols_catalog.py` (`ICONES_MATERIAL_SYMBOLS`).
Qualquer ícone citado pelo LLM fora desta lista é descartado de volta para `""` antes de chegar
a `ComponentSpec.icon` (GR-UI-7) — ao contrário de um componente inválido (GR-UI-1, que
descarta a tela inteira do componente), um ícone inválido nunca invalida o componente que o
cita, só o campo `icon` fica vazio.

- **search** — iniciar uma busca (ex.: dentro de uma Search Bar).
- **calendar_today** — abrir um seletor de data ou indicar um campo/ação de agendamento.
- **schedule** — indicar horário/tempo (ex.: um horário disponível, uma duração).
- **arrow_back** — voltar à tela/passo anterior.
- **arrow_forward** — avançar para a próxima tela/passo.
- **close** — fechar um diálogo, bottom sheet ou modal sem confirmar.
- **check** — confirmar uma ação simples ou marcar como concluído.
- **check_circle** — indicar sucesso/conclusão com destaque maior que `check`.
- **person** — representar um usuário/perfil individual.
- **group** — representar múltiplos usuários/um grupo.
- **error** — sinalizar um estado de erro (ícone, não a cor).
- **warning** — sinalizar um alerta que não é um erro bloqueante.
- **info** — indicar uma informação complementar/contextual.
- **add** — criar/adicionar um novo item (ação comum de um FAB).
- **remove** — remover/diminuir um valor ou item.
- **edit** — editar um item ou campo existente.
- **delete** — excluir um item permanentemente.
- **delete_outline** — variante de contorno de `delete`, para ações menos destacadas.
- **filter_list** — abrir/aplicar filtros sobre uma lista.
- **sort** — reordenar uma lista.
- **expand_more** — expandir um conteúdo recolhido (aponta para baixo).
- **expand_less** — recolher um conteúdo expandido (aponta para cima).
- **menu** — abrir uma Navigation Drawer ou menu de navegação principal.
- **home** — navegar para a tela inicial.
- **notifications** — indicar/abrir notificações.
- **settings** — navegar para configurações.
- **favorite** — favoritar/curtir um item.
- **star** — marcar como destaque/avaliação.
- **share** — compartilhar conteúdo.
- **download** — baixar um arquivo/conteúdo.
- **upload** — enviar um arquivo/conteúdo.
- **visibility** — exibir conteúdo oculto (ex.: mostrar senha).
- **visibility_off** — ocultar conteúdo visível (ex.: esconder senha).
- **lock** — indicar conteúdo/ação protegida ou bloqueada.
- **logout** — encerrar a sessão do usuário.
- **login** — iniciar sessão do usuário.
- **refresh** — recarregar/atualizar o conteúdo de uma tela.
- **attach_file** — anexar um arquivo.
- **location_on** — indicar/selecionar uma localização.
- **more_vert** — abrir um menu de mais opções (contexto vertical).

## Como este agente usa este documento

- `identify_screens_and_components` só pode citar um nome de ícone que apareça na lista acima
  (idêntico a `ICONES_MATERIAL_SYMBOLS` em código) para `ComponentSpec.icon` — qualquer outro
  nome é descartado de volta para `""` (GR-UI-7).
- `workflow/generate_ui_specification.py` deduplica todos os ícones não vazios usados nas telas
  em `UISpecification.icons`, em Python puro (sem chamada nova ao LLM) — sempre um subconjunto
  desta lista.
