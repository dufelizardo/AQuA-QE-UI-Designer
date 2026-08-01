# WCAG 2.2 — Princípios e critérios usados por este agente

> Fonte: W3C Web Content Accessibility Guidelines (WCAG) 2.1. Base para `review_accessibility` — o agente só **recomenda verificar** conformidade, nunca **certifica** conformidade (GR-UX-2); conformidade real exige ferramentas de auditoria e testes com usuários reais, fora do escopo deste agente.

## Os 4 princípios (POUR)

1. **Perceptível** — informação e componentes de interface devem ser apresentáveis aos usuários de formas que eles possam perceber (ex.: texto alternativo para imagens, contraste de cor suficiente, conteúdo adaptável sem perda de estrutura).
2. **Operável** — componentes de interface e navegação devem ser operáveis (ex.: toda funcionalidade disponível via teclado, tempo suficiente para ler/usar o conteúdo, navegação previsível e consistente).
3. **Compreensível** — informação e a operação da interface devem ser compreensíveis (ex.: texto legível, comportamento previsível, assistência para evitar/corrigir erros de entrada).
4. **Robusto** — conteúdo deve ser robusto o suficiente para ser interpretado de forma confiável por uma variedade de agentes de usuário, incluindo tecnologias assistivas.

## Critérios mais relevantes para fluxos de navegação e arquitetura da informação

- **1.3.1 Informação e Relações** — a estrutura/relações transmitidas visualmente devem estar disponíveis em texto (relevante para `InformationArchitecture` — categorização e hierarquia devem ser semanticamente claras, não só visuais).
- **2.4.3 Ordem de Foco** — se uma sequência de navegação afeta o significado/operação, componentes recebem foco em uma ordem que preserva significado (relevante para `UserFlow` — a ordem dos passos deve fazer sentido também via navegação por teclado).
- **2.4.5 Múltiplas Formas** — mais de uma forma de localizar uma página/tarefa dentro de um conjunto (relevante para `InformationArchitecture`).
- **3.2.3 Navegação Consistente** — mecanismos de navegação repetidos aparecem na mesma ordem relativa em cada tela (relevante para `UserFlow` e `InformationArchitecture`).
- **3.3.1 Identificação de Erro** — se um erro de entrada é detectado automaticamente, o item com erro é identificado e o erro descrito ao usuário em texto (relevante para passos de `UserFlow` que envolvem preenchimento de dados).

## Como este agente usa este documento

`review_accessibility` gera recomendações apontando qual critério WCAG 2.2 específico motiva cada recomendação (ex.: "o passo X de confirmação deveria seguir 3.3.1 — identificar o erro em texto, não só com cor") — sempre com o fraseado de "recomenda-se verificar", nunca "está em conformidade" (RULE-UX-2).
