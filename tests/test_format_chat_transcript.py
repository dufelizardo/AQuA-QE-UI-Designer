from aqua_qe_ui_designer.models import ChatMessage
from aqua_qe_ui_designer.skills.format_chat_transcript import format_chat_transcript
from aqua_qe_ui_designer.skills.parse_chat_transcript import parse_chat_transcript


def test_formats_multiple_messages_with_speaker_prefix():
    mensagens = [
        ChatMessage(speaker="Arquiteto", text="qual a integracao com o legado?"),
        ChatMessage(speaker="Dev", text="via fila"),
    ]

    resultado = format_chat_transcript(mensagens)

    assert resultado == "Arquiteto: qual a integracao com o legado?\n\nDev: via fila"


def test_single_unattributed_message_returns_original_text_unchanged():
    texto_original = "Sistema precisa consultar saldo em tempo real"

    resultado = format_chat_transcript([ChatMessage(speaker="", text=texto_original)])

    assert resultado == texto_original


def test_empty_list_returns_empty_string():
    assert format_chat_transcript([]) == ""


def test_roundtrip_parse_then_format_preserves_plain_text():
    texto_original = "O sistema deve responder em: 2 segundos"

    resultado = format_chat_transcript(parse_chat_transcript(texto_original))

    assert resultado == texto_original
