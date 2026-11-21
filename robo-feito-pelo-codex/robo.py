"""Robô de publicação. Execute: python robo.py --help."""
import argparse
import base64
import csv
import hashlib
import io
import json
import logging
import math
import os
import re
import secrets
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse


BASE = Path(__file__).resolve().parent
COLUNAS = ["data", "hora", "rede", "tema", "texto", "imagem", "status", "resultado"]
REDES = {"linkedin", "facebook", "instagram", "x"}
CALLBACK = "http://127.0.0.1:8080/callback"
SEGREDOS = set()
LOGGER = logging.getLogger("robo")
LOGGER.propagate = False


class Erro(Exception):
    pass


def proteger(valor):
    if valor:
        SEGREDOS.add(str(valor))
    return valor


def limpar(texto):
    texto = str(texto)
    for segredo in sorted(SEGREDOS, key=len, reverse=True):
        texto = texto.replace(segredo, "[SEGREDO OCULTO]")
    return texto


def avisar(texto):
    texto = limpar(texto)
    print(texto)
    LOGGER.info(texto)


def iniciar_log():
    for handler in list(LOGGER.handlers):
        handler.close()
        LOGGER.removeHandler(handler)
    handler = logging.FileHandler(BASE / "registro.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)


def gravar_atomico(caminho, conteudo):
    """Grava no mesmo diretório e só então substitui o arquivo original."""
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(dir=BASE, prefix=".robo-", delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except OSError:
        raise Erro("Não consegui salvar um arquivo. Feche a planilha no Excel e confira a permissão da pasta.") from None
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()


@contextmanager
def trava():
    caminho = BASE / ".robo.lock"
    try:
        fd = os.open(caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Erro("Já existe uma execução ou uma trava antiga. Feche o outro robô; se nenhum estiver rodando, apague .robo.lock.") from None
    try:
        with os.fdopen(fd, "w") as arquivo:
            arquivo.write(str(os.getpid()))
        yield
    finally:
        caminho.unlink(missing_ok=True)


def ler_config():
    caminho = BASE / "config.env"
    if not caminho.exists():
        raise Erro("Crie config.env copiando config.exemplo.env e preencha suas chaves.")
    config = {}
    for linha in caminho.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if "=" not in linha:
            raise Erro("Há uma linha inválida em config.env. Use NOME=valor, um por linha.")
        chave, valor = linha.split("=", 1)
        chave, valor = chave.strip(), valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        config[chave] = valor
        if not chave.endswith("_CRIADO_EM") and any(parte in chave for parte in ("TOKEN", "SECRET", "API_KEY")):
            proteger(valor)
    return config


def preenchido(valor):
    return bool(valor and not valor.upper().startswith(("PREENCHA", "COLE_", "EXEMPLO", "SEU_", "SUA_")))


def exigir(config, *chaves):
    faltam = [chave for chave in chaves if not preenchido(config.get(chave, ""))]
    if faltam:
        raise Erro("Preencha em config.env: " + ", ".join(faltam) + ".")


def ler_pauta():
    try:
        conteudo = (BASE / "pauta.csv").read_bytes()
        try:
            texto = conteudo.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = conteudo.decode("cp1252")
        with io.StringIO(texto, newline="") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";", strict=True)
            if leitor.fieldnames != COLUNAS:
                raise Erro("O cabeçalho da pauta deve ser: " + ";".join(COLUNAS))
            linhas = list(leitor)
        if any(None in linha or any(valor is None for valor in linha.values()) for linha in linhas):
            raise Erro("Há uma linha com colunas a mais ou a menos. Abra pauta.csv no Excel e confira as oito colunas.")
        for linha in linhas:
            # Só normaliza a apresentação; datas inexistentes continuam sendo
            # rejeitadas por agendamento, sem impedir a leitura de outras linhas.
            data, hora = linha["data"].strip(), linha["hora"].strip()
            if re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", data):
                linha["data"] = "/".join(parte.zfill(2) for parte in data.split("/"))
            if re.fullmatch(r"[0-9]{1,2}:[0-9]{1,2}", hora):
                linha["hora"] = ":".join(parte.zfill(2) for parte in hora.split(":"))
        return linhas
    except (UnicodeError, csv.Error):
        raise Erro("Não consegui ler pauta.csv. Salve como CSV UTF-8, separado por ponto e vírgula.") from None
    except FileNotFoundError:
        raise Erro("Não encontrei pauta.csv nesta pasta.") from None


def salvar_pauta(linhas):
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(buffer, fieldnames=COLUNAS, delimiter=";", lineterminator="\r\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    gravar_atomico(BASE / "pauta.csv", buffer.getvalue().encode("utf-8-sig"))


def agendamento(linha):
    data, hora = linha["data"].strip(), linha["hora"].strip()
    if not re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", data) or not re.fullmatch(r"[0-9]{1,2}:[0-9]{1,2}", hora):
        raise Erro("Corrija a data para dd/mm/aaaa e a hora para hh:mm.")
    try:
        return datetime.strptime(data + " " + hora, "%d/%m/%Y %H:%M")
    except ValueError:
        raise Erro("A data ou hora não existe. Corrija na planilha.") from None


def validar_post(linha):
    rede = linha["rede"].strip().lower()
    texto, imagem = linha["texto"], linha["imagem"].strip()
    if rede not in REDES:
        raise Erro("Use uma destas redes: linkedin, facebook, instagram, x.")
    if not texto.strip():
        raise Erro("Preencha e aprove o texto antes de publicar.")
    limite = {"linkedin": 3000, "instagram": 2200}.get(rede)
    if limite and len(texto) > limite:
        raise Erro(f"Encurte o texto de {rede} para até {limite} caracteres.")
    if rede == "x":
        # Intervalos de peso 1 do X; os demais pontos de código pesam 2.
        sem_links = re.sub(r"https?://\S+", "a" * 23, texto)
        peso = sum(1 if (c <= 0x10FF or 0x2000 <= c <= 0x200D or
                         0x2010 <= c <= 0x201F or 0x2032 <= c <= 0x2037) else 2
                   for c in map(ord, sem_links))
        if peso > 280:
            raise Erro("Encurte o texto do X. O limite é 280; links contam 23, acentos portugueses contam 1 e emojis/CJK geralmente contam 2 por ponto de código.")
    if imagem and rede in {"linkedin", "x"}:
        raise Erro(f"Esta versão publica apenas texto em {rede}. Remova a imagem ou publique manualmente no site.")
    if rede == "instagram":
        url = urlparse(imagem)
        if url.scheme not in {"http", "https"} or not url.netloc or url.username or url.password:
            raise Erro("O Instagram precisa de uma imagem JPEG em endereço público http(s). Preencha imagem.")
        if not url.path.lower().endswith((".jpg", ".jpeg")):
            raise Erro("Use no Instagram um endereço público de JPEG terminado em .jpg ou .jpeg (antes de ?).")
    if imagem and rede == "facebook":
        url = urlparse(imagem)
        if url.scheme in {"http", "https"} and url.netloc and not url.username and not url.password:
            pass
        else:
            caminho = (BASE / imagem).resolve()
            if not caminho.is_relative_to(BASE.resolve()) or not caminho.is_file():
                raise Erro("A foto do Facebook deve ser um endereço público http(s) ou um arquivo dentro desta pasta.")
    return rede


def requisitar(metodo, url, rede, esperados=(200,), **kwargs):
    try:
        import requests
    except ImportError:
        raise Erro("Instale requests com: python -m pip install --user requests") from None
    avisar(f"{rede}: fazendo chamada {metodo} à API; credenciais e resposta bruta ficam ocultas.")
    try:
        resposta = requests.request(metodo, url, timeout=30, allow_redirects=False, **kwargs)
    except requests.RequestException:
        raise Erro(f"Sem resposta de {rede}. Confira a internet. Se era um envio, confira a rede antes de tentar novamente.") from None
    if resposta.status_code not in esperados:
        status = resposta.status_code
        if status in (401, 403):
            dicas = {
                "linkedin": "O token do LinkedIn venceu ou não tem permissão; gere outro no Token Generator e cole em config.env.",
                "facebook": "Gere um token de Página no Explorador da Graph API e confira pages_manage_posts e pages_read_engagement.",
                "instagram": "Gere outro token no painel do app (Casos de uso > API do Instagram > Gerar token) e confira as permissões instagram_basic e instagram_content_publish.",
                "x": "Confira as permissões Read and write e execute python robo.py autorizar-x novamente.",
            }
            raise Erro(dicas.get(rede, "Confira a chave e as permissões em config.env."))
        if status == 429:
            raise Erro(f"{rede} limitou as chamadas. Aguarde e confira a publicação antes de repetir.")
        raise Erro(f"{rede} recusou a chamada (HTTP {status}). Confira texto, imagem, permissões e saldo no painel da rede.")
    return resposta


def dados_json(resposta):
    try:
        dados = resposta.json()
        if not isinstance(dados, dict):
            raise ValueError()
        return dados
    except (ValueError, TypeError):
        raise Erro("A API respondeu em formato inesperado. Confira na rede antes de tentar novamente.") from None


def campo(dados, nome):
    valor = dados.get(nome)
    if not isinstance(valor, (str, int)) or not str(valor):
        raise Erro("A API não devolveu o identificador esperado. Confira na rede antes de tentar novamente.")
    return str(valor)


def ler_tokens_x():
    # Mesmo uma resposta inválida ou de recuperação pode conter segredos.
    dados = None
    for nome in ("x-tokens.json", "x-tokens.json.novo"):
        try:
            carregado = json.loads((BASE / nome).read_text(encoding="utf-8"))
            if isinstance(carregado, dict):
                proteger(carregado.get("access_token"))
                proteger(carregado.get("refresh_token"))
                if nome == "x-tokens.json":
                    dados = carregado
        except (OSError, ValueError):
            pass
    if (BASE / "x-tokens.json.novo").exists():
        raise Erro("Há tokens recuperáveis em x-tokens.json.novo. Feche o robô, resolva a permissão da pasta e substitua x-tokens.json por esse arquivo antes de tentar de novo. Não compartilhe os arquivos.")
    try:
        validar_tokens_x(dados)
        if not isinstance(dados.get("expires_at"), (int, float)) or not math.isfinite(dados["expires_at"]):
            raise ValueError()
        return dados
    except (Erro, ValueError, TypeError, AttributeError, OverflowError):
        raise Erro("Os tokens do X estão ausentes ou inválidos. Execute python robo.py autorizar-x.") from None


def validar_tokens_x(dados):
    try:
        if not all(isinstance(dados.get(chave), str) and dados[chave].strip()
                   for chave in ("access_token", "refresh_token")):
            raise ValueError()
        duracao = int(dados.get("expires_in", 7200))
        if duracao <= 0 or not math.isfinite(time.time() + duracao):
            raise ValueError()
        return duracao
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise Erro("A resposta do X tem tokens ou prazo inválidos. Se recebida agora, foi preservada no arquivo de tokens. Autorize novamente com offline.access: python robo.py autorizar-x.") from None


def salvar_tokens_x(dados):
    proteger(dados.get("access_token"))
    proteger(dados.get("refresh_token"))
    # Não descartar o refresh de uso único por causa de metadados inválidos.
    try:
        duracao = int(dados.get("expires_in", 7200))
        expires_at = time.time() + duracao
        if duracao <= 0 or not math.isfinite(expires_at):
            expires_at = 0
    except (ValueError, TypeError, OverflowError):
        expires_at = 0
    dados = dict(dados, expires_at=expires_at)
    conteudo = json.dumps(dados).encode("utf-8")
    try:
        gravar_atomico(BASE / "x-tokens.json", conteudo)
    except (Erro, OSError):
        try:
            gravar_atomico(BASE / "x-tokens.json.novo", conteudo)
        except (Erro, OSError):
            raise Erro("Não consegui salvar os novos tokens do X em nenhum dos dois arquivos. Nenhum post foi enviado. Resolva a gravação na pasta e execute python robo.py autorizar-x; o refresh antigo pode estar inutilizado.") from None
        raise Erro("Os novos tokens foram salvos em x-tokens.json.novo. Nenhum post foi enviado. Feche o robô, resolva a permissão da pasta e substitua x-tokens.json por x-tokens.json.novo antes de tentar de novo. Não compartilhe os arquivos.") from None
    validar_tokens_x(dados)
    return dados


def trocar_token_x(config, formulario):
    if (BASE / "x-tokens.json.novo").exists():
        # Não consumir outro refresh nem sobrescrever uma recuperação pendente.
        ler_tokens_x()
    exigir(config, "X_CLIENT_ID")
    formulario = dict(formulario, client_id=config["X_CLIENT_ID"])
    extra = {}
    if preenchido(config.get("X_CLIENT_SECRET", "")):
        extra["auth"] = (config["X_CLIENT_ID"], config["X_CLIENT_SECRET"])
    resposta = requisitar("POST", "https://api.x.com/2/oauth2/token", "x", data=formulario, **extra)
    # O refresh token é de uso único: salvar antes de qualquer outra chamada.
    return salvar_tokens_x(dados_json(resposta))


def token_x(config, renovar=True):
    dados = ler_tokens_x()
    if dados["expires_at"] <= time.time() + 60:
        if not renovar:
            raise Erro("O token do X venceu. A próxima publicação renova automaticamente; conferir não altera tokens.")
        if not dados.get("refresh_token"):
            raise Erro("Falta o refresh token do X. Execute python robo.py autorizar-x.")
        dados = trocar_token_x(config, {"grant_type": "refresh_token", "refresh_token": dados["refresh_token"]})
    return dados["access_token"]


def instagram_unificado(config):
    """Apps novos da Meta (login unificado): token do painel do app + número da conta; host graph.facebook.com."""
    return preenchido(config.get("INSTAGRAM_USER_ID", ""))


def token_instagram(config):
    if instagram_unificado(config):
        exigir(config, "INSTAGRAM_ACCESS_TOKEN")
        return config["INSTAGRAM_ACCESS_TOKEN"]  # token de usuário do sistema: não se renova
    exigir(config, "INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_TOKEN_CRIADO_EM")
    try:
        criado = datetime.strptime(config["INSTAGRAM_TOKEN_CRIADO_EM"], "%d/%m/%Y")
    except ValueError:
        raise Erro("Corrija INSTAGRAM_TOKEN_CRIADO_EM em config.env para dd/mm/aaaa.") from None
    if criado > datetime.now():
        raise Erro("A data de criação do token do Instagram está no futuro. Corrija config.env.")
    if datetime.now() - criado >= timedelta(days=45):
        resposta = requisitar("GET", "https://graph.instagram.com/refresh_access_token", "instagram", params={"grant_type": "ig_refresh_token", "access_token": config["INSTAGRAM_ACCESS_TOKEN"]})
        novo = proteger(campo(dados_json(resposta), "access_token"))
        atualizacoes = {"INSTAGRAM_ACCESS_TOKEN": novo, "INSTAGRAM_TOKEN_CRIADO_EM": datetime.now().strftime("%d/%m/%Y")}
        atualizar_config(atualizacoes)
        config.update(atualizacoes)
        avisar("Instagram: token renovado e salvo em config.env.")
    return config["INSTAGRAM_ACCESS_TOKEN"]


def atualizar_config(atualizacoes):
    original = (BASE / "config.env").read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    texto = original.decode("utf-8-sig")
    linhas = texto.splitlines(keepends=True)
    encontradas = set()
    for indice, linha in enumerate(linhas):
        corpo = linha.rstrip("\r\n")
        chave, separador, valor = corpo.partition("=")
        if separador and chave.strip() in atualizacoes:
            encontradas.add(chave.strip())
            espacos = valor[:len(valor) - len(valor.lstrip())]
            linhas[indice] = chave + "=" + espacos + atualizacoes[chave.strip()] + linha[len(corpo):]
    fim = "\r\n" if "\r\n" in texto else "\n"
    for chave, valor in atualizacoes.items():
        if chave not in encontradas:
            if linhas and not linhas[-1].endswith(("\r", "\n")):
                linhas[-1] += fim
            linhas.append(f"{chave}={valor}{fim}")
    gravar_atomico(BASE / "config.env", "".join(linhas).encode("utf-8-sig" if bom else "utf-8"))


def esperar_container(url_container, token, tentativas=6, primeira=5, intervalo=60):
    """Instagram (login unificado): só publica quando o container da imagem está pronto (status FINISHED)."""
    time.sleep(primeira)
    for vez in range(tentativas):
        estado = dados_json(requisitar("GET", url_container, "instagram", params={"fields": "status_code", "access_token": token})).get("status_code")
        if estado == "FINISHED":
            return
        if estado in ("ERROR", "EXPIRED"):
            raise Erro("O Instagram recusou a imagem (precisa ser JPEG num endereço público, proporção entre 4:5 e 1,91:1). Nada foi publicado.")
        if estado == "PUBLISHED":
            raise Erro("O Instagram informa que esta imagem já foi publicada. Confira o perfil no Instagram antes de aprovar a linha de novo, para não publicar duas vezes.")
        if vez + 1 < tentativas:
            time.sleep(intervalo)  # a Meta recomenda consultar uma vez por minuto, por até 5 minutos
    raise Erro("O Instagram ainda está processando a imagem. Nada foi publicado; tente de novo em alguns minutos.")


def enviar(linha, config, token_preparado=None):
    rede = validar_post(linha)
    texto, imagem = linha["texto"], linha["imagem"].strip()
    if rede == "linkedin":
        exigir(config, "LINKEDIN_ACCESS_TOKEN")
        headers = {"Authorization": "Bearer " + config["LINKEDIN_ACCESS_TOKEN"]}
        autor = campo(dados_json(requisitar("GET", "https://api.linkedin.com/v2/userinfo", rede, headers=headers)), "sub")
        headers.update({"Linkedin-Version": "202611", "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"})
        corpo = {"author": "urn:li:person:" + autor, "commentary": texto, "visibility": "PUBLIC", "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []}, "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
        resposta = requisitar("POST", "https://api.linkedin.com/rest/posts", rede, esperados=(201,), headers=headers, json=corpo)
        return campo({"id": resposta.headers.get("x-restli-id")}, "id")
    if rede == "facebook":
        exigir(config, "FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_ACCESS_TOKEN")
        url = "https://graph.facebook.com/v27.0/" + config["FACEBOOK_PAGE_ID"]
        dados = {"access_token": config["FACEBOOK_PAGE_ACCESS_TOKEN"]}
        if not imagem:
            resposta = requisitar("POST", url + "/feed", rede, data=dict(dados, message=texto))
        elif urlparse(imagem).scheme in {"http", "https"}:
            resposta = requisitar("POST", url + "/photos", rede, data=dict(dados, caption=texto, url=imagem))
        else:
            with (BASE / imagem).open("rb") as foto:
                resposta = requisitar("POST", url + "/photos", rede, data=dict(dados, caption=texto), files={"source": foto})
        return campo(dados_json(resposta), "id")
    if rede == "instagram":
        token = token_preparado if token_preparado is not None else token_instagram(config)
        if instagram_unificado(config):
            host = "https://graph.facebook.com/v27.0/"
            url = host + config["INSTAGRAM_USER_ID"].strip()
        else:
            host = "https://graph.instagram.com/v27.0/"
            identidade = dados_json(requisitar("GET", host + "me", rede, params={"fields": "user_id,username", "access_token": token}))
            url = host + campo(identidade, "user_id")
        criado = campo(dados_json(requisitar("POST", url + "/media", rede, data={"image_url": imagem, "caption": texto, "access_token": token})), "id")
        if instagram_unificado(config):
            esperar_container(host + criado, token)
        publicado = dados_json(requisitar("POST", url + "/media_publish", rede, data={"creation_id": criado, "access_token": token}))
        return campo(publicado, "id")
    token = token_preparado if token_preparado is not None else token_x(config)
    dados = dados_json(requisitar("POST", "https://api.x.com/2/tweets", "x", esperados=(200, 201), headers={"Authorization": "Bearer " + token}, json={"text": texto}))
    if not isinstance(dados.get("data"), dict):
        raise Erro("O X não devolveu o identificador. Confira a rede antes de tentar novamente.")
    return campo(dados["data"], "id")


def publicar(config, ensaio=False, numero=None):
    linhas = ler_pauta()
    if numero is not None and not 2 <= numero <= len(linhas) + 1:
        raise Erro("Número inexistente. Use o número da linha no Excel: o primeiro post é a linha 2.")
    erros, quantidade = 0, 0
    agora = datetime.now()
    for indice, linha in enumerate(linhas, 2):
        if numero is not None and indice != numero:
            continue
        if linha["status"].strip() != "APROVADO":
            if linha["status"].strip() in {"PUBLICANDO", "REVISAR"}:
                avisar(f"Linha {indice}: envio pendente de revisão. Confira na rede se o post existe antes de mudar o status. Não haverá reenvio automático.")
            elif linha["status"].strip().upper() == "APROVADO":
                avisar(f"Linha {indice}: pulada; escreva APROVADO em maiúsculas para autorizar a publicação.")
            else:
                avisar(f"Linha {indice}: pulada; somente APROVADO pode publicar.")
            continue
        if numero is None and linha["rede"].strip().lower() == "linkedin":
            avisar(f"Linha {indice}: LinkedIn pulado. Para enviar por sua iniciativa, use publicar-agora {indice}.")
            continue
        try:
            if numero is None and agendamento(linha) > agora:
                avisar(f"Linha {indice}: aguardando a data e a hora da planilha.")
                continue
            rede = validar_post(linha)
            if ensaio:
                avisar(f"ENSAIO — linha {indice}; rede: {rede}\nTexto exato:\n{linha['texto']}\nImagem: {linha['imagem'] or '(sem imagem)'}\nNenhuma chamada será feita; a planilha permanece igual.")
            else:
                # Renovar não publica. Se falhar, a linha permanece APROVADO.
                token = token_x(config) if rede == "x" else token_instagram(config) if rede == "instagram" else None
                # Persistir ANTES da chamada. Uma queda posterior não libera reenvio.
                linha["status"] = "PUBLICANDO"
                linha["resultado"] = "Envio iniciado. Se parar aqui, confira na rede antes de aprovar de novo."
                salvar_pauta(linhas)
                resultado = enviar(linha, config, token) if token is not None else enviar(linha, config)
                linha["status"], linha["resultado"] = "PUBLICADO", limpar(resultado)
                salvar_pauta(linhas)
                avisar(f"Linha {indice}: publicada em {rede}. Identificador: {resultado}")
            quantidade += 1
        except Erro as erro:
            if linha["status"] == "PUBLICANDO":
                linha["status"], linha["resultado"] = "REVISAR", limpar(str(erro))
                salvar_pauta(linhas)
            avisar(f"Linha {indice}: {erro}")
            erros += 1
    avisar(f"{'Ensaio concluído' if ensaio else 'Publicação concluída'}: {quantidade} linha(s); {erros} erro(s).")
    return 1 if erros else 0


def escrever(config, ensaio=False):
    linhas = ler_pauta()
    try:
        perfil = (BASE / "perfil.txt").read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise Erro("Crie perfil.txt com seu estilo e suas regras.") from None
    ia = config.get("IA", "claude").strip().lower()
    if ia not in {"claude", "openai"}:
        raise Erro("Em config.env, use IA=claude ou IA=openai.")
    modelo = config.get("CLAUDE_MODELO" if ia == "claude" else "OPENAI_MODELO", "")
    if not modelo:
        raise Erro("Preencha o nome do modelo da IA em config.env.")
    erros = 0
    for indice, linha in enumerate(linhas, 2):
        if not linha["tema"].strip() or linha["texto"].strip():
            avisar(f"Linha {indice}: escrita pulada; já tem texto ou não tem tema.")
            continue
        if linha["status"].strip() in {"PUBLICADO", "PUBLICANDO", "REVISAR"}:
            avisar(f"Linha {indice}: escrita pulada para preservar o histórico de envio.")
            continue
        rede = linha["rede"].strip().lower()
        if rede not in REDES:
            avisar(f"Linha {indice}: corrija a rede antes de escrever.")
            erros += 1
            continue
        prompt = f"Escreva somente o texto de um post em português para {rede}. Respeite o limite da rede (LinkedIn 3000, Instagram 2200, X 280). Não invente fatos.\nEstilo e regras da pessoa:\n{perfil}\nTema:\n{linha['tema']}"
        if ensaio:
            avisar(f"ENSAIO — linha {indice}; IA: {ia}; modelo: {modelo}; rede: {rede}\nPedido exato à IA:\n{prompt}\nTexto final ainda não existe: depende da IA. Nenhuma chamada ou alteração será feita.")
            continue
        try:
            texto = gerar_texto(config, ia, modelo, prompt)
            if not texto.strip():
                raise Erro("A IA devolveu texto vazio. Confira o modelo e tente novamente.")
            linha["texto"], linha["status"], linha["resultado"] = texto, "RASCUNHO", ""
            salvar_pauta(linhas)
            if texto.lstrip().startswith(("=", "+", "-", "@")):
                avisar(f"Linha {indice}: atenção, o Excel pode interpretar o início do texto como fórmula. Importe a coluna texto como Texto, conforme o LEIA-ME, antes de editar.")
            avisar(f"Linha {indice}: rascunho salvo. Leia e só depois troque o status para APROVADO.")
        except Erro as erro:
            avisar(f"Linha {indice}: {erro}")
            erros += 1
    return 1 if erros else 0


def gerar_texto(config, ia, modelo, prompt):
    chave = "ANTHROPIC_API_KEY" if ia == "claude" else "OPENAI_API_KEY"
    exigir(config, chave)
    try:
        if ia == "claude":
            import anthropic
            with anthropic.Anthropic(api_key=config[chave], timeout=60, max_retries=0) as client:
                resposta = client.messages.create(model=modelo, max_tokens=1500, messages=[{"role": "user", "content": prompt}])
                return "\n".join(bloco.text for bloco in resposta.content if getattr(bloco, "type", "") == "text")
        import openai
        with openai.OpenAI(api_key=config[chave], timeout=60, max_retries=0) as client:
            return client.responses.create(model=modelo, input=prompt).output_text
    except ImportError:
        pacote = "anthropic" if ia == "claude" else "openai"
        raise Erro(f"Instale a IA escolhida: python -m pip install --user {pacote}") from None
    except Exception:
        raise Erro("A IA não respondeu. Confira a chave, o saldo e o nome do modelo em config.env; tente novamente.") from None


def conferir(config, ensaio=False):
    erros = 0
    ia = config.get("IA", "claude")
    try:
        if ia not in {"claude", "openai"}:
            raise Erro("Use IA=claude ou IA=openai em config.env.")
        exigir(config, *(('ANTHROPIC_API_KEY', 'CLAUDE_MODELO') if ia == 'claude' else ('OPENAI_API_KEY', 'OPENAI_MODELO')))
        avisar("IA: chave e modelo preenchidos; a validade não foi testada e nenhum crédito foi usado.")
    except Erro as erro:
        avisar(str(erro))
        erros += 1
    for rede in ("linkedin", "facebook", "instagram", "x"):
        try:
            if ensaio:
                avisar(f"ENSAIO — {rede}: faria uma consulta GET de identificação; credenciais ocultas, sem publicar nem renovar tokens.")
            if rede == "linkedin":
                exigir(config, "LINKEDIN_ACCESS_TOKEN")
                url, extra = "https://api.linkedin.com/v2/userinfo", {"headers": {"Authorization": "Bearer " + config["LINKEDIN_ACCESS_TOKEN"]}}
            elif rede == "facebook":
                exigir(config, "FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_ACCESS_TOKEN")
                url, extra = "https://graph.facebook.com/v27.0/" + config["FACEBOOK_PAGE_ID"], {"params": {"fields": "id,name", "access_token": config["FACEBOOK_PAGE_ACCESS_TOKEN"]}}
            elif rede == "instagram":
                exigir(config, "INSTAGRAM_ACCESS_TOKEN")
                if instagram_unificado(config):
                    url, extra = "https://graph.facebook.com/v27.0/" + config["INSTAGRAM_USER_ID"].strip(), {"params": {"fields": "id,username", "access_token": config["INSTAGRAM_ACCESS_TOKEN"]}}
                else:
                    url, extra = "https://graph.instagram.com/v27.0/me", {"params": {"fields": "user_id,username", "access_token": config["INSTAGRAM_ACCESS_TOKEN"]}}
            else:
                exigir(config, "X_CLIENT_ID")
                token = token_x(config, renovar=False)
                url, extra = "https://api.x.com/2/users/me", {"headers": {"Authorization": "Bearer " + token}}
            if not ensaio:
                dados_json(requisitar("GET", url, rede, **extra))
                avisar(f"{rede}: respondeu à consulta de leitura. Isso não garante permissão para publicar.")
            else:
                avisar(f"{rede}: faria GET {url}; credenciais presentes e ocultas; conexão não testada no ensaio.")
        except Erro as erro:
            avisar(f"{rede}: {erro}")
            erros += 1
    return 1 if erros else 0


def autorizar_x(config, ensaio=False):
    if ensaio:
        avisar("ENSAIO — X: abriria a autorização OAuth 2.0 PKCE no navegador, com tweet.read tweet.write users.read offline.access; receberia o código em http://127.0.0.1:8080/callback e trocaria por tokens via POST /2/oauth2/token. Não abre navegador, não inicia servidor, não acessa a rede e não grava tokens.")
        return 0
    exigir(config, "X_CLIENT_ID")
    import webbrowser
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    recebido = {}

    class Retorno(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # A URL de callback contém um código secreto.

        def do_GET(self):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            valido = url.path == "/callback" and secrets.compare_digest(query.get("state", [""])[0].encode("utf-8"), state.encode("utf-8"))
            if valido:
                if query.get("code"):
                    recebido["code"] = proteger(query["code"][0])
                elif query.get("error"):
                    recebido["negado"] = True
            self.send_response(200 if valido else 400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Volte ao terminal para conferir o resultado.".encode())

    params = {"response_type": "code", "client_id": config["X_CLIENT_ID"], "redirect_uri": CALLBACK, "scope": "tweet.read tweet.write users.read offline.access", "state": state, "code_challenge": challenge, "code_challenge_method": "S256"}
    try:
        with HTTPServer(("127.0.0.1", 8080), Retorno) as servidor:
            servidor.timeout = 1
            avisar("X: abrindo o navegador para você autorizar. Há 3 minutos para concluir.")
            if not webbrowser.open("https://x.com/i/oauth2/authorize?" + urlencode(params, quote_via=quote)):
                raise Erro("Não consegui abrir o navegador. Configure o navegador padrão e execute autorizar-x novamente.")
            limite = time.monotonic() + 180
            while not recebido and time.monotonic() < limite:
                servidor.handle_request()
    except OSError:
        raise Erro("Não consegui receber a autorização na porta 8080. Feche outro programa nessa porta e tente novamente.") from None
    if "code" not in recebido:
        raise Erro("Autorização cancelada ou tempo esgotado. Execute autorizar-x novamente quando estiver pronto.")
    trocar_token_x(config, {"code": recebido["code"], "grant_type": "authorization_code", "redirect_uri": CALLBACK, "code_verifier": verifier})
    avisar("X autorizado. Tokens salvos em x-tokens.json; não compartilhe esse arquivo.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Robô de publicação. A primeira linha de conteúdo no Excel é a 2.")
    parser.add_argument("--ensaio", action="store_true", help="Mostra o plano sem acessar redes ou IA.")
    comandos = parser.add_subparsers(dest="comando", required=True)
    for nome in ("escrever", "publicar", "publicar-agora", "conferir", "autorizar-x"):
        sub = comandos.add_parser(nome)
        sub.add_argument("--ensaio", action="store_true", default=argparse.SUPPRESS)
        if nome == "publicar-agora":
            sub.add_argument("linha", type=int, help="Número da linha no Excel, começando em 2.")
    args = parser.parse_args(argv)
    try:
        iniciar_log()
        with trava():
            config = ler_config()
            # Oculta também tokens já salvos, antes de qualquer prévia de texto.
            if (BASE / "x-tokens.json").exists() or (BASE / "x-tokens.json.novo").exists():
                try:
                    ler_tokens_x()
                except Erro:
                    pass
            avisar(f"Iniciando {args.comando}; ensaio={'sim' if args.ensaio else 'não'}.")
            if args.comando == "publicar-agora":
                return publicar(config, args.ensaio, args.linha)
            return {"escrever": escrever, "publicar": publicar, "conferir": conferir, "autorizar-x": autorizar_x}[args.comando](config, args.ensaio)
    except Erro as erro:
        avisar(str(erro))
        return 1
    except KeyboardInterrupt:
        avisar("Execução interrompida. Se houver PUBLICANDO na planilha, confira a rede antes de aprovar de novo.")
        return 1
    except Exception:
        # Exceções de bibliotecas podem conter URL, token e corpo HTTP.
        avisar("Não foi possível concluir. Feche o Excel e confira os arquivos e permissões. Se houver PUBLICANDO ou REVISAR, confira a rede antes de aprovar novamente. Detalhes internos foram ocultados para proteger suas chaves.")
        return 1


if __name__ == "__main__":
    # No Windows, saídas capturadas podem usar uma codificação antiga.
    # UTF-8 preserva o português também ao salvar/copiar o terminal.
    for saida in (sys.stdout, sys.stderr):
        if hasattr(saida, "reconfigure"):
            saida.reconfigure(encoding="utf-8")
    sys.exit(main())
