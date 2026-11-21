# O robô que pede licença

> Guia prático, do zero, para usar a sua inteligência artificial (Claude ou ChatGPT)
> e publicar nas redes sociais (Instagram, Facebook, LinkedIn e X), por agendamento
> ou sob demanda. Para advogados, contadores e empresários que nunca configuraram nada.

**Comece pelo livro:** [`O-robo-que-pede-licenca.pdf`](O-robo-que-pede-licenca.pdf).
Ele é ilustrado com telas reais, passo a passo, e não exige conhecimento prévio.

## A ideia

O robô propõe; você aprova; ele publica. Nada vai ao ar sem a sua licença, a menos que
você decida o contrário de forma consciente. Não é só cautela: é o que pedem as regras
das plataformas (o LinkedIn, por exemplo, veda automatizar publicações pela API) e as
normas de publicidade das profissões.

## Os três degraus

| Degrau | O que é | Precisa de código? |
|---|---|---|
| 1. A IA escreve, você agenda | prompt-modelo no Claude ou no ChatGPT; agendamento nativo do LinkedIn, do X e da Meta | não |
| 2. O robô de conversa | o Claude (ou o ChatGPT) deixa rascunhos no Buffer pelo conector oficial; você aprova | não |
| 3. O robô próprio | a IA (Claude Code ou Codex) escreve um programa em Python que publica pelas APIs oficiais, com aprovação numa planilha e o Agendador de Tarefas do Windows | a IA escreve por você |

## O que há neste repositório

| Caminho | Conteúdo |
|---|---|
| `O-robo-que-pede-licenca.pdf` | o livro |
| `prompts/PROMPT-MESTRE.txt` | o pedido que você cola no Claude Code ou no Codex para criar o robô, com a ficha técnica conferida |
| `robo-feito-pelo-claude/` | o robô que o Claude escreveu a partir do prompt-mestre, com testes e a revisão feita pelo Codex |
| `robo-feito-pelo-codex/` | o robô que o Codex escreveu a partir do mesmo prompt, com testes e a revisão feita pelo Claude |
| `livro/` | o texto-fonte do livro, capítulo por capítulo |
| `figuras/` | as telas usadas no livro, já sem dados pessoais |

Os dois robôs fazem a mesma coisa: `escrever`, `publicar`, `publicar-agora`, `conferir`,
`autorizar-x`, sempre com a opção `--ensaio`, que mostra o que seria enviado sem enviar.
O LinkedIn só sai por `publicar-agora`, de propósito.

**Primeiro contato, sem chave e sem custo** (Windows, com Python instalado), dentro da pasta
`robo-feito-pelo-codex`:

```
python -m pip install -r requirements.txt
copy config.exemplo.env config.env
python robo.py publicar --ensaio
```

## Como foi testado

- Documentação oficial de Anthropic, OpenAI, Microsoft, Meta, LinkedIn, X e Buffer
  conferida em 20/11/2026, com trecho literal e endereço de cada afirmação.
- Degrau 1: telas reais de agendamento do LinkedIn e do X, até o botão de programar, sem publicar.
  No Business Suite da Meta, um post com imagem foi programado de verdade para o Facebook e o
  Instagram e apagado em seguida na aba Programados (a imagem foi anexada por programa, não pela
  janela de arquivos do Windows).
- Degrau 2: caminho completo numa conta nova do Buffer, com uma publicação real de teste
  no LinkedIn, apagada em seguida. O mesmo pedido de rascunho foi feito pelo ChatGPT, e uma
  tarefa agendada do Claude rodou e deixou o rascunho; tudo conferido no Buffer e apagado.
- Degrau 3: o mesmo prompt-mestre entregue ao Claude e ao Codex em pastas vazias; os dois
  robôs passaram nos próprios testes e no ensaio, foram revisados pela outra IA, corrigidos
  e revisados de novo. Os dois leem a planilha salva pelo Excel (testado com o Excel de verdade).
  Com o robô do Codex, houve **publicação real de teste no LinkedIn e no X** (`publicar-agora`)
  **e no Facebook pelo Agendador de Tarefas do Windows**, todas apagadas em seguida.
- Instagram: apps novos da Meta só aceitam a configuração com login unificado, que os robôs,
  feitos pela ficha antiga, não conheciam. Os dois robôs foram ajustados depois (chave
  `INSTAGRAM_USER_ID`, host `graph.facebook.com`, espera da imagem antes de publicar); o código
  novo passou nos testes automáticos (hoje 40 no robô do Claude e 113 no do Codex) e numa
  revisão do Codex, sem falha grave. Com ele, houve **publicação real de teste no Instagram**:
  duas pelo robô do Codex e uma pelo do Claude, todas apagadas em seguida pelo Instagram (a API
  não apaga). O `PROMPT-MESTRE.txt` foi atualizado com esse caminho, mas ainda não foi entregue
  de novo a uma IA numa pasta vazia. Antes de usar com as suas contas, rode o `--ensaio` e leia
  o `LEIA-ME.txt`.
- Leitura de teste: o Codex e o Copilot (Microsoft) leram o livro, separadamente, no papel de
  uma contadora que nunca configurou nada, em três rodadas. Nota na terceira, já com os testes reais,
  para "eu conseguiria fazer sozinha": Copilot 8, 5 e 1 (degraus 1, 2 e 3); Codex 7, 6 e 1 (os dois
  dão 9 ao degrau 1 só com o LinkedIn). Ainda faltam um caminho completo para o Instagram e mais
  figuras nas telas técnicas do degrau 3, que é avançado e pede um ajudante na primeira vez.

## Licença e atribuição

Licenciamento duplo, como explicado no arquivo `NOTICE`: código e prompts sob
**AGPL-3.0** (`LICENSE`); texto e figuras sob **CC BY-SA 4.0** (`LICENSE-DOCS`).
Uso pessoal não gera obrigação nenhuma. Se redistribuir, preserve a atribuição.

Marcas citadas pertencem aos seus titulares. Este material é independente e não é
endossado por Anthropic, OpenAI, Microsoft, Meta, LinkedIn, X ou Buffer.

---

cognitio.one · *Tudo verificável; nada sem você.*
