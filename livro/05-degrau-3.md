# Degrau 3 (avançado) | O robô próprio

::: atencao Para quem é este degrau
Este degrau mexe com telas técnicas: a janela de comandos do Windows, portais de desenvolvedor das redes e chaves de acesso. Se é a sua primeira vez, faça antes os degraus 1 e 2 e, para a primeira montagem, chame alguém que já tenha usado o Terminal. A recompensa é um robô seu, que custa centavos por post.
:::

| Parte | Você faz | O ajudante faz (na primeira vez) | Você confere |
|---|---|---|---|
| A. Preparar o Windows | abre o Terminal | instala o Python, se travar | `python --version` mostra "Python" |
| B. Ensaio guiado | baixa o ZIP | extrai e copia os arquivos para a pasta | o ensaio mostra o texto e diz que nada foi enviado |
| C e D. A IA que programa | entra na sua conta da IA | acompanha o Claude Code ou o Codex | os testes passam e o ensaio roda |
| E. As chaves | entra nas suas contas e clica em Permitir | cria os apps nos portais e cola as chaves no `config.env` | `python robo.py conferir` diz que está tudo pronto |
| F, G e H. Publicar e manter | aprova cada post na planilha | registra a tarefa no Agendador | o post saiu na rede, uma vez só |

Este é o caminho que nós usamos. Em vez de uma ferramenta intermediária, um pequeno programa no seu computador conversa direto com as portas oficiais das redes (as **APIs**). Você não vai programar: a sua IA programa, e você supervisiona.

O que você ganha: custo de centavos por publicação, controle total sobre o que sai e quando, e nenhuma dependência de serviço de terceiro. O que você paga: uma tarde de configuração e a rotina de renovar chaves de tempos em tempos.

::: porque Por que "a IA programa"
Ferramentas como o **Claude Code** (da Anthropic) e o **Codex** (da OpenAI) são versões da IA que trabalham dentro de uma pasta do seu computador: criam arquivos, instalam o que falta e testam o resultado. Você descreve o que quer em português; elas escrevem o programa. Para este livro, entregamos o mesmo pedido (o **prompt-mestre**, adiante) ao Claude e ao Codex, cada um numa pasta vazia, e os dois devolveram um robô funcionando, com testes.
:::

## Seis palavras deste degrau

| Palavra | O que é |
|---|---|
| **Terminal** | a janela de comandos do Windows, onde se digita uma ordem e se aperta Enter |
| **Pasta** | o lugar no computador onde ficam os arquivos do robô; aqui, a pasta `robo`, dentro da sua pasta pessoal do Windows |
| **Arquivo `.csv`** | uma planilha simples, que o Excel abre; a pauta do robô |
| **Arquivo `.env`** | um arquivo de texto com as chaves, que se edita no Bloco de Notas |
| **App de desenvolvedor** | um cadastro que você faz no portal técnico de cada rede para o robô poder entrar por lá; não é um aplicativo de celular |
| **Crédito de API** | dinheiro pré-pago que a empresa desconta a cada uso do robô; é separado da assinatura do Claude ou do ChatGPT |

## Como o robô funciona

O robô é uma planilha mais um programa. A planilha (`pauta.csv`) é a sua agenda de posts e abre no Excel. O programa (`robo.py`) lê a planilha e faz o trabalho, sempre em três tempos.

| Tempo | Você digita | O robô faz | Status na planilha |
|---|---|---|---|
| 1. Escrever | `python robo.py escrever` | pede à IA o texto de cada tema | **RASCUNHO** |
| 2. Aprovar | (nada: você abre a planilha no Excel) | nada; espera você | você troca para **APROVADO** |
| 3. Publicar | `python robo.py publicar` | publica o que está aprovado e com hora vencida | **PUBLICADO** |

Três travas protegem você:

1. **Sem aprovação, nada sai.** Linha que não diz APROVADO é ignorada.
2. **Ensaio antes de tudo.** Qualquer comando com `--ensaio` mostra exatamente o que seria enviado, sem enviar.
3. **LinkedIn só sob demanda.** Os termos da API do LinkedIn proíbem automatizar publicações. Por isso o robô pula o LinkedIn no comando `publicar` e só publica lá pelo comando `publicar-agora`, que você roda na hora, de propósito.

::: atencao A nossa leitura do LinkedIn
Os termos da API do LinkedIn (seção 3.1) vedam "usar as APIs para automatizar publicações". Entendemos que a publicação disparada por você, na hora, a partir de um texto que você aprovou, não é automação. É a nossa leitura; o LinkedIn não traz exceção expressa. Se preferir não correr risco nenhum, use o agendador do próprio LinkedIn (degrau 1) ou o Buffer (degrau 2) para essa rede.
:::

## Parte A. Preparar o Windows

### A1. Abrir o Terminal

O **Terminal** é a janela onde se digitam comandos. Parece antiga, mas é só uma caixa de texto.

::: passo
1. Clique com o botão direito no botão **Iniciar** (o ícone do Windows, na barra de tarefas).
2. Escolha **Terminal** (no Windows 10, **Windows PowerShell**).
:::

Para colar um comando no Terminal, clique com o botão direito dentro da janela ou use **Ctrl+V**. Para executar, aperte **Enter**. Uma regra vale para o degrau inteiro: nas caixas escuras, **cada linha é um comando**. Digite (ou cole) um comando, aperte Enter e espere o Terminal voltar a mostrar o começo de linha, terminado em `>`, antes do próximo. Quando um comando é longo demais para a largura da página, ele continua na linha de baixo com um leve recuo: é o mesmo comando, e o Enter vai só no fim dele.

### A2. Criar a pasta do robô

O Terminal abre na sua pasta pessoal do Windows (a que tem o seu nome de usuário). Crie ali dentro uma pasta só para o robô:

::: comando
mkdir $HOME\robo
cd $HOME\robo
:::

O primeiro comando cria a pasta; o segundo entra nela. Repare que o começo da linha do Terminal passa a terminar em `\robo>`. Para ver essa pasta no Explorador de Arquivos, digite `explorer .` (com o ponto) e aperte Enter.

### A3. Instalar o Python

O robô é escrito em **Python**, uma linguagem de programação gratuita. A documentação oficial recomenda instalar pelo **Python install manager** ("gerenciador de instalação do Python").

::: passo
1. Abra a **Microsoft Store** (a loja de aplicativos do Windows: aperte a tecla do Windows e digite "Store"), procure **Python install manager** e clique no botão de instalar (na loja, ele costuma se chamar **Obter**).
:::

::: porque Alternativa para quem prefere o Terminal
O comando `winget install 9NQ7512CXL7T -e --accept-package-agreements` faz a mesma instalação, sem abrir a loja.
:::

Feche o Terminal, abra de novo (para ele "enxergar" a instalação nova) e confira:

::: comando
python --version
:::

::: resultado
Aparece uma linha como `Python 3.15.2`. O número pode ser outro; o importante é aparecer "Python".
:::

::: atencao Se abrir a Microsoft Store em vez de mostrar a versão
O Windows tem um atalho que manda o comando `python` para a loja. Abra **Configurações**, procure por **aliases de execução de aplicativo** e desligue as duas linhas do Python que apontam para a loja. Abra um Terminal novo e tente de novo.
:::

::: atencao Como voltar no dia seguinte
Sempre que for mexer no robô: abra o Terminal, digite `cd $HOME\robo` e aperte Enter. Para conversar de novo com a IA que programou o robô, digite `claude` (ou `codex`) dentro dessa pasta: ela lê os arquivos e continua de onde parou.
:::

## Parte B. Ver o robô funcionando, sem chave e sem custo

Antes de criar qualquer conta técnica, faça um ensaio com o robô pronto do repositório do livro. Ele não publica nada e não usa chave nenhuma: só mostra o que faria. Você já tem o que precisa: o Terminal e o Python da Parte A.

::: passo
1. Abra `github.com/cognitio-one/robo-que-pede-licenca` (ou aponte o celular para o QR code da abertura).
2. Clique no botão verde **Code** ("código") e depois em **Download ZIP** ("baixar ZIP"). O arquivo vai para a pasta **Downloads**.
3. Na pasta Downloads, clique com o botão direito no arquivo baixado e escolha a opção de extrair (**Extrair tudo**). Abra a pasta extraída, entre em `robo-feito-pelo-codex`, selecione tudo com **Ctrl+A** e copie com **Ctrl+C**. No Terminal, digite `explorer $HOME\robo` para abrir a pasta do robô e cole com **Ctrl+V**.
4. Abra o Terminal (Parte A1), entre na pasta e instale as bibliotecas do robô:
:::

::: comando
cd $HOME\robo
python -m pip install -r requirements.txt
copy config.exemplo.env config.env
python robo.py publicar --ensaio
:::

A terceira linha cria o arquivo de configuração a partir do modelo, ainda sem nenhuma chave de verdade; o robô precisa dele para começar.

::: resultado
O Terminal mostra o que o robô mandaria para cada rede da planilha de exemplo e avisa que pulou a linha do LinkedIn, que só sai pelo comando `publicar-agora`. Nada foi enviado. Se viu isso, o seu computador está pronto para o robô.
:::

::: figura O ensaio do robô no Terminal do Windows
![Terminal do Windows mostrando o ensaio do robô](d3-20-terminal-ensaio.png)
O robô mostra o texto exato que mandaria para o Facebook, avisa que nenhuma chamada foi feita e que pulou a linha do LinkedIn.
:::

## Parte C. Instalar a IA que programa

::: atencao Se você fez a Parte B, já tem um robô
O robô da Parte B está pronto e testado: você pode pular as Partes C e D e ir direto às chaves (Parte E). As Partes C e D são para quem quer que a própria IA escreva um robô do zero, ou ajuste o pronto ao seu gosto. Nesse caso, crie outra pasta para não misturar: `mkdir $HOME\robo-meu` e `cd $HOME\robo-meu`.
:::

Escolha uma das duas. O Claude Code exige plano pago do Claude (a partir do Pro) ou uma conta do Console com créditos. O Codex usa a sua conta do ChatGPT; confira na página da OpenAI se o seu plano o inclui.

### C1. Claude Code (recomendado)

No Terminal, cole o comando oficial de instalação para Windows:

::: comando
irm https://claude.ai/install.ps1 | iex
:::

Depois, ainda na pasta do robô:

::: comando
claude
:::

Na primeira vez, o Claude Code abre o navegador para você entrar na sua conta do Claude.

::: suaparte
Entre com a sua conta e autorize. Quando o Terminal mostrar a caixa de conversa do Claude Code, ele está pronto para receber o pedido.
:::

### C2. Codex (alternativa, para quem usa ChatGPT)

::: comando
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
codex
:::

Na primeira vez, escolha **Sign in with ChatGPT** ("entrar com o ChatGPT") e autorize no navegador.

## Parte D. O prompt-mestre

Com o Claude Code (ou o Codex) aberto na pasta do robô novo (`robo-meu`), entregue a ele o pedido inteiro. Não copie do PDF: baixe o arquivo `PROMPT-MESTRE.txt` do repositório (pasta `prompts`), abra no Bloco de Notas, aperte **Ctrl+A** (seleciona tudo) e **Ctrl+C** (copia), volte ao Terminal e clique com o botão direito para colar. Aperte Enter. Ele é longo de propósito: diz o que o robô faz, quais travas tem e traz uma **ficha técnica** com os endereços oficiais de cada rede, conferidos na documentação em 20 de novembro de 2026. Sem a ficha, a IA pode usar endereços antigos que ela aprendeu no passado.

O texto completo também está no **Apêndice A**. Você não precisa entender a ficha técnica: ela é para a IA, não para você.

::: prompt Prompt-mestre (resumo; o texto integral está no Apêndice A)
Você vai criar, nesta pasta, um robô de publicação em redes sociais para uma pessoa que não sabe programar. Eu sou essa pessoa. Explique cada passo em português simples e me pergunte o que precisar antes de decidir por mim.

O robô lê pauta.csv (data;hora;rede;tema;texto;imagem;status;resultado), escreve rascunhos com a IA, só publica o que eu marcar como APROVADO, nunca republica, publica no LinkedIn só sob demanda, tem modo --ensaio, comando conferir e registro sem chaves. [...]

Use a FICHA TÉCNICA abaixo [...]
:::

O que acontece em seguida: a IA lê o pedido, cria os arquivos (`robo.py`, `pauta.csv`, `perfil.txt`, `config.exemplo.env` e os testes), instala o que falta e roda os testes. Ela vai pedir permissão antes de executar comandos; leia cada pedido e aprove.

::: resultado
No nosso teste, o Claude e o Codex entregaram, cada um, um robô com testes automáticos, todos aprovados, e os dois rodaram o ensaio. Depois de revisados pela outra IA e corrigidos, o do Claude ficou com 32 testes e o do Codex com 106. O robô da Parte B é o do Codex.
:::


## Parte E. As chaves

O robô precisa de uma chave para a IA e de uma chave (ou token) para cada rede onde vai publicar. Todas vão para um único arquivo, `config.env`, dentro da pasta do robô. A IA já criou um modelo dele, `config.exemplo.env`. Faça uma cópia com o nome certo e abra no Bloco de Notas (se você já fez a cópia na Parte B, digite só a segunda linha):

::: comando
copy config.exemplo.env config.env
notepad config.env
:::

Cada linha do arquivo tem um nome e um valor, separados por `=`. Você vai colar cada chave depois do `=` da linha correspondente e salvar.

::: atencao Chave não se cola em conversa
Cole as chaves só no `config.env`, pelo Bloco de Notas. Não cole na conversa com o Claude Code ou o Codex: o robô lê o arquivo sozinho.
:::

Você só precisa das redes que vai usar. Pule as outras.

### E1. A chave da IA

**Claude.** Entre em `platform.claude.com` (o Console, diferente do `claude.ai` das conversas). Crie a conta com o mesmo e-mail, compre créditos em **Billing** ("cobrança") e, em **API keys**, clique em **Create key** ("criar chave"). Copie a chave e cole na linha `ANTHROPIC_API_KEY=` do `config.env`.

::: figura A entrada do Console do Claude
![Tela de entrada do Claude Console](d3-01-claude-console.png)
:::

**OpenAI.** Entre em `platform.openai.com`, adicione créditos (o faturamento é pré-pago) e abra **API keys**. Clique em **Create new secret key** ("criar nova chave secreta").

::: figura A janela de criar chave da OpenAI
![Janela Create new secret key da OpenAI](d3-03-openai-criar-chave.png)
Dê um nome à chave (1), por exemplo "robô de posts", e clique em **Create secret key** (2). A chave aparece uma única vez: copie na hora e cole na linha `OPENAI_API_KEY=`.
:::

::: custo Quanto custa a IA por post
Um post pede algo como mil "tokens" (pedaços de palavra) de entrada e meio milhar de saída. Pelos preços oficiais de 20 de novembro de 2026, isso dá menos de um centavo de dólar por post com o Claude Sonnet 5.5 (US$ 2 por milhão de tokens de entrada e US$ 10 por milhão de saída) e fica perto de zero com o Claude Haiku 5.5. É uma estimativa nossa a partir da tabela de preços; o painel de cada empresa mostra o gasto real.
:::

### E2. LinkedIn (perfil pessoal, sob demanda)

São três etapas no portal **LinkedIn Developers** (`linkedin.com/developers`): criar o app, conferir os produtos e gerar o token.

::: passo
1. Em **My apps** ("meus apps"), clique em **Create app** ("criar app").
2. Preencha **App name** (o nome, por exemplo "Meu robô"), **LinkedIn Page** (uma Página de empresa sua; o LinkedIn não aceita perfil pessoal aqui), o logotipo e marque a concordância com os termos.
3. Clique em **Create app**.
:::

::: figura O formulário "Create an app"
![Formulário de criação de app no LinkedIn Developers](d3-05-linkedin-criar-app.png)
O campo **LinkedIn Page** (1) é o que mais trava iniciantes: se você ainda não tem uma Página de empresa, crie uma pelo link **Create a new LinkedIn Page**.
:::

Pela central de ajuda do LinkedIn, o app novo já nasce com os dois produtos de que o robô precisa: **Share on LinkedIn** ("compartilhar no LinkedIn") e **Sign In with LinkedIn using OpenID Connect** ("entrar com o LinkedIn"). Confira na aba **Products** do app.

Agora o token, sem programar, pelo **Token Generator** ("gerador de token"), em `linkedin.com/developers/tools/oauth/token-generator`.

::: figura O gerador de token do LinkedIn
![Ferramenta Create OAuth 2.0 access token](d3-06-linkedin-gerador-token.png)
Escolha o app (1), marque os escopos **openid**, **profile** e **w_member_social** (2), marque a caixa de concordância (3) e clique em **Request access token** ("pedir token de acesso").
:::

::: suaparte
O LinkedIn pergunta se o seu app pode publicar por você. Clique em **Permitir**. O gerador mostra o token: copie e cole no `config.env`, depois do `=` da linha `LINKEDIN_ACCESS_TOKEN=`, no lugar do texto de exemplo.
:::

::: atencao O token do LinkedIn vence em 60 dias
Não há renovação automática para esse tipo de app. Anote no calendário: a cada 50 dias, repita o gerador de token e troque a linha no `config.env`. O comando `python robo.py conferir` avisa quando o token parou de funcionar.
:::

::: figura O post de teste que o robô publicou no LinkedIn
![Post de teste publicado pelo robô no perfil do LinkedIn](d3-31-linkedin-post-do-robo.png)
No nosso teste, de 20 de novembro de 2026, o robô publicou este post com `publicar-agora` e nós o apagamos em seguida, pelo menu **...** do post.
:::

### E3. Facebook (Página, pode ir no relógio)

O Facebook publica por uma **Página**. O token sai do **Explorador da Graph API** (`developers.facebook.com/tools/explorer`), uma ferramenta oficial da Meta que dispensa programação. Antes, você precisa de um app na Meta.

::: passo
1. Em `developers.facebook.com`, entre com a sua conta do Facebook e clique em **Criar aplicativo**.
2. Dê um nome ao app (por exemplo "Meu robô") e confirme o e-mail de contato. Clique em **Avançar**.
:::

::: figura O assistente "Criar um app" da Meta
![Primeira etapa do assistente Criar um app](d3-11-meta-criar-app.png)
:::

::: passo
3. Em **Casos de uso**, clique no filtro **Gerenciamento de conteúdo** (1) e marque **Gerenciar tudo na sua Página** (2). Se também for usar o Instagram, marque **Gerenciar mensagens e conteúdo no Instagram**. Clique em **Avançar**.
4. Em **Empresa**, escolha **Ainda não quero me conectar a um portfólio empresarial**. Avance por **Requisitos** e, em **Visão geral**, clique em **Criar aplicativo**. A Meta pede a sua senha do Facebook de novo.
:::

::: figura Os casos de uso do app
![Assistente da Meta com os casos de uso de Página e de Instagram marcados](d3-11b-meta-casos-de-uso.png)
:::

::: passo
5. No painel do app, abra **Casos de uso** e, em **Gerenciar tudo na sua Página**, clique em **Personalizar**. Na lista de permissões, clique em **Adicionar** nas linhas `pages_manage_posts` e `pages_read_engagement`. As duas passam a mostrar **Pronto para teste**.
:::

::: figura As duas permissões ligadas
![Permissões pages_manage_posts e pages_read_engagement prontas para teste](d3-12b-meta-permissoes-pagina.png)
Sem este passo, o Explorador não oferece a permissão de publicar. Foi o que vimos no nosso teste.
:::

::: passo
6. Abra o **Explorador da Graph API** (`developers.facebook.com/tools/explorer`). Em **App da Meta** (1), escolha o seu app.
7. Em **Permissões** (2), adicione `pages_show_list`, `pages_read_engagement` e `pages_manage_posts`. Se a sua Página fica num portfólio empresarial (quem usa o Business Suite costuma ter um), adicione também `business_management`.
8. Clique em **Generate Access Token** ("gerar token") (3).
:::

::: figura O Explorador pronto para gerar o token
![Explorador da Graph API com o app e as permissões escolhidos](d3-12c-meta-explorador-pronto.png)
:::

::: suaparte
Abre uma janela do Facebook. Siga com **Continuar** e, quando ela pedir para escolher as **Páginas**, marque a Página do robô. Se não marcar nenhuma, a lista de Páginas do passo 10 vem vazia: foi o que aconteceu na nossa primeira tentativa.
:::

O token que o Explorador mostra vale cerca de uma hora. Para o robô, você precisa de um que dure:

::: passo
9. Clique no **i** azul dentro da caixa do token e em **Abrir na ferramenta Token de Acesso**. Na página que abre, clique em **Estender token de acesso** no rodapé. A Meta pede a senha de novo e mostra um token novo, de cerca de dois meses. Copie esse token.
10. Volte ao Explorador e cole o token novo na caixa **Token de acesso**, no lugar do antigo. No alto do Explorador, na caixa comprida à direita de **v27.0** (onde está escrito `me?fields=id,name`), apague o texto e escreva `me/accounts?fields=id,name,access_token`. Clique em **Enviar**. A resposta lista as suas Páginas, cada uma com `id` (só números) e `access_token` (um texto longo entre aspas). Ache a sua Página pelo `name` e copie, sem as aspas, o `id` para a linha `FACEBOOK_PAGE_ID=` e o `access_token` para a linha `FACEBOOK_PAGE_ACCESS_TOKEN=` do `config.env`.
:::

::: figura O token estendido
![Depurador de token de acesso com o token de vida longa](d3-13b-meta-token-estendido.png)
:::

::: resultado
Um token de Página que não vence: no nosso teste, de 20 de novembro de 2026, a consulta à Meta devolveu para ele a data de expiração zero, o que quer dizer que não tem validade marcada. Com ele, o robô publicou na Página pelo Agendador de Tarefas (Parte G) e nós apagamos o post logo depois.
:::

::: figura O post de teste na Página
![Post de teste publicado pelo robô na Página do Facebook](d3-42-facebook-post-do-robo.png)
:::

### E4. Instagram (conta profissional, pode ir no relógio)

O Instagram usa o mesmo app da Meta. Para apps criados hoje, a Meta oferece um caminho só, a **configuração da API com login unificado**; a própria tela avisa que a configuração com login do Instagram "não está disponível para apps mais recentes". São quatro etapas: ligar o app a um portfólio empresarial, pôr a sua conta do Instagram como testadora do app, gerar o token e preencher duas linhas do `config.env`. A conta do Instagram precisa ser profissional e estar ligada à Página do Facebook (capítulo 1).

::: atencao O Instagram exige imagem num endereço público
A API do Instagram não aceita post só de texto e não recebe o arquivo do seu computador: a imagem precisa estar num endereço público da internet (um link que qualquer pessoa abre), ser JPEG (arquivo terminado em `.jpg`) e ter proporção entre 4:5 (em pé) e 1,91:1 (deitada); quadrada serve. Coloque esse link na coluna `imagem` da pauta. Para o primeiro teste, use a imagem de exemplo do repositório, que já cumpre tudo isso: `https://raw.githubusercontent.com/cognitio-one/robo-que-pede-licenca/main/exemplos/imagem-de-teste.jpg`. Para as suas imagens, você precisa de um lugar que dê um link direto para o arquivo `.jpg`, como o seu site. Se isso complicar, publique no Instagram pelo degrau 1 (Business Suite) ou pelo degrau 2 (Buffer), que recebem a imagem do computador.
:::

::: passo
1. No painel do app, abra **Casos de uso**. Na linha **API do Instagram** (é o caso de uso do Instagram que você marcou no passo 3 do E3), clique em **Personalizar** e, à esquerda, em **API setup with Unified login**.
2. No alto da tela, a Meta pede que o app seja ligado a um **portfólio empresarial** (no passo 4 do E3 você deixou isso para depois). Clique no aviso, escolha o seu portfólio, o mesmo em que está a sua Página, e confirme.
:::

::: figura A tela do Instagram no painel do app
![Tela API setup with Unified login com os itens 1 e 2](d3-14b-meta-instagram-api-setup.png)
À esquerda, **API setup with Unified login** (1). À direita, o item **1. Configure seu app** (2), aqui já com a configuração do passo 5, e o item **2. Gerar tokens de acesso** (3), do passo 6. Os itens 3 e 4 o robô não usa.
:::

::: suaparte
Nessa hora, a Meta pode pedir que você confirme a identidade (com a chave de acesso, a digital ou o PIN do computador). No nosso teste, de 20 de novembro de 2026, ela pediu: à tarde, num computador novo, a confirmação não passou; à noite, com a chave de acesso já cadastrada no Windows, passou.
:::

::: passo
3. No menu da esquerda do painel, abra **Funções do app** e depois **Funções**. Clique em **Adicionar pessoas**, escolha **Testador do Instagram**, digite o nome de usuário da sua conta do Instagram (o que vem depois do @ no seu perfil, sem o @) e escolha a conta certa na lista. A função fica **Pendente** até você aceitar.
:::

::: suaparte
4. Aceite o convite: abra `instagram.com/accounts/manage_access` no navegador (a página **Apps e sites**), aba **Convites do testador**, e clique em **Aceitar** embaixo do nome do app (o nome que você deu no E3; no nosso teste, a Meta acrescentou `-IG` no fim). Esse clique aceita os termos da Meta para o app de teste. O texto do convite diz que você é funcionária da empresa dona do app ou tem um acordo para testá-lo: como o app é seu, está tudo certo.
:::

::: figura O convite de testador no Instagram
![Página Apps e sites do Instagram com o convite do app de teste](d3-15-instagram-convite-testador.png)
:::

::: passo
5. Volte a **Casos de uso**, **API do Instagram**, **Personalizar**, **API setup with Unified login**. No item **1. Configure seu app**, a Meta avisa, na primeira vez, que não há configuração; clique no botão para criar uma e use o modelo que ela oferece. Na janela de confirmação, clique em **Criar do modelo**.
:::

::: figura A janela de confirmação da configuração
![Janela de confirmação da configuração de login unificado](d3-17-meta-instagram-configuracao.png)
Repare em **Token de acesso do usuário do sistema** e em **O token nunca expira**. Não é preciso mudar nada nesta janela. Mais abaixo, fora da figura, ela lista as permissões, e no fim fica o botão **Criar do modelo**. A janela também fala em acesso a **Contas de anúncios**; o robô não usa anúncios, e no nosso teste a conta de anúncios ficou em branco no passo 6 sem problema.
:::

::: passo
6. No item **2. Gerar tokens de acesso**, a sua conta aparece numa linha (se não aparecer, clique em **Adicionar conta** e entre com a conta do Instagram). Anote o número embaixo do nome da conta (1) e clique em **Gerar token** (2).
:::

::: figura A linha da conta, com o número e o botão Gerar token
![Item Gerar tokens de acesso com a conta do Instagram](d3-16-meta-instagram-gerar-token.png)
:::

::: suaparte
Abre uma janela separada, chamada **Login do Facebook para Empresas**. Ela pode abrir atrás do Chrome: no nosso teste foi o que aconteceu. Se clicar em **Gerar token** e nada mudar, passe o mouse no ícone do Chrome na barra de tarefas (a faixa no pé da tela) e clique na miniatura dessa janela. Confira o portfólio e a conta do Instagram, deixe a conta de anúncios sem marcar e clique em **Continuar** até a janela fechar. De volta ao painel, aparece o token, um texto longo que começa com `EAA`. Copie o token inteiro: são centenas de caracteres.
:::

::: passo
7. Abra o `config.env` no Bloco de Notas (no Terminal, na pasta do robô: `notepad config.env`). Cole o token depois do `=` da linha `INSTAGRAM_ACCESS_TOKEN=` e o número da conta (o do passo 6) depois do `=` da linha `INSTAGRAM_USER_ID=`, sem espaços. Salve com **Ctrl+S**. A linha `INSTAGRAM_TOKEN_CRIADO_EM` pode ficar como está: com o número da conta preenchido, o robô não usa essa data e não tenta renovar o token.
8. No Terminal, na pasta do robô, confira: `python robo.py conferir`. A linha do Instagram deve dizer `instagram: respondeu à consulta de leitura`.
9. Na pauta (no Excel, como na Parte F), preencha uma linha com `instagram` na coluna `rede`, o texto do post, o link da imagem na coluna `imagem` e `APROVADO` no `status`. Veja o número dessa linha no Excel (o cabeçalho é a linha 1). Ensaie com esse número, por exemplo `python robo.py publicar-agora 4 --ensaio` se for a linha 4: o robô mostra o texto e a imagem e termina com `Ensaio concluído: 1 linha(s); 0 erro(s)`. Se estiver certo, publique: `python robo.py publicar-agora 4`. Depois disso, as linhas de Instagram podem ir no relógio (Parte G).
:::

::: figura O robô publicando no Instagram
![Terminal com a publicação no Instagram concluída](d3-60-terminal-instagram.png)
O que importa é a linha `Linha 4: publicada em instagram`; as de cima são o robô contando o que faz. Antes de publicar, ele espera a Meta avisar que a imagem está pronta. Se a imagem for recusada, ele para e não publica nada.
:::

::: resultado
No nosso teste, de 20 de novembro de 2026, o robô publicou a imagem de teste com a legenda na conta do Instagram, e nós apagamos o post logo depois. O robô do Claude, ajustado do mesmo jeito, também publicou, e também apagamos. A API não apaga post do Instagram: para apagar, abra o post no Instagram, clique nos três pontos e em **Excluir**. O painel do app fala numa análise da Meta para o app acessar dados "ao vivo"; para publicar na própria conta, cadastrada como testadora, não precisou.
:::

::: figura O post de teste no Instagram
![Post de teste publicado pelo robô no Instagram](d3-61-instagram-post-do-robo.png)
:::

Se você criou o app agora, no E3, ignore este parágrafo. Se o seu app for antigo e a tela oferecer a configuração com login do Instagram, o robô também funciona por ela (deixe `INSTAGRAM_USER_ID` vazio e preencha a data do token), mas esse caminho nós não testamos.

### E5. X (pode ir no relógio; cada post é cobrado)

O X cobra por uso: em 20 de novembro de 2026, **US$ 0,015 por post** e **US$ 0,20 por post com link** (página oficial de preços). Você compra créditos antes, no console.

::: passo
1. Entre em `console.x.com` com a sua conta do X e compre créditos em **Buy Credits** ("comprar créditos").
2. Em **Apps**, clique em **Create app** ("criar app"), dê um nome e clique em **Create**. O X mostra umas chaves "OAuth 1.0a" e um "Bearer Token": o robô não usa nenhuma delas, pode fechar com **Close**.
3. Na página do app, na linha **User authentication settings** ("configurações de autenticação"), clique em **Set up**.
4. Marque **Read and write** ("ler e escrever") e, em **Type of app**, deixe **Native app** ("app nativo"). Em **Callback URI**, escreva `http://127.0.0.1:8080/callback` (com 127.0.0.1, não "localhost"); em **Website URL**, o endereço do seu site ou perfil. Clique em **Save changes**.
5. O X mostra o **Client ID** e um **Client Secret**. Copie só o **Client ID** para a linha `X_CLIENT_ID=` do `config.env`. Com **Native app**, o robô não precisa do Client Secret: deixe a linha `X_CLIENT_SECRET=` vazia.
:::

::: figura As configurações de autenticação do app
![Tela de configuração de autenticação do app no console do X](d3-08e-x-autenticacao.png)
Leitura e escrita (1), app nativo (2) e o endereço de retorno (3). Depois de salvar, o **Client ID** fica sempre visível na aba **Keys & Tokens** do app.
:::

::: figura A aba Keys & Tokens de um app do X
![Aba Keys and Tokens no console do X](d3-09-x-chaves.png)
A seção **OAuth 2.0 Keys** (1) é a que o robô usa. As chaves "OAuth 1.0a", acima, serão desligadas pelo X em 31 de janeiro de 2027.
:::

Por fim, autorize o robô uma única vez:

::: comando
python robo.py autorizar-x
:::

::: suaparte
O navegador abre a página do X pedindo autorização para o seu app. Confira o nome do app e autorize. O robô guarda o token e passa a renová-lo sozinho.
:::

::: resultado
O robô diz "X autorizado" e guarda os tokens num arquivo da pasta, `x-tokens.json`, que você não deve compartilhar. No nosso teste, de 20 de novembro de 2026, a autorização levou um clique, e o robô publicou no X com `publicar-agora`. Apagamos o post em seguida.
:::

::: figura O post de teste no X
![Post de teste publicado pelo robô no X](d3-51-x-post-do-robo.png)
:::

## Parte F. A primeira publicação

Com as chaves no lugar, faça a primeira volta completa, devagar.

::: passo
1. Confira tudo: `python robo.py conferir`. O robô diz, rede por rede, o que está pronto e o que falta.
2. Abra a `pauta.csv` no Excel, preencha uma linha com data, hora, rede e tema, e salve no mesmo formato (CSV).
3. Peça os rascunhos: `python robo.py escrever`.
4. Abra a pauta de novo, leia o texto, corrija o que quiser e troque o status para `APROVADO`. Salve.
5. Ensaie: `python robo.py publicar --ensaio` (Facebook, Instagram, X) ou, para o LinkedIn, `python robo.py publicar-agora 2 --ensaio`. Leia o que ele mandaria.
6. Publique: `python robo.py publicar` (Facebook, Instagram, X) ou `python robo.py publicar-agora 2` (qualquer rede, inclusive LinkedIn; o número é o da linha no Excel).
:::

::: figura A pauta aberta no Excel
![Planilha pauta.csv aberta no Excel](d3-21-excel-pauta.png)
Cada linha é um post; o número da linha (à esquerda) é o que vai no comando `publicar-agora`. Se a coluna da data (1) mostrar `########`, ela só está estreita: dê dois cliques na divisa entre as letras **A** e **B**, no alto, para alargar. A coluna **status** (2) é onde você troca RASCUNHO por APROVADO. Ao salvar, se o Excel perguntar sobre o formato, escolha manter o formato CSV.
:::

::: resultado
A coluna `status` vira `PUBLICADO` e a coluna `resultado` traz o endereço ou o número do post. Tudo fica anotado em `registro.log`, sem nenhuma chave.
:::

::: figura O registro das nossas três publicações de teste
![Linhas do registro.log com as publicações no LinkedIn, no Facebook e no X](d3-52-terminal-registro.png)
O comando mostra só as linhas de publicação do `registro.log`. Estas são as do nosso teste, de 20 de novembro de 2026: LinkedIn e X com `publicar-agora`, Facebook pelo Agendador (Parte G). Apagamos os três posts logo depois.
:::

## Parte G. O robô no relógio

Para o robô publicar sozinho o que você aprovou, o Windows precisa chamá-lo de tempos em tempos. Quem faz isso é o **Agendador de Tarefas**, que já vem no Windows.

Primeiro, crie na pasta do robô um arquivo chamado `publicar.cmd`. No Terminal, dentro da pasta, digite `notepad publicar.cmd` e aperte Enter. Se o Bloco de Notas perguntar se quer criar o arquivo, responda **Sim**. Cole as três linhas abaixo, salve com **Ctrl+S** e feche.

::: comando Conteúdo do arquivo publicar.cmd (no Bloco de Notas, não no Terminal)
@echo off
cd /d "%USERPROFILE%\robo"
python robo.py publicar >> agendador.log 2>&1
:::

Depois, de volta ao Terminal, registre a tarefa para rodar de hora em hora. São três comandos, que começam com `$acao`, `$relogio` e `Register`. O segundo não cabe na largura da página e continua na linha de baixo: digite-o inteiro e só então aperte Enter. Aperte Enter uma vez no fim de cada um dos três.

::: comando
$acao = New-ScheduledTaskAction -Execute "$HOME\robo\publicar.cmd"
$relogio = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "Robo de publicacao" -Action $acao -Trigger $relogio
:::

O Windows responde com uma pequena tabela: o nome da tarefa e o estado **Ready** ("pronta"). A partir daí, a cada hora, o robô publica as linhas APROVADO cuja data e hora já chegaram, e só elas. O LinkedIn continua de fora, por regra.

Não espere uma hora para saber se deu certo. Peça uma rodada agora:

::: comando
Start-ScheduledTask -TaskName "Robo de publicacao"
:::

::: figura A tarefa registrada e a rodada pedida
![Terminal com os comandos de registro da tarefa e a resposta Ready](d3-40-terminal-agendador.png)
:::

Espere uns dez segundos e leia o resultado:

::: comando
Get-ScheduledTaskInfo -TaskName "Robo de publicacao"
Get-Content agendador.log -Encoding UTF8
:::

::: figura O resultado da rodada
![Terminal com LastTaskResult 0 e o agendador.log mostrando a publicação no Facebook](d3-41-terminal-agendador-conferir.png)
Na linha **LastTaskResult** ("último resultado"), **0** quer dizer que a tarefa rodou sem erro (1). O `agendador.log` mostra o que o robô fez (2): no nosso teste, de 20 de novembro de 2026, publicou na Página do Facebook a linha aprovada e pulou as outras. Sem o `-Encoding UTF8`, o Windows mostra os acentos trocados ("nÃ£o" no lugar de "não"); o arquivo está certo, só a leitura é que falha.
:::

::: porque Por que três linhas, e não o comando schtasks
Existe um comando mais curto, o `schtasks`, mas no nosso teste ele falhou quando o nome da pasta do usuário tem espaço (como `C:\Users\Maria Silva`): a tarefa é registrada, mas não roda. Os três comandos acima funcionaram nos dois casos.
:::

::: atencao O computador precisa estar ligado
O Agendador só roda com o computador ligado e com você conectado. Se o computador estiver desligado na hora marcada, o post sai na próxima rodada depois que você ligar. Para apagar a tarefa: `Unregister-ScheduledTask -TaskName "Robo de publicacao" -Confirm:$false`.
:::

## Parte H. A manutenção

| O quê | De quanto em quanto tempo | Como |
|---|---|---|
| Token do LinkedIn | 60 dias | Token Generator de novo; trocar no `config.env` |
| Token do Instagram | sem data marcada | a tela da configuração diz "O token nunca expira"; se o `conferir` acusar problema, gere outro no painel (E4, passo 6) |
| Token da Página do Facebook | raramente | pela documentação da Meta, o token de Página de longa duração não tem data de validade, mas pode ser invalidado em algumas situações; o `conferir` avisa |
| Token do X | automático | o robô renova sozinho; refaça `autorizar-x` se ficar meses parado |
| Créditos da IA e do X | conforme o uso | painel de cada empresa |

Uma vez por semana, rode `python robo.py conferir`. É o check-up do robô.
