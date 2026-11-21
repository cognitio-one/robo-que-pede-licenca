"""Correções após a revisão independente. Cada teste daqui falhava antes da correção.
Nenhum acessa a internet. A fixture 'pasta' e as simulações vêm de test_robo.py."""
import json
from datetime import datetime

import pytest

import robo
from test_robo import (  # noqa: F401  (pasta é fixture)
    HTTP_REAL, SEGREDO_FB, FalsaRede, Resp, escrever_pauta, estado, pasta,
)


def _tela_e_log(pasta, capsys):
    return capsys.readouterr().out, (pasta / "registro.log").read_text(encoding="utf-8")


# ---- duplicação após envio e falha local ----------------------------------
def test_post_saiu_mas_planilha_nao_gravou_nao_republica(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    original = robo.gravar_pauta
    contagem = {"n": 0}

    def falha_na_segunda(linhas):
        contagem["n"] += 1
        if contagem["n"] >= 2:  # a gravação de PUBLICADO (depois do envio) falha, como Excel aberto
            raise robo.ErroRobo("Excel aberto")
        original(linhas)

    monkeypatch.setattr(robo, "gravar_pauta", falha_na_segunda)
    robo.main(["publicar"])
    assert len(rede.chamadas) == 1
    assert estado(pasta)[2][0] == "PUBLICANDO"  # nunca volta a APROVADO
    monkeypatch.setattr(robo, "gravar_pauta", original)
    rede.chamadas.clear()
    robo.main(["publicar"])
    assert robo.main(["publicar-agora", "2"]) == 1  # recusa e explica
    assert rede.chamadas == []
    tela, log = _tela_e_log(pasta, capsys)
    assert "ENVIADO no facebook: 999_111" in log  # o resultado não se perde


def test_sem_gravar_a_intencao_nao_envia(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)

    def sempre_falha(linhas):
        raise robo.ErroRobo("Excel aberto")

    monkeypatch.setattr(robo, "gravar_pauta", sempre_falha)
    robo.main(["publicar"])
    assert rede.chamadas == []
    assert estado(pasta)[2][0] == "APROVADO"


def test_queda_de_conexao_no_envio_vira_verificar_e_nao_repete(pasta, monkeypatch):
    import requests

    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    chamadas = []

    def cai(metodo, url, **kw):
        chamadas.append(url)
        raise requests.ConnectionError("caiu")

    monkeypatch.setattr(requests, "request", cai)
    monkeypatch.setattr(robo, "_http", HTTP_REAL)
    robo.main(["publicar"])
    assert estado(pasta)[2][0] == "VERIFICAR"
    robo.main(["publicar"])
    assert len(chamadas) == 1


def test_http_5xx_no_envio_vira_verificar(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(503, {}))
    robo.main(["publicar"])
    assert estado(pasta)[2][0] == "VERIFICAR"


def test_excecao_inesperada_no_envio_vira_verificar_sem_vazar(pasta, monkeypatch, capsys):
    escrever_pauta(
        pasta,
        ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;", "01/11/2026;09:00;facebook;t;Outro;;APROVADO;"],
    )

    def explode(rede, cfg, texto, imagem):
        raise RuntimeError("corpo externo com DESCONHECIDO-ZZZ-999")

    monkeypatch.setattr(robo, "publicar_na_rede", explode)
    robo.main(["publicar"])
    est = estado(pasta)
    assert est[2][0] == "VERIFICAR" and est[3][0] == "VERIFICAR"
    tela, log = _tela_e_log(pasta, capsys)
    assert "DESCONHECIDO-ZZZ-999" not in tela + log + est[2][1]


def test_duas_execucoes_ao_mesmo_tempo_sao_barradas(pasta, monkeypatch):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    (pasta / "robo.lock").write_text("pid 1")
    assert robo.main(["publicar"]) == 1
    assert robo.main(["publicar-agora", "2"]) == 1
    assert rede.chamadas == []
    (pasta / "robo.lock").unlink()
    assert robo.main(["publicar"]) == 0
    assert len(rede.chamadas) == 1
    assert not (pasta / "robo.lock").exists()  # solta a trava no fim


# ---- vazamento de segredos -------------------------------------------------
def test_segredo_curto_e_mascarado():
    robo.SEGREDOS.clear()
    robo.registrar_segredo("ab123")  # 5 caracteres: antes era ignorado
    assert "ab123" not in robo.mascarar("token ab123 aqui")


def test_corpo_de_erro_externo_nao_vaza_nem_pelo_truncamento(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    # o segredo conhecido fica perto do corte de 300 caracteres; antes aparecia pela metade
    corpo = {
        "error": {"message": "a" * 270 + SEGREDO_FB + " fim", "code": 100},
        "access_token": "DESCONHECIDO-TOKEN-777",
        "debug": "outro DESCONHECIDO-DEBUG-888",
    }
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(400, corpo))
    robo.main(["publicar"])
    tela, log = _tela_e_log(pasta, capsys)
    planilha = (pasta / "pauta.csv").read_text(encoding="utf-8-sig")
    for parte in ("FB-SEG", "DESCONHECIDO-TOKEN-777", "DESCONHECIDO-DEBUG-888"):
        assert parte not in tela and parte not in log and parte not in planilha
    assert "code=100" in log


def test_excecao_geral_nao_registra_texto_da_excecao(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])

    def quebra():
        raise RuntimeError("resposta externa SEGREDO-NAO-CADASTRADO-555")

    monkeypatch.setattr(robo, "ler_pauta", quebra)
    assert robo.main(["publicar"]) == 1
    tela, log = _tela_e_log(pasta, capsys)
    assert "SEGREDO-NAO-CADASTRADO-555" not in tela + log
    assert "RuntimeError" in log


# ---- X: refresh token de uso único -----------------------------------------
def _x_com_token_vencido(pasta):
    (pasta / "x-tokens.json").write_text(
        json.dumps({"access_token": "VELHO-ACESSO-123456", "refresh_token": "VELHO-REFRESH-123456", "expires_at": 0}),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "resposta",
    [
        {"access_token": "NOVO-ACESSO-123456", "refresh_token": "NOVO-REFRESH-123456", "expires_in": "abc"},
        {"refresh_token": "NOVO-REFRESH-123456", "expires_in": 7200},  # sem access_token
    ],
)
def test_x_grava_o_novo_refresh_antes_de_converter_qualquer_campo(pasta, monkeypatch, resposta):
    _x_com_token_vencido(pasta)
    escrever_pauta(pasta, ["01/11/2026;09:00;x;t;Post curto;;APROVADO;"])

    def rede(m, u, **k):
        return Resp(200, resposta) if u.endswith("/oauth2/token") else Resp(201, {"data": {"id": "1"}})

    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["publicar"])
    tokens = json.loads((pasta / "x-tokens.json").read_text(encoding="utf-8"))
    assert tokens["refresh_token"] == "NOVO-REFRESH-123456"  # antes: erro e o token novo se perdia


# ---- conferir só lê ----------------------------------------------------------
def test_conferir_nao_renova_o_token_do_x(pasta, monkeypatch, capsys):
    _x_com_token_vencido(pasta)
    antes = (pasta / "x-tokens.json").read_bytes()
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    robo.main(["conferir"])
    assert not any(u.endswith("/oauth2/token") for _, u, _ in rede.chamadas)
    assert all(m == "GET" for m, _, _ in rede.chamadas)  # só leitura
    assert (pasta / "x-tokens.json").read_bytes() == antes
    assert "conferir não renova" in capsys.readouterr().out


# ---- Instagram: renovação -----------------------------------------------------
def test_renovar_instagram_grava_token_novo_e_validade(pasta, monkeypatch, capsys):
    chamadas = []

    def rede(metodo, url, **kw):
        chamadas.append((metodo, url, kw))
        return Resp(200, {"access_token": "IG-NOVO-TOKEN-999", "token_type": "bearer", "expires_in": 5184000})

    monkeypatch.setattr(robo, "_http", rede)
    assert robo.main(["renovar-instagram"]) == 0
    metodo, url, kw = chamadas[0]
    assert metodo == "GET" and url == "https://graph.instagram.com/refresh_access_token"
    assert kw["params"] == {"grant_type": "ig_refresh_token", "access_token": "IG-SEGREDO-123456"}
    config = (pasta / "config.env").read_text(encoding="utf-8")
    assert "INSTAGRAM_TOKEN=IG-NOVO-TOKEN-999" in config and "FACEBOOK_PAGE_ID=999" in config
    validade = json.loads((pasta / "instagram-validade.json").read_text(encoding="utf-8"))
    assert validade["expira_em"].startswith("2027-01-19")  # 20/11/2026 + 60 dias
    tela, log = _tela_e_log(pasta, capsys)
    assert "IG-NOVO-TOKEN-999" not in tela + log and "IG-SEGREDO-123456" not in tela + log


def test_renovar_instagram_token_vencido_da_mensagem_em_portugues(pasta, monkeypatch, capsys):
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(400, {"error": {"code": 190, "message": "expired"}}))
    assert robo.main(["renovar-instagram"]) == 1
    assert "INSTAGRAM_TOKEN" in capsys.readouterr().out
    assert "INSTAGRAM_TOKEN=IG-SEGREDO-123456" in (pasta / "config.env").read_text(encoding="utf-8")


def test_conferir_mostra_validade_do_instagram(pasta, monkeypatch, capsys):
    (pasta / "instagram-validade.json").write_text(
        json.dumps({"expira_em": datetime(2026, 11, 25).isoformat()}), encoding="utf-8"
    )
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(200, {"username": "u"}))
    robo.main(["conferir"])
    assert "vence em 4 dia(s)" in capsys.readouterr().out


# ---- terceira rodada ------------------------------------------------------------
def test_escrever_usa_a_trava_e_nao_restaura_status_de_publicar_concorrente(pasta, monkeypatch):
    escrever_pauta(
        pasta,
        ["01/11/2026;09:00;facebook;Prazos;;;;", "01/11/2026;09:00;facebook;t;Texto;;APROVADO;"],
    )
    rede = FalsaRede()
    monkeypatch.setattr(robo, "_http", rede)
    resultados = {}

    def ia(cfg, sistema, pedido):
        # um "publicar" concorrente chega enquanto o escrever espera a IA
        resultados["publicar"] = robo.main(["publicar"])
        return "Post da IA"

    monkeypatch.setattr(robo, "chamar_ia", ia)
    assert robo.main(["escrever"]) == 0
    assert resultados["publicar"] == 1  # barrado pela trava
    assert rede.chamadas == []
    assert not (pasta / "robo.lock").exists()
    assert estado(pasta)[3][0] == "APROVADO"
    robo.main(["publicar"])  # agora sim, uma única vez
    robo.main(["publicar"])
    assert len(rede.chamadas) == 1 and estado(pasta)[3][0] == "PUBLICADO"  # a linha 3 sai uma única vez


def test_erro_com_objeto_aninhado_e_aspas_simples_nao_vaza(pasta, monkeypatch, capsys):
    escrever_pauta(pasta, ["01/11/2026;09:00;facebook;t;Texto;;APROVADO;"])
    corpo = {"error": {"message": {"access_token": "ANINHADO-AAA-111", "x": {"client_secret": "ANINHADO-BBB-222"}}, "code": 1}}
    monkeypatch.setattr(robo, "_http", lambda *a, **k: Resp(400, corpo))
    robo.main(["publicar"])
    tela, log = _tela_e_log(pasta, capsys)
    planilha = (pasta / "pauta.csv").read_text(encoding="utf-8-sig")
    for parte in ("ANINHADO-AAA-111", "ANINHADO-BBB-222"):
        assert parte not in tela + log + planilha


def test_mascarar_aspas_simples():
    robo.SEGREDOS.clear()
    assert "XYZ-999" not in robo.mascarar("{'access_token': 'XYZ-999', 'refresh_token':'XYZ-999'}")
