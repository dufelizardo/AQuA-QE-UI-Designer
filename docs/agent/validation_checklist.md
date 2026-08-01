# Validation Checklist

> Checklist aplicado pela skill `validate_ui_specification` antes de qualquer UI Specification
> ser marcada como `draft_validated` (ver `output_schema.md` e RULE-UI-6 em `rules.md`).

## 1. Rastreabilidade (GR-UI-5)

- [ ] Título e contexto do problema têm origem identificável na UX Specification de entrada.
- [ ] Nenhuma tela ou componente foi preenchido por suposição não sinalizada.

## 2. Telas e Componentes (GR-UI-1)

- [ ] Há ao menos uma `UIScreen`.
- [ ] Cada tela tem ao menos um componente do catálogo fechado Material Design 3.

## 3. Estados dos Componentes

- [ ] Toda tela com componentes identificados tem ao menos um estado de interação definido.

## 4. Design Tokens (Sugestão, GR-UI-2)

- [ ] Há ao menos uma sugestão de design token (cor, tipografia ou espaçamento).
- [ ] Nenhuma sugestão é apresentada como a identidade visual definitiva do produto sem que a fonte já a especifique.

## 5. Layout Responsivo

- [ ] `responsive_notes` não está vazio.

## 6. Acessibilidade Visual (WCAG 2.2, `../../knowledge/methodology/wcag.md`, GR-UI-3)

- [ ] Há ao menos uma recomendação de acessibilidade visual.
- [ ] Nenhuma recomendação usa linguagem de certificação ("está em conformidade") — sempre "recomenda-se verificar".

## 7. Nenhum render visual fabricado (GR-UI-4)

- [ ] A saída não contém uma alegação de render visual real já produzido; `figma_file_reference` permanece vazio nesta fase.

## 8. Formato

- [ ] A saída segue a estrutura de `../../knowledge/templates/ui_specification.md`.
