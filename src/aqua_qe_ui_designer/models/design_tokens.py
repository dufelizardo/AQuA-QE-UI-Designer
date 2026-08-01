from dataclasses import dataclass, field


@dataclass
class DesignTokensSuggestion:
    """Sugestão de design tokens (cores/tipografia/espaçamento) para a UI Specification —
    sempre rotulada como sugestão a confirmar, nunca como a identidade visual definitiva do
    produto, a menos que a fonte já a especifique explicitamente (GR-UI-2)."""

    colors: list[str] = field(default_factory=list)
    typography: list[str] = field(default_factory=list)
    spacing: list[str] = field(default_factory=list)
