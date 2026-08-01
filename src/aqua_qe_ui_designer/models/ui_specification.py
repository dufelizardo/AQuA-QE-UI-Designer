from dataclasses import dataclass, field

from .design_tokens import DesignTokensSuggestion
from .status import ArtifactStatus
from .ui_screen import UIScreen


@dataclass
class UISpecification:
    """UI Specification (UIS), conforme docs/agent/output_schema.md."""

    id: str
    title: str
    context_problem: str
    screens: list[UIScreen] = field(default_factory=list)
    design_tokens: DesignTokensSuggestion = field(default_factory=DesignTokensSuggestion)
    responsive_notes: str = ""
    accessibility_recommendations: list[str] = field(default_factory=list)
    source_reference: str = ""
    uxs_reference: str = ""
    figma_file_reference: str = ""
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
    recommendations_synthesis: list[str] = field(default_factory=list)
