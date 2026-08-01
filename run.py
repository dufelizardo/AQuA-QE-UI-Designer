"""CLI simples para rodar o AQuA-QE UI Designer sem precisar mexer em sys.path manualmente."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

_RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(_RAIZ / "src"))
load_dotenv(_RAIZ / ".env")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from aqua_qe_ui_designer.models import ArtifactStatus, UISpecification  # noqa: E402
from aqua_qe_ui_designer.orchestrator.ui_designer import handle_request  # noqa: E402
from aqua_qe_ui_designer.skills.create_confluence_page import create_confluence_page  # noqa: E402
from aqua_qe_ui_designer.skills.format_chat_transcript import format_chat_transcript  # noqa: E402
from aqua_qe_ui_designer.skills.format_ui_specification_markdown import (  # noqa: E402
    format_ui_specification_markdown,
)
from aqua_qe_ui_designer.skills.generate_ui_clarifying_questions import (  # noqa: E402
    generate_ui_clarifying_questions,
)
from aqua_qe_ui_designer.skills.get_confluence_publish_location import (  # noqa: E402
    get_confluence_publish_location,
)
from aqua_qe_ui_designer.skills.parse_chat_transcript import parse_chat_transcript  # noqa: E402
from aqua_qe_ui_designer.skills.read_confluence_page import read_confluence_page  # noqa: E402
from aqua_qe_ui_designer.skills.read_jira_issue import read_jira_issue  # noqa: E402
from aqua_qe_ui_designer.skills.read_text_file import read_text_file  # noqa: E402
from aqua_qe_ui_designer.skills.record_refinement_answer import (  # noqa: E402
    record_refinement_answer,
)
from aqua_qe_ui_designer.skills.suggest_refinement_answer import (  # noqa: E402
    suggest_refinement_answer,
)
from aqua_qe_ui_designer.skills.update_confluence_page import update_confluence_page  # noqa: E402
from aqua_qe_ui_designer.workflow.generate_ui_specification import (  # noqa: E402
    refine_and_finalize_ui_specification,
)


def _ler_entrada(args: argparse.Namespace) -> tuple[str, str]:
    """Lê a UX Specification de origem a partir da fonte informada (única entre as quatro
    mutuamente exclusivas) e retorna (texto, referência) — a referência é usada só para a
    seção 2 (Escopo) do export em Markdown, nunca para leitura."""
    if args.arquivo:
        return read_text_file(args.arquivo), args.arquivo
    if args.jira:
        return read_jira_issue(args.jira), args.jira
    if args.confluence:
        return read_confluence_page(args.confluence), args.confluence
    # chat (--texto): normaliza a transcrição (remetente por linha), quando houver;
    # texto corrido sem remetentes volta inalterado (ver parse_chat_transcript).
    return format_chat_transcript(parse_chat_transcript(args.texto)), ""


def _imprimir_spec(spec: UISpecification) -> None:
    print(f"status: {spec.status.value}")
    print(f"título: {spec.title}")
    print(f"contexto: {spec.context_problem}")
    for tela in spec.screens:
        print(f"tela '{tela.name}': {len(tela.components)} componente(s), {len(tela.states)} estado(s)")
    print(
        "design tokens (sugestão): "
        f"cores={spec.design_tokens.colors}, tipografia={spec.design_tokens.typography}, "
        f"espaçamento={spec.design_tokens.spacing}"
    )
    print(f"layout responsivo: {spec.responsive_notes}")
    print(f"recomendações de acessibilidade: {spec.accessibility_recommendations}")
    if spec.review_notes:
        print("observações da revisão:")
        for nota in spec.review_notes:
            print(f"  - {nota}")


def _perguntar_sim_nao(mensagem: str) -> bool:
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def _ciclo_de_refinamento(spec: UISpecification) -> UISpecification:
    """Gera perguntas, pede respostas ao usuário, refina e reavalia até aprovar ou o usuário desistir."""
    while spec.status != ArtifactStatus.DRAFT_VALIDATED and spec.review_notes:
        perguntas = generate_ui_clarifying_questions(spec)
        if not perguntas:
            break

        print("\nO revisor apontou problemas. Responda para ajudar a refinar a UI Specification:")
        respostas = []
        for pergunta in perguntas:
            sugestao = suggest_refinement_answer(pergunta)
            if sugestao:
                print(
                    f"  \U0001F4A1 Resposta usada antes p/ pergunta parecida "
                    f"(similaridade {sugestao['score']:.2f}): {sugestao['resposta']}"
                )
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})
            if resposta.strip():
                record_refinement_answer(pergunta, resposta, tipo_artefato="ui_specification")

        spec = refine_and_finalize_ui_specification(spec, respostas)
        print("\n--- UI Specification refinada ---")
        _imprimir_spec(spec)

        if spec.status != ArtifactStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return spec


def _publicar_ou_atualizar_confluence(
    spec: UISpecification,
    pagina_origem: str | None,
    publicar_confluence: bool,
    atualizar_confluence: str | None,
) -> None:
    """Cria uma página nova (irmã da página de origem da UX Specification) ou atualiza uma
    existente no Confluence, sempre sob confirmação humana explícita."""
    texto_formatado = format_ui_specification_markdown(spec)

    if atualizar_confluence:
        if not _perguntar_sim_nao(
            f"\nAtualizar a página {atualizar_confluence} no Confluence com esta UI Specification?"
        ):
            return
        update_confluence_page(atualizar_confluence, texto_formatado)
        print(f"página atualizada no Confluence: {atualizar_confluence}")
        return

    if publicar_confluence:
        if not _perguntar_sim_nao(
            "\nPublicar no Confluence como página irmã da UX Specification de origem?"
        ):
            return
        titulo = input("Título da página no Confluence: ").strip()
        space_key, parent_page_id = get_confluence_publish_location(pagina_origem)
        url = create_confluence_page(texto_formatado, titulo, space_key, parent_page_id)
        print(f"publicado no Confluence: {url}")


def _rodar(
    texto: str,
    uxs_reference: str,
    saida: str | None,
    refinar: bool,
    pagina_origem: str | None,
    publicar_confluence: bool,
    atualizar_confluence: str | None,
) -> None:
    spec = handle_request(texto, uxs_reference)
    _imprimir_spec(spec)

    if refinar:
        spec = _ciclo_de_refinamento(spec)

    if not _perguntar_sim_nao("\nAceitar esta UI Specification?"):
        return

    spec.status = ArtifactStatus.ACCEPTED

    if saida:
        with open(saida, "w", encoding="utf-8") as arquivo:
            arquivo.write(format_ui_specification_markdown(spec))
        print(f"exportado para: {saida}")

    if publicar_confluence or atualizar_confluence:
        _publicar_ou_atualizar_confluence(
            spec, pagina_origem, publicar_confluence, atualizar_confluence
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o AQuA-QE UI Designer.")
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument(
        "--arquivo", help="Caminho de um arquivo .txt/.md de entrada (ex.: uma UX Specification exportada)."
    )
    entrada.add_argument("--texto", help="Texto de entrada direto (chat).")
    entrada.add_argument("--jira", help="Chave do ticket Jira (ex.: AQUAQE-11).")
    entrada.add_argument(
        "--confluence",
        help="URL completa ou ID de uma página do Confluence Cloud (ex.: a UX Specification publicada).",
    )
    parser.add_argument("--saida", help="Caminho do .md exportado.")
    parser.add_argument(
        "--refinar",
        action="store_true",
        help=(
            "Ativa o ciclo interativo de perguntas/refinamento para a UI Specification não "
            "aprovada, antes do aceite humano (que é sempre perguntado, com ou sem esta flag)."
        ),
    )
    publicacao = parser.add_mutually_exclusive_group()
    publicacao.add_argument(
        "--publicar-confluence",
        action="store_true",
        dest="publicar_confluence",
        help=(
            "Após aceitar a UI Specification, pergunta o título e publica como página nova no "
            "Confluence, irmã da página de origem (só válido com --confluence)."
        ),
    )
    publicacao.add_argument(
        "--atualizar-confluence",
        dest="atualizar_confluence",
        help=(
            "Após aceitar a UI Specification, atualiza a página existente informada (URL "
            "completa ou ID) no Confluence, em vez de criar uma nova (só válido com --confluence)."
        ),
    )
    args = parser.parse_args()

    if (args.publicar_confluence or args.atualizar_confluence) and not args.confluence:
        parser.error(
            "--publicar-confluence/--atualizar-confluence só são válidos com --confluence "
            "(é preciso uma página de origem para publicar ao lado dela)."
        )

    texto, uxs_reference = _ler_entrada(args)
    _rodar(
        texto,
        uxs_reference,
        args.saida,
        args.refinar,
        args.confluence,
        args.publicar_confluence,
        args.atualizar_confluence,
    )


if __name__ == "__main__":
    main()
