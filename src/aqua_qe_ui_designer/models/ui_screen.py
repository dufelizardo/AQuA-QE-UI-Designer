from dataclasses import dataclass, field


@dataclass
class UIScreen:
    """Tela de navegação com os componentes recomendados do catálogo fechado Material Design 3
    e seus estados de interação, conforme docs/agent/output_schema.md."""

    name: str
    components: list[str] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    source_reference: str = ""
