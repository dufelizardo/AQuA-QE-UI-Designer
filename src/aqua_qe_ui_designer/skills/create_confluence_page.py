import os

from ..services.confluence_service import create_page


def create_confluence_page(
    texto: str, titulo: str, space_key: str, parent_page_id: str | None = None
) -> str:
    """Publica a UI Specification formatada como página nova no Confluence Cloud e retorna a URL da página criada."""
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")

    page_id = create_page(space_key, titulo, texto, parent_page_id)
    return f"{base_url}/wiki/pages/viewpage.action?pageId={page_id}"
