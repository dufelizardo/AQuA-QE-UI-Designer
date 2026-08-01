from dataclasses import dataclass


@dataclass
class StateSpec:
    """Um estado de interação (hover/focus/disabled/loading/error/success — mesmo vocabulário
    de sempre) com o contexto real em que ele ocorre, quando a UX Specification de origem
    descreve um ponto assíncrono/de espera específico (ex.: "enquanto consulta horários
    disponíveis"), conforme docs/agent/output_schema.md. `context` nunca é inventado do zero —
    só preenchido quando a fonte realmente descreve o que acontece naquele ponto do fluxo.
    """

    name: str
    context: str = ""
