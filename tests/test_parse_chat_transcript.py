from aqua_qe_ui_designer.models import ChatMessage
from aqua_qe_ui_designer.skills.parse_chat_transcript import parse_chat_transcript


def test_parses_multiple_speakers():
    texto = "Arquiteto: qual a integracao com o legado?\nDev: via fila\nArquiteto: ok"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="Arquiteto", text="qual a integracao com o legado?"),
        ChatMessage(speaker="Dev", text="via fila"),
        ChatMessage(speaker="Arquiteto", text="ok"),
    ]


def test_speaker_with_multiple_words():
    texto = "Maria Silva: precisamos revisar o escopo"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="Maria Silva", text="precisamos revisar o escopo")]


def test_continuation_line_attaches_to_previous_speaker():
    texto = "Arquiteto: precisamos escalar\ne tambem garantir disponibilidade"

    resultado = parse_chat_transcript(texto)

    assert len(resultado) == 1
    assert resultado[0].speaker == "Arquiteto"
    assert resultado[0].text == "precisamos escalar\ne tambem garantir disponibilidade"


def test_plain_text_without_speakers_falls_back_to_single_message():
    texto = "Sistema precisa consultar saldo em tempo real via integracao com o legado"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_colon_mid_sentence_is_not_mistaken_for_a_speaker():
    texto = "O sistema deve responder em: 2 segundos"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_empty_lines_are_ignored():
    texto = "Arquiteto: primeira mensagem\n\n\nDev: segunda mensagem"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="Arquiteto", text="primeira mensagem"),
        ChatMessage(speaker="Dev", text="segunda mensagem"),
    ]
