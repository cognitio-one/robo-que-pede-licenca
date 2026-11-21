# Capítulo 7 | Quando algo dá errado

Procure na coluna da esquerda o que você está vendo. As mensagens entre aspas são as que as próprias plataformas mostram, segundo a documentação oficial, ou as que o robô do degrau 3 escreve.

## No degrau 1 e no degrau 2

| O que você vê | O que costuma ser | O que fazer |
|---|---|---|
| A IA escreveu algo que você sabe que está errado | a IA "preencheu" uma lacuna com um fato inventado | corrija você mesmo; peça na conversa: "o dado X está errado, use só o que eu informei"; use o prompt-modelo 7 numa conversa nova |
| O botão de agendar não aparece | a rede mudou a tela, ou o seu tipo de conta não tem o recurso | procure por um ícone de relógio ou calendário perto do botão de publicar; no X, a opção pode depender da conta |
| O Claude não encontra o Buffer | o plugin não foi adicionado, ou a conexão caiu | volte a **Plugins**, abra o Buffer e confira se diz **Conectado**; se não, clique em conectar de novo |
| O Claude pede licença a cada passo | é o comportamento padrão, e é bom | se quiser menos cliques, use **Sempre permitir** só nas ferramentas de leitura; mantenha as de gravação pedindo aprovação |
| O Buffer não deixa agendar mais | o plano grátis guarda até 10 posts agendados por canal | espere sair um dos posts agendados, ou apague um post agendado de que você não precisa mais |
| O post do Instagram não sai sozinho pelo Buffer | a conta do Instagram é pessoal | mude para conta profissional (capítulo 1); com conta pessoal, o Buffer só manda lembrete |

## No degrau 3 (o robô próprio)

| O que você vê | O que costuma ser | O que fazer |
|---|---|---|
| "python não é reconhecido como comando" | o Python não foi instalado, ou o Terminal foi aberto antes da instalação | instale (degrau 3, Parte A3) e abra um Terminal **novo** |
| Digitar `python` abre a Microsoft Store | atalho do Windows para a loja | desligue os aliases de execução do Python em Configurações (degrau 3, Parte A3) |
| "No module named requests" (ou anthropic, openai) | faltam as bibliotecas do robô | na pasta do robô: `python -m pip install -r requirements.txt` |
| O robô diz que falta uma chave | a linha do `config.env` está vazia ou com espaço sobrando | abra `notepad config.env`, confira a linha, salve |
| LinkedIn: erro 401 | o token venceu (vale 60 dias) ou foi gerado sem `w_member_social` | gere outro no Token Generator, marcando os três escopos |
| X: "Callback URL not approved for this client application" | o endereço de retorno no app do X não é exatamente `http://127.0.0.1:8080/callback` | corrija em **Settings** do app, com 127.0.0.1 e sem barra sobrando |
| X: as chamadas falham por limite de uso | os créditos acabaram | compre créditos em **Buy Credits** no console do X |
| Instagram: erro ao criar a mídia | a imagem não está num endereço público ou não é JPEG | teste o link da imagem numa janela anônima do navegador; converta para JPEG |
| A linha ficou com status de alerta (ERRO, REVISAR ou VERIFICAR, conforme o robô) | a rede recusou a publicação, ou o robô não conseguiu confirmar se ela saiu | leia a coluna `resultado` e o `registro.log`; **confira na própria rede se o post saiu** antes de voltar o status para APROVADO, para não publicar duas vezes |
| A planilha abriu toda numa coluna só | o Excel não reconheceu o ponto e vírgula | no Excel, use a importação de texto (menu **Dados**) e escolha "ponto e vírgula" como separador |

::: atencao Quando nada disso resolve
Copie a mensagem de erro inteira, **apague dela qualquer chave ou token**, e cole no Claude Code (ou no Codex) aberto na pasta do robô: "deu este erro; explique em português simples e corrija". Foi a IA que escreveu o robô; ela também sabe consertar.
:::
