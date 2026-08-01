from dataclasses import dataclass


@dataclass
class ComponentSpec:
    """Um componente do catálogo fechado Material Design 3, com detalhe de configuração
    (variante/tamanho/ícone/notas) suficiente para um time de front-end implementar, conforme
    docs/agent/output_schema.md.

    `name` está sujeito à mesma disciplina de catálogo fechado do GR-UI-1 — nunca um nome fora
    de `COMPONENTES_MD3`. `variant`/`size` usam apenas vocabulário real de variante/estilo do
    Material Design 3 (ex.: "Filled"/"Outlined"/"Text" para Buttons, "Small"/"Center Aligned"
    para Top App Bar) — nunca um rótulo inventado fora desse vocabulário. `icon`, quando
    presente, está sujeito ao catálogo fechado Material Symbols (GR-UI-7) — um ícone fora dele
    é descartado de volta para `""`, nunca invalida o componente inteiro. `notes` é uma nota de
    configuração curta (ex.: "Placeholder: Pesquisar cidadão"), não copy final de UI.
    """

    name: str
    variant: str = ""
    size: str = ""
    icon: str = ""
    notes: str = ""
