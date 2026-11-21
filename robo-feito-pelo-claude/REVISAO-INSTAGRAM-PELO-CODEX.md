# Revisão do ajuste do Instagram (login unificado), feita pelo Codex em 20/11/2026

Pedido: revisão só de leitura dos dois robôs depois do ajuste. Observação: o arquivo de diferenças enviado saiu vazio; o Codex revisou os arquivos inteiros. Depois desta revisão, o estado PUBLISHED passou a ter mensagem própria nos dois robôs, com testes; a recusa de endereço sem .jpg é anterior ao ajuste e ficou como está.

Revisei os dois arquivos e executei simulações em memória, sem chamadas às redes sociais nem gravação de arquivos. **GRAVE: nenhum.** O `diff.txt` está vazio; portanto, não foi possível atribuir os problemas à alteração nem comprovar regressões.

**1. Lógica do caminho novo e comportamento do antigo**

- **MÉDIO — URLs de JPEG válidas são recusadas pela extensão.** [Codex, linha 199](robo/codex/robo.py:199) e [Claude, linha 423](robo/claude/robo.py:423): ambos rejeitam, antes de consultar a API, uma URL como `https://servidor/imagem?id=123`, mesmo que entregue um JPEG público. A exigência documentada refere-se ao formato da imagem, não ao sufixo da URL. Afeta os dois modos; não é possível afirmar que seja regressão. [Documentação da Meta](https://developers.facebook.com/documentation/instagram-platform/content-publishing#limitations).

- **MENOR — A espera não respeita um limite de cinco minutos de tempo decorrido.** [Codex, linha 390](robo/codex/robo.py:390) e [Claude, linha 402](robo/claude/robo.py:402): são seis consultas, com pausas que somam **305 segundos**, além do tempo das requisições. O tempo de rede pode ampliar significativamente a espera. Seria necessário controlar um prazo com relógio monotônico. Trata-se de divergência da recomendação, não de evidência de rejeição pela API. [Recomendação da Meta](https://developers.facebook.com/documentation/instagram-platform/content-publishing#container-publishing-status).

**Regressões comprovadas no caminho antigo: nenhum achado**, com a limitação do diff vazio. Nas simulações, sem `INSTAGRAM_USER_ID`, ambos conservaram a sequência `/me` → `/media` → `/media_publish` em `graph.instagram.com`.

**2. Publicação indevida, duplicação e exposição de token**

- **MÉDIO — `PUBLISHED` termina com uma mensagem falsa que pode induzir duplicação manual.** [Codex, linhas 395–401](robo/codex/robo.py:395) e [Claude, linhas 409–415](robo/claude/robo.py:409): esse estado não recebe tratamento próprio. A simulação confirmou seis consultas seguidas de “Nada foi publicado; tente de novo”. Entretanto, `PUBLISHED` significa que a mídia já foi publicada. [Definição da Meta](https://developers.facebook.com/documentation/instagram-platform/content-publishing#container-publishing-status).

  No Claude, a linha ainda termina como `ERRO`, com orientação para voltar a `APROVADO` ([linha 824](robo/claude/robo.py:824)). Se o operador seguir essa orientação, a execução seguinte cria outro container e pode duplicar o post. **Esse risco depende de receber `PUBLISHED` e de reaprovação manual**; não demonstrei esse estado surgindo espontaneamente no fluxo normal de um container recém-criado.

**Publicação sem aprovação ou duplicação automática: nenhum achado.** Ambos persistem `PUBLICANDO` antes do envio e bloqueiam o reenvio automático das linhas pendentes.

**Token na tela ou no registro: nenhum achado nos fluxos examinados.** As credenciais carregadas são mascaradas, e exceções de transporte não expõem seu texto bruto.

**3. Lacunas de teste relevantes**

- **MÉDIO — Estados e respostas excepcionais incompletos.** Os testes novos cobrem principalmente `IN_PROGRESS` → `FINISHED` e `ERROR`: [Codex, linha 454](robo/codex/tests/test_robo.py:454), [Claude, linha 278](robo/claude/test_robo.py:278). Faltam `PUBLISHED`, `EXPIRED`, estado ausente/desconhecido, JSON inválido e falha HTTP durante a consulta, verificando mensagem, status persistido e ausência de `/media_publish`.

- **MÉDIO — Falta exercitar a recuperação no fluxo unificado completo.** Simular timeout após a aceitação de `/media_publish`, interrupção durante a espera e falha ao salvar o resultado; executar novamente e verificar que nenhum segundo post sai. Existem testes gerais de proteção contra duplicação, mas os novos testes de Instagram chamam diretamente as funções de envio e não verificam essa integração.

- **MENOR — O teste de duração não mede tempo decorrido.** [Codex, linha 513](robo/codex/tests/test_robo.py:513) aceita explicitamente 305 segundos de pausas e ignora a latência HTTP. No Claude, falta também o teste de esgotamento das tentativas.

- **MENOR — Cobertura incompleta da seleção do modo e do legado.** Faltam casos com ID vazio, espaços e placeholders; no Claude, falta um teste de publicação antiga bem-sucedida que confira host, descoberta da conta e payloads. Também faltam URLs públicas sem extensão que entreguem JPEG.