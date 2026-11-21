"""Testes do robô. Nenhum acessa a internet: _http e a IA são trocados por simulações."""
import json
from datetime import datetime

import pytest

import robo

HTTP_REAL = robo._http  # guardado antes de a fixture trocá-lo

CABECALHO = "data;hora;rede;tema;texto;imagem;status;resultado"
SEGREDO_LI = "LI-SEGREDO-123456"
SEGREDO_FB = "FB-SEGREDO-123456"
PROIBIDAS = []

CONFIG = f"""IA=claude
ANTHROPIC_API_KEY=ANT-SEGREDO-123456
LINKEDIN_TOKEN={SEGREDO_LI}
FACEBOOK_PAGE_ID=999
FACEBOOK_PAGE_TOKEN={SEGREDO_FB}
INSTAGRAM_TOKEN=IG-SEGREDO-123456
X_CLIENT_ID=cliente-x-123456
"""


class Resp:
    def __init__(self, status=200, corpo=None, headers=None):
        self.status_code = status
        self._corpo = corpo if corpo is not None else {}
        self.headers = headers or {}
        self.text = json.dumps(self._corpo)

    def json(self):
        return self._corpo


class FalsaRede:
    def __init__(self):
        self.chamadas = []

    def __call__(self, metodo, url, **kw):
        self.chamadas.append((metodo, url, kw))
        if "userinfo" in url:
            return Resp(200, {"sub": "abc"})
        if url.endswith("/rest/posts"):
            return Resp(201, headers={"x-restli-id": "urn:li:share:1"})
        if url.endswith("/feed"):
            return Resp(200, {"id": "999_111"})
        if url.endswith("/tweets"):
            return Resp(201, {"data": {"id": "777"}})
        if url.endswith("/oauth2/token"):
            return Resp(200, {"access_token": "NOVO-ACESSO-123456", "refresh_token": "NOVO-REFRESH-123456", "expires_in": 7200})
        return Resp(200, {})


def escrever_pauta(pasta, linhas):
    conteudo = CABECALHO + "\r\n" + "\r\n".join(linhas) + "\r\n"
    (pasta / "pauta.csv").write_bytes(b"\xef\xbb\xbf" + conteudo.encode("utf-8"))


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    monkeypatch.setattr(robo, "PASTA", tmp_path)
    monkeypatch.setattr(robo, "agora", lambda: datetime(2026, 11, 20, 12, 0))
    robo.SEGREDOS.clear()
    (tmp_path / "config.env").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "perfil.txt").write_text("Seja claro.", encoding="utf-8")

    PROIBIDAS.clear()

    def proibida(*a, **k):
        PROIBIDAS.append(a)  # main() engole AssertionError: por isso o teste confere esta lista
        raise AssertionError("chamada de rede não esperada neste teste")

    monkeypatch.setattr(robo, "_http", proibida)
    monkeypatch.setattr(robo, "chamar_ia", proibida)
    return tmp_path


def estado(pasta):
    return {d["_linha"]: (d["status"], d["resultado"]) for d in robo.ler_pauta()}


def test_rascunho_nao_e_publicado(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto pronto;;RASCUNHO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    assert robo.main(["publicar"]) == 0
    assert rede.chamadas == []
    assert estado(pasta)[2] == ("RASCUNHO", "")


def test_publicado_nao_e_republicado(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;PUBLICADO;999_1"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    assert rede.chamadas == []
    assert robo.main(["publicar-agora", "2"]) == 1  # recusa
    assert rede.chamadas == []
    assert estado(pasta)[2] == ("PUBLICADO", "999_1")


def test_aprovado_com_hora_chegada_publica_e_grava_resultado(pasta, monkeypatch):
    escrever_pauta(
        pasta,
        [
            "01/11/2026;09:00;facebook;t;Olá, ação ágil;;APROVADO;",
            "30/12/2026;09:00;facebook;t;Futuro;;APROVADO;",
        ],
    )
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    assert len(rede.chamadas) == 1
    assert rede.chamadas[0][2]["data"]["message"] == "Olá, ação ágil"
    est = estado(pasta)
    assert est[2] == ("PUBLICADO", "999_111")
    assert est[3] == ("APROVADO", "")  # a hora ainda não chegou
    rede.chamadas.clear()
    robo.main(["publicar"])  # segunda rodada não repete
    assert rede.chamadas == []


def test_linkedin_nao_sai_pelo_publicar_mas_sai_pelo_publicar_agora(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;linkedin;t;Post sério;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    assert rede.chamadas == []
    assert "PULADA" in capsys.readouterr().out
    assert estado(pasta)[2] == ("APROVADO", "")
    assert robo.main(["publicar-agora", "2"]) == 0
    urls = [c[1] for c in rede.chamadas]
    assert any(u.endswith("/rest/posts") for u in urls)
    assert estado(pasta)[2] == ("PUBLICADO", "urn:li:share:1")


def test_publicar_agora_exige_aprovado(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;RASCUNHO;"])
    monkeypatch.setattr(robo, "_http", FalsaRede())
    assert robo.main(["publicar-agora", "2"]) == 1
    assert estado(pasta)[2] == ("RASCUNHO", "")


def test_ensaio_nao_faz_chamada_de_rede_nem_altera_a_planilha(pasta, capsys):
    escrever_pauta(
        pasta,
        [
            "01/11/2026;09:00;facebook;t;Texto do face;;APROVADO;",
            "01/11/2026;09:00;linkedin;t;Texto do linkedin;;APROVADO;",
            "01/11/2026;09:00;x;t;;;;",
        ],
    )
    antes = (pasta / "pauta.csv").read_bytes()
    # _http e chamar_ia levantam AssertionError se forem chamados (fixture)
    for cmd in (
        ["publicar"], ["publicar-agora", "2"], ["publicar-agora", "3"], ["escrever"], ["conferir"],
        ["autorizar-x"], ["renovar-instagram"],
    ):
        assert robo.main(cmd + ["--ensaio"]) == 0, cmd  # main() engole exceções: o retorno precisa ser 0
    assert PROIBIDAS == []  # nenhuma chamada de rede nem de IA foi tentada
    assert not (pasta / "robo.lock").exists()
    saida = capsys.readouterr().out
    assert "ERRO" not in saida
    assert "ENSAIO" in saida and "Texto do face" in saida and "FACEBOOK" in saida
    assert (pasta / "pauta.csv").read_bytes() == antes
    assert not (pasta / "x-tokens.json").exists()


def test_planilha_com_acento_e_ponto_e_virgula_nao_estraga(pasta):
    texto = 'Ação: "prazo"; direito\nsegunda linha; fim'
    escrever_pauta(pasta, ['01/11/2026;09:00;facebook;Café;"Ação: ""prazo""; direito\nsegunda linha; fim";;RASCUNHO;'])
    linhas = robo.ler_pauta()
    assert linhas[0]["tema"] == "Café"
    assert linhas[0]["texto"] == texto.replace(";", ";")
    robo.gravar_pauta(linhas)
    bruto = (pasta / "pauta.csv").read_bytes()
    assert bruto.startswith(b"\xef\xbb\xbf" + CABECALHO.encode())
    assert robo.ler_pauta() == linhas  # idêntico após gravar e reler
    assert "Café".encode("utf-8") in bruto


def test_planilha_cp1252_do_excel_antigo_e_lida(pasta):
    conteudo = CABECALHO + "\r\n01/11/2026;09:00;facebook;Café;Ação;;RASCUNHO;\r\n"
    (pasta / "pauta.csv").write_bytes(conteudo.encode("cp1252"))
    assert robo.ler_pauta()[0]["texto"] == "Ação"


def test_escrever_grava_rascunho(pasta, monkeypatch):
    escrever_pauta(
        pasta,
        [
            "01/11/2026;09:00;facebook;Prazos;;;;",
            "01/11/2026;09:00;x;Já tem;Texto antigo;;APROVADO;",
        ],
    )
    pedidos = []

    def ia(cfg, sistema, pedido):
        pedidos.append((sistema, pedido))
        return "Post escrito pela IA"

    monkeypatch.setattr(robo, "chamar_ia", ia)
    assert robo.main(["escrever"]) == 0
    assert len(pedidos) == 1 and pedidos[0][0] == "Seja claro." and "Prazos" in pedidos[0][1]
    est = estado(pasta)
    assert est[2] == ("RASCUNHO", "")
    assert robo.ler_pauta()[0]["texto"] == "Post escrito pela IA"
    assert robo.ler_pauta()[1]["texto"] == "Texto antigo"


def test_chaves_nunca_aparecem_no_registro_nem_na_tela(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])

    def rede_com_erro(metodo, url, **kw):
        return Resp(500, {"erro": f"falhou com {SEGREDO_FB} e access_token={SEGREDO_FB}"})

    monkeypatch.setattr(robo, "_http", rede_com_erro)
    robo.main(["publicar"])
    robo.main(["conferir"])
    tela = capsys.readouterr().out
    log = (pasta / "registro.log").read_text(encoding="utf-8")
    for segredo in (SEGREDO_FB, SEGREDO_LI, "ANT-SEGREDO-123456", "IG-SEGREDO-123456"):
        assert segredo not in tela and segredo not in log
    assert "***" in log
    assert log.startswith("20/11/2026 12:00:00")


def test_token_x_renovado_grava_novo_refresh_na_hora(pasta, monkeypatch):
    (pasta / "x-tokens.json").write_text(
        json.dumps({"access_token": "VELHO-ACESSO-123456", "refresh_token": "VELHO-REFRESH-123456", "expires_at": 0}),
        encoding="utf-8",
    )
    escrever_pauta(pasta, ["01/11/2026;09:00;x;t;Post curto;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    tokens = json.loads((pasta / "x-tokens.json").read_text(encoding="utf-8"))
    assert tokens["refresh_token"] == "NOVO-REFRESH-123456"
    assert tokens["access_token"] == "NOVO-ACESSO-123456"
    renovacao = [c for c in rede.chamadas if c[1].endswith("/oauth2/token")][0]
    assert renovacao[2]["data"]["refresh_token"] == "VELHO-REFRESH-123456"
    assert estado(pasta)[2] == ("PUBLICADO", "https://x.com/i/web/status/777")


def test_limites_de_tamanho_e_erro_marca_status(pasta, monkeypatch):
    longo = "a" * 281
    escrever_pauta(pasta, [f"01/11/2026;09:00;x;t;{longo};;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    assert rede.chamadas == []
    assert estado(pasta)[2][0] == "ERRO"
    assert robo.tamanho_x("veja https://exemplo.com/um/link/muito/comprido/mesmo ok") == 5 + 23 + 3


def test_instagram_sem_imagem_publica_nada(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;instagram;t;Legenda;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    assert rede.chamadas == []
    st, res = estado(pasta)[2]
    assert st == "ERRO" and "imagem" in res.lower()


def test_token_vencido_da_mensagem_em_portugues(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;linkedin;t;Texto;;APROVADO;"])
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(401, {}))
    robo.main(["publicar-agora", "2"])
    assert "Token Generator" in capsys.readouterr().out


CFG_IG_UNI = {"INSTAGRAM_TOKEN": "EAA-SISTEMA-123456", "INSTAGRAM_USER_ID": "1784000"}


def test_instagram_unificado_usa_graph_facebook_espera_e_publica(monkeypatch):
    chamadas = []
    estados = iter(["IN_PROGRESS", "FINISHED"])

    def rede(metodo, url, **kw):
        chamadas.append((metodo, url))
        if url.endswith("/media"):
            return Resp(200, {"id": "cont"})
        if url.endswith("/cont"):
            return Resp(200, {"status_code": next(estados)})
        assert kw["data"]["creation_id"] == "cont"
        return Resp(200, {"id": "ig-post"})

    monkeypatch.setattr(robo, "_http", rede)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    assert robo.publicar_instagram(CFG_IG_UNI, "Legenda", "https://exemplo.com/foto.jpg") == "ig-post"
    assert [u for _, u in chamadas] == [
        "https://graph.facebook.com/v27.0/1784000/media",
        "https://graph.facebook.com/v27.0/cont",
        "https://graph.facebook.com/v27.0/cont",
        "https://graph.facebook.com/v27.0/1784000/media_publish",
    ]


def test_instagram_unificado_imagem_recusada_nao_publica(monkeypatch):
    urls = []

    def rede(metodo, url, **kw):
        urls.append(url)
        return Resp(200, {"id": "cont"} if url.endswith("/media") else {"status_code": "ERROR"})

    monkeypatch.setattr(robo, "_http", rede)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    with pytest.raises(robo.ErroRobo, match="Nada foi publicado"):
        robo.publicar_instagram(CFG_IG_UNI, "Legenda", "https://exemplo.com/foto.jpg")
    assert not any(u.endswith("/media_publish") for u in urls)


def test_conferir_instagram_unificado(monkeypatch):
    urls = []

    def rede(metodo, url, **kw):
        urls.append(url)
        return Resp(200, {"username": "conta"})

    monkeypatch.setattr(robo, "_http", rede)
    assert "conta" in robo._conf_ig(CFG_IG_UNI)
    assert urls == ["https://graph.facebook.com/v27.0/1784000"]


def test_renovar_instagram_unificado_nao_chama_a_rede(pasta, monkeypatch, capsys):
    (pasta / "config.env").write_text(CONFIG + "INSTAGRAM_USER_ID=1784000\n", encoding="utf-8")
    assert robo.main(["renovar-instagram"]) == 0
    assert PROIBIDAS == []
    assert "não se renova" in capsys.readouterr().out


def test_ensaio_instagram_unificado_descreve_sem_chamar(pasta, capsys):
    (pasta / "config.env").write_text(CONFIG + "INSTAGRAM_USER_ID=1784000\n", encoding="utf-8")
    escrever_pauta(pasta, ["01/11/2026;09:00;instagram;t;Legenda;https://exemplo.com/foto.jpg;APROVADO;"])
    assert robo.main(["publicar-agora", "2", "--ensaio"]) == 0
    assert PROIBIDAS == []
    assert "graph.facebook.com" in capsys.readouterr().out


@pytest.mark.parametrize("estado, trecho", [("EXPIRED", "Nada foi publicado"), ("PUBLISHED", "já foi publicada"), ("IN_PROGRESS", "em processamento")])
def test_instagram_unificado_estados_sem_media_publish(monkeypatch, estado, trecho):
    urls = []

    def rede(metodo, url, **kw):
        urls.append(url)
        return Resp(200, {"id": "cont"} if url.endswith("/media") else {"status_code": estado})

    monkeypatch.setattr(robo, "_http", rede)
    monkeypatch.setattr(robo.time, "sleep", lambda s: None)
    with pytest.raises(robo.ErroRobo, match=trecho):
        robo.publicar_instagram(CFG_IG_UNI, "Legenda", "https://exemplo.com/foto.jpg")
    assert not any(u.endswith("/media_publish") for u in urls)
