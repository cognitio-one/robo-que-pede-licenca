#!/usr/bin/env python3
"""Robo de publicacao em redes sociais.

Comandos:
  python robo.py escrever [--ensaio]
  python robo.py publicar [--ensaio]
  python robo.py publicar-agora <numero da linha> [--ensaio]
  python robo.py conferir [--ensaio]
  python robo.py autorizar-x [--ensaio]
  python robo.py renovar-instagram [--ensaio]

Veja o LEIA-ME.txt. Tudo o que o robo faz vai para registro.log.
"""
import argparse
import base64
import csv
import hashlib
import json
import os
import re
import secrets
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

PASTA = Path(__file__).resolve().parent  # os testes trocam este valor

COLUNAS = ["data", "hora", "rede", "tema", "texto", "imagem", "status", "resultado"]
REDES = ["linkedin", "facebook", "instagram", "x"]
LIMITES = {"linkedin": 3000, "facebook": 63000, "instagram": 2200, "x": 280}
MODELOS_PADRAO = {"claude": "claude-sonnet-5-5", "openai": "gpt-6.2-sol"}

FB_VERSAO = "v27.0"
IG_VERSAO = "v27.0"
LI_VERSAO = "202611"
X_TOKEN_URL = "https://api.x.com/2/oauth2/token"
X_CALLBACK = "http://127.0.0.1:8080/callback"

SEGREDOS = set()  # valores que nunca podem aparecer na tela nem no registro


class ErroRobo(Exception):
    """Erro com mensagem em portugues dizendo o que fazer."""


class ErroIncerto(ErroRobo):
    """O pedido de envio pode ter sido aceito pela rede (queda de conexao, HTTP 5xx).
    Nunca se tenta de novo sozinho: a linha fica VERIFICAR."""


# --------------------------------------------------------------------------
# Utilidades: caminhos, hora, segredos, registro
# --------------------------------------------------------------------------
def caminho(nome):
    return Path(PASTA) / nome


def agora():
    return datetime.now()


def registrar_segredo(valor):
    """Qualquer valor nao vazio, de qualquer tamanho, passa a ser escondido."""
    if isinstance(valor, str) and valor.strip():
        valor = valor.strip()
        SEGREDOS.add(valor)
        SEGREDOS.add(quote(valor, safe=""))


def mascarar(texto):
    texto = str(texto)
    for s in sorted(SEGREDOS, key=len, reverse=True):
        texto = texto.replace(s, "***")
    texto = re.sub(r"(?i)(bearer|basic)\s+[A-Za-z0-9._~+/=-]+", r"\1 ***", texto)
    texto = re.sub(
        r"(?i)([\"']?(?:access_token|refresh_token|client_secret|code_verifier|id_token|api_key|x-api-key)[\"']?\s*[:=]\s*)"
        r"(\"[^\"]*\"|'[^']*'|[^&\s,\"'}]+)",
        r"\1***",
        texto,
    )
    texto = re.sub(r"\bsk-[A-Za-z0-9_-]{16,}", "***", texto)
    return texto


def descrever_excecao(e):
    """Tipo e lugar da excecao, nunca o texto dela (pode trazer corpo de resposta externa)."""
    onde = ""
    tb = traceback.extract_tb(e.__traceback__)
    if tb:
        onde = f" em {Path(tb[-1].filename).name}:{tb[-1].lineno}"
    return f"{type(e).__name__}{onde}"


def registrar(msg):
    linha = f"{agora().strftime('%d/%m/%Y %H:%M:%S')} {mascarar(msg)}\n"
    try:
        with open(caminho("registro.log"), "a", encoding="utf-8") as f:
            f.write(linha)
    except OSError:
        pass


def dizer(msg=""):
    """Mostra na tela e grava no registro, sempre sem chaves."""
    msg = mascarar(msg)
    print(msg)
    registrar(msg.replace("\n", " | "))


# --------------------------------------------------------------------------
# Configuracao (config.env)
# --------------------------------------------------------------------------
def preenchido(valor):
    v = (valor or "").strip()
    return bool(v) and not v.lower().startswith(("cole-", "cole_", "exemplo", "xxx"))


def carregar_config():
    arq = caminho("config.env")
    if not arq.exists():
        raise ErroRobo(
            "Não achei o arquivo config.env. Copie config.exemplo.env para config.env "
            "e preencha com as suas chaves."
        )
    cfg = {}
    for bruta in arq.read_text(encoding="utf-8-sig").splitlines():
        linha = bruta.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        cfg[nome.strip()] = valor
    for nome, valor in cfg.items():
        if preenchido(valor) and re.search(r"TOKEN|KEY|SECRET", nome.upper()):
            registrar_segredo(valor)
    return cfg


def escolha_ia(cfg):
    ia = (cfg.get("IA") or "claude").strip().lower()
    if ia not in ("claude", "openai"):
        raise ErroRobo("No config.env, IA deve ser claude ou openai.")
    modelo = (cfg.get("IA_MODELO") or "").strip()
    if not preenchido(modelo):
        modelo = MODELOS_PADRAO[ia]
    return ia, modelo


def exigir(cfg, nome, onde):
    v = cfg.get(nome, "")
    if not preenchido(v):
        raise ErroRobo(f"Falta preencher {nome} no config.env. {onde}")
    return v.strip()


# --------------------------------------------------------------------------
# Planilha pauta.csv (UTF-8 com BOM, separador ponto e virgula)
# --------------------------------------------------------------------------
def ler_pauta():
    arq = caminho("pauta.csv")
    if not arq.exists():
        raise ErroRobo("Não achei pauta.csv nesta pasta. Crie a planilha com as colunas: " + ";".join(COLUNAS))
    bruto = arq.read_bytes()
    try:
        texto = bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Excel "CSV (separado por vírgulas)" antigo salva em cp1252
        texto = bruto.decode("cp1252")
    import io

    leitor = csv.reader(io.StringIO(texto, newline=""), delimiter=";")
    linhas = list(leitor)
    if not linhas:
        raise ErroRobo("pauta.csv está vazio. A primeira linha deve ser: " + ";".join(COLUNAS))
    cab = [c.strip().lower() for c in linhas[0]]
    if cab != COLUNAS:
        raise ErroRobo(
            "A primeira linha de pauta.csv deve ser exatamente: " + ";".join(COLUNAS)
            + ". Ao salvar no Excel, escolha 'CSV UTF-8 (delimitado por vírgulas)'."
        )
    saida = []
    for i, campos in enumerate(linhas[1:], start=2):
        if not any(c.strip() for c in campos):
            continue
        campos = (campos + [""] * len(COLUNAS))[: len(COLUNAS)]
        d = {c: v for c, v in zip(COLUNAS, campos)}
        d["_linha"] = i
        saida.append(d)
    return saida


def gravar_pauta(linhas):
    """Grava de forma atômica: escreve um arquivo temporário e troca."""
    arq = caminho("pauta.csv")
    tmp = caminho("pauta.csv.tmp")
    # mantém as linhas em branco originais: grava por número de linha
    por_linha = {d["_linha"]: d for d in linhas}
    ultimo = max(por_linha) if por_linha else 1
    try:
        with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";", lineterminator="\r\n")
            w.writerow(COLUNAS)
            for n in range(2, ultimo + 1):
                d = por_linha.get(n)
                w.writerow([d[c] for c in COLUNAS] if d else [""] * len(COLUNAS))
        os.replace(tmp, arq)
    except OSError:
        raise ErroRobo("Não consegui gravar pauta.csv. Feche o Excel (o arquivo está aberto) e rode de novo.")


def parse_data_hora(d):
    try:
        return datetime.strptime(f"{d['data'].strip()} {d['hora'].strip()}", "%d/%m/%Y %H:%M")
    except ValueError:
        raise ErroRobo(
            f"Linha {d['_linha']}: data/hora inválida ('{d['data']}' '{d['hora']}'). "
            "Use dd/mm/aaaa e hh:mm."
        )


def status_de(d):
    return d["status"].strip().upper()


# --------------------------------------------------------------------------
# Rede (uma única porta, fácil de simular nos testes)
# --------------------------------------------------------------------------
def _http(metodo, url, **kw):
    import requests

    kw.setdefault("timeout", 30)
    try:
        return requests.request(metodo, url, **kw)
    except requests.RequestException:
        msg = f"Não consegui falar com {url.split('?')[0]}. Verifique a internet e tente de novo."
        base = url.split("?")[0]
        if metodo.upper() == "POST" and not base.endswith("/oauth2/token"):
            raise ErroIncerto(msg + " Se era um envio, ele pode ter saído: confira na rede antes de repetir.") from None
        raise ErroRobo(msg) from None


def _corpo(resp):
    try:
        return resp.json()
    except Exception:
        return {}


MSG_TOKEN = {
    "linkedin": "o token do LinkedIn venceu ou é inválido; gere outro no Token Generator "
    "(https://www.linkedin.com/developers/tools/oauth/token-generator) e cole em LINKEDIN_TOKEN no config.env.",
    "facebook": "o token da Página do Facebook venceu ou é inválido; gere outro no Explorador da Graph API "
    "e cole em FACEBOOK_PAGE_TOKEN no config.env.",
    "instagram": "o token do Instagram venceu ou é inválido; gere outro no painel do app "
    "e cole em INSTAGRAM_TOKEN no config.env.",
    "x": "o X recusou a autorização; rode 'python robo.py autorizar-x' para autorizar de novo.",
}


CAMPOS_ERRO = ("type", "code", "error_subcode", "message")
CAMPOS_ERRO_RAIZ = ("error_description", "detail", "title", "message", "status", "erro")


CHAVES_SENSIVEIS = ("token", "secret", "key", "verifier", "password", "senha", "authorization")


def _limpar_aninhado(v, fundo=0):
    """Troca por *** o valor de qualquer campo sensivel, em qualquer nivel, antes de virar texto."""
    if fundo > 6:
        return "***"
    if isinstance(v, dict):
        return {
            k: "***" if any(c in str(k).lower() for c in CHAVES_SENSIVEIS) else _limpar_aninhado(x, fundo + 1)
            for k, x in v.items()
        }
    if isinstance(v, (list, tuple)):
        return [_limpar_aninhado(x, fundo + 1) for x in v]
    return v


def _como_texto(v):
    v = _limpar_aninhado(v)
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)


def _resumo_erro(corpo):
    """So campos conhecidos de erro, nunca o corpo bruto; mascara ANTES de truncar."""
    partes = []
    if isinstance(corpo, dict):
        e = corpo.get("error")
        if isinstance(e, dict):
            partes += [f"{k}={_como_texto(e[k])}" for k in CAMPOS_ERRO if e.get(k) not in (None, "")]
        elif isinstance(e, (str, int)) and e != "":
            partes.append(f"error={e}")
        partes += [f"{k}={_como_texto(corpo[k])}" for k in CAMPOS_ERRO_RAIZ if corpo.get(k) not in (None, "")]
    return mascarar("; ".join(partes) or "(sem detalhe)")[:300]


def _checar(rede, resp, aceitos=(200, 201)):
    if resp.status_code in aceitos:
        return
    corpo = _corpo(resp)
    codigo = ""
    if isinstance(corpo, dict) and isinstance(corpo.get("error"), dict):
        codigo = corpo["error"].get("code")
    if resp.status_code in (401, 403) or codigo == 190:
        raise ErroRobo(f"{rede.upper()}: {MSG_TOKEN[rede]}")
    msg = f"{rede.upper()} recusou o pedido (HTTP {resp.status_code}): {_resumo_erro(corpo)}"
    if resp.status_code >= 500:
        raise ErroIncerto(msg + " (erro do servidor: o envio pode ter saído; confira na rede antes de repetir)")
    raise ErroRobo(msg)


def _eh_url(s):
    return s.strip().lower().startswith(("http://", "https://"))


def tamanho_x(texto):
    return len(re.sub(r"https?://\S+", "x" * 23, texto))


def checar_tamanho(rede, texto):
    n = tamanho_x(texto) if rede == "x" else len(texto)
    if n > LIMITES[rede]:
        raise ErroRobo(
            f"O texto tem {n} caracteres e o limite do {rede} é {LIMITES[rede]}. Encurte no Excel."
        )


# ---- LinkedIn
def linkedin_autor(cfg):
    token = exigir(cfg, "LINKEDIN_TOKEN", "Gere no Token Generator do LinkedIn.")
    r = _http("GET", "https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {token}"})
    _checar("linkedin", r)
    sub = _corpo(r).get("sub")
    if not sub:
        raise ErroRobo("LINKEDIN: a resposta não trouxe o seu identificador (sub). Gere o token com os escopos openid e profile.")
    return f"urn:li:person:{sub}"


def publicar_linkedin(cfg, texto, imagem):
    token = exigir(cfg, "LINKEDIN_TOKEN", "Gere no Token Generator do LinkedIn.")
    if imagem.strip():
        dizer("Aviso: o robô ainda não envia imagem no LinkedIn; saiu só o texto.")
    autor = linkedin_autor(cfg)
    corpo = {
        "author": autor,
        "commentary": texto,
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    r = _http(
        "POST",
        "https://api.linkedin.com/rest/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Linkedin-Version": LI_VERSAO,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        json=corpo,
    )
    _checar("linkedin", r, aceitos=(201,))
    return r.headers.get("x-restli-id", "(publicado; o LinkedIn não devolveu o identificador)")


# ---- Facebook
def publicar_facebook(cfg, texto, imagem):
    pagina = exigir(cfg, "FACEBOOK_PAGE_ID", "Veja /me/accounts no Explorador da Graph API.")
    token = exigir(cfg, "FACEBOOK_PAGE_TOKEN", "Gere no Explorador da Graph API.")
    base = f"https://graph.facebook.com/{FB_VERSAO}/{pagina}"
    imagem = imagem.strip()
    if imagem and _eh_url(imagem):
        r = _http("POST", base + "/photos", data={"url": imagem, "caption": texto, "access_token": token})
    elif imagem:
        arq = caminho(imagem) if not Path(imagem).is_absolute() else Path(imagem)
        if not arq.exists():
            raise ErroRobo(f"Não achei a imagem '{imagem}'. Confira o nome na coluna imagem.")
        with open(arq, "rb") as f:
            r = _http("POST", base + "/photos", data={"caption": texto, "access_token": token}, files={"source": f})
    else:
        r = _http("POST", base + "/feed", data={"message": texto, "access_token": token})
    _checar("facebook", r)
    c = _corpo(r)
    return str(c.get("post_id") or c.get("id") or "(publicado; sem identificador)")


# ---- Instagram
def ig_unificado(cfg):
    """Apps novos da Meta usam o login unificado: token do painel + INSTAGRAM_USER_ID, host graph.facebook.com."""
    return preenchido(cfg.get("INSTAGRAM_USER_ID"))


def ig_esperar_container(url_container, token, tentativas=6, primeira=5, intervalo=60):
    """Só publica quando o container da imagem está pronto (status FINISHED); senão, não publica nada."""
    time.sleep(primeira)  # imagem costuma ficar pronta em segundos
    for vez in range(tentativas):
        r = _http("GET", url_container, params={"fields": "status_code", "access_token": token})
        _checar("instagram", r)
        estado = _corpo(r).get("status_code")
        if estado == "FINISHED":
            return
        if estado in ("ERROR", "EXPIRED"):
            raise ErroRobo("INSTAGRAM: a rede recusou a imagem (JPEG público, proporção entre 4:5 e 1,91:1). Nada foi publicado.")
        if estado == "PUBLISHED":
            raise ErroRobo("INSTAGRAM: a rede informa que esta imagem já foi publicada. Confira o perfil no Instagram antes de "
                           "aprovar a linha de novo, para não publicar duas vezes.")
        if vez + 1 < tentativas:
            time.sleep(intervalo)  # a Meta recomenda consultar uma vez por minuto, por até 5 minutos
    raise ErroRobo("INSTAGRAM: a imagem ainda está em processamento. Nada foi publicado; tente de novo em alguns minutos.")


def publicar_instagram(cfg, texto, imagem):
    token = exigir(cfg, "INSTAGRAM_TOKEN", "Gere o token no painel do app do Instagram.")
    imagem = imagem.strip()
    if not imagem or not _eh_url(imagem):
        raise ErroRobo("O Instagram exige imagem: coloque na coluna imagem o endereço público (https://...) de uma foto JPEG.")
    if not re.search(r"\.jpe?g$", imagem.split("?")[0], re.I):
        raise ErroRobo("O Instagram só aceita imagem JPEG pela API: o endereço da imagem deve terminar em .jpg ou .jpeg.")
    if ig_unificado(cfg):
        # apps novos da Meta (login unificado): número da conta no config e host graph.facebook.com
        base = f"https://graph.facebook.com/{IG_VERSAO}"
        ig_id = cfg["INSTAGRAM_USER_ID"].strip()
    else:
        base = f"https://graph.instagram.com/{IG_VERSAO}"
        r = _http("GET", f"{base}/me", params={"fields": "user_id,username", "access_token": token})
        _checar("instagram", r)
        c = _corpo(r)
        ig_id = c.get("user_id") or c.get("id")
        if not ig_id:
            raise ErroRobo("INSTAGRAM: não consegui descobrir o id da conta. Confira o token e as permissões.")
    r = _http("POST", f"{base}/{ig_id}/media", data={"image_url": imagem, "caption": texto, "access_token": token})
    _checar("instagram", r)
    criacao = _corpo(r).get("id")
    if not criacao:
        raise ErroRobo("INSTAGRAM: a rede não devolveu o id da mídia criada.")
    if ig_unificado(cfg):
        ig_esperar_container(f"{base}/{criacao}", token)
    r = _http("POST", f"{base}/{ig_id}/media_publish", data={"creation_id": criacao, "access_token": token})
    _checar("instagram", r)
    return str(_corpo(r).get("id", "(publicado; sem identificador)"))


IG_REFRESH_URL = "https://graph.instagram.com/refresh_access_token"


def _ig_aviso_validade():
    """Lê só o arquivo local (sem rede): quantos dias faltam, segundo a última renovação."""
    try:
        exp = datetime.fromisoformat(json.loads(caminho("instagram-validade.json").read_text(encoding="utf-8"))["expira_em"])
    except (OSError, ValueError, KeyError, TypeError):
        return "; validade do token desconhecida (rode: python robo.py renovar-instagram)"
    dias = (exp - agora()).days
    if dias < 0:
        return "; ATENÇÃO: o token venceu (gere outro no painel do app e cole no config.env)"
    if dias <= 10:
        return f"; ATENÇÃO: o token vence em {dias} dia(s); rode: python robo.py renovar-instagram"
    return f"; token vale por mais {dias} dia(s)"


def _ig_gravar_token(novo):
    arq = caminho("config.env")
    tmp = caminho("config.env.tmp")
    texto = arq.read_bytes().decode("utf-8")
    texto2, n = re.subn(r"(?m)^(\s*INSTAGRAM_TOKEN\s*=)[^\r\n]*", lambda m: m.group(1) + novo, texto)
    if n == 0:
        raise ErroRobo("Não achei a linha INSTAGRAM_TOKEN no config.env.")
    tmp.write_bytes(texto2.encode("utf-8"))
    os.replace(tmp, arq)


def cmd_renovar_instagram(ensaio):
    """GET refresh_access_token (ficha técnica). Grava o token NA HORA, antes de ler a validade."""
    if ig_unificado(carregar_config()):
        dizer("Instagram: com INSTAGRAM_USER_ID preenchido (login unificado), o token vem do painel do app e não se renova "
              "por aqui. Se ele parar de funcionar, gere outro no painel (Casos de uso > API do Instagram > Gerar token).")
        return 0
    if ensaio:
        dizer(
            f"[ENSAIO] Faria GET {IG_REFRESH_URL}?grant_type=ig_refresh_token (com o INSTAGRAM_TOKEN do config.env) "
            "e gravaria o token devolvido no config.env e a validade em instagram-validade.json. Não fiz."
        )
        return 0
    cfg = carregar_config()
    token = exigir(cfg, "INSTAGRAM_TOKEN", "Gere o token no painel do app do Instagram.")
    r = _http("GET", IG_REFRESH_URL, params={"grant_type": "ig_refresh_token", "access_token": token})
    _checar("instagram", r)
    c = _corpo(r)
    novo = c.get("access_token") if isinstance(c, dict) else None
    if not isinstance(novo, str) or not novo.strip():
        raise ErroRobo("INSTAGRAM: a renovação não devolveu o token. Gere outro no painel do app e cole no config.env.")
    registrar_segredo(novo)
    if novo != token:
        try:
            _ig_gravar_token(novo)
        except OSError:
            raise ErroRobo("INSTAGRAM: renovou, mas não consegui gravar o config.env. Feche o programa que o usa e gere outro token no painel.") from None
    try:
        segundos = int(c.get("expires_in"))
    except (TypeError, ValueError):
        segundos = None
    if segundos:
        expira = agora() + timedelta(seconds=segundos)
        caminho("instagram-validade.json").write_text(
            json.dumps({"renovado_em": agora().isoformat(), "expira_em": expira.isoformat()}), encoding="utf-8"
        )
        dizer(f"Instagram: token renovado; vale até {expira.strftime('%d/%m/%Y')}. Renove de novo antes dessa data.")
    else:
        dizer("Instagram: token renovado, mas a rede não informou a validade. Renove de novo em até 50 dias.")
    return 0


# ---- X
def _x_salvar(tokens):
    arq = caminho("x-tokens.json")
    tmp = caminho("x-tokens.json.tmp")
    for k in ("access_token", "refresh_token"):
        registrar_segredo(tokens.get(k))
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(tokens, indent=2))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, arq)
    except OSError:
        raise ErroRobo(
            "ATENÇÃO: não consegui gravar x-tokens.json (o X já trocou o refresh token, que é de uso único). "
            "Libere a pasta e rode: python robo.py autorizar-x"
        ) from None


def _x_ler():
    arq = caminho("x-tokens.json")
    if not arq.exists():
        raise ErroRobo("O X ainda não foi autorizado. Rode: python robo.py autorizar-x")
    try:
        tokens = json.loads(arq.read_text(encoding="utf-8"))
        if not isinstance(tokens, dict):
            raise ValueError
    except ValueError:
        raise ErroRobo("O arquivo x-tokens.json está ilegível. Rode de novo: python robo.py autorizar-x") from None
    for k in ("access_token", "refresh_token"):
        registrar_segredo(tokens.get(k))
    return tokens


def _x_pedir_token(cfg, form):
    """Pede token ao X e GRAVA o que chegou antes de qualquer conversão ou validação:
    o refresh token é de uso único, perdê-lo exige autorizar de novo."""
    client_id = exigir(cfg, "X_CLIENT_ID", "Pegue no console.x.com, no seu app.")
    form = dict(form, client_id=client_id)
    kw = {"data": form, "headers": {"Content-Type": "application/x-www-form-urlencoded"}}
    segredo = cfg.get("X_CLIENT_SECRET", "")
    if preenchido(segredo):
        cred = base64.b64encode(f"{client_id}:{segredo}".encode()).decode()
        kw["headers"]["Authorization"] = f"Basic {cred}"
    r = _http("POST", X_TOKEN_URL, **kw)
    if r.status_code != 200:
        raise ErroRobo(
            "O X não aceitou o pedido de token (o código de autorização ou o refresh token já foi usado ou venceu). "
            "Rode de novo: python robo.py autorizar-x"
        )
    c = _corpo(r)
    if not isinstance(c, dict):
        c = {}
    tokens = {
        "access_token": str(c.get("access_token") or ""),
        "refresh_token": str(c.get("refresh_token") or form.get("refresh_token", "")),
        "expires_at": 0,
    }
    _x_salvar(tokens)  # na hora, antes de converter expires_in ou checar o resto
    try:
        tokens["expires_at"] = time.time() + int(c.get("expires_in", 7200))
    except (TypeError, ValueError):
        tokens["expires_at"] = 0  # validade ilegível: renova na próxima vez
    if not tokens["access_token"]:
        raise ErroRobo("O X respondeu sem token de acesso. Rode de novo: python robo.py autorizar-x")
    _x_salvar(tokens)
    return tokens


def x_renovar(cfg):
    antigo = _x_ler()
    novo = _x_pedir_token(cfg, {"grant_type": "refresh_token", "refresh_token": antigo.get("refresh_token", "")})
    registrar("X: token renovado e novo refresh token gravado em x-tokens.json")
    return novo


def x_token_valido(cfg, forcar=False, renovar=True):
    """Com renovar=False nunca chama o X: devolve None se o token de acesso já venceu."""
    t = _x_ler()
    if forcar or t.get("expires_at", 0) - 60 <= time.time():
        if not renovar:
            return None
        t = x_renovar(cfg)
    return t["access_token"]


def publicar_x(cfg, texto, imagem):
    if imagem.strip():
        dizer("Aviso: o robô ainda não envia imagem no X; saiu só o texto.")
    for tentativa in (0, 1):
        token = x_token_valido(cfg, forcar=bool(tentativa))
        r = _http(
            "POST",
            "https://api.x.com/2/tweets",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"text": texto},
        )
        if r.status_code == 401 and tentativa == 0:
            continue
        _checar("x", r, aceitos=(201,))
        break
    id_ = _corpo(r).get("data", {}).get("id", "")
    return f"https://x.com/i/web/status/{id_}" if id_ else "(publicado; sem identificador)"


def publicar_na_rede(rede, cfg, texto, imagem):
    f = {"linkedin": publicar_linkedin, "facebook": publicar_facebook, "instagram": publicar_instagram, "x": publicar_x}[rede]
    return f(cfg, texto, imagem)


def descrever_envio(rede, texto, imagem):
    img = imagem.strip()
    if rede == "linkedin":
        alvo = "POST https://api.linkedin.com/rest/posts (visibilidade PUBLIC)"
    elif rede == "facebook":
        alvo = f"POST https://graph.facebook.com/{FB_VERSAO}/<PAGE_ID>/" + ("photos" if img else "feed")
    elif rede == "instagram":
        alvo = (f"POST .../{IG_VERSAO}/<id da conta>/media e depois /media_publish "
                "(graph.facebook.com se INSTAGRAM_USER_ID estiver preenchido; graph.instagram.com no modo antigo)")
    else:
        alvo = "POST https://api.x.com/2/tweets"
    s = f"  rede: {rede.upper()}\n  chamada: {alvo}\n  imagem: {img or '(nenhuma)'}\n  texto ({len(texto)} caracteres):\n"
    return s + "\n".join("    | " + l for l in texto.splitlines() or [""])


# --------------------------------------------------------------------------
# Inteligência artificial
# --------------------------------------------------------------------------
def chamar_ia(cfg, sistema, pedido):
    ia, modelo = escolha_ia(cfg)
    if ia == "claude":
        chave = exigir(cfg, "ANTHROPIC_API_KEY", "Crie a chave em console.anthropic.com.")
        try:
            import anthropic
        except ImportError:
            raise ErroRobo("A biblioteca 'anthropic' não está instalada. Rode: python -m pip install anthropic")
        cli = anthropic.Anthropic(api_key=chave)
        r = cli.messages.create(
            model=modelo, max_tokens=1500, system=sistema, messages=[{"role": "user", "content": pedido}]
        )
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
    chave = exigir(cfg, "OPENAI_API_KEY", "Crie a chave em platform.openai.com.")
    try:
        import openai
    except ImportError:
        raise ErroRobo("A biblioteca 'openai' não está instalada. Rode: python -m pip install openai")
    cli = openai.OpenAI(api_key=chave)
    r = cli.responses.create(model=modelo, input=f"{sistema}\n\n{pedido}")
    return r.output_text.strip()


def montar_pedido(d):
    rede = d["rede"].strip().lower()
    lim = LIMITES.get(rede, 3000)
    return (
        f"Escreva um post para {rede} sobre o tema: {d['tema'].strip()}\n"
        f"O texto deve ter no máximo {lim} caracteres. "
        "Responda apenas com o texto do post, sem aspas e sem comentários seus."
    )


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------
def cmd_escrever(ensaio):
    """Quem grava a pauta usa a mesma trava do publicar durante TODO o ciclo (ler, esperar a IA, gravar)."""
    if ensaio:
        return _escrever(ensaio)
    with trava_de_execucao():
        return _escrever(ensaio)


def _escrever(ensaio):
    linhas = ler_pauta()
    arq_perfil = caminho("perfil.txt")
    if not arq_perfil.exists():
        raise ErroRobo("Não achei perfil.txt. Crie esse arquivo com o seu estilo e as suas regras de escrita.")
    perfil = arq_perfil.read_text(encoding="utf-8-sig")
    cfg = carregar_config() if not ensaio else _config_ou_vazia()
    alvos = [d for d in linhas if d["tema"].strip() and not d["texto"].strip()]
    if not alvos:
        dizer("Nenhuma linha com tema e sem texto. Nada a escrever.")
        return 0
    for d in alvos:
        n = d["_linha"]
        rede = d["rede"].strip().lower()
        if rede not in REDES:
            dizer(f"Linha {n}: rede '{d['rede']}' inválida (use linkedin, facebook, instagram ou x). Pulei.")
            continue
        if status_de(d) not in ("", "RASCUNHO"):
            dizer(f"Linha {n}: status {d['status']} não é vazio nem RASCUNHO. Pulei.")
            continue
        pedido = montar_pedido(d)
        if ensaio:
            dizer(f"[ENSAIO] Linha {n}: pediria à IA ({escolha_ia(cfg)[0]}) este texto, junto com o perfil.txt:\n  {pedido}")
            continue
        try:
            texto = chamar_ia(cfg, perfil, pedido)
        except ErroRobo as e:
            dizer(f"Linha {n}: {e}")
            continue
        except Exception as e:  # erro da biblioteca da IA
            dizer(f"Linha {n}: a IA não respondeu ({type(e).__name__}). Confira a chave e a internet e tente de novo.")
            registrar(f"detalhe do erro da IA: {descrever_excecao(e)}")
            continue
        if not texto:
            dizer(f"Linha {n}: a IA devolveu texto vazio. Tente de novo.")
            continue
        d["texto"], d["status"] = texto, "RASCUNHO"
        gravar_pauta(linhas)
        dizer(f"Linha {n}: rascunho escrito ({len(texto)} caracteres). Leia no Excel e troque o status para APROVADO.")
        try:
            checar_tamanho(rede, texto)
        except ErroRobo as e:
            dizer(f"Atenção na linha {n}: {e}")
    return 0


def _config_ou_vazia():
    try:
        return carregar_config()
    except ErroRobo:
        return {}


def _validar_linha(d):
    """Confere a linha antes de qualquer envio. Devolve (rede, texto)."""
    n = d["_linha"]
    rede = d["rede"].strip().lower()
    texto = d["texto"]
    if rede not in REDES:
        raise ErroRobo(f"rede '{d['rede']}' inválida (use linkedin, facebook, instagram ou x).")
    if not texto.strip():
        raise ErroRobo(f"está APROVADO mas sem texto. Escreva o texto no Excel.")
    checar_tamanho(rede, texto)
    return rede, texto


def _gravar_seguro(linhas, n):
    """Grava a planilha sem levantar erro; devolve True se gravou."""
    try:
        gravar_pauta(linhas)
        return True
    except ErroRobo as e:
        dizer(f"Linha {n}: {e}")
        return False


def _fechar_linha(linhas, d, status, resultado):
    d["status"], d["resultado"] = status, mascarar(resultado)[:300]
    _gravar_seguro(linhas, d["_linha"])


@contextmanager
def trava_de_execucao():
    """Impede duas execuções ao mesmo tempo (duplicaria posts). Fica robo.lock enquanto roda."""
    arq = caminho("robo.lock")
    try:
        fd = os.open(arq, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ErroRobo(
            "Já existe uma execução em andamento (arquivo robo.lock). Se tem certeza de que o robô não está "
            "rodando (por exemplo, o computador caiu), apague robo.lock e confira na pauta as linhas PUBLICANDO."
        ) from None
    except OSError:
        raise ErroRobo("Não consegui criar robo.lock nesta pasta. Verifique as permissões da pasta.") from None
    try:
        os.write(fd, f"pid {os.getpid()}\n".encode())
        os.close(fd)
        yield
    finally:
        try:
            os.unlink(arq)
        except OSError:
            pass


def _tentar_publicar(cfg, linhas, d, ensaio):
    """Fluxo à prova de duplicação: 1) grava PUBLICANDO na planilha; se não gravar, NÃO envia;
    2) envia; 3) grava PUBLICADO. Se 3 falhar, a linha segue PUBLICANDO (nunca volta a APROVADO)."""
    n = d["_linha"]
    try:
        rede, texto = _validar_linha(d)
    except ErroRobo as e:
        dizer(f"Linha {n}: {e}")
        if not ensaio:
            _fechar_linha(linhas, d, "ERRO", str(e))
            dizer(f"Linha {n}: marquei como ERRO. Corrija e troque o status para APROVADO.")
        return False
    if ensaio:
        dizer(f"[ENSAIO] Linha {n}: NÃO fiz nenhuma chamada. Mandaria isto:\n{descrever_envio(rede, texto, d['imagem'])}")
        return True

    original = (d["status"], d["resultado"])
    d["status"], d["resultado"] = "PUBLICANDO", f"envio iniciado em {agora().strftime('%d/%m/%Y %H:%M')}"
    if not _gravar_seguro(linhas, n):
        d["status"], d["resultado"] = original  # nada saiu
        dizer(f"Linha {n}: NÃO enviei, porque não consegui registrar na planilha que o envio ia começar.")
        return False
    try:
        resultado = publicar_na_rede(rede, cfg, texto, d["imagem"])
    except ErroIncerto as e:
        dizer(f"Linha {n}: {e}")
        _fechar_linha(linhas, d, "VERIFICAR", f"resultado incerto, confira na rede: {e}")
        dizer(f"Linha {n}: marquei como VERIFICAR. Confira na rede; se NÃO saiu, troque para APROVADO.")
        return False
    except ErroRobo as e:
        dizer(f"Linha {n}: {e}")
        _fechar_linha(linhas, d, "ERRO", str(e))
        dizer(f"Linha {n}: marquei como ERRO. Corrija e troque o status para APROVADO.")
        return False
    except Exception as e:
        registrar(f"Linha {n}: falha inesperada durante o envio: {descrever_excecao(e)}")
        _fechar_linha(linhas, d, "VERIFICAR", f"falha inesperada ({type(e).__name__}); confira na rede")
        dizer(f"Linha {n}: falha inesperada; marquei como VERIFICAR. Confira na rede; se NÃO saiu, troque para APROVADO.")
        return False
    registrar(f"Linha {n}: ENVIADO no {rede}: {resultado}")  # fica no registro mesmo se a planilha falhar
    d["status"], d["resultado"] = "PUBLICADO", resultado
    if _gravar_seguro(linhas, n):
        dizer(f"Linha {n}: PUBLICADO no {rede} -> {d['resultado']}")
    else:
        d["status"] = "PUBLICANDO"
        dizer(
            f"Linha {n}: o post SAIU no {rede} -> {resultado}, mas não consegui gravar PUBLICADO na planilha. "
            "Feche o Excel e troque o status da linha para PUBLICADO à mão. O robô não vai repetir o post."
        )
    return True


def cmd_publicar(ensaio):
    if ensaio:
        return _publicar(ensaio)
    with trava_de_execucao():
        return _publicar(ensaio)


def _publicar(ensaio):
    linhas = ler_pauta()
    cfg = _config_ou_vazia() if ensaio else carregar_config()
    agora_ = agora()
    qtd = 0
    for d in linhas:
        if status_de(d) != "APROVADO":
            continue
        n = d["_linha"]
        rede = d["rede"].strip().lower()
        try:
            quando = parse_data_hora(d)
        except ErroRobo as e:
            dizer(str(e))
            continue
        if rede == "linkedin":
            dizer(
                f"Aviso: linha {n} é do LinkedIn e foi PULADA (os termos do LinkedIn proíbem automatizar). "
                f"Para publicar, rode de propósito: python robo.py publicar-agora {n}"
            )
            continue
        if quando > agora_:
            dizer(f"Linha {n}: ainda não chegou a hora ({d['data']} {d['hora']}).")
            continue
        if _tentar_publicar(cfg, linhas, d, ensaio):
            qtd += 1
    dizer(f"Fim. {'Simulei' if ensaio else 'Publiquei'} {qtd} linha(s).")
    return 0


def cmd_publicar_agora(numero, ensaio):
    if ensaio:
        return _publicar_agora(numero, ensaio)
    with trava_de_execucao():
        return _publicar_agora(numero, ensaio)


def _publicar_agora(numero, ensaio):
    linhas = ler_pauta()
    cfg = _config_ou_vazia() if ensaio else carregar_config()
    d = next((x for x in linhas if x["_linha"] == numero), None)
    if d is None:
        raise ErroRobo(f"Não existe a linha {numero} na pauta (o número é o da linha no Excel; a 1 é o cabeçalho).")
    st = status_de(d)
    if st == "PUBLICADO":
        raise ErroRobo(f"A linha {numero} já está PUBLICADO. O robô nunca publica de novo.")
    if st in ("PUBLICANDO", "VERIFICAR"):
        raise ErroRobo(
            f"A linha {numero} está {st}: o envio pode ter saído. Confira na rede; se saiu, troque o status para "
            "PUBLICADO; se NÃO saiu, troque para APROVADO. O robô não decide isso sozinho."
        )
    if st != "APROVADO":
        raise ErroRobo(f"A linha {numero} está com status '{d['status']}'. Só publico linha APROVADO.")
    return 0 if _tentar_publicar(cfg, linhas, d, ensaio) else 1


def cmd_conferir(ensaio):
    cfg = _config_ou_vazia()
    if not cfg:
        raise ErroRobo("Não achei config.env. Copie config.exemplo.env para config.env e preencha.")
    faltando = 0
    ia, modelo = escolha_ia(cfg)
    nome_chave = "ANTHROPIC_API_KEY" if ia == "claude" else "OPENAI_API_KEY"
    if preenchido(cfg.get(nome_chave)):
        dizer(f"IA ({ia}, modelo {modelo}): chave preenchida (não testo a IA para não gastar).")
    else:
        faltando += 1
        dizer(f"IA ({ia}): falta preencher {nome_chave} no config.env.")
    testes = [
        ("LinkedIn", ["LINKEDIN_TOKEN"], lambda: linkedin_autor(cfg) and "responde (identificou o autor)"),
        ("Facebook", ["FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_TOKEN"], lambda: _conf_fb(cfg)),
        ("Instagram", ["INSTAGRAM_TOKEN"], lambda: _conf_ig(cfg)),
        ("X", ["X_CLIENT_ID"], lambda: _conf_x(cfg)),
    ]
    for nome, chaves, teste in testes:
        falta = [c for c in chaves if not preenchido(cfg.get(c))]
        if falta:
            faltando += 1
            dizer(f"{nome}: falta preencher {', '.join(falta)} no config.env.")
            continue
        if ensaio:
            dizer(f"[ENSAIO] {nome}: faria uma chamada só de leitura. Não fiz.")
            continue
        try:
            dizer(f"{nome}: OK, {teste()}.")
        except ErroRobo as e:
            faltando += 1
            dizer(f"{nome}: PROBLEMA. {e}")
    dizer("Tudo certo." if not faltando else f"Há {faltando} item(ns) a resolver (veja acima).")
    return 0 if not faltando else 1


def _conf_fb(cfg):
    r = _http(
        "GET",
        f"https://graph.facebook.com/{FB_VERSAO}/{cfg['FACEBOOK_PAGE_ID'].strip()}",
        params={"fields": "name", "access_token": cfg["FACEBOOK_PAGE_TOKEN"].strip()},
    )
    _checar("facebook", r)
    return f"responde (Página: {_corpo(r).get('name', '?')})"


def _conf_ig(cfg):
    if ig_unificado(cfg):
        r = _http(
            "GET",
            f"https://graph.facebook.com/{IG_VERSAO}/{cfg['INSTAGRAM_USER_ID'].strip()}",
            params={"fields": "id,username", "access_token": cfg["INSTAGRAM_TOKEN"].strip()},
        )
        _checar("instagram", r)
        return f"responde (conta: {_corpo(r).get('username', '?')}; token do painel, sem validade marcada)"
    r = _http(
        "GET",
        f"https://graph.instagram.com/{IG_VERSAO}/me",
        params={"fields": "user_id,username", "access_token": cfg["INSTAGRAM_TOKEN"].strip()},
    )
    _checar("instagram", r)
    return f"responde (conta: {_corpo(r).get('username', '?')}){_ig_aviso_validade()}"


def _conf_x(cfg):
    token = x_token_valido(cfg, renovar=False)  # conferir só lê: nunca gasta o refresh token
    if token is None:
        return "autorizado; o token de acesso (dura 2 horas) já venceu e o robô renova sozinho ao publicar (conferir não renova, por isso não testei a chamada)"
    r = _http("GET", "https://api.x.com/2/users/me", headers={"Authorization": f"Bearer {token}"})
    _checar("x", r)
    return f"responde (conta: {_corpo(r).get('data', {}).get('username', '?')})"


def cmd_autorizar_x(ensaio):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs, quote, urlparse

    cfg = _config_ou_vazia()
    client_id = exigir(cfg, "X_CLIENT_ID", "Pegue no console.x.com, no seu app (permissão Read and write).")
    verificador = secrets.token_urlsafe(64)
    desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).decode().rstrip("=")
    estado = secrets.token_urlsafe(16)
    url = (
        "https://x.com/i/oauth2/authorize?response_type=code"
        f"&client_id={quote(client_id)}&redirect_uri={quote(X_CALLBACK, safe='')}"
        "&scope=tweet.read%20tweet.write%20users.read%20offline.access"
        f"&state={estado}&code_challenge={desafio}&code_challenge_method=S256"
    )
    if ensaio:
        dizer("[ENSAIO] Abriria o navegador neste endereço e esperaria o código em " + X_CALLBACK + ":\n  " + url.replace(client_id, "<X_CLIENT_ID>"))
        return 0
    recebido = {}

    class Tratador(BaseHTTPRequestHandler):
        def do_GET(self):
            p = urlparse(self.path)
            if p.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            recebido.update({k: v[0] for k, v in parse_qs(p.query).items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>Pronto. Pode fechar esta janela e voltar ao robô.</h2>".encode("utf-8"))

        def log_message(self, *a):
            pass

    try:
        servidor = HTTPServer(("127.0.0.1", 8080), Tratador)
    except OSError:
        raise ErroRobo("A porta 8080 está ocupada. Feche o programa que a usa e rode autorizar-x de novo.")
    import webbrowser

    dizer("Vou abrir o navegador para você autorizar o robô no X. Se não abrir, copie este endereço no navegador:\n" + url)
    webbrowser.open(url)
    servidor.timeout = 5
    limite = time.time() + 300
    while not recebido and time.time() < limite:
        servidor.handle_request()
    servidor.server_close()
    if not recebido.get("code"):
        raise ErroRobo("Não recebi o código do X em 5 minutos. Rode autorizar-x de novo.")
    if recebido.get("state") != estado:
        raise ErroRobo("O retorno do X não confere (state diferente). Rode autorizar-x de novo.")
    tokens = _x_pedir_token(
        cfg,
        {"grant_type": "authorization_code", "code": recebido["code"], "redirect_uri": X_CALLBACK, "code_verifier": verificador},
    )
    dizer("X autorizado. Tokens gravados em x-tokens.json. Daqui em diante o robô renova sozinho.")
    return 0


# --------------------------------------------------------------------------
def montar_parser():
    p = argparse.ArgumentParser(prog="robo.py", description="Robô de publicação em redes sociais.")
    sub = p.add_subparsers(dest="comando", required=True)
    for nome, ajuda in [
        ("escrever", "pede à IA o texto das linhas com tema e sem texto"),
        ("publicar", "publica as linhas APROVADO cuja hora já chegou (pula LinkedIn)"),
        ("conferir", "confere as chaves e se cada rede responde"),
        ("autorizar-x", "autoriza o X uma única vez"),
        ("renovar-instagram", "renova o token do Instagram (rode a cada ~50 dias) e grava no config.env"),
    ]:
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("--ensaio", action="store_true", help="só mostra o que faria, sem chamar nenhuma rede")
    s = sub.add_parser("publicar-agora", help="publica uma linha agora (vale para qualquer rede, inclusive LinkedIn)")
    s.add_argument("linha", type=int, help="número da linha no Excel (a 1 é o cabeçalho)")
    s.add_argument("--ensaio", action="store_true", help="só mostra o que faria, sem chamar nenhuma rede")
    return p


def main(argv=None):
    args = montar_parser().parse_args(argv)
    registrar(f"=== comando: {args.comando}{' --ensaio' if args.ensaio else ''}")
    try:
        if args.comando == "escrever":
            return cmd_escrever(args.ensaio)
        if args.comando == "publicar":
            return cmd_publicar(args.ensaio)
        if args.comando == "publicar-agora":
            return cmd_publicar_agora(args.linha, args.ensaio)
        if args.comando == "conferir":
            return cmd_conferir(args.ensaio)
        if args.comando == "autorizar-x":
            return cmd_autorizar_x(args.ensaio)
        if args.comando == "renovar-instagram":
            return cmd_renovar_instagram(args.ensaio)
    except ErroRobo as e:
        dizer(f"ERRO: {e}")
        return 1
    except Exception as e:
        dizer(f"ERRO inesperado ({type(e).__name__}). Os detalhes estão em registro.log.")
        registrar(f"detalhe: {descrever_excecao(e)}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
