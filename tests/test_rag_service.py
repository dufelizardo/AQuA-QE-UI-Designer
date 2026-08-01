import pytest

from aqua_qe_ui_designer.services import rag_service


def _fake_embed(textos: list[str]) -> list[list[float]]:
    """Embedding falso e determinístico: perguntas sobre o mesmo tópico caem no mesmo eixo
    (similaridade de cosseno 1.0), perguntas sobre tópicos diferentes caem em eixos
    ortogonais (similaridade 0.0) — suficiente para testar a busca sem precisar de um
    modelo de embedding real."""
    vetores = []
    for texto in textos:
        vetor = [0.0] * rag_service._VECTOR_SIZE
        if "acessibilidade" in texto.lower():
            vetor[0] = 1.0
        elif "jornada" in texto.lower():
            vetor[1] = 1.0
        else:
            vetor[2] = 1.0
        vetores.append(vetor)
    return vetores


@pytest.fixture
def rag_isolado(tmp_path, monkeypatch):
    monkeypatch.setattr(rag_service, "_STORAGE_PATH", tmp_path / "qdrant")
    monkeypatch.setattr(rag_service, "embed", _fake_embed)


def test_record_refinement_answer_cria_colecao_e_permite_busca(rag_isolado):
    rag_service.record_refinement_answer(
        "Qual critério de acessibilidade se aplica aqui?",
        "Seguir WCAG 2.2 nível AA.",
        "ui_specification",
    )

    resultados = rag_service.find_similar_refinement_answers(
        "Qual critério de acessibilidade se aplica aqui?"
    )

    assert len(resultados) == 1
    assert resultados[0]["resposta"] == "Seguir WCAG 2.2 nível AA."
    assert resultados[0]["tipo_artefato"] == "ui_specification"
    assert resultados[0]["score"] == pytest.approx(1.0, abs=1e-3)


def test_find_similar_refinement_answers_retorna_vazio_sem_colecao(rag_isolado):
    assert rag_service.find_similar_refinement_answers("qualquer pergunta") == []


def test_find_similar_refinement_answers_distingue_perguntas_diferentes(rag_isolado):
    rag_service.record_refinement_answer(
        "Qual critério de acessibilidade se aplica aqui?",
        "resposta sobre acessibilidade",
        "ui_specification",
    )
    rag_service.record_refinement_answer(
        "Qual é a jornada do usuário nesse caso?",
        "resposta sobre jornada",
        "ui_specification",
    )

    resultados = rag_service.find_similar_refinement_answers(
        "Qual critério de acessibilidade se aplica aqui?", k=1
    )

    assert len(resultados) == 1
    assert resultados[0]["resposta"] == "resposta sobre acessibilidade"
