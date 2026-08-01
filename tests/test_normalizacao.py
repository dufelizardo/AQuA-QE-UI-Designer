from aqua_qe_ui_designer.skills import _normalizacao as m


def test_item_para_string_returns_plain_string_unchanged():
    assert m.item_para_string("Cards") == "Cards"


def test_item_para_string_converte_objeto_com_campo_prioritario():
    item = {"nome": "Cards", "descricao": "usado para agrupar conteúdo"}
    assert m.item_para_string(item, ("nome",)) == "Cards: usado para agrupar conteúdo"


def test_item_para_string_sem_campo_prioritario_usa_primeiro_valor_nao_vazio():
    item = {"algo": "", "outro": "valor real"}
    assert m.item_para_string(item) == "valor real"


def test_item_para_string_objeto_totalmente_vazio_cai_no_repr():
    item = {"a": "", "b": ""}
    assert m.item_para_string(item) == str(item)


def test_valor_para_string_achata_dict_aninhado():
    valor = {"descricao": "texto", "objetivos": ["a", "b"]}
    resultado = m.valor_para_string(valor)
    assert "descricao: texto" in resultado
    assert "objetivos: a, b" in resultado


def test_valor_para_string_lista_simples():
    assert m.valor_para_string(["a", "b"]) == "a, b"


def test_dict_para_texto_com_chave_unica_mapeando_lista():
    dicionario = {"caminho": ["passo 1", "passo 2"]}
    assert m.dict_para_texto(dicionario) == "passo 1\npasso 2"


def test_dict_para_texto_com_multiplas_chaves_e_valores_vazios():
    dicionario = {"Item 1": "", "Item 2": ""}
    assert m.dict_para_texto(dicionario) == "Item 1\nItem 2"


def test_dict_para_texto_com_detalhe_aninhado():
    dicionario = {"Cidadãos": {"descricao": "buscam atendimento", "pontos_de_dor": []}}
    resultado = m.dict_para_texto(dicionario)
    assert "Cidadãos: descricao: buscam atendimento" in resultado


def test_string_como_estrutura_reconhece_repr_de_dict():
    valor = "{'a': 1}"
    assert m.string_como_estrutura(valor) == {"a": 1}


def test_string_como_estrutura_retorna_none_para_prosa_comum():
    assert m.string_como_estrutura("um texto qualquer") is None


def test_string_como_estrutura_retorna_none_para_repr_invalido():
    assert m.string_como_estrutura("{isso nao é python valido") is None


def test_texto_ou_lista_converte_lista_de_objetos():
    valor = [
        {"nome": "Cards", "descricao": "agrupa conteúdo"},
        {"nome": "Chips", "descricao": "filtra opções"},
    ]
    resultado = m.texto_ou_lista(valor)
    assert resultado == "Cards: agrupa conteúdo\nChips: filtra opções"


def test_texto_ou_lista_converte_dict_com_passos_como_chave():
    valor = {"Abrir tela": "", "Confirmar": ""}
    assert m.texto_ou_lista(valor) == "Abrir tela\nConfirmar"


def test_texto_ou_lista_converte_string_com_repr_de_dict():
    valor = "{'caminho': ['passo 1', 'passo 2']}"
    resultado = m.texto_ou_lista(valor)
    assert resultado == "passo 1\npasso 2"
    assert "{" not in resultado


def test_texto_ou_lista_retorna_string_normal_inalterada():
    assert m.texto_ou_lista("prosa comum") == "prosa comum"


def test_texto_ou_lista_valor_vazio_retorna_string_vazia():
    assert m.texto_ou_lista("") == ""
    assert m.texto_ou_lista(None) == ""


def test_lista_de_strings_converte_lista_de_objetos():
    valor = [{"nome": "Cards"}, {"nome": "Chips"}]
    assert m.lista_de_strings(valor, ("nome",)) == ["Cards", "Chips"]


def test_lista_de_strings_de_dict_vira_lista_de_linhas():
    valor = {"Item 1": "", "Item 2": ""}
    assert m.lista_de_strings(valor) == ["Item 1", "Item 2"]


def test_lista_de_strings_string_unica_vira_lista_de_um_item():
    assert m.lista_de_strings("uma recomendação só") == ["uma recomendação só"]


def test_lista_de_strings_string_vazia_vira_lista_vazia():
    assert m.lista_de_strings("") == []


def test_lista_de_strings_string_com_repr_de_lista_embutido():
    valor = "['Cards', 'Chips']"
    assert m.lista_de_strings(valor) == ["Cards", "Chips"]


def test_lista_de_strings_valor_de_tipo_inesperado_retorna_vazio():
    assert m.lista_de_strings(123) == []
