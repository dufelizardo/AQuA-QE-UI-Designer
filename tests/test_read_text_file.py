from aqua_qe_ui_designer.skills.read_text_file import read_text_file


def test_read_text_file_returns_content(tmp_path):
    arquivo = tmp_path / "uxs.md"
    arquivo.write_text("# UX Specification\n\nConteúdo de teste.", encoding="utf-8")

    assert read_text_file(str(arquivo)) == "# UX Specification\n\nConteúdo de teste."
