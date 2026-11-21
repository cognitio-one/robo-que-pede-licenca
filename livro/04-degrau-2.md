# Degrau 2 | O robô de conversa

No degrau 1, você copiava o texto da IA e colava na rede. Aqui, a IA entrega o post pronto direto numa ferramenta de agendamento, como **rascunho**, e você só aprova. Ninguém programa nada: você conversa.

Neste degrau há duas licenças diferentes, e vale distinguir desde já. A primeira é **deixar a IA usar o Buffer**: o Claude ou o ChatGPT pergunta se pode, e você permite. A segunda é **aprovar a publicação**: você abre o rascunho no Buffer, lê e só então manda publicar. A primeira não substitui a segunda.

::: porque Cinco palavras deste degrau
**Canal** é cada rede ligada ao Buffer (o seu LinkedIn, o seu Instagram). **Fila** é a lista de horários fixos em que o Buffer publica o que você aprovou. **Rascunho** é o post guardado, que não sai sozinho. **Ferramenta**, aqui, é cada ação que a IA pode fazer no Buffer (ler, criar, apagar). **Permissão** é a regra que diz se a IA precisa da sua licença para usar cada ferramenta.
:::

A peça que faz a ponte chama-se **Buffer**, um serviço de agendamento de redes sociais que publica um **conector** próprio para o Claude e para o ChatGPT. O conector é o que permite à IA "entrar" no Buffer, com a sua autorização, e deixar os posts lá.

::: custo
O plano grátis do Buffer permite ligar até **3 canais** (por exemplo, LinkedIn, Instagram e Facebook) e manter até **10 posts agendados por canal** ao mesmo tempo; quando um sai, abre vaga para outro (página oficial `buffer.com/pricing`, conferida em 20 de novembro de 2026). O conector funciona com o Claude grátis.
:::

O caminho tem quatro etapas, e cada uma só se faz uma vez: criar a conta no Buffer, ligar as redes ao Buffer, ligar o Buffer ao Claude e ajustar as permissões. Depois disso, o uso diário é uma frase.

Nós fizemos este caminho inteiro, do zero, em 20 de novembro de 2026, e publicamos um post de teste no LinkedIn por ele. As figuras abaixo são desse teste, com nome e foto apagados.

## Etapa 1. Criar a conta no Buffer

::: passo
1. Abra `buffer.com`. O site aparece em português.
2. Clique em **Comece agora gratuitamente**, no canto superior direito (1).
:::

::: figura O site do Buffer
![Topo do site do Buffer com o botão de começar](d2-01-buffer-site.png)
:::

::: passo
3. Na tela **Create a Buffer Account** ("crie uma conta no Buffer"), digite o seu e-mail (1) e crie uma senha (2). A senha precisa de pelo menos 8 caracteres, uma letra maiúscula e um número ou símbolo.
4. Clique em **Sign Up** ("cadastrar") (3).
:::

::: figura O cadastro
![Formulário de cadastro do Buffer](d2-02-buffer-cadastro.png)
As telas internas do Buffer estão em inglês. Ao lado de cada botão, damos a tradução.
:::

::: suaparte
O e-mail e a senha são seus. Se o Buffer mandar um link de confirmação para o e-mail, abra e confirme.
:::

O Buffer faz então quatro perguntas rápidas sobre você. Nenhuma é obrigatória; há sempre um **Skip** ("pular"). Na última, **What social channel(s) are in focus?** ("em quais redes você quer focar?"), marque as redes que pretende usar e clique em **Continue** ("continuar") (1).

::: figura Escolhendo as redes
![Tela do Buffer para escolher as redes](d2-07-buffer-redes.png)
:::

## Etapa 2. Ligar as suas redes ao Buffer

Você chega ao painel do Buffer. Em **First Steps** ("primeiros passos"), clique em **Connect Channel** ("conectar canal") (1).

::: figura O painel do Buffer, recém-criado
![Primeiros passos no painel do Buffer](d2-08-buffer-painel.png)
:::

Escolha a rede. No nosso teste, ligamos o LinkedIn (1).

::: figura A escolha do canal
![Janela Connect a New Channel com o LinkedIn destacado](d2-09-buffer-conectar.png)
No cartão de cada rede, o Buffer diz que tipo de conta aceita: **Page or Profile** (página ou perfil) no LinkedIn, **Page or Group** (página ou grupo) no Facebook, e **Business, Creator, or Personal** (empresa, criador ou pessoal) no Instagram.
:::

::: suaparte
O Buffer abre a página de entrada da própria rede. Entre com a sua conta e, quando a rede perguntar se o Buffer pode publicar por você, clique em **Permitir**. Se a rede perguntar onde publicar, escolha o perfil ou a página que você quer.
:::

::: atencao Instagram pessoal e grupos do Facebook
Na documentação do Buffer, perfis pessoais do Instagram e grupos do Facebook só recebem **lembretes**: o Buffer avisa no seu celular e você publica com um toque. Para a publicação sair sozinha no Instagram, a conta precisa ser profissional (veja o capítulo 1).
:::

Depois de ligar, o Buffer oferece uma meta de posts por semana e sugere horários. Pode aceitar: os horários servem para a **fila** (veremos adiante) e podem ser mudados depois.

## Etapa 3. Ligar o Buffer ao Claude

Agora a ponte entre a IA e o Buffer.

::: passo
1. No Claude (`claude.ai`), abra a barra lateral, à esquerda (se estiver fechada, clique no ícone de painel, no canto de cima). Clique em **Plugins** (2). O item **Agendados** (1), logo acima, é o das tarefas agendadas, usado no fim deste capítulo.
:::

::: figura A barra lateral do Claude
![Barra lateral do Claude com Agendados e Plugins](d2-11b-claude-barra.png)
:::

::: passo
2. Na página de Plugins, clique na caixa **Procurar** (1) e digite **Buffer**.
:::

::: figura A página de Plugins do Claude
![Página de Plugins do Claude com a caixa de busca](d2-12-claude-plugins.png)
:::

::: passo
3. Clique no resultado **Buffer**, marcado como **Conector · Buffer** (1). Cuidado com nomes parecidos: o certo é o que diz "Buffer" duas vezes.
:::

::: figura O resultado certo
![Resultados da busca por Buffer](d2-13-claude-busca.png)
:::

::: passo
4. Na página do plugin, clique em **Adicionar** (1).
:::

::: figura A página do plugin Buffer
![Página do plugin Buffer no Claude](d2-14-claude-plugin-buffer.png)
O selo **Comunidade** (2) indica um plugin de terceiro: quem o desenvolve e mantém é o Buffer, como diz a ficha ao lado, em **Desenvolvedor**. Em **Segurança e acesso**, o Claude avisa para onde os dados podem ir: `mcp.buffer.com`.
:::

::: passo
5. O Buffer abre a tela **Claude wants to connect to Buffer** ("o Claude quer se conectar ao Buffer"). Ela lista o que o Claude poderá ver e fazer: sua conta, seus canais, seus posts, suas ideias e outros itens.
:::

::: figura O pedido de autorização
![Tela de autorização do Buffer para o Claude](d2-15-buffer-autorizar.png)
:::

::: suaparte
Leia a lista e, se concordar, clique em **Connect Claude** ("conectar o Claude") (1). Você pode retirar o acesso quando quiser, pela sua conta no Buffer.
:::

O Claude volta à página do plugin e mostra **Conectado** (1).

::: figura Conectado
![Plugin Buffer conectado no Claude](d2-16-claude-conectado.png)
:::

## Etapa 4. As permissões: onde mora a licença

Antes do primeiro uso, abra a aba **Permissões** do plugin. Ela decide quando o Claude precisa da sua aprovação para usar cada ferramenta do Buffer.

::: figura A aba Permissões
![Aba Permissões do plugin Buffer](d2-17-claude-permissoes.png)
O texto do alto explica as duas formas de trabalho do Claude: no modo **Manual**, ele pede a sua aprovação; no modo **Automático**, uma verificação bloqueia o que parecer arriscado, e o resto pode acontecer sem perguntar. Para que ele pergunte sempre, escolha **Sempre perguntar** (1) na linha da ferramenta.
:::

Recomendamos manter **Requer aprovação** em tudo no começo. Para as ferramentas de gravação, em especial **Create Post** ("criar post") e **Delete Post** ("apagar post"), escolha **Sempre perguntar**: clique na lista ao lado do nome da ferramenta (onde está escrito **Requer aprovação**, como no item 1 da figura) e escolha a opção. Assim, nada é criado ou apagado no seu Buffer sem um clique seu, mesmo no modo automático.

| Ferramenta | O que faz | Recomendação | Quando permitir |
|---|---|---|---|
| Get Account, List Channels, List Posts e outras "Get" e "List" | só leem a sua conta, os seus canais e os seus posts | Requer aprovação (ou Sempre permitir, se cansar dos cliques) | sempre que você tiver feito um pedido |
| Create Post | cria um post no Buffer | Sempre perguntar | só se os detalhes mostrarem `saveToDraft` = `true` (rascunho) |
| Edit Post | altera um post existente | Sempre perguntar | quando você pediu a alteração |
| Delete Post | apaga um post | Sempre perguntar | só quando você pediu para apagar aquele post |

## Usando: o pedido sob demanda

Abra uma conversa nova no Claude e peça. O modelo abaixo deixa o post como **rascunho**; nada sai para a rede.

::: prompt Prompt-modelo 2 · Rascunho no Buffer
Use o Buffer. Escreva um post para o meu [LinkedIn] sobre [tema], seguindo estas regras: [cole aqui as regras do prompt-modelo 1]. Salve no meu canal do [LinkedIn] como RASCUNHO. Não agende e não publique. Depois me mostre o texto salvo e o status do post.
:::

O Claude vai chamar as ferramentas do Buffer uma por uma: primeiro para ler a sua conta, depois para listar os canais e, por fim, para criar o post. A cada chamada, aparece um quadro **O Claude quer usar … de Buffer**, com o nome da ferramenta.

::: figura O robô pedindo licença
![Quadro de aprovação de ferramenta no Claude](d2-19-claude-pede-licenca.png)
Os números marcam três opções, não uma ordem. **Permitir uma vez** (1) aprova só esta chamada. **Sempre permitir** (2) aprova esta ferramenta para as próximas vezes. **Recusar** (3) nega. Nas ferramentas que só leem (Get Account, List Channels), permitir é seguro.
:::

::: suaparte
Este clique é seu, e só seu. Quando preparamos este livro, o assistente automatizado que nos ajudava a configurar foi impedido, pelas próprias regras de segurança, de aprovar no lugar da pessoa. Antes de permitir **Create Post**, abra os detalhes do quadro (a setinha ao lado de **Esquema bruto** ou do nome da ferramenta) e confira se aparece `saveToDraft` com o valor `true`, que quer dizer "salvar como rascunho". Se aparecer outra coisa, clique em **Recusar** e repita o pedido dizendo "somente rascunho".
:::

Quando termina, o Claude confirma o que fez.

::: figura O rascunho salvo
![Resposta do Claude confirmando o rascunho no Buffer](d2-20-claude-rascunho-salvo.png)
Repare na última frase: "Nada foi enviado ao LinkedIn."
:::

## Aprovando no Buffer

Abra o Buffer (`publish.buffer.com`). Na barra da esquerda, em **Channels** ("canais"), clique no canal e depois em **Publish**. No alto, clique na aba **Drafts** ("rascunhos") (1). O post está lá, esperando você.

::: figura Os rascunhos no Buffer
![Aba Drafts do Buffer com o rascunho](d2-21-buffer-rascunhos.png)
:::

Leia, edite se precisar (ícone de lápis) e escolha o destino. Os números marcam as duas opções: **Publish Now** ("publicar agora") (1), no menu de três pontos, publica na hora; **Add to Queue** ("pôr na fila") (2) agenda o post para o próximo horário livre da sua fila, que são os horários que o Buffer sugeriu quando você ligou a rede.

::: figura As duas formas de aprovar
![Menu do rascunho com Publish Now e Add to Queue](d2-22-buffer-publicar.png)
:::

::: resultado
No nosso teste, escolhemos **Publish Now**. O Buffer avisou "Post published", o post passou para a aba **Sent** ("enviados") e apareceu no LinkedIn em seguida. Apagamos o post logo depois, como combinado.
:::

::: figura O post na aba Sent e no LinkedIn
![Post enviado no Buffer](d2-23-buffer-enviado.png)
:::

::: figura O post publicado no LinkedIn
![Post de teste no LinkedIn](d2-24-linkedin-publicado.png)
:::

## No ChatGPT

O Buffer também tem plugin para o ChatGPT, e o caminho é parecido. As etapas 1 e 2 (conta no Buffer e redes ligadas) são as mesmas.

::: passo
1. No ChatGPT (`chatgpt.com`), abra a área **Plugins**, na barra da esquerda.
2. Clique na caixa **Procurar plugins** (1), digite **Buffer** e clique no resultado **Buffer**, descrito como "Social media scheduling" (2).
:::

::: figura A busca pelo Buffer nos Plugins do ChatGPT
![Busca por Buffer nos plugins do ChatGPT](d2-31-chatgpt-busca-buffer.png)
:::

::: passo
3. Na página do plugin, clique em **Instalar plugin** (1).
:::

::: figura A página do plugin Buffer no ChatGPT
![Página do plugin Buffer no ChatGPT com o botão Instalar plugin](d2-32-chatgpt-plugin-buffer.png)
O aviso no pé da página explica o que o ChatGPT pode compartilhar com o Buffer quando conectado.
:::

::: suaparte
Depois de instalar, o ChatGPT pede para conectar a sua conta do Buffer. Pela documentação do Buffer, abre-se a mesma tela de autorização da etapa 3, agora com o botão **Connect ChatGPT** ("conectar o ChatGPT"). Leia e, se concordar, clique.
:::

::: figura O plugin instalado
![Página do plugin Buffer já instalado no ChatGPT](d2-33-chatgpt-buffer-instalado.png)
Instalado, o plugin troca o botão por dois: **Gerenciar** (1), onde ficam a conta conectada e as permissões, e **Testar no chat** (2), que abre uma conversa já com o Buffer.
:::

::: atencao Antes do primeiro pedido, decida a licença
Pelo padrão, o ChatGPT mexe no Buffer sem perguntar: no nosso teste, ele criou o rascunho sem pedir nada. Para mudar, clique em **Gerenciar** e, no item **Permissão**, veja as quatro opções da figura abaixo. O padrão é **Permitir ferramentas de baixo risco** (1), e o ChatGPT tratou o rascunho como baixo risco. Se quiser aprovar antes de cada alteração no Buffer, escolha **Permitir ferramentas somente de leitura** (2), que, pela descrição da própria tela, lê sem perguntar e pede antes de alterar, ou **Sempre perguntar** (3). Não escolha **Permitir todas as ferramentas**. Seja qual for a escolha, nada sai do Buffer sem o seu **Publish Now** ou **Add to Queue**.
:::

::: figura As permissões do plugin no ChatGPT
![Opções de permissão do plugin Buffer no ChatGPT](d2-37-chatgpt-permissoes.png)
:::

::: passo
4. Volte à página do plugin e clique em **Testar no chat**. O campo de mensagem já vem com a etiqueta **Buffer** (1). Escreva o pedido abaixo, trocando o texto entre aspas pelo seu post, e envie (2).
:::

::: prompt O pedido que usamos no teste
No meu canal do LinkedIn, salve como RASCUNHO (não agende e não publique) este texto, exatamente assim: "[cole aqui o texto do seu post]". Depois me diga se o rascunho foi salvo.
:::

::: figura O pedido com o Buffer marcado
![Campo de mensagem do ChatGPT com a etiqueta Buffer](d2-34-chatgpt-pedido-rascunho.png)
:::

::: figura A resposta do ChatGPT
![Resposta do ChatGPT confirmando o rascunho no Buffer](d2-35-chatgpt-rascunho-salvo.png)
O ChatGPT mostra cada uso do plugin: primeiro lê os dados da sua conta no Buffer (1), depois cria o rascunho (2). Confira o rascunho no Buffer, na aba **Drafts**, como em "Aprovando no Buffer".
:::

::: resultado
Um rascunho no Buffer, sem data e sem publicação. Testamos este caminho em 20 de novembro de 2026: o ChatGPT salvou o rascunho, conferimos na aba **Drafts** do Buffer e o apagamos em seguida.
:::

## O robô no relógio: a tarefa agendada

Até aqui, você pediu e o robô fez. Com uma **tarefa agendada**, o Claude faz o pedido sozinho, num dia e hora fixos, por exemplo toda segunda às 8h, e deixa os rascunhos da semana no Buffer para você aprovar. As tarefas agendadas exigem plano pago do Claude (a partir do Pro).

::: passo
1. Na barra lateral do Claude, clique em **Agendados** (o item 1 da figura da barra lateral, no começo da etapa 3).
2. Clique em **Nova tarefa** (1) e escolha **Configurar manualmente** (2). A outra opção, **Criar com o Claude**, monta a tarefa conversando com você.
:::

::: figura O menu Nova tarefa
![Página Tarefas agendadas com o menu Nova tarefa aberto](d2-41-claude-nova-tarefa-menu.png)
Abaixo, o Claude sugere modelos prontos, como **Ideias de conteúdo**. Servem de inspiração, mas o nosso pedido é mais preciso.
:::

::: passo
3. Dê um nome à tarefa (1) e cole como instrução o prompt-modelo 8 do capítulo 5 (2).
4. Em **Acionamento**, escolha a frequência (3), por exemplo **Semanal** e **segunda-feira**, e o horário (4). Clique em **Criar** (5).
:::

::: figura A janela Nova tarefa agendada
![Formulário de nova tarefa agendada no Claude](d2-43-claude-nova-tarefa.png)
As frequências possíveis são **A cada hora**, **Diariamente**, **Dias úteis**, **Semanal** e **Mensal**. Prefira um horário alguns minutos antes da hora cheia, como 7h55: o próprio Claude avisa que tarefas marcadas para a hora cheia podem começar com vários minutos de atraso.
:::

::: passo
5. Na página da tarefa, clique em **Executar agora** para ver a primeira rodada sem esperar a segunda-feira. Ela aparece em **Histórico**; clique nela para ler a conversa.
:::

::: figura A primeira rodada da tarefa
![Conversa criada pela tarefa agendada, com o rascunho salvo no Buffer](d2-46-claude-tarefa-execucao.png)
A tarefa vira uma conversa comum. No nosso teste, de 20 de novembro de 2026, ela usou o Buffer (1) e deixou o rascunho (2), que conferimos no Buffer e apagamos em seguida, junto com a tarefa.
:::

::: atencao Na tarefa agendada, o Claude não pergunta antes de usar o Buffer
A janela da tarefa avisa: o Claude "usará conectores sem pausar para aprovação". O modo padrão, **Auto**, executa sem perguntar; no nosso teste, a tarefa criou o rascunho sem pedir licença. Por isso, mantenha no pedido a ordem "salve como RASCUNHO; não agende e não publique". A licença que importa continua com você: nada sai do Buffer sem o seu **Publish Now** ou **Add to Queue**. Se quiser que o Claude pergunte antes, o próprio aviso indica o caminho: marque a ferramenta como **Sempre perguntar** nas configurações do conector. Não testamos esse modo numa tarefa agendada: conte com a tarefa parada até você responder.
:::

::: figura As opções de permissão da tarefa
![Menu de permissões da tarefa agendada: Manual, Auto e Pular todas as aprovações](d2-42-claude-tarefa-permissoes.png)
**Manual** pergunta antes de usar ferramentas novas; **Auto** executa sem perguntar; **Pular todas as aprovações** nunca pausa, nem antes de ações arriscadas. Não use a última.
:::
