from dataclasses import dataclass, field

from .component_spec import ComponentSpec
from .state_spec import StateSpec


@dataclass
class UIScreen:
    """Tela de navegação com os componentes recomendados do catálogo fechado Material Design 3
    e seus estados de interação, conforme docs/agent/output_schema.md."""

    name: str
    components: list[ComponentSpec] = field(default_factory=list)
    states: list[StateSpec] = field(default_factory=list)
    hierarchy: list[str] = field(default_factory=list)
    empty_states: list[str] = field(default_factory=list)
    error_states: list[str] = field(default_factory=list)
    source_reference: str = ""
