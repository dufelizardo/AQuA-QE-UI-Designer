import re

from ..services.confluence_service import get_page_parent_context


def get_confluence_publish_location(pagina_origem: str) -> tuple[str, str | None]:
    """A partir da página de origem da UX Specification (URL ou ID), retorna (espaço, id do
    ancestral imediato) para publicar a UI Specification como página irmã no mesmo local."""
    match = re.search(r"/pages/(\d+)", pagina_origem)
    page_id = match.group(1) if match else pagina_origem
    return get_page_parent_context(page_id)
