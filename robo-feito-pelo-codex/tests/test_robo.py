import csv
import io
import json
import socket
import sys
import time
import types
import webbrowser
from datetime import datetime, timedelta

import pytest
import requests

import robo


@pytest.fixture(autouse=True)
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setattr(robo, "BASE", tmp_path)
    robo.SEGREDOS.clear()

    def proibido(*args, **kwargs):
        raise AssertionError("Rede ou navegador não pode ser usado nos testes")

    monkeypatch.setattr(requests, "request", proibido)
    monkeypatch.setattr(socket.socket, "connect", proibido)
    monkeypatch.setattr(socket.socket, "connect_ex", proibido)
    monkeypatch.setattr(socket.socket, "bind", proibido)
    monkeypatch.setattr(socket, "create_connection", proibido)
    monkeypatch.setattr(webbrowser, "open", proibido)
    (tmp_path / "config.env").write_text("IA=claude\nCLAUDE_MODELO=claude-sonnet-5-5\n", encoding="utf-8")
    (tmp_path / "perfil.txt").write_text("Meu estilo: útil; simples, com ação.", encoding="utf-8")
    yield tmp_path
    for handler in list(robo.LOGGER.handlers):
        handler.close()
        robo.LOGGER.removeHandler(handler)


def linha(**mudancas):
    dados = dict(zip(robo.COLUNAS, ["01/01/2020", "09:00", "facebook", "Tema", "Olá; ação!", "", "APROVADO", ""]))
    dados.update(mudancas)
    return dados


def resposta(dados=None, status=200, headers=None):
    return types.SimpleNamespace(status_code=status, headers=headers or {}, json=lambda: dados or {})


def config_completa():
    return {
        "IA": "claude", "CLAUDE_MODELO": "claude-sonnet-5-5", "ANTHROPIC_API_KEY": "chave-teste-falsa",
        "LINKEDIN_ACCESS_TOKEN": "linkedin-falso", "FACEBOOK_PAGE_ID": "123",
        "FACEBOOK_PAGE_ACCESS_TOKEN": "pagina-falsa", "INSTAGRAM_ACCESS_TOKEN": "insta-falso",
        "INSTAGRAM_TOKEN_CRIADO_EM": datetime.now().strftime("%d/%m/%Y"), "X_CLIENT_ID": "client-falso",
    }


@pytest.mark.parametrize("status", ["RASCUNHO", "PUBLICADO", "PUBLICANDO", "REVISAR", "", "aprovado"])
@pytest.mark.parametrize("manual", [False, True])
def test_somente_aprovado_publica(status, manual, monkeypatch):
    robo.salvar_pauta([linha(status=status)])
    chamadas = []
    monkeypatch.setattr(robo, "enviar", lambda *args: chamadas.append(args))
    assert robo.publicar({}, numero=2 if manual else None) == 0
    assert chamadas == []
    assert robo.ler_pauta()[0]["status"] == status


def test_linkedin_nunca_sai_no_publicar(monkeypatch):
    robo.salvar_pauta([linha(rede="linkedin")])
    monkeypatch.setattr(robo, "enviar", lambda *args: pytest.fail("LinkedIn automático"))
    assert robo.publicar({}) == 0
    assert robo.ler_pauta()[0]["status"] == "APROVADO"


def test_publicado_nao_repete_e_persiste_antes_do_envio(monkeypatch):
    robo.salvar_pauta([linha()])
    chamadas = []

    def enviar(*args):
        assert robo.ler_pauta()[0]["status"] == "PUBLICANDO"
        chamadas.append(args)
        return "post-123"

    monkeypatch.setattr(robo, "enviar", enviar)
    assert robo.publicar({}) == 0
    assert robo.publicar({}) == 0
    assert len(chamadas) == 1
    assert robo.ler_pauta()[0]["resultado"] == "post-123"
    assert robo.ler_pauta()[0]["status"] == "PUBLICADO"


def test_linkedin_manual_ignora_data_futura(monkeypatch):
    robo.salvar_pauta([linha(rede="linkedin", data="01/01/2099")])
    monkeypatch.setattr(robo, "enviar", lambda *args: "urn:li:share:123")
    assert robo.publicar({}, numero=2) == 0
    assert robo.ler_pauta()[0]["status"] == "PUBLICADO"


def test_futuro_nao_publica(monkeypatch):
    robo.salvar_pauta([linha(data="01/01/2099")])
    monkeypatch.setattr(robo, "enviar", lambda *args: pytest.fail("Publicou antes da hora"))
    assert robo.publicar({}) == 0


@pytest.mark.parametrize("data,hora", [("31/02/2026", "10:00"), ("01/01/2026", "24:00"), ("1/1/26", "10:00")])
def test_data_invalida(data, hora):
    robo.salvar_pauta([linha(data=data, hora=hora)])
    assert robo.publicar({}) == 1
    assert robo.ler_pauta()[0]["status"] == "APROVADO"


@pytest.mark.parametrize("comando", ["publicar", "publicar-agora", "escrever", "conferir", "autorizar-x"])
@pytest.mark.parametrize("antes", [False, True])
def test_todos_comandos_ensaio_sem_rede_ou_alteracao(comando, antes, ambiente, monkeypatch):
    cfg = config_completa()
    (ambiente / "config.env").write_text("\n".join(f"{k}={v}" for k, v in cfg.items()), encoding="utf-8")
    robo.salvar_tokens_x({"access_token": "acesso-falso", "refresh_token": "renovacao-falsa", "expires_in": 7200})
    robo.salvar_pauta([linha(texto="" if comando == "escrever" else "Texto aprovado")])
    monkeypatch.setattr(robo, "gerar_texto", lambda *args: pytest.fail("IA no ensaio"))
    monkeypatch.setattr(robo, "enviar", lambda *args: pytest.fail("Envio no ensaio"))
    monkeypatch.setattr(robo, "requisitar", lambda *args, **kwargs: pytest.fail("HTTP no ensaio"))
    arquivos = [ambiente / nome for nome in ("pauta.csv", "config.env", "x-tokens.json")]
    original = [arquivo.read_bytes() for arquivo in arquivos]
    args = [comando] + (["2"] if comando == "publicar-agora" else [])
    args = ["--ensaio"] + args if antes else args + ["--ensaio"]
    assert robo.main(args) == 0
    assert original == [arquivo.read_bytes() for arquivo in arquivos]
    assert "ensaio=sim" in (ambiente / "registro.log").read_text(encoding="utf-8")


def test_csv_preserva_acentos_ponto_virgula_aspas_e_quebra(ambiente):
    dados = [linha(tema='Educação; "ação"', texto='Olá, São Paulo; "bom dia"!\nSegunda linha: coração.')]
    robo.salvar_pauta(dados)
    assert (ambiente / "pauta.csv").read_bytes().startswith(b"\xef\xbb\xbf")
    assert robo.ler_pauta() == dados
    robo.salvar_pauta(robo.ler_pauta())
    assert robo.ler_pauta() == dados


@pytest.mark.parametrize("encoding", ["cp1252", "utf-8", "utf-8-sig"])
def test_csv_excel_acentos_e_regravacao_utf8_bom(ambiente, encoding):
    dados = [linha(tema="organização do mês", texto="é")]
    conteudo = ";".join(robo.COLUNAS) + "\r\n"
    conteudo += ";".join(dados[0][coluna] for coluna in robo.COLUNAS) + "\r\n"
    caminho = ambiente / "pauta.csv"
    caminho.write_bytes(conteudo.encode(encoding))

    lidas = robo.ler_pauta()
    assert lidas == dados
    robo.salvar_pauta(lidas)
    assert caminho.read_bytes() == conteudo.encode("utf-8-sig")
    assert robo.ler_pauta() == dados


def test_cabecalho_invalido(ambiente):
    (ambiente / "pauta.csv").write_text("data,texto\n", encoding="utf-8-sig")
    with pytest.raises(robo.Erro, match="cabeçalho"):
        robo.ler_pauta()


def test_falha_ambigua_exige_revisao(monkeypatch):
    robo.salvar_pauta([linha()])

    def falha(*args):
        raise robo.Erro("Sem resposta; confira a rede.")

    monkeypatch.setattr(robo, "enviar", falha)
    assert robo.publicar({}) == 1
    assert robo.ler_pauta()[0]["status"] == "REVISAR"
    monkeypatch.setattr(robo, "enviar", lambda *args: pytest.fail("Reenvio incerto"))
    assert robo.publicar({}) == 0


def test_falha_salvamento_final_impede_reenvio(monkeypatch):
    robo.salvar_pauta([linha()])
    salvar = robo.salvar_pauta

    def salvar_simulado(linhas):
        if linhas[0]["status"] == "PUBLICADO":
            raise robo.Erro("Excel bloqueou arquivo")
        salvar(linhas)

    monkeypatch.setattr(robo, "salvar_pauta", salvar_simulado)
    monkeypatch.setattr(robo, "enviar", lambda *args: "publicado-mas-nao-salvo")
    assert robo.publicar({}) == 1
    assert robo.ler_pauta()[0]["status"] == "PUBLICANDO"
    monkeypatch.setattr(robo, "enviar", lambda *args: pytest.fail("Duplicou"))
    assert robo.publicar({}) == 0


def test_trava_impede_duas_execucoes(ambiente):
    with robo.trava():
        with pytest.raises(robo.Erro, match="execução"):
            with robo.trava():
                pytest.fail("Entrou duas vezes")
    assert not (ambiente / ".robo.lock").exists()


@pytest.mark.parametrize("rede,imagem", [("instagram", ""), ("instagram", "https://example.com/foto.png"), ("linkedin", "foto.jpg"), ("x", "foto.jpg"), ("facebook", "../fora.jpg")])
def test_imagem_invalida_rejeitada(rede, imagem):
    with pytest.raises(robo.Erro):
        robo.validar_post(linha(rede=rede, imagem=imagem))


@pytest.mark.parametrize("rede,tamanho", [("linkedin", 3001), ("instagram", 2201), ("x", 281)])
def test_limites_de_texto(rede, tamanho):
    with pytest.raises(robo.Erro, match="Encurte"):
        robo.validar_post(linha(rede=rede, texto="a" * tamanho))


def test_x_link_conta_23():
    assert robo.validar_post(linha(rede="x", texto="a" * 256 + " " + "https://example.com/" + "b" * 300)) == "x"


def test_payload_linkedin(monkeypatch):
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append((metodo, url, kwargs))
        return resposta({"sub": "pessoa"}) if metodo == "GET" else resposta(status=201, headers={"x-restli-id": "urn:post:1"})

    monkeypatch.setattr(requests, "request", http)
    assert robo.enviar(linha(rede="linkedin"), config_completa()) == "urn:post:1"
    dados = chamadas[1][2]
    assert dados["headers"]["Linkedin-Version"] == "202611"
    assert dados["headers"]["X-Restli-Protocol-Version"] == "2.0.0"
    assert dados["json"]["author"] == "urn:li:person:pessoa"
    assert dados["json"]["commentary"] == "Olá; ação!"
    assert dados["json"]["lifecycleState"] == "PUBLISHED"
    assert dados["timeout"] == 30
    assert dados["allow_redirects"] is False


@pytest.mark.parametrize("imagem,final", [("", "/feed"), ("https://example.com/foto.jpg", "/photos"), ("foto.jpg", "/photos")])
def test_facebook_texto_url_e_arquivo(imagem, final, ambiente, monkeypatch):
    (ambiente / "foto.jpg").write_bytes(b"foto-falsa")
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append((metodo, url, kwargs))
        if "files" in kwargs:
            assert kwargs["files"]["source"].read() == b"foto-falsa"
        return resposta({"id": "pagina_post"})

    monkeypatch.setattr(requests, "request", http)
    assert robo.enviar(linha(imagem=imagem), config_completa()) == "pagina_post"
    assert chamadas[0][1] == "https://graph.facebook.com/v27.0/123" + final
    assert chamadas[0][2]["data"]["caption" if imagem else "message"] == "Olá; ação!"


def test_instagram_cria_depois_publica(monkeypatch):
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append((metodo, url, kwargs))
        if url.endswith("/me"):
            return resposta({"user_id": "ig-conta"})
        if url.endswith("/media"):
            return resposta({"id": "container"})
        assert kwargs["data"]["creation_id"] == "container"
        return resposta({"id": "post-ig"})

    monkeypatch.setattr(requests, "request", http)
    assert robo.enviar(linha(rede="instagram", imagem="https://example.com/foto.jpeg"), config_completa()) == "post-ig"
    assert [x[0] for x in chamadas] == ["GET", "POST", "POST"]
    assert chamadas[2][1] == "https://graph.instagram.com/v27.0/ig-conta/media_publish"


def test_instagram_renova_e_persiste(ambiente, monkeypatch):
    cfg = config_completa()
    cfg["INSTAGRAM_TOKEN_CRIADO_EM"] = (datetime.now() - timedelta(days=46)).strftime("%d/%m/%Y")
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: resposta({"access_token": "novo-ig"}))
    assert robo.token_instagram(cfg) == "novo-ig"
    assert robo.ler_config()["INSTAGRAM_ACCESS_TOKEN"] == "novo-ig"


def test_x_refresh_persistido_antes_de_publicar(ambiente, monkeypatch):
    robo.salvar_tokens_x({"access_token": "velho", "refresh_token": "refresh-velho", "expires_in": 1})
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append(url)
        if url.endswith("/token"):
            assert kwargs["data"]["refresh_token"] == "refresh-velho"
            return resposta({"access_token": "novo", "refresh_token": "refresh-novo", "expires_in": 7200})
        salvo = json.loads((ambiente / "x-tokens.json").read_text())
        assert salvo["refresh_token"] == "refresh-novo"
        assert kwargs["headers"]["Authorization"] == "Bearer novo"
        assert kwargs["json"] == {"text": "Olá; ação!"}
        return resposta({"data": {"id": "post-x"}}, status=201)

    monkeypatch.setattr(requests, "request", http)
    assert robo.enviar(linha(rede="x"), config_completa()) == "post-x"
    assert len(chamadas) == 2


def test_falha_ao_salvar_refresh_nao_publica(monkeypatch):
    robo.salvar_tokens_x({"access_token": "velho", "refresh_token": "refresh-velho", "expires_in": 1})
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append(url)
        return resposta({"access_token": "novo", "refresh_token": "refresh-novo"})

    def falha(*args):
        raise robo.Erro("Falha ao gravar")

    monkeypatch.setattr(requests, "request", http)
    monkeypatch.setattr(robo, "gravar_atomico", falha)
    with pytest.raises(robo.Erro):
        robo.enviar(linha(rede="x"), config_completa())
    assert chamadas == ["https://api.x.com/2/oauth2/token"]


def test_conferir_uma_leitura_por_rede(monkeypatch):
    robo.salvar_tokens_x({"access_token": "falso", "refresh_token": "refresh-falso", "expires_in": 7200})
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append((metodo, url))
        return resposta({"id": "teste"})

    monkeypatch.setattr(requests, "request", http)
    assert robo.conferir(config_completa()) == 0
    assert len(chamadas) == 4
    assert all(metodo == "GET" for metodo, url in chamadas)
    assert not any("refresh" in url for metodo, url in chamadas)


def test_conferir_x_expirado_nao_renova(monkeypatch):
    robo.salvar_tokens_x({"access_token": "falso", "refresh_token": "refresh-falso", "expires_in": 1})
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append(url)
        return resposta({"id": "teste"})

    monkeypatch.setattr(requests, "request", http)
    assert robo.conferir(config_completa()) == 1
    assert len(chamadas) == 3
    assert all("api.x.com" not in url for url in chamadas)


def test_segredos_nunca_na_tela_ou_log(ambiente, capsys, monkeypatch):
    segredo = "token-super-secreto-falso"
    (ambiente / "config.env").write_text("LINKEDIN_ACCESS_TOKEN=" + segredo, encoding="utf-8")
    robo.salvar_pauta([linha(texto="Texto contendo " + segredo)])
    assert robo.main(["publicar", "--ensaio"]) == 0
    assert segredo not in capsys.readouterr().out
    assert segredo not in (ambiente / "registro.log").read_text(encoding="utf-8")

    def falha(*args, **kwargs):
        raise requests.ConnectionError("https://api.invalid/?token=" + segredo)

    monkeypatch.setattr(requests, "request", falha)
    assert robo.main(["conferir"]) == 1
    assert segredo not in capsys.readouterr().out
    assert segredo not in (ambiente / "registro.log").read_text(encoding="utf-8")


@pytest.mark.parametrize("ia,modulo", [("claude", "anthropic"), ("openai", "openai")])
def test_sdk_correto_importado_so_ao_usar(ia, modulo, monkeypatch):
    chamadas = []

    class Cliente:
        def __init__(self, **kwargs):
            self.messages = self.responses = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def create(self, **kwargs):
            chamadas.append(kwargs)
            return types.SimpleNamespace(output_text="Texto gerado", content=[types.SimpleNamespace(type="text", text="Texto gerado")])

    monkeypatch.setitem(sys.modules, modulo, types.SimpleNamespace(Anthropic=Cliente, OpenAI=Cliente))
    monkeypatch.setitem(sys.modules, "openai" if modulo == "anthropic" else "anthropic", None)
    cfg = dict(config_completa(), IA=ia, OPENAI_API_KEY="falsa", OPENAI_MODELO="gpt-6.2-sol")
    robo.salvar_pauta([linha(texto="", status="APROVADO")])
    assert robo.escrever(cfg) == 0
    assert robo.ler_pauta()[0]["status"] == "RASCUNHO"
    assert robo.ler_pauta()[0]["texto"] == "Texto gerado"
    pedido = chamadas[0]["messages"][0]["content"] if ia == "claude" else chamadas[0]["input"]
    assert "Meu estilo: útil; simples" in pedido
    assert "Tema" in pedido


@pytest.mark.parametrize("state_invalido", ["invalido", "%C3%A7"])
def test_oauth_pkce_callback_e_troca_simulados(monkeypatch, state_invalido):
    from urllib.parse import parse_qs, urlparse
    aberto = {}
    capturado = {}
    urls = []

    def abrir(url):
        urls.append(url)
        aberto.update(parse_qs(urlparse(url).query))
        return True

    class Servidor:
        def __init__(self, endereco, handler):
            assert endereco == ("127.0.0.1", 8080)
            self.handler = handler
            self.tentativas = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def handle_request(self):
            self.tentativas += 1
            objeto = object.__new__(self.handler)
            state = state_invalido if self.tentativas == 1 else aberto["state"][0]
            objeto.path = "/callback?code=code-falso&state=" + state
            objeto.wfile = io.BytesIO()
            codigos = []
            objeto.send_response = codigos.append
            objeto.send_header = lambda *args: None
            objeto.end_headers = lambda: None
            objeto.do_GET()
            assert codigos == ([400] if self.tentativas == 1 else [200])

    def http(metodo, url, **kwargs):
        capturado.update(kwargs)
        return resposta({"access_token": "novo", "refresh_token": "refresh-novo", "expires_in": 7200})

    monkeypatch.setattr(robo, "HTTPServer", Servidor)
    monkeypatch.setattr(webbrowser, "open", abrir)
    monkeypatch.setattr(requests, "request", http)
    assert robo.autorizar_x(dict(config_completa(), X_CLIENT_SECRET="segredo-falso")) == 0
    assert aberto["redirect_uri"] == ["http://127.0.0.1:8080/callback"]
    assert aberto["code_challenge_method"] == ["S256"]
    assert "offline.access" in aberto["scope"][0]
    verifier = capturado["data"]["code_verifier"]
    desafio = robo.base64.urlsafe_b64encode(robo.hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    assert aberto["code_challenge"] == [desafio]
    assert capturado["auth"] == ("client-falso", "segredo-falso")
    assert robo.ler_tokens_x()["refresh_token"] == "refresh-novo"
    assert "scope=tweet.read%20tweet.write%20users.read%20offline.access&" in urls[0]


def config_unificada():
    cfg = config_completa()
    cfg.update({"INSTAGRAM_USER_ID": "1784000", "INSTAGRAM_TOKEN_CRIADO_EM": "01/01/2020"})
    return cfg


def test_instagram_unificado_cria_espera_e_publica(monkeypatch):
    chamadas = []
    estados = iter(["IN_PROGRESS", "FINISHED"])

    def http(metodo, url, **kwargs):
        chamadas.append((metodo, url, kwargs))
        if url.endswith("/media"):
            return resposta({"id": "container"})
        if url.endswith("/container"):
            return resposta({"status_code": next(estados)})
        assert kwargs["data"]["creation_id"] == "container"
        return resposta({"id": "post-ig"})

    monkeypatch.setattr(requests, "request", http)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    assert robo.enviar(linha(rede="instagram", imagem="https://example.com/foto.jpg"), config_unificada()) == "post-ig"
    assert [c[1] for c in chamadas] == [
        "https://graph.facebook.com/v27.0/1784000/media",
        "https://graph.facebook.com/v27.0/container",
        "https://graph.facebook.com/v27.0/container",
        "https://graph.facebook.com/v27.0/1784000/media_publish",
    ]


def test_instagram_unificado_nao_publica_se_imagem_recusada(monkeypatch):
    chamadas = []

    def http(metodo, url, **kwargs):
        chamadas.append(url)
        if url.endswith("/media"):
            return resposta({"id": "container"})
        return resposta({"status_code": "ERROR"})

    monkeypatch.setattr(requests, "request", http)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    with pytest.raises(robo.Erro, match="Nada foi publicado"):
        robo.enviar(linha(rede="instagram", imagem="https://example.com/foto.jpg"), config_unificada())
    assert not any(u.endswith("/media_publish") for u in chamadas)


def test_instagram_unificado_nao_renova_token(monkeypatch):
    monkeypatch.setattr(requests, "request", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deve chamar a rede")))
    assert robo.token_instagram(config_unificada()) == "insta-falso"


def test_conferir_instagram_unificado_usa_graph_facebook(monkeypatch):
    urls = []

    def http(metodo, url, **kwargs):
        urls.append(url)
        return resposta({"id": "x", "username": "conta", "sub": "s", "name": "n", "data": {"id": "1"}})

    monkeypatch.setattr(requests, "request", http)
    monkeypatch.setattr(robo, "token_x", lambda config, renovar=True: "token-x")
    robo.conferir(config_unificada())
    assert "https://graph.facebook.com/v27.0/1784000" in urls
    assert not any("graph.instagram.com" in u for u in urls)


def test_instagram_unificado_espera_conforme_a_meta(monkeypatch):
    pausas = []
    monkeypatch.setattr(requests, "request", lambda m, u, **k: resposta({"id": "container"} if u.endswith("/media") else {"status_code": "IN_PROGRESS"}))
    monkeypatch.setattr(robo.time, "sleep", pausas.append)
    with pytest.raises(robo.Erro, match="ainda está processando"):
        robo.enviar(linha(rede="instagram", imagem="https://example.com/foto.jpg"), config_unificada())
    assert pausas[0] == 5 and set(pausas[1:]) == {60} and sum(pausas) <= 5 + 5 * 60


@pytest.mark.parametrize("estado, trecho", [("EXPIRED", "Nada foi publicado"), ("PUBLISHED", "já foi publicada")])
def test_instagram_unificado_estados_finais_sem_media_publish(monkeypatch, estado, trecho):
    urls = []

    def http(metodo, url, **kwargs):
        urls.append(url)
        return resposta({"id": "container"} if url.endswith("/media") else {"status_code": estado})

    monkeypatch.setattr(requests, "request", http)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    with pytest.raises(robo.Erro, match=trecho):
        robo.enviar(linha(rede="instagram", imagem="https://example.com/foto.jpg"), config_unificada())
    assert not any(u.endswith("/media_publish") for u in urls)
