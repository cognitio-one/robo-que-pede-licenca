# Apêndices | Para consultar

## Apêndice A. O prompt-mestre, na íntegra

O jeito mais seguro de usar este texto é baixar o arquivo pronto: `github.com/cognitio-one/robo-que-pede-licenca`, pasta `prompts`, arquivo `PROMPT-MESTRE.txt` (veja a Parte D do degrau 3). Ele está aqui para consulta. Você não precisa entender a ficha técnica: ela é para a IA.

::: prompt Prompt-mestre do robô de publicação
Você vai criar, nesta pasta, um robô de publicação em redes sociais para uma pessoa que não sabe programar. Eu sou essa pessoa. Explique cada passo em português simples e me pergunte o que precisar antes de decidir por mim.

O QUE O ROBÔ FAZ
1. Lê uma planilha chamada pauta.csv, que eu edito no Excel. Colunas, nesta ordem: data;hora;rede;tema;texto;imagem;status;resultado. Separador ponto e vírgula, arquivo em UTF-8 com BOM (o Excel brasileiro abre assim). Data no formato dd/mm/aaaa e hora hh:mm. "rede" é uma destas: linkedin, facebook, instagram, x.
2. Comando "escrever": para cada linha com tema e sem texto, pede à inteligência artificial um post no meu estilo e grava o texto na coluna texto, com status RASCUNHO. O meu estilo e as minhas regras ficam no arquivo perfil.txt, que o robô manda à IA junto com o tema.
3. Eu leio os rascunhos no Excel, corrijo o que quiser e troco o status para APROVADO. O robô NUNCA publica linha que não esteja APROVADO.
4. Comando "publicar": publica as linhas APROVADO cuja data e hora já chegaram, grava o status PUBLICADO e, na coluna resultado, o endereço ou o identificador do post. Linha PUBLICADO nunca é publicada de novo.
5. LinkedIn só sob demanda: os termos da API do LinkedIn proíbem automatizar publicações. Por isso, no comando "publicar", linhas do LinkedIn são puladas com um aviso; elas só saem pelo comando "publicar-agora <número da linha>", que eu rodo na hora, de propósito. O comando "publicar-agora" vale para qualquer rede.
6. Modo ensaio: qualquer comando aceita --ensaio. No ensaio, o robô mostra exatamente o que mandaria, para qual rede e com qual texto, e NÃO faz nenhuma chamada às redes.
7. Comando "conferir": verifica se as chaves estão preenchidas e se cada rede responde, com uma chamada só de leitura por rede, e diz em linguagem simples o que está faltando.
8. Tudo o que o robô faz vai para um arquivo registro.log, com data e hora. Chaves e tokens NUNCA aparecem no registro nem na tela.

REGRAS TÉCNICAS
- Python 3, um único arquivo robo.py. Além da biblioteca padrão, só requests, anthropic e openai, listadas em requirements.txt. Importe anthropic e openai só na hora de usar, para o robô funcionar com apenas uma delas instalada.
- Comando "autorizar-x": faz a autorização do X uma única vez (abre o navegador, recebe o código em http://127.0.0.1:8080/callback, troca pelo token) e grava os tokens num arquivo x-tokens.json. Daí em diante, o robô renova o token sozinho e grava o novo refresh token na hora.
- Chaves e tokens ficam num arquivo config.env (nunca no código). Crie também config.exemplo.env, com todos os nomes e valores de exemplo, e um .gitignore que exclua config.env, tokens e registro.log.
- Escolha da IA no config.env: IA=claude ou IA=openai, com o nome do modelo também configurável.
- Mensagens de erro em português, dizendo o que fazer (por exemplo: "o token do LinkedIn venceu; gere outro no Token Generator e cole em config.env").
- Antes de terminar, rode o robô em modo ensaio com uma pauta de exemplo de duas linhas, me mostre o resultado e escreva um LEIA-ME.txt curto com os comandos.
- Escreva testes automáticos (pytest) que provem, sem acessar a internet: que linha RASCUNHO não é publicada; que linha PUBLICADO não é republicada; que o LinkedIn não sai pelo "publicar"; que o ensaio não faz chamada de rede; que a planilha com acento e ponto e vírgula é lida e gravada sem estragar.

Use a FICHA TÉCNICA abaixo, conferida na documentação oficial em novembro de 2026. Se algo nela parecer desatualizado, me avise em vez de trocar por conta própria.

FICHA TÉCNICA (conferida na documentação oficial de cada empresa em 20/11/2026)

Inteligência artificial
- Claude: SDK oficial "anthropic" (pip install anthropic); lê a chave da variável ANTHROPIC_API_KEY; client.messages.create(model=..., max_tokens=..., messages=[...]). Modelo sugerido: claude-sonnet-5-5 (ou claude-haiku-5-5, mais barato).
- OpenAI: SDK oficial "openai" (pip install openai); lê a chave de OPENAI_API_KEY; client.responses.create(model=..., input=...) e response.output_text. Modelo sugerido: gpt-6.2-sol.

LinkedIn (perfil pessoal; só sob demanda)
- Token: gerado sem programar em https://www.linkedin.com/developers/tools/oauth/token-generator (app próprio com os produtos "Share on LinkedIn" e "Sign In with LinkedIn using OpenID Connect"; escopos openid, profile, w_member_social). Vale 60 dias; não há renovação automática para esse produto.
- Autor: GET https://api.linkedin.com/v2/userinfo com Authorization: Bearer <token>; o campo "sub" vira "urn:li:person:<sub>".
- Publicar: POST https://api.linkedin.com/rest/posts com cabeçalhos Authorization: Bearer <token>, Linkedin-Version: 202611, X-Restli-Protocol-Version: 2.0.0, Content-Type: application/json. Corpo: {"author": "urn:li:person:<sub>", "commentary": "<texto>", "visibility": "PUBLIC", "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []}, "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": false}. Sucesso: HTTP 201 e o identificador no cabeçalho x-restli-id. Texto até 3.000 caracteres.

Facebook (Página; pode ir no relógio)
- Graph API versão v27.0, host https://graph.facebook.com.
- Token de Página: no app, caso de uso "Gerenciar tudo na sua Página", Personalizar, adicionar pages_manage_posts e pages_read_engagement. No Explorador da Graph API (developers.facebook.com/tools/explorer), gerar token com pages_show_list, pages_read_engagement e pages_manage_posts (mais business_management se a Página estiver num portfólio empresarial), marcando a Página na janela de autorização. Estender o token na ferramenta Token de Acesso ("Estender token de acesso", cerca de 60 dias) e, com o token estendido, GET /me/accounts?fields=id,name,access_token devolve o id e o token de cada Página; esse token de Página não tem data de expiração marcada.
- Texto: POST https://graph.facebook.com/v27.0/<PAGE_ID>/feed com message e access_token. Foto: POST .../<PAGE_ID>/photos com url (endereço público da imagem) ou o arquivo, mais caption.

Instagram (conta profissional; pode ir no relógio)
- Apps novos da Meta usam só a "configuração da API com login unificado" (a rota "login do Instagram" não está disponível para apps novos). Host https://graph.facebook.com, versão v27.0. O app precisa estar ligado a um portfólio empresarial, e a conta do Instagram precisa ter a função "Testador do Instagram" no app (aceita pelo dono em instagram.com, Apps e sites, Convites do testador).
- Token: no painel do app, Casos de uso, API do Instagram, "1. Configure seu app": criar a configuração pelo modelo (token de acesso do usuário do sistema; a tela diz "O token nunca expira"); depois, em "2. Gerar tokens de acesso", Gerar token na linha da conta. O token começa com EAA e só funciona em graph.facebook.com (em graph.instagram.com dá "Cannot parse access token"). Não há renovação.
- Id da conta: o número que o painel mostra embaixo do nome da conta, em "2. Gerar tokens de acesso". Guardar em INSTAGRAM_USER_ID.
- Publicar imagem: (1) POST https://graph.facebook.com/v27.0/<INSTAGRAM_USER_ID>/media com image_url e caption; devolve o id do container; (2) GET https://graph.facebook.com/v27.0/<id do container>?fields=status_code até FINISHED (ERROR ou EXPIRED: parar sem publicar; a Meta recomenda consultar no máximo uma vez por minuto por até 5 minutos); (3) POST https://graph.facebook.com/v27.0/<INSTAGRAM_USER_ID>/media_publish com creation_id=<id do container>. A imagem PRECISA estar num endereço público na internet e ser JPEG (proporção entre 4:5 e 1,91:1, até 8 MB). Instagram não aceita post só de texto. Legenda até 2.200 caracteres. A API não apaga post do Instagram: apaga-se pelo aplicativo ou por instagram.com.
- A rota antiga (host graph.instagram.com, token de 60 dias renovado por refresh_access_token) só vale para apps antigos e não foi testada por nós.

X (pode ir no relógio; cobrado por uso)
- OAuth 2.0 com PKCE (o OAuth 1.0a será desligado em 31/01/2027). App criado no console.x.com; em User authentication settings: permissão "Read and write", tipo "Native App" (cliente público, sem client secret), Callback URI http://127.0.0.1:8080/callback (127.0.0.1, não localhost).
- Autorizar uma vez: abrir https://x.com/i/oauth2/authorize?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<CALLBACK>&scope=tweet.read%20tweet.write%20users.read%20offline.access&state=<aleatório>&code_challenge=<desafio>&code_challenge_method=S256 ; receber o code no endereço local; trocar em POST https://api.x.com/2/oauth2/token (form: code, grant_type=authorization_code, client_id, redirect_uri, code_verifier; se o app for confidencial, cabeçalho Authorization: Basic base64(client_id:client_secret)).
- O token de acesso vale 2 horas; o refresh token (vem com offline.access) vale cerca de 6 meses e é de USO ÚNICO: a cada renovação (POST https://api.x.com/2/oauth2/token com grant_type=refresh_token e refresh_token) vem um novo, que o robô precisa gravar na hora.
- Publicar: POST https://api.x.com/2/tweets com Authorization: Bearer <token> e JSON {"text": "<texto>"}. Até 280 caracteres (link conta 23). Custo em 20/11/2026: US$ 0,015 por post; US$ 0,20 por post com link.
:::

## Apêndice B. Lista de conferência antes de cada publicação

1. Li o post inteiro, como se fosse o meu cliente mais exigente.
2. Conferi na fonte oficial cada data, número, lei, decisão ou nome citado.
3. Não há dado de cliente, nem detalhe que permita reconhecer alguém.
4. Não há preço, honorário, promessa de resultado nem comparação com colegas.
5. O texto respeita o limite da rede (Instagram 2.200 caracteres; LinkedIn 3.000; X 280).
6. A imagem, se houver, está correta, inclusive as letras.
7. No degrau 2, li o rascunho no Buffer antes de publicar ou pôr na fila. No degrau 3, marquei APROVADO, rodei o ensaio, li o que ele mostrou e só então publiquei.

## Apêndice C. Quanto custa, em uma página

Preços das páginas oficiais em 20 de novembro de 2026, em dólares, sem impostos. Confira antes de contratar: eles mudam.

| Item | Preço | Fonte |
|---|---|---|
| Claude, plano Free | US$ 0 (sem Claude Code e sem tarefas agendadas) | `claude.com/pricing` |
| Claude, plano Pro | US$ 17 por mês no anual; US$ 20 no mensal | `claude.com/pricing` |
| API do Claude, Sonnet 5.5 | US$ 2 por milhão de tokens de entrada; US$ 10 por milhão de saída | documentação de preços da Claude Platform |
| API do Claude, Haiku 5.5 | US$ 0,10 de entrada e US$ 0,50 de saída por milhão (para pedidos de até 100 mil tokens) | idem |
| API da OpenAI, gpt-6.2-sol | US$ 2 por milhão de entrada; US$ 10 por milhão de saída | página de preços da OpenAI |
| Buffer, plano Free | US$ 0, até 3 canais e 10 posts agendados por canal | `buffer.com/pricing` |
| API do X | US$ 0,015 por post; US$ 0,20 por post com link (créditos pré-pagos) | página de preços da documentação do X |
| APIs do LinkedIn, do Instagram e do Facebook usadas aqui | a documentação consultada não indica preço; confira no painel de cada uma | documentação de cada uma |

## Apêndice D. Como este livro foi feito e testado

Tudo o que está aqui foi conferido na documentação oficial de cada empresa e nas telas reais em 20 de novembro de 2026. Onde não testamos de ponta a ponta, o texto diz, numa caixa "Descrito pela documentação".

- **Degrau 1:** prompt rodado no Claude e no ChatGPT; agendamento do LinkedIn e do X aberto e conferido nas telas reais, até o botão de programar, sem publicar. No Business Suite, programamos de verdade um post com imagem para o Facebook e o Instagram, marcado para 25 de novembro, e o apagamos em seguida na aba Programados. A imagem foi anexada por programa, e não pela janela de arquivos do Windows, que o assistente não opera.
- **Degrau 2:** caminho inteiro feito do zero numa conta nova do Buffer, com uma publicação real de teste no LinkedIn, apagada em seguida. O mesmo pedido de rascunho foi feito pelo ChatGPT, e uma tarefa agendada do Claude rodou e deixou o rascunho; os dois rascunhos foram conferidos no Buffer e apagados, e a tarefa também.
- **Degrau 3:** o prompt-mestre foi entregue ao Claude e ao Codex, cada um numa pasta vazia. Os dois robôs passaram nos próprios testes automáticos e no ensaio; depois, cada um foi revisado pela outra IA, corrigido e revisado de novo, até não sobrar falha grave apontada. Com o robô do Codex, fizemos publicações reais de teste no LinkedIn e no X (com `publicar-agora`) e no Facebook (pelo Agendador de Tarefas do Windows), todas apagadas em seguida. No Instagram, descobrimos que apps novos da Meta só aceitam a configuração com login unificado, que os dois robôs, feitos pela ficha antiga, não conheciam. Ajustamos os dois robôs depois (o código novo passou nos testes automáticos e numa revisão do Codex, sem falha grave; uma falha média apontada foi corrigida) e, com eles, publicamos de verdade no Instagram: duas vezes com o robô do Codex e uma com o do Claude, todas apagadas em seguida pelo próprio Instagram. O prompt-mestre foi atualizado com esse caminho, mas ainda não foi entregue de novo a uma IA numa pasta vazia.
- **Leitura de teste:** pedimos a dois leitores automáticos (o Codex, da OpenAI, e o Copilot, da Microsoft), separadamente, que lessem o livro no papel de uma contadora que nunca configurou nada e apontassem cada ponto em que ela travaria. Fizemos três rodadas e corrigimos o livro entre elas. Na terceira, já com os testes reais desta edição, a nota para "eu conseguiria fazer sozinha" foi, no Copilot, 8 no degrau 1, 5 no degrau 2 e 1 no degrau 3; no Codex, 7, 6 e 1 (os dois deram 9 ao degrau 1 se a rede for só o LinkedIn). O que eles pediam e esta edição acrescentou depois da terceira rodada: o caminho completo do Instagram pelo robô (E4) e o Business Suite com imagem. O que ainda pedem: mais figuras de entrada e de resultado nas telas técnicas do degrau 3. Por isso o degrau 3 continua marcado como avançado e pede um ajudante na primeira vez.
- **Planilha no Excel:** abrimos a pauta no Excel, trocamos um status para APROVADO, salvamos como um usuário salvaria e rodamos o ensaio nos dois robôs: os dois leram o arquivo, com os acentos certos.

Os prints vieram de contas reais, com nome, foto, e-mail, chaves e identificadores apagados ou trocados por exemplos ("Seu Nome", "Meu Robô").

## Apêndice E. O repositório

O endereço é **github.com/cognitio-one/robo-que-pede-licenca** (o QR code está na abertura). Para baixar tudo de uma vez, clique no botão verde **Code** e depois em **Download ZIP**. Lá estão:

- `prompts/PROMPT-MESTRE.txt`, o pedido do degrau 3, pronto para copiar;
- `robo-feito-pelo-claude` e `robo-feito-pelo-codex`, os dois robôs, lado a lado, cada um com os seus testes e as revisões que recebeu;
- este livro em PDF e o texto-fonte de cada capítulo.

Você não precisa criar conta no GitHub para baixar.
