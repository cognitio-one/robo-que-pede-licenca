# Abertura | Antes da primeira tecla

Este guia é para quem nunca configurou nada. Se você é advogado, contador ou empresário e as palavras "conta de desenvolvedor", "chave" ou "token" soam como outra língua, você está no lugar certo. Vamos começar do zero e explicar cada termo na hora em que ele aparecer; os que ficarem para trás estão no capítulo 1.

O objetivo é um só: fazer a sua inteligência artificial (o **Claude**, da empresa Anthropic, ou o **ChatGPT**, da empresa OpenAI) trabalhar nas suas redes sociais. Ela escreve, organiza o calendário, prepara a publicação e, se você quiser, publica. Chamamos de **robô** o conjunto que faz isso por você, do jeito que você combinou.

## O robô que pede licença

Há um detalhe que atravessa o livro inteiro. O robô que vamos montar **não publica nada sem a sua aprovação**, a menos que você decida o contrário de forma consciente. Ele propõe; você aprova; ele publica.

Isso não é excesso de zelo. É o que as próprias plataformas e as profissões pedem. O LinkedIn proíbe que programas automatizem publicações pela porta técnica que ele oferece aos desenvolvedores. A OAB e o Conselho Federal de Contabilidade têm regras de publicidade. E a inteligência artificial erra: às vezes inventa um número, às vezes erra uma data. O seu olho é a última barreira entre o erro e o público.

## Os três degraus

Você não precisa subir até o topo. Cada degrau já entrega um resultado completo.

| | O que é | Você vai precisar de | Custo de partida | Tempo estimado |
|---|---|---|---|---|
| **Degrau 1** | A IA escreve; você agenda no próprio site da rede | conta na IA e nas redes | zero | meia hora |
| **Degrau 2** | O robô de conversa: você pede à IA, e ela deixa os posts prontos num serviço de agendamento chamado **Buffer**, para você aprovar | conta grátis no Buffer | zero | uma hora |
| **Degrau 3** (avançado) | O robô próprio: a IA escreve um pequeno programa que publica sozinho, no horário, depois da sua aprovação | Windows, um plano pago de IA e paciência | alguns dólares por mês | uma tarde, de preferência com ajuda |

O degrau 1 resolve a maior parte das necessidades. O degrau 2 é o que recomendamos para quem quer um robô sem programar. O degrau 3 é para quem quer controle total e custo mínimo por publicação; é o caminho que nós usamos, mas ele exige lidar com telas técnicas. Se é a sua primeira vez, faça os degraus 1 e 2 antes.

## Por onde começar

Primeiro, leia o **capítulo 1** (<a class="pg" href="#02-vocabulario"></a>). Ele explica as palavras e as contas de que todos os degraus precisam. Depois, encontre a sua linha na tabela:

| Se você... | Vá para |
|---|---|
| quer só que a IA escreva melhor e mais rápido, e não se importa de colar o texto e marcar o horário | Degrau 1 (<a class="pg" href="#03-degrau-1"></a>) |
| quer pedir em uma frase ("prepare os posts da semana") e só aprovar | Degrau 1 e depois Degrau 2 (<a class="pg" href="#04-degrau-2"></a>) |
| publica muito, em várias redes, e quer o robô no relógio | os três degraus, nesta ordem; o Degrau 3 começa na <a class="pg" href="#05-degrau-3"></a> |
| só precisa dos textos prontos para pedir à IA | Prompts-modelo (<a class="pg" href="#06-prompts"></a>) |
| é advogado ou contador | leia também os Cuidados (<a class="pg" href="#07-cuidados"></a>) antes de publicar |

::: atencao Claude ou ChatGPT?
Os dois servem. O degrau 1 funciona igual nos dois. No degrau 2, o livro mostra o caminho no Claude, que testamos do começo ao fim, e indica o caminho equivalente no ChatGPT. Se você já assina o ChatGPT, não precisa trocar: use o que já tem.
:::

## O que você vai precisar

- Um computador com **Windows 10 ou 11** e acesso à internet. Para saber qual é o seu, aperte a tecla do Windows, digite `winver` e aperte **Enter**: abre uma janela pequena com a versão. Os degraus 1 e 2 funcionam em qualquer computador com navegador.
- Um **navegador**, que é o programa com que você abre sites: o Google Chrome ou o Microsoft Edge. As imagens deste livro foram feitas no Chrome.
- Um **e-mail** que você abre todos os dias. Várias contas vão mandar códigos de confirmação para ele.
- O **celular** com você. Algumas redes confirmam a sua identidade por mensagem de texto (SMS).

## Os arquivos prontos

Tudo o que este livro manda copiar (os prompts, o modelo de planilha, o pedido completo do degrau 3) está num endereço público na internet, pronto para baixar, sem precisar selecionar texto no PDF:

**github.com/cognitio-one/robo-que-pede-licenca**

::: figura O endereço dos arquivos, para abrir pelo celular
![QR code do repositório](qr-repositorio.png)
Aponte a câmera do celular para o quadrado. O site é o GitHub, um serviço onde se guardam arquivos e programas; você não precisa criar conta para baixar.
:::

## Como ler este guia

Cada passo vem numerado. Nas imagens das telas (os "prints"), os **círculos verdes numerados** correspondem aos números do texto logo acima ou da legenda: o círculo 1 é o item 1. Quando os círculos marcam opções diferentes, e não uma ordem de cliques, a legenda avisa. Os contornos verdes destacam o que você deve conferir.

Cinco caixas aparecem com frequência:

::: suaparte
Coisas que só você pode fazer: digitar uma senha, receber um código no celular, clicar em "Permitir". Nenhum robô deve fazer isso por você.
:::

::: atencao
Um ponto onde iniciantes costumam errar, ou uma regra que pode custar caro se for ignorada.
:::

::: resultado
Como saber que deu certo: o que deve aparecer na tela depois do passo.
:::

::: prompt
O texto que você copia e cola na inteligência artificial. Troque o que estiver entre colchetes [assim] pelos seus dados, apagando os colchetes.
:::

::: comando
O que você digita no Terminal, a janela de comandos do Windows. Só aparece no degrau 3.
:::

::: atencao Se a tela mudou
As plataformas trocam botões de lugar e de nome. Tudo aqui foi conferido nas telas reais e na documentação oficial em 20 de novembro de 2026. Se um botão não estiver onde a figura mostra: (1) procure um ícone com o mesmo desenho perto do lugar indicado; (2) use a busca da própria página ou da central de ajuda da rede, digitando a palavra (por exemplo, "agendar"); (3) pergunte à sua IA, descrevendo a tela: "no LinkedIn, onde fica hoje o botão de agendar publicação?".
:::
