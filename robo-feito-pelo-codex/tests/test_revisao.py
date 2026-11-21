"""Regressões da revisão independente; usam o bloqueio de rede da suíte."""
import json
from datetime import datetime, timedelta

import pytest
import requests

import robo
from test_robo import ambiente, config_completa, linha, resposta


@pytest.mark.parametrize("mudancas", [
    {"expires_in": "invalido"}, {"expires_in": None}, {"expires_in": -1},
    {"expires_in": float("inf")}, {"refresh_token": None}, {"access_token": None},
])
def test_a1_resposta_preservada_antes_da_validacao(ambiente, mudancas):
    dados = dict(access_token="acesso-novo", refresh_token="refresh-novo", expires_in=7200,
                 campo_extra="preservado")
    dados.update(mudancas)
    with pytest.raises(robo.Erro):
        robo.salvar_tokens_x(dados)
    salvo = json.loads((ambiente / "x-tokens.json").read_text(encoding="utf-8"))
    for chave, valor in dados.items():
        assert salvo[chave] == valor
    assert isinstance(salvo["expires_at"], (int, float))
    # A leitura seguinte também não pode usar uma resposta inválida.
    with pytest.raises(robo.Erro):
        robo.token_x(config_completa())


def test_a1_fallback_preserva_refresh_e_bloqueia_token_antigo(ambiente, monkeypatch, capsys):
    robo.salvar_tokens_x(dict(access_token="antigo", refresh_token="refresh-antigo", expires_in=1))
    original = (ambiente / "x-tokens.json").read_bytes()
    substituir = robo.os.replace

    def bloqueado(origem, destino):
        if destino.name == "x-tokens.json":
            raise PermissionError("arquivo bloqueado")
        substituir(origem, destino)

    chamadas = []

    def http(*args, **kwargs):
        chamadas.append(args)
        return resposta(dict(access_token="acesso-novo", refresh_token="refresh-novo", expires_in=7200))

    monkeypatch.setattr(robo.os, "replace", bloqueado)
    monkeypatch.setattr(requests, "request", http)
    with pytest.raises(robo.Erro, match=r"x-tokens.json.novo") as erro:
        robo.token_x(config_completa())
    salvo = json.loads((ambiente / "x-tokens.json.novo").read_text())
    assert salvo["refresh_token"] == "refresh-novo"
    assert (ambiente / "x-tokens.json").read_bytes() == original
    with pytest.raises(robo.Erro, match=r"x-tokens.json.novo"):
        robo.token_x(config_completa())
    assert len(chamadas) == 1
    robo.avisar(str(erro))
    assert "refresh-novo" not in capsys.readouterr().out
    # Recuperação manual, sem renovar novamente.
    substituir(ambiente / "x-tokens.json.novo", ambiente / "x-tokens.json")
    assert robo.token_x(config_completa()) == "acesso-novo"
    assert len(chamadas) == 1


def test_a1_falha_nos_dois_arquivos_orienta_sem_expor(monkeypatch):
    tentativas = []

    def falhar(caminho, conteudo):
        tentativas.append(caminho.name)
        raise robo.Erro("falha")

    monkeypatch.setattr(robo, "gravar_atomico", falhar)
    with pytest.raises(robo.Erro, match="autorizar-x") as erro:
        robo.salvar_tokens_x(dict(access_token="segredo-acesso", refresh_token="segredo-refresh"))
    assert tentativas == ["x-tokens.json", "x-tokens.json.novo"]
    assert "segredo" not in str(erro.value)


def test_a1_ensaio_oculta_tokens_do_arquivo_de_recuperacao(ambiente, capsys):
    tokens = dict(access_token="acesso-resgatado", refresh_token="refresh-resgatado")
    (ambiente / "x-tokens.json.novo").write_text(json.dumps(tokens), encoding="utf-8")
    robo.salvar_pauta([linha(texto="Teste acesso-resgatado refresh-resgatado")])
    assert robo.main(["publicar", "--ensaio"]) == 0
    for saida in (capsys.readouterr().out, (ambiente / "registro.log").read_text(encoding="utf-8")):
        assert "acesso-resgatado" not in saida
        assert "refresh-resgatado" not in saida


@pytest.mark.parametrize("falha", ["http", "conexao", "gravacao"])
def test_a1_m1_renovacao_real_simulada_nao_bloqueia_pauta(ambiente, monkeypatch, falha):
    robo.salvar_tokens_x(dict(access_token="antigo", refresh_token="refresh-antigo", expires_in=1))
    robo.salvar_pauta([linha(rede="x")])
    original = (ambiente / "pauta.csv").read_bytes()
    chamadas = []
    substituir = robo.os.replace

    def substituir_simulado(origem, destino):
        if falha == "gravacao" and destino.name == "x-tokens.json":
            raise PermissionError("bloqueado")
        substituir(origem, destino)

    def http(metodo, url, **kwargs):
        chamadas.append(url)
        assert robo.ler_pauta()[0]["status"] == "APROVADO"
        if falha == "conexao":
            raise requests.ConnectionError("sem conexão simulada")
        return resposta(dict(access_token="novo", refresh_token="refresh-novo", expires_in=7200),
                        status=400 if falha == "http" else 200)

    monkeypatch.setattr(robo.os, "replace", substituir_simulado)
    monkeypatch.setattr(requests, "request", http)
    assert robo.publicar(config_completa()) == 1
    assert chamadas == ["https://api.x.com/2/oauth2/token"]
    assert (ambiente / "pauta.csv").read_bytes() == original
    if falha == "gravacao":
        assert json.loads((ambiente / "x-tokens.json.novo").read_text())["refresh_token"] == "refresh-novo"


@pytest.mark.parametrize("rede", ["x", "instagram"])
@pytest.mark.parametrize("falha", [False, True])
def test_m1_renova_antes_de_publicando_uma_unica_vez(rede, falha, monkeypatch):
    robo.salvar_pauta([linha(rede=rede, imagem="https://example.com/foto.jpg" if rede == "instagram" else "")])
    preparacoes, chamadas = [], []

    def preparar(config):
        preparacoes.append(robo.ler_pauta()[0]["status"])
        if falha:
            raise robo.Erro("Falhou a renovação simulada")
        return "token-preparado"

    def http(metodo, url, **kwargs):
        assert robo.ler_pauta()[0]["status"] == "PUBLICANDO"
        chamadas.append(url)
        if rede == "x":
            assert kwargs["headers"]["Authorization"] == "Bearer token-preparado"
            return resposta({"data": {"id": "post"}}, status=201)
        assert kwargs.get("params", kwargs.get("data"))["access_token"] == "token-preparado"
        return resposta({"user_id": "conta", "id": "post"})

    monkeypatch.setattr(robo, "token_" + rede, preparar)
    monkeypatch.setattr(requests, "request", http)
    assert robo.publicar(config_completa()) == int(falha)
    assert preparacoes == ["APROVADO"]
    assert robo.ler_pauta()[0]["status"] == ("APROVADO" if falha else "PUBLICADO")
    assert bool(chamadas) is not falha


def test_m2_data_nao_e_segredo_mas_credenciais_sao(ambiente, capsys):
    cfg = dict(config_completa(), OPENAI_API_KEY="openai-secreto", X_CLIENT_SECRET="cliente-secreto")
    (ambiente / "config.env").write_text("\n".join(f"{k}={v}" for k, v in cfg.items()), encoding="utf-8")
    robo.ler_config()
    data = cfg["INSTAGRAM_TOKEN_CRIADO_EM"]
    assert data not in robo.SEGREDOS
    robo.iniciar_log()
    robo.avisar(" ".join(cfg.values()))
    tela = capsys.readouterr().out
    log = (ambiente / "registro.log").read_text(encoding="utf-8")
    for saida in (tela, log):
        assert data in saida
        for chave, valor in cfg.items():
            if chave.endswith(("_TOKEN", "_SECRET", "_API_KEY")):
                assert valor not in saida


def test_m2_texto_da_ia_preservado_sem_mascarar(monkeypatch):
    texto = "Oferta em 20/11/2026; código coincidencia-falsa."
    robo.proteger("coincidencia-falsa")
    robo.salvar_pauta([linha(texto="")])
    monkeypatch.setattr(robo, "gerar_texto", lambda *args: texto)
    assert robo.escrever(config_completa()) == 0
    assert robo.ler_pauta()[0]["texto"] == texto


@pytest.mark.parametrize("data,hora", [("5/1/2020", "9:00"), ("05/1/2020", "09:0"), ("5/01/2020", "9:0")])
def test_m3_excel_normaliza_e_publica(data, hora, ambiente, monkeypatch):
    robo.salvar_pauta([linha(data=data, hora=hora)])
    antes = (ambiente / "pauta.csv").read_bytes()
    lida = robo.ler_pauta()[0]
    assert (lida["data"], lida["hora"]) == ("05/01/2020", "09:00")
    assert robo.agendamento(linha(data=data, hora=hora)) == datetime(2020, 1, 5, 9)
    assert robo.publicar({}, ensaio=True) == 0
    assert (ambiente / "pauta.csv").read_bytes() == antes
    monkeypatch.setattr(robo, "enviar", lambda *args: "post")
    assert robo.publicar({}) == 0
    assert robo.ler_pauta()[0]["status"] == "PUBLICADO"


@pytest.mark.parametrize("caractere", ["á", "ç", "ã", "\u10ff", "\u200d", "\u2010", "\u201f", "\u2032", "\u2037"])
def test_m4_caracteres_de_peso_um(caractere):
    assert robo.validar_post(linha(rede="x", texto=caractere * 280)) == "x"
    with pytest.raises(robo.Erro, match="280"):
        robo.validar_post(linha(rede="x", texto=caractere * 281))


@pytest.mark.parametrize("caractere", ["😀", "中", "\u1100", "\u200e", "\u2020", "\u2038"])
def test_m4_peso_dois_e_link(caractere):
    assert robo.validar_post(linha(rede="x", texto=caractere * 128 + " " + "https://example.com/" + "a" * 300)) == "x"
    with pytest.raises(robo.Erro, match="280"):
        robo.validar_post(linha(rede="x", texto=caractere * 141))


@pytest.mark.parametrize("inicio", ["=", "+", "-", "@"])
def test_b4_avisa_sobre_formula_sem_alterar_post(inicio, monkeypatch, capsys):
    texto = inicio + "Meu texto"
    robo.salvar_pauta([linha(texto="")])
    monkeypatch.setattr(robo, "gerar_texto", lambda *args: texto)
    assert robo.escrever(config_completa()) == 0
    assert robo.ler_pauta()[0]["texto"] == texto
    saida = capsys.readouterr().out
    assert "Excel" in saida and "fórmula" in saida


@pytest.mark.parametrize("fim", ["\r\n", "\n"])
@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"])
def test_b6_renovacao_preserva_config(ambiente, monkeypatch, fim, bom):
    antigo = (datetime.now() - timedelta(days=46)).strftime("%d/%m/%Y")
    texto = fim.join(["# Meu comentário", "INSTAGRAM_ACCESS_TOKEN = velho", "", "IA=claude",
                      "INSTAGRAM_TOKEN_CRIADO_EM=" + antigo, "# fim"])
    (ambiente / "config.env").write_bytes(bom + texto.encode("utf-8"))
    cfg = robo.ler_config()
    monkeypatch.setattr(requests, "request", lambda *a, **kw: resposta({"access_token": "novo"}))
    assert robo.token_instagram(cfg) == "novo"
    esperado = texto.replace("= velho", "= novo").replace(antigo, datetime.now().strftime("%d/%m/%Y"))
    assert (ambiente / "config.env").read_bytes() == bom + esperado.encode("utf-8")


def test_b8_avisa_maiusculas_sem_publicar(capsys):
    robo.salvar_pauta([linha(status="aprovado")])
    assert robo.publicar({}) == 0
    assert robo.ler_pauta()[0]["status"] == "aprovado"
    assert "APROVADO em maiúsculas" in capsys.readouterr().out
