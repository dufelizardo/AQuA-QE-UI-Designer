from ..models import UISpecification
from ..workflow.generate_ui_specification import generate_ui_specification


def handle_request(texto_uxs: str, uxs_reference: str = "") -> UISpecification:
    """Ponto de entrada único do agente — gera a UI Specification a partir do texto da UX Specification de origem."""
    return generate_ui_specification(texto_uxs, uxs_reference)
