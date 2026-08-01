# Prompt

> Estrutura conforme `../standards/prompt_standard.md`. Este documento descreve a composição
> do prompt de sistema; o texto literal enviado ao LLM é implementação e deve apenas
> referenciar, não duplicar, o conteúdo dos documentos abaixo.

## Composição do prompt de sistema

1. **Papel/persona** — derivado integralmente de `persona.md` (consultivo, ancorado no
   catálogo fechado, honesto sobre os limites do próprio papel).
2. **Objetivo da tarefa** — derivado de `objectives.md`, específico a cada skill (identificar
   telas/componentes, definir estados, sugerir tokens, definir layout responsivo, recomendar
   acessibilidade visual — ver `agent_design.md`).
3. **Instruções de comportamento** — derivadas de `ai_spec.md` (comportamento em caminho
   feliz, fonte ambígua e fora de escopo).
4. **Regras/guardrails reforçados** — RULE-UI-1 a RULE-UI-7 (`rules.md`) e os guardrails
   GR-UI-1 a GR-UI-5 (`guardrails.md`) devem aparecer de forma explícita e não negociável no
   prompt, não apenas implícita no tom. Em particular, `identify_screens_and_components` e
   `refine_ui_specification` sempre recebem o catálogo fechado Material Design 3 explicitamente
   no prompt (GR-UI-1).
5. **Formato de saída** — schema de `output_schema.md`, incluindo os valores válidos de
   `status`.
6. **Exemplos (few-shot)** — extraídos de `knowledge/examples/` quando existir (ainda não
   criado nesta fase); ausência de exemplos não deve degradar o comportamento esperado, apenas
   reduzir a calibração fina de estilo.

## Convenções de versionamento

- Cada versão do prompt é identificada, permitindo associar uma versão a um conjunto de
  resultados de `evaluation.md`.
- Mudanças que alterem comportamento observável (não apenas fraseado) exigem rodar os casos de
  teste de `evaluation.md` antes de substituir a versão em uso.

## O que o prompt não deve conter

- Não deve conter conhecimento de domínio específico de cliente diretamente embutido.
- Não deve reafirmar informações já garantidas estruturalmente pelo schema de saída.
- Não deve instruir o modelo a citar um componente fora do catálogo fechado Material Design 3
  — isso violaria GR-UI-1 mesmo que a fonte pareça sugerir a necessidade de um componente
  diferente.
- Não deve instruir o modelo a afirmar que um design token sugerido é a identidade visual
  definitiva do produto (GR-UI-2), nem a descrever um render visual como se já existisse
  (GR-UI-4).
