from enum import Enum


class ArtifactStatus(str, Enum):
    """Estados possíveis da UI Specification, conforme docs/agent/output_schema.md."""

    DRAFT_VALIDATED = "draft_validated"
    PENDING_CLARIFICATION = "pending_clarification"
    ACCEPTED = "accepted"
