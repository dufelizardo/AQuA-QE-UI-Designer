from ..models import UIScreen
from ..services.llm_service import complete_json
from ._material_design_3_catalog import COMPONENTES_MD3
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você identifica, para cada tela de navegação descrita em uma UX Specification, quais "
    "componentes do catálogo fechado do Material Design 3 (listado abaixo) se aplicam. Nunca "
    "cite um componente fora desta lista (GR-UI-1, o guardrail mais importante deste agente) — "
    "se nenhum componente do catálogo se aplicar claramente a uma tela, deixe a lista de "
    "componentes dessa tela menor, nunca invente um nome de componente novo. Baseie-se apenas "
    "nas telas/fluxos realmente descritos na UX Specification; nunca invente uma tela que não "
    "esteja lá (GR-UI-5). Cada componente citado deve ser o nome exato do catálogo, como uma "
    "única string de texto, nunca um objeto/dicionário com campos separados."
)


def identify_screens_and_components(texto_uxs: str, contexto: dict) -> list[UIScreen]:
    """Identifica as telas da UX Specification e, para cada uma, os componentes do catálogo
    fechado Material Design 3 que se aplicam — descarta qualquer componente fora do catálogo
    em vez de repassá-lo adiante (GR-UI-1)."""
    catalogo = ", ".join(COMPONENTES_MD3)
    prompt = (
        f"Contexto: {contexto.get('context_problem', '')}\n"
        f"UX Specification:\n{texto_uxs}\n\n"
        f"Catálogo fechado de componentes Material Design 3: {catalogo}\n\n"
        'Responda apenas em JSON: {"telas": [{"nome": "...", "componentes": ["..."], '
        '"trecho_fonte": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    telas = []
    for item in dados.get("telas", []):
        if not isinstance(item, dict):
            continue
        componentes = [
            componente
            for componente in lista_de_strings(item.get("componentes", []))
            if componente in COMPONENTES_MD3
        ]
        telas.append(
            UIScreen(
                name=item.get("nome", ""),
                components=componentes,
                source_reference=item.get("trecho_fonte", ""),
            )
        )
    return telas
