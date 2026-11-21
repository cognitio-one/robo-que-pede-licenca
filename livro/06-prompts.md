# Capítulo 5 | Prompts-modelo para a sua profissão

Os modelos deste capítulo funcionam nos três degraus: cole no Claude ou no ChatGPT (degrau 1), peça que o resultado vá para o Buffer (degrau 2) ou copie o texto para o arquivo `perfil.txt` do robô (degrau 3). Troque o que está entre colchetes.

Uma regra vale para todos: **a IA escreve, você responde pelo que sai**. Os modelos já trazem as travas de honestidade ("diga quando não tiver certeza") e de conferência ("liste o que eu preciso conferir"). Não as tire.

## 1. O seu perfil de voz (faça uma vez)

Em vez de explicar quem você é a cada pedido, deixe a IA entrevistar você e escrever um perfil que você reutiliza sempre.

::: prompt Prompt-modelo 3 · Entrevista para o perfil de voz
Quero que você me ajude a escrever o meu "perfil de voz" para redes sociais. Faça-me perguntas, uma de cada vez, e espere a minha resposta antes da próxima. Pergunte sobre: minha profissão e área; meu público; as redes que uso; o tom que quero (formal, próximo, didático); palavras e assuntos que eu não quero ver; exemplos de posts que gosto. Depois de no máximo dez perguntas, escreva o perfil em até 15 linhas, em tópicos, começando por "Escreva como". Não invente nada que eu não tenha dito.
:::

Guarde o resultado num arquivo de texto ou nas suas notas. No degrau 1, cole o perfil no começo de cada conversa. No degrau 3, ele vira o arquivo `perfil.txt`.

## 2. O calendário do mês

::: prompt Prompt-modelo 4 · Calendário editorial
[Cole aqui o seu perfil de voz.]

Monte um calendário de [8] posts para [mês], para o [LinkedIn e o Instagram], com [2] posts por semana. Para cada post, dê: a data sugerida, a rede, o tema em uma linha e o objetivo (informar, explicar uma dúvida comum, mostrar bastidores). Varie os temas. Não repita o mesmo assunto na mesma semana. Entregue em tabela com as colunas data;hora;rede;tema, separadas por ponto e vírgula, pronta para colar numa planilha.
:::

::: porque Por que a tabela com ponto e vírgula
É o formato que o Excel brasileiro abre direto e o mesmo da `pauta.csv` do robô. No degrau 3, você cola a tabela na pauta e roda `python robo.py escrever`.
:::

### Temas que costumam funcionar

| Profissão | Ideias de tema (informativo, sem oferta de serviço) |
|---|---|
| Advocacia | o que levar à primeira conversa com um advogado; como ler uma notificação extrajudicial; a diferença entre prazo e data de audiência; cuidados ao assinar um contrato de aluguel |
| Contabilidade | como organizar os documentos do mês para o contador; a diferença entre pró-labore e distribuição de lucros; o calendário de obrigações explicado em linguagem simples; o que muda quando a empresa cresce de faixa |
| Empresa | bastidores de um processo da equipe; resposta a uma pergunta frequente de clientes; uma lição aprendida no mês; como funciona a garantia ou a troca |

## 3. Um carrossel para o Instagram

::: prompt Prompt-modelo 5 · Carrossel
[Cole aqui o seu perfil de voz.]

Escreva o texto de um carrossel de [6] telas para o Instagram sobre [tema]. Tela 1: uma pergunta ou frase que prenda, com no máximo 10 palavras. Telas 2 a 5: um ponto por tela, com no máximo 30 palavras cada. Tela 6: um resumo em uma frase, sem pedir contato. Depois, escreva a legenda do post com no máximo 600 caracteres. Se não tiver certeza de um fato, diga. No fim, liste o que eu preciso conferir.
:::

O texto das telas você leva para uma ferramenta de design (o Canva, por exemplo) ou pede a uma IA de imagens. Confira sempre a imagem antes de publicar: IAs de imagem ainda erram letras.

## 4. Um conteúdo, várias redes

::: prompt Prompt-modelo 6 · Adaptar para cada rede
Abaixo está um texto meu. Adapte para três redes, respeitando o jeito de cada uma: LinkedIn (até 1.300 caracteres, tom profissional), Instagram (legenda até 600 caracteres, mais próxima) e X (até 260 caracteres). Mantenha os fatos exatamente como estão; não acrescente nenhum dado novo. Texto: [cole aqui].
:::

## 5. O revisor rigoroso (use antes de publicar)

Peça a uma conversa nova, sem o histórico da que escreveu o post, que faça a revisão. Uma conversa limpa não "defende" o próprio texto.

::: prompt Prompt-modelo 7 · Revisão ética e de fatos
Você é um revisor rigoroso de publicações de [advogado / contador / empresa] no Brasil. Leia o post abaixo e aponte, em lista: (1) qualquer afirmação de fato, número, data, lei ou decisão que precise de conferência em fonte oficial; (2) qualquer trecho que ofereça serviço, fale de preço ou honorários, prometa resultado, se compare a colegas ou identifique cliente; (3) qualquer dado pessoal. Não reescreva o post. Para cada ponto, cite o trecho exato. Post: [cole aqui].
:::

::: atencao O revisor também é IA
Ele ajuda a enxergar, mas não substitui a sua leitura nem a fonte oficial. Se o revisor disser que uma lei diz tal coisa, confira a lei.
:::

## 6. O pedido semanal (degrau 2)

Este modelo é para usar com o Buffer conectado ao Claude, sob demanda ou numa tarefa agendada.

::: prompt Prompt-modelo 8 · Rascunhos da semana no Buffer
Use o Buffer. [Cole aqui o seu perfil de voz.] Escreva [3] posts para a próxima semana, um por tema: [tema 1], [tema 2], [tema 3]. Salve cada um como RASCUNHO no meu canal do [LinkedIn]. Não agende e não publique nada. No fim, liste os rascunhos salvos, com o texto de cada um, e o que eu preciso conferir antes de aprovar.
:::
