# Fechamento da Lotofácil — desenho

Data: 22/08/2026
Estado: aprovado para planejamento

## Problema

O motor de pontuação do site não melhora a chance de acerto. Um backtest de
200 concursos (3557 a 3756), gerando cada palpite apenas com os dados
anteriores àquele sorteio, mostrou:

| estratégia | média de acertos | faixas premiadas |
|---|---|---|
| jogo campeão | 9,035 | 17× 11ac · 3× 12ac · 1× 13ac |
| jogo gerado | 9,040 | 20× 11ac · 4× 12ac · 1× 13ac |
| aleatório | 9,035 | 19× 11ac · 2× 12ac |
| teoria | 9,000 | — |

Empate. E não poderia ser diferente: todo jogo de 15 dezenas tem média de
exatamente 9 acertos, qualquer que seja o critério de escolha.

O que ainda não existe no site é a única alavanca legítima da Lotofácil: o
**fechamento**. Escolher mais dezenas do que cabem num jogo e distribuir os
descartes de modo a obter uma **garantia matemática** de faixa premiada.

A Caixa vende apostas de 16 a 20 dezenas cobrando todas as combinações
(18 dezenas = 816 jogos = R$ 2.856). A mesma garantia sai por R$ 17,50 com
apenas 5 jogos bem escolhidos.

## Objetivo

Uma página dedicada em `sortelabs.com.br/fechamento.html` que:

1. Explica o que é fechamento em linguagem simples
2. Monta o fechamento do visitante, com garantia declarada e verificada
3. Mantém um placar público comparando um fechamento do jogo campeão contra
   um fechamento aleatório, sorteio a sorteio
4. Mostra a conta acumulada dos dois lados, em dinheiro real

O item 4 é o coração. O placar existe para **demonstrar que os dois empatam** —
é a mesma tese do Desafio do Campeão, com números maiores e mais visíveis.

## Não é objetivo

- Prometer aumento de chance. Não existe e a página dirá isso explicitamente.
- Estender fechamento às outras sete loterias. Só Lotofácil nesta entrega.
- Guardar fechamentos montados por visitantes. Sem dados de terceiros.
- Alterar o comportamento do Desafio do Campeão, dos geradores ou das oito
  páginas de loteria existentes.

## A matemática

Com `n` dezenas escolhidas, cada jogo de 15 descarta `m = n - 15` delas.
Se `d` das suas `n` dezenas forem sorteadas, um jogo que descarta o conjunto
`T` acerta `d - |T ∩ sorteadas|`.

Para garantir `alvo` acertos é preciso que, para **todo** conjunto `U` de
não-sorteadas dentro das suas `n` (com `|U| = n - d`), exista algum descarte
escolhido `T` com `|T ∩ U| ≥ m - d + alvo`.

### Insight de arquitetura

Os padrões são **posicionais**. "Descarte as posições 0, 1 e 2" vale para
qualquer conjunto de 18 dezenas. Logo os padrões são calculados uma vez,
verificados por força bruta e embarcados como tabela constante. O navegador
nunca resolve combinatória.

### Presets

| id | dezenas | jogos | custo | garantia |
|---|---|---|---|---|
| `18-5` | 18 | 5 | R$ 17,50 | 11 se 13 saírem · 12 se 14 · 12 se 15 |
| `18-6` | 18 | 6 | R$ 21,00 | 11 se 13 saírem · 12 se 14 · **13 se 15** |
| `17-7` | 17 | 7 | R$ 24,50 | 11 se 12 saírem |
| `18-12` | 18 | 12 | R$ 42,00 | 11 se **12** saírem (1 em 4) |

Os padrões `18-5` e `18-6` já estão verificados e são regulares — trios
disjuntos consecutivos:

```
18-5   descarta {0,1,2} {3,4,5} {6,7,8} {9,10,11} {12,13,14}
       posições 15, 16 e 17 entram em todos os jogos
18-6   descarta {0,1,2} {3,4,5} {6,7,8} {9,10,11} {12,13,14} {15,16,17}
```

Os padrões `17-7` e `18-12` vêm de busca gulosa e são irregulares. Serão
gerados por `robo/gerar_padroes.py`, verificados por força bruta e **congelados**
na tabela. Nenhum padrão entra em produção sem passar na verificação.

### Aviso obrigatório na página

A garantia mínima paga trocado: 11 acertos valem cerca de R$ 7. Gastar
R$ 17,50 para garantir R$ 7 uma vez a cada 16 sorteios é mau negócio se
apresentado como oportunidade.

O valor real do fechamento é a **concentração**: quando você acerta bastante,
fatura em vários jogos de uma vez em vez de um só. A garantia é o piso, não
o objetivo. A página dirá isso com todas as letras, no mesmo bloco em que
apresenta a garantia — nunca em nota de rodapé.

## Arquitetura

### Arquivos novos

| arquivo | papel |
|---|---|
| `fechamento.html` | a página |
| `js/fechamento.js` | motor: tabela de padrões, montagem, avaliação |
| `js/paginafechamento.js` | lógica da página (formulário, placar) |
| `robo/fechamento.py` | espelho Python do motor, usado pelo robô |
| `robo/gerar_padroes.py` | gera e verifica os padrões irregulares |
| `robo/testar_fechamento.py` | testes |
| `dados/fechamento.json` | pendente, histórico e rateios |

O par `fechamento.js` ↔ `fechamento.py` segue o padrão já estabelecido por
`motor.js` ↔ `gerador_loterias.py`: mesma lógica em duas linguagens, com teste
de paridade.

### Arquivos alterados

| arquivo | mudança |
|---|---|
| `robo/atualizar.py` | chama o novo passo depois da Lotofácil |
| `robo/campeao.py` | expõe `pool_campeao(slug, concursos, tamanho)` |
| `robo/gerar_paginas.py` | inclui `fechamento.html` no sitemap |
| `index.html` | link para a página nova |
| `lotofacil.html` | link para a página nova |
| `css/estilo.css` | estilos do placar e da conta |
| `teste.html` | roda os testes de JS do fechamento |

## Interfaces

### `js/fechamento.js` / `robo/fechamento.py`

```
PADROES[id] -> { dezenas, jogos, custo, descartes: [[int]], garantias: [{d, acertos}] }

montar(dezenas, id) -> [[int]]
    dezenas: lista ordenada de tamanho PADROES[id].dezenas
    devolve um jogo por descarte, cada um com 15 dezenas ordenadas

avaliar(jogos, resultado, rateio) -> { acertos: [int], premios: {faixa: qtd}, retorno: float }
    acertos: um valor por jogo, na mesma ordem
    premios: quantos jogos caíram em cada faixa de 11 a 15
    retorno: soma sobre TODOS os jogos premiados, não sobre as faixas
```

Cada jogo é uma aposta independente e paga por si. Um fechamento com três
jogos de 11 acertos recebe três vezes o rateio de 11 — é o caso comum, não a
exceção, e é justamente daí que vem o ganho de concentração.

### `robo/campeao.py`

```
pool_campeao(slug, concursos, tamanho) -> [int]
    O jogo campeão mais as dezenas seguintes do ranking de pontuação, até
    completar `tamanho`. Determinístico. Para tamanho == k devolve o próprio
    jogo campeão.
```

### Sorteio auditável do controle aleatório

O lado aleatório precisa ser reproduzível por qualquer pessoa, senão o
experimento não vale nada. `random.Random` do Python não serve: a
implementação pode mudar entre versões e não existe equivalente em JS.

Definimos um PRNG explícito, implementado igual nas duas linguagens:

```
mulberry32(semente) -> gerador de floats em [0, 1)
dezenas_aleatorias(semente, quantidade, lo, hi) -> [int]
    Fisher-Yates sobre lo..hi usando mulberry32, pega as `quantidade`
    primeiras, devolve ordenado.
```

A semente é o **número do concurso alvo**. Para o concurso 3757, a semente é
3757. A regra e o código do PRNG ficam publicados na própria página, para que
qualquer um confira.

O teste de paridade Python ↔ JS cobre esse gerador.

## Dados

### `dados/fechamento.json`

```json
{
  "preset": "18-5",
  "pendente": {
    "apos": 3756,
    "campeao": { "dezenas": [2, 3, 5, "..."] },
    "aleatorio": { "dezenas": [1, 4, 6, "..."], "semente": 3757 }
  },
  "historico": [
    {
      "concurso": 3757,
      "data": "09/08/2026",
      "resultado": [1, 2, 4, "..."],
      "rateio": { "11": 7.0, "12": 14.0, "13": 35.0, "14": 1341.42, "15": 565758.41 },
      "campeao":   { "dezenas": ["..."], "acertos": [11, 10, 10, 9, 10], "retorno": 7.0 },
      "aleatorio": { "dezenas": ["..."], "acertos": [10, 9, 10, 10, 8], "retorno": 0.0 }
    }
  ]
}
```

**A conta acumulada não é gravada.** Gasto, retorno e saldo são calculados na
hora pela página, a partir do histórico. Dado derivado gravado sai do ar com o
tempo; recalcular é barato e nunca diverge. O robô não calcula a conta — ele
não exibe nada, só grava o histórico de onde ela sai.

Concursos cujo rateio não veio entram no gasto mas não no retorno, o que
distorce o saldo. A página conta esses casos e informa quantos são, em vez de
apresentar um saldo silenciosamente errado.

O gasto por sorteio é `PADROES[preset].custo` por lado — hoje R$ 17,50.

### Rateio

Os valores de prêmio vêm de `listaRateioPremio` na resposta da API da Caixa
para aquele concurso, e ficam gravados junto do resultado. São dinheiro real
daquele sorteio, não estimativa. Se o rateio não vier na resposta, o concurso
é conferido normalmente e o retorno fica `null` — a página mostra os acertos
e omite o valor, em vez de inventar um.

## Fluxo do robô

Em `atualizar.py`, dentro do laço, logo após `atualizar_desafio` para a
Lotofácil:

1. **Confere o pendente.** Enquanto existir concurso `pendente.apos + 1` nos
   dados, monta os jogos dos dois lados, conta acertos, busca o rateio,
   grava no histórico.
2. **Crava o próximo.** Calcula as 18 dezenas do campeão com
   `pool_campeao("lotofacil", corte, 18)`, usando apenas concursos até o que
   acabou de ser conferido — nunca olhando o futuro. Sorteia as 18 do controle
   com semente igual ao número do próximo concurso.
3. **Grava** `dados/fechamento.json`.

O passo repete em laço, igual ao Desafio, para o caso de o robô ficar dias
sem rodar e precisar recuperar vários concursos de uma vez.

Falha nesse passo é capturada e registrada sem derrubar o resto da rodada,
seguindo o tratamento que `atualizar.py` já dá ao Desafio e ao CSV.

## A página

Quatro blocos, nesta ordem:

1. **O que é fechamento** — a explicação dos grupinhos, com o exemplo visual
   dos cinco descartes. Linguagem simples, no padrão de escrita que o site
   adotou.
2. **Monte o seu** — escolhe o preset; usa as 18 dezenas do campeão
   (pré-preenchidas) ou digita as próprias; sai a lista de jogos pronta para
   copiar, com custo e garantia declarados junto do aviso obrigatório.
3. **Placar público** — campeão contra aleatório, sorteio a sorteio, com o
   pendente do próximo concurso em destaque.
4. **A conta** — gasto, retorno e saldo acumulados dos dois lados.

Segue o sistema visual existente: fontes Bricolage Grotesque, Inter Tight e
JetBrains Mono, tokens derivados por `color-mix()`, sem emojis, revelação por
scroll que nunca esconde conteúdo se o JS falhar.

## Testes

`robo/testar_fechamento.py`, rodando antes da publicação no workflow:

1. **Garantia por força bruta.** Para cada preset e cada `d` declarado,
   percorre todos os cenários `C(n, d)` e confirma que o pior caso atinge a
   faixa prometida. A garantia é uma afirmação pública; não vai ao ar sem
   prova. Se um padrão falhar, o teste quebra.
2. **Paridade JS ↔ Python.** Python gera o gabarito em
   `dados/gabarito_teste.json`, `teste.html` roda o JS contra ele — mesmo
   mecanismo já usado pelo motor. Cobre `montar`, `avaliar` e o PRNG.
3. **Conferência.** Concurso conhecido, dezenas conhecidas, acertos e retorno
   esperados.
4. **Determinismo do controle.** A mesma semente devolve as mesmas dezenas em
   execuções e linguagens diferentes.

## Riscos

**A página soar como promessa de ganho.** É o risco central: destrói a
credibilidade que o Desafio construiu. Mitigação: o aviso fica junto da
garantia, no mesmo bloco, e a conta acumulada — que mostrará prejuízo —
aparece na página, não escondida.

**Padrão irregular errado indo ao ar.** Mitigação: verificação por força bruta
no CI, bloqueando a publicação.

**Rateio ausente na API.** Mitigação: retorno `null` e valor omitido, nunca
estimado.

**Crescimento do JSON.** Cerca de 400 bytes por concurso, três sorteios por
semana: aproximadamente 60 KB por ano. Aceitável; sem ação necessária.
