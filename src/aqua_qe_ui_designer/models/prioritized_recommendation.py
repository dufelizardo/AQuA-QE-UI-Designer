from dataclasses import dataclass


@dataclass
class PrioritizedRecommendation:
    """Um item da síntese priorizada de recomendações (`synthesize_recommendations`), conforme
    docs/agent/output_schema.md. `priority` é sempre um de "Alta"/"Média"/"Baixa" — a skill que
    produz este objeto nunca inventa um quarto nível de prioridade; um valor fora desses três,
    vindo do LLM, é normalizado para "Média"."""

    priority: str
    text: str
