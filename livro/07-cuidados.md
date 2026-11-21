# Capítulo 6 | Cuidados: profissão, dados e plataformas

Um robô que publica bem e publica errado faz o erro chegar mais longe e mais rápido. Este capítulo reúne, em linguagem simples, as regras que mais pesam para quem publica com ajuda de IA. Cada ponto traz a norma de onde saiu, para você conferir na fonte. Ele não substitui a leitura das normas nem a orientação do seu conselho profissional.

## Para a advocacia

A publicidade do advogado é regida pelo **Provimento nº 205/2021** do Conselho Federal da OAB e pelo **Código de Ética e Disciplina da OAB**. O ponto de partida está no art. 3º do Provimento:

> "A publicidade profissional deve ter caráter meramente informativo e primar pela discrição e sobriedade, não podendo configurar captação de clientela ou mercantilização da profissão [...]"

Na prática, para posts escritos com IA:

::: regra O que o advogado pode e não pode postar
- **Pode** publicar conteúdo jurídico informativo: explicar um tema, um direito, um procedimento (Provimento 205/2021, art. 3º, caput, e art. 4º; Anexo Único, item sobre criação de conteúdo).
- **Não pode** mencionar valores de honorários, forma de pagamento, gratuidade ou descontos como forma de captar clientes (art. 3º, I).
- **Não pode** prometer resultados nem usar casos concretos para oferecer a sua atuação (art. 6º e parágrafo único; art. 4º, § 2º). Também **não pode** usar expressões persuasivas, de autoengrandecimento ou de comparação (art. 3º, IV).
- **Impulsionar** (pagar para o post alcançar mais gente) é permitido, desde que o post não ofereça serviços jurídicos (Anexo Único do Provimento, item sobre patrocínio e impulsionamento); é vedado usar meios que inflem o alcance de forma fraudulenta (art. 4º, § 5º).
- **Robô que responde consultas** jurídicas automaticamente a quem não é cliente não é admitido de forma indiscriminada (Anexo Único, item sobre aplicativos para responder consultas jurídicas). Este livro trata de robôs que **publicam** conteúdo, não de robôs que dão consultas.
:::

Sobre a própria IA, o Conselho Federal da OAB editou a **Recomendação nº 001/2024**. Ela recomenda, entre outros pontos, cuidado com o sigilo ao inserir informações em sistemas de IA (item 2.1) e supervisão humana sobre o uso da IA (itens 3.1 e 3.3). É uma recomendação, não uma regra com punição prevista no próprio texto. O item 2.1 diz:

> "Ao incluir informações em sistemas de IA, o(a) advogado(a) deve zelar pela confidencialidade e sigilo profissional dos dados apresentados, devendo o profissional ter especial atenção ao inserir dados que possam inadvertidamente tornar o cliente identificável."

## Para a contabilidade

O **Código de Ética Profissional do Contador (NBC PG 01)**, do Conselho Federal de Contabilidade, trata da publicidade nos itens 11 a 15.

::: regra O que o contador deve observar
- A publicidade deve ser técnica, científica e meramente informativa, moderada e discreta, sem mercantilização (itens 11 e 12).
- Guarde as provas do que afirmar: dados fáticos, técnicos e científicos (item 13).
- Não faça afirmações desproporcionais sobre os seus serviços, capacitação ou experiência, nem comparações depreciativas (item 15).
- Informe número de registro, nome e categoria profissional em todo anúncio (item 4, alínea r).
- Não faça referência a cliente, com quebra de sigilo, em publicação que mencione o seu trabalho (item 5, alínea o); a relação de clientes só pode ser indicada quando autorizada por eles (item 6, alínea d).
:::

## Para todos: dados pessoais

A **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)** define dado pessoal como a informação relacionada a pessoa natural identificada ou identificável (art. 5º, I), e manda tratar só o necessário para a finalidade (art. 6º, III).

Para quem publica com IA, a nossa orientação prática a partir da lei se resume a duas regras:

1. **Não ponha dado de cliente no pedido à IA.** Nome, CPF, número de processo, valores e detalhes que permitam identificar alguém ficam fora do prompt.
2. **Não ponha dado de cliente no post.** Nem "para ilustrar", nem com nome trocado se os detalhes ainda permitirem reconhecer a pessoa.

## As regras das plataformas

| Plataforma | O que diz, em resumo | Onde conferir |
|---|---|---|
| LinkedIn | os termos da API vedam automatizar publicações; o contrato do usuário veda robôs não autorizados para publicar | Termos de Uso da API (seção 3.1) e Contrato do Usuário (seção 8.2) |
| X | conta que publica de forma automatizada deve ativar o rótulo **Automated** ("automatizada"), dizer na biografia que é automatizada e quem a opera, e ser ligada a uma conta humana; nada de menção não solicitada nem de texto repetido em várias contas | diretrizes de automação na documentação do X |
| Meta (Instagram e Facebook) | spam é proibido; publicar em nome de alguém exige consentimento | Políticas para Desenvolvedores da Meta |
| Anthropic (Claude) | proíbe spam, engano e perfis falsos; quem usa responde pelos agentes que põe para trabalhar | Política de Uso da Anthropic |
| OpenAI (ChatGPT) | proíbe engano, fraude, spam e fingir ser outra pessoa; responsabiliza quem faz uso inadequado | Políticas de Uso da OpenAI |

::: atencao O rótulo de conta automatizada no X
Se o seu robô publica sozinho no X (degrau 3, no relógio), a documentação do X pede para ativar o rótulo **Automated** no perfil, em **Settings**, **Your account**, **Automation**. Uma página da documentação trata o rótulo como obrigação, e outra, como opção. Na dúvida, ative.
:::
