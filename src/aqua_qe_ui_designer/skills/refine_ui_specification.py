from ..models import ComponentSpec, DesignTokensSuggestion, StateSpec, UIScreen, UISpecification
from ..services.llm_service import complete_json
from ._material_design_3_catalog import COMPONENTES_MD3
from ._normalizacao import lista_de_strings

_SYSTEM = (
    "Você refina uma UI Specification existente com base nas respostas que quem a propôs deu "
    "às perguntas de esclarecimento levantadas por um revisor. Baseie-se apenas na UI "
    "Specification atual e nas respostas fornecidas; nunca invente uma tela, componente, "
    "design token ou recomendação de acessibilidade que não tenha sido informado nelas. "
    "Componentes citados devem sempre vir do catálogo fechado do Material Design 3 (GR-UI-1) "
    "— nunca cite um nome fora dele. Design tokens continuam sempre uma sugestão a confirmar, "
    "nunca a identidade visual definitiva do produto (GR-UI-2), a menos que a resposta cite "
    "algo já estabelecido explicitamente. Nunca remova ou resuma um detalhe que já existe em "
    "um campo atual, a menos que uma resposta contradiga esse detalhe especificamente — "
    "preserve o texto/nível de detalhe existente nos campos que as respostas não abordam. "
    "Responda sempre em português."
)


def refine_ui_specification(spec: UISpecification, respostas: list[dict]) -> UISpecification:
    """Reescreve os campos da UI Specification usando as respostas do usuário, preservando o
    nível de detalhe dos campos que as respostas não abordam."""
    telas_atuais = [
        {
            "nome": tela.name,
            "componentes": [componente.name for componente in tela.components],
            "estados": [estado.name for estado in tela.states],
        }
        for tela in spec.screens
    ]
    perguntas_respostas = [f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas]

    prompt = (
        f"Título atual: {spec.title}\n"
        f"Contexto atual: {spec.context_problem}\n"
        f"Telas atuais: {telas_atuais}\n"
        f"Design tokens atuais: cores={spec.design_tokens.colors}, "
        f"tipografia={spec.design_tokens.typography}, espaçamento={spec.design_tokens.spacing}\n"
        f"Notas de layout responsivo atuais: {spec.responsive_notes}\n"
        f"Recomendações de acessibilidade atuais: {spec.accessibility_recommendations}\n\n"
        "Respostas às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva os campos incorporando essas respostas, resolvendo as lacunas "
        "apontadas. Campos (ou itens de lista) que não têm relação com nenhuma das "
        "respostas acima devem manter o texto atual, com o mesmo nível de detalhe — nunca "
        "simplifique um item para menos palavras do que já tinha.\n\n"
        'Responda apenas em JSON: {"titulo": "...", "contexto": "...", '
        '"telas": [{"nome": "...", "componentes": ["..."], "estados": ["..."]}], '
        '"cores": ["..."], "tipografia": ["..."], "espacamento": ["..."], '
        '"notas_responsivas": "...", "acessibilidade": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    spec.title = dados.get("titulo") or spec.title
    spec.context_problem = dados.get("contexto") or spec.context_problem
    spec.accessibility_recommendations = (
        lista_de_strings(dados.get("acessibilidade")) or spec.accessibility_recommendations
    )
    spec.responsive_notes = dados.get("notas_responsivas") or spec.responsive_notes

    telas_atuais_por_nome = {tela.name: tela for tela in spec.screens}
    novas_telas = []
    for item in dados.get("telas", []):
        if not isinstance(item, dict):
            continue
        nome = item.get("nome", "")
        tela_atual = telas_atuais_por_nome.get(nome)
        novas_telas.append(
            UIScreen(
                name=nome,
                components=[
                    ComponentSpec(name=componente)
                    for componente in lista_de_strings(item.get("componentes", []))
                    if componente in COMPONENTES_MD3
                ],
                states=[
                    StateSpec(name=estado) for estado in lista_de_strings(item.get("estados", []))
                ],
                # Hierarquia/empty states/error states não são reabordados por este ciclo de
                # refino (o revisor só aponta lacunas de componentes/estados/tokens/
                # acessibilidade nesta fase) — preserva o que já existia na tela de mesmo nome,
                # em vez de apagar detalhe que as respostas não abordaram.
                hierarchy=tela_atual.hierarchy if tela_atual else [],
                empty_states=tela_atual.empty_states if tela_atual else [],
                error_states=tela_atual.error_states if tela_atual else [],
                source_reference=spec.source_reference,
            )
        )
    spec.screens = novas_telas or spec.screens

    cores = lista_de_strings(dados.get("cores", []))
    tipografia = lista_de_strings(dados.get("tipografia", []))
    espacamento = lista_de_strings(dados.get("espacamento", []))
    if cores or tipografia or espacamento:
        spec.design_tokens = DesignTokensSuggestion(
            colors=cores or spec.design_tokens.colors,
            typography=tipografia or spec.design_tokens.typography,
            spacing=espacamento or spec.design_tokens.spacing,
        )

    return spec
