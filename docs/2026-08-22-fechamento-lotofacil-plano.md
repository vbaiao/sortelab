# Fechamento da Lotofácil — Plano de Implementação

> **Para trabalhadores agênticos:** SUB-SKILL OBRIGATÓRIA: use
> superpowers:subagent-driven-development (recomendado) ou
> superpowers:executing-plans para implementar tarefa a tarefa. Os passos usam
> caixas (`- [ ]`) para acompanhamento.

**Objetivo:** Publicar `sortelabs.com.br/fechamento.html` com uma ferramenta de
fechamento da Lotofácil de garantia verificada, e um placar público que
compara um fechamento do jogo campeão contra um fechamento aleatório
auditável, sorteio a sorteio.

**Arquitetura:** Os padrões de fechamento são posicionais ("descarte as
posições 0, 1 e 2"), calculados uma vez, verificados por força bruta e
embarcados como tabela constante nas duas linguagens. O robô confere o
pendente e crava o próximo a cada rodada, gravando em `dados/fechamento.json`.
A página lê esse JSON. A conta acumulada nunca é gravada — é recalculada a
partir do histórico.

**Stack:** Python 3.12 sem dependências externas (só biblioteca padrão);
JavaScript ES5/ES6 sem build e sem bibliotecas; HTML e CSS escritos à mão;
GitHub Actions.

**Spec:** `docs/2026-08-22-fechamento-lotofacil-design.md`

## Restrições globais

- **Só Lotofácil.** Nenhuma outra loteria é tocada nesta entrega.
- **Nada existente muda de comportamento:** Desafio do Campeão, geradores,
  as oito páginas de loteria e `motor.js` ficam intactos.
- **Sem dependências externas.** Nem Python nem JS. O robô roda com a
  biblioteca padrão; a página não carrega biblioteca nenhuma.
- **Sem emojis** em qualquer texto visível ao usuário.
- **Linguagem simples** nos textos da página, no padrão que o site adotou:
  frases curtas, sem jargão, explicando o porquê.
- **O aviso de que fechamento não aumenta a chance fica no mesmo bloco da
  garantia**, nunca em rodapé.
- **Preço do jogo de 15 dezenas: R$ 3,50.** Constante única, sem repetir o
  número solto pelo código.
- **Faixa mínima premiada da Lotofácil: 11 acertos.**
- **Nenhum padrão vai ao ar sem passar na verificação por força bruta.**
- **Arquivos JSON de dados** são gravados com
  `json.dump(..., ensure_ascii=False, separators=(",", ":"))`, igual ao resto
  do projeto.
- **Determinismo:** nada de `random` da biblioteca padrão em código que gera
  dado publicado. Só o PRNG definido na Tarefa 3.
- **Commits em português**, no tom dos commits que já existem no repositório.

---

### Task 1: Motor de fechamento em Python, padrões regulares

Cria o núcleo matemático e o teste de garantia por força bruta. Só os dois
padrões regulares (trios disjuntos consecutivos), que são provadamente
corretos e fáceis de explicar. Os irregulares vêm na Tarefa 2.

**Files:**
- Create: `robo/fechamento.py`
- Create: `robo/testar_fechamento.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `PRECO_JOGO = 3.50`, `FAIXA_MINIMA = 11`
  - `PADROES: dict[str, dict]` com chaves `dezenas`, `descartes`, `garantias`
  - `jogos_do_padrao(padrao_id) -> int`
  - `custo_do_padrao(padrao_id) -> float`
  - `montar(dezenas: list[int], padrao_id: str) -> list[list[int]]`
  - `avaliar(jogos, resultado, rateio=None) -> dict` com `acertos`,
    `premios`, `retorno`
  - `verificar_garantia(padrao_id, saem, acertos) -> bool`

- [ ] **Step 1: Escrever os testes que falham**

Crie `robo/testar_fechamento.py`:

```python
# -*- coding: utf-8 -*-
"""Testes do motor de fechamento.

A garantia de faixa é uma afirmação pública. Aqui ela é conferida por força
bruta, cenário por cenário — se um padrão falhar, o teste quebra e a
publicação para.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fechamento as F

falhas = []


def checar(condicao, texto):
    print(("OK   " if condicao else "ERRO ") + texto)
    if not condicao:
        falhas.append(texto)


def testar_estrutura():
    for pid, p in F.PADROES.items():
        tamanho = p["dezenas"] - 15
        checar(all(len(d) == tamanho for d in p["descartes"]),
               f"{pid}: todo descarte tem {tamanho} posicao(oes)")
        checar(all(0 <= i < p["dezenas"] for d in p["descartes"] for i in d),
               f"{pid}: descartes dentro do intervalo de posicoes")
        checar(len({tuple(d) for d in p["descartes"]}) == len(p["descartes"]),
               f"{pid}: sem descartes repetidos")


def testar_montagem():
    dezenas = [2, 3, 5, 6, 9, 10, 11, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
    jogos = F.montar(dezenas, "18-5")
    checar(len(jogos) == 5, "18-5: monta 5 jogos")
    checar(all(len(j) == 15 for j in jogos), "18-5: todo jogo tem 15 dezenas")
    checar(all(j == sorted(j) for j in jogos), "18-5: jogos vem ordenados")
    checar(all(set(j) <= set(dezenas) for j in jogos),
           "18-5: jogos so usam as dezenas escolhidas")
    checar(jogos[0] == sorted(dezenas)[3:],
           "18-5: primeiro jogo descarta as tres primeiras posicoes")


def testar_montagem_recusa_entrada_ruim():
    try:
        F.montar([1, 2, 3], "18-5")
        checar(False, "montar recusa quantidade errada de dezenas")
    except ValueError:
        checar(True, "montar recusa quantidade errada de dezenas")
    try:
        F.montar([1] * 18, "18-5")
        checar(False, "montar recusa dezenas repetidas")
    except ValueError:
        checar(True, "montar recusa dezenas repetidas")


def testar_avaliacao():
    jogos = [[1, 2, 3], [4, 5, 6]]
    r = F.avaliar(jogos, [1, 2, 3, 7, 8], None)
    checar(r["acertos"] == [3, 0], "avaliar conta acertos por jogo")
    checar(r["retorno"] is None, "sem rateio, retorno fica None")

    # Tres jogos de 11 acertos pagam TRES vezes o rateio de 11.
    resultado = list(range(1, 16))
    jogos = [list(range(1, 12)) + [20, 21, 22, 23]] * 3
    r = F.avaliar(jogos, resultado, {"11": 7.0})
    checar(r["acertos"] == [11, 11, 11], "avaliar conta 11 acertos em cada jogo")
    checar(r["premios"] == {11: 3}, "avaliar agrupa tres jogos na faixa 11")
    checar(abs(r["retorno"] - 21.0) < 1e-9,
           "retorno soma por JOGO premiado, nao por faixa")


def testar_garantias():
    """Forca bruta: percorre TODOS os cenarios de cada garantia declarada."""
    for pid, p in F.PADROES.items():
        for g in p["garantias"]:
            ok = F.verificar_garantia(pid, g["saem"], g["acertos"])
            checar(ok, f"{pid}: se {g['saem']} das suas {p['dezenas']} sairem, "
                       f"garante {g['acertos']} acertos")


if __name__ == "__main__":
    testar_estrutura()
    testar_montagem()
    testar_montagem_recusa_entrada_ruim()
    testar_avaliacao()
    testar_garantias()
    print()
    if falhas:
        print(f"{len(falhas)} FALHA(S).")
        sys.exit(1)
    print("Tudo certo.")
```

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `python robo/testar_fechamento.py`
Expected: FALHA com `ModuleNotFoundError: No module named 'fechamento'`

- [ ] **Step 3: Escrever o motor**

Crie `robo/fechamento.py`:

```python
# -*- coding: utf-8 -*-
"""Fechamento da Lotofácil — montagem e avaliação.

Com n dezenas escolhidas, cada jogo de 15 descarta m = n - 15 delas. Se d das
suas n forem sorteadas, um jogo que descarta o conjunto T acerta
d - |T ∩ sorteadas|.

Os padrões são POSICIONAIS: "descarte as posições 0, 1 e 2" vale para qualquer
conjunto de 18 dezenas. Por isso são constantes, calculados e verificados uma
vez (ver robo/gerar_padroes.py e robo/testar_fechamento.py).

Espelhado em js/fechamento.js. Os dois são testados um contra o outro.
"""

from itertools import combinations

DEZENAS_POR_JOGO = 15
PRECO_JOGO = 3.50
FAIXA_MINIMA = 11        # menor faixa que paga na Lotofácil


def _trios_consecutivos(quantidade):
    return [[i, i + 1, i + 2] for i in range(0, quantidade * 3, 3)]


PADROES = {
    # Cinco trios disjuntos cobrindo as posições 0..14. As posições 15, 16 e
    # 17 nunca são descartadas — entram em todos os jogos. Por isso este
    # padrão trava em 12 acertos mesmo quando as 15 saem dentro das suas 18.
    "18-5": {
        "dezenas": 18,
        "descartes": _trios_consecutivos(5),
        "garantias": [{"saem": 13, "acertos": 11},
                      {"saem": 14, "acertos": 12},
                      {"saem": 15, "acertos": 12}],
    },
    # Seis trios disjuntos cobrindo todas as 18 posições. Custa R$ 3,50 a mais
    # que o 18-5 e chega a 13 acertos quando as 15 saem dentro das suas 18.
    "18-6": {
        "dezenas": 18,
        "descartes": _trios_consecutivos(6),
        "garantias": [{"saem": 13, "acertos": 11},
                      {"saem": 14, "acertos": 12},
                      {"saem": 15, "acertos": 13}],
    },
}


def jogos_do_padrao(padrao_id):
    return len(PADROES[padrao_id]["descartes"])


def custo_do_padrao(padrao_id):
    return round(jogos_do_padrao(padrao_id) * PRECO_JOGO, 2)


def montar(dezenas, padrao_id):
    """Devolve um jogo por descarte, cada um com 15 dezenas ordenadas."""
    padrao = PADROES[padrao_id]
    if len(dezenas) != padrao["dezenas"]:
        raise ValueError(f"O padrão {padrao_id} precisa de exatamente "
                         f"{padrao['dezenas']} dezenas.")
    if len(set(dezenas)) != len(dezenas):
        raise ValueError("Há dezenas repetidas na escolha.")
    base = sorted(dezenas)
    jogos = []
    for descarte in padrao["descartes"]:
        fora = set(descarte)
        jogos.append([base[i] for i in range(len(base)) if i not in fora])
    return jogos


def avaliar(jogos, resultado, rateio=None):
    """Acertos por jogo, prêmios por faixa e retorno em dinheiro.

    Cada jogo é uma aposta independente e paga por si: três jogos de 11
    acertos recebem três vezes o rateio de 11. O retorno soma por JOGO
    premiado, não por faixa.

    rateio: {"11": 7.0, "12": 14.0, ...}. Sem ele o retorno fica None — a
    página mostra os acertos e omite o valor, em vez de inventar um.
    """
    alvo = set(resultado)
    acertos = [len(alvo & set(jogo)) for jogo in jogos]
    premios = {}
    for a in acertos:
        if a >= FAIXA_MINIMA:
            premios[a] = premios.get(a, 0) + 1
    retorno = None
    if rateio:
        retorno = round(sum(float(rateio.get(str(a), 0.0))
                            for a in acertos if a >= FAIXA_MINIMA), 2)
    return {"acertos": acertos, "premios": premios, "retorno": retorno}


def verificar_garantia(padrao_id, saem, acertos):
    """Força bruta: confere a garantia em TODOS os cenários possíveis.

    Percorre cada jeito de `saem` das suas dezenas serem sorteadas e confirma
    que o melhor jogo do fechamento atinge `acertos`. Devolve False no
    primeiro cenário que não atingir.
    """
    padrao = PADROES[padrao_id]
    n = padrao["dezenas"]
    posicoes = set(range(n))
    jogos = [posicoes - set(d) for d in padrao["descartes"]]
    for sorteadas in combinations(range(n), saem):
        alvo = set(sorteadas)
        if max(len(jogo & alvo) for jogo in jogos) < acertos:
            return False
    return True
```

- [ ] **Step 4: Rodar os testes**

Run: `python robo/testar_fechamento.py`
Expected: PASSA — todas as linhas em `OK`, terminando com `Tudo certo.`

Se `18-5: se 15 das suas 18 sairem, garante 12 acertos` falhar com 13, o
padrão está errado: confira que apenas cinco trios foram gerados.

- [ ] **Step 5: Commit**

```bash
git add robo/fechamento.py robo/testar_fechamento.py
git commit -m "Motor de fechamento da Lotofácil com garantia verificada

Padrões posicionais de 18 dezenas em 5 e em 6 jogos. A garantia de cada
um é conferida por força bruta, cenário por cenário — é uma afirmação
pública e não vai ao ar sem prova."
```

---

### Task 2: Padrões irregulares 17-7 e 18-12

Os dois padrões regulares saem de trios consecutivos. Estes dois não têm forma
fechada e precisam de busca gulosa. O gerador roda uma vez, a saída é
**congelada** na tabela, e o teste da Tarefa 1 passa a cobri-los
automaticamente (ele percorre `PADROES` inteiro).

**Files:**
- Create: `robo/gerar_padroes.py`
- Modify: `robo/fechamento.py` (acrescenta duas entradas em `PADROES`)

**Interfaces:**
- Consumes: `fechamento.PADROES`, `fechamento.verificar_garantia`
- Produces: entradas `"17-7"` e `"18-12"` em `PADROES`, mesma forma das outras.

- [ ] **Step 1: Escrever o gerador**

Crie `robo/gerar_padroes.py`:

```python
# -*- coding: utf-8 -*-
"""Gera os padrões de fechamento que não têm forma regular.

Rode à mão, confira a saída e COLE em robo/fechamento.py. Os padrões são
constantes congeladas — este script existe para deixar registrado de onde
elas vieram e para permitir recalcular se um dia mudarmos as faixas.

    python robo/gerar_padroes.py

A busca é gulosa e não promete o mínimo absoluto de jogos. Promete apenas um
conjunto que CUMPRE a garantia — e isso é conferido por força bruta aqui e de
novo em robo/testar_fechamento.py.
"""

from itertools import combinations


def resolver(n, saem, acertos, limite=30):
    """Menor conjunto de descartes (guloso) que garante a faixa.

    Para garantir `acertos` é preciso que, para todo conjunto U de
    não-sorteadas dentro das suas n dezenas (|U| = n - saem), exista algum
    descarte T escolhido com |T ∩ U| >= m - saem + acertos.
    """
    m = n - 15
    precisa = m - saem + acertos
    if precisa <= 0:
        return []
    universo = [frozenset(u) for u in combinations(range(n), n - saem)]
    candidatos = [frozenset(t) for t in combinations(range(n), m)]
    cobre = {t: {u for u in universo if len(t & u) >= precisa}
             for t in candidatos}
    escolhidos, faltam = [], set(universo)
    while faltam and len(escolhidos) < limite:
        melhor = max(candidatos, key=lambda t: len(cobre[t] & faltam))
        ganho = cobre[melhor] & faltam
        if not ganho:
            return None
        escolhidos.append(sorted(melhor))
        faltam -= ganho
    return escolhidos if not faltam else None


def conferir(n, descartes, saem, acertos):
    posicoes = set(range(n))
    jogos = [posicoes - set(d) for d in descartes]
    for sorteadas in combinations(range(n), saem):
        alvo = set(sorteadas)
        if max(len(j & alvo) for j in jogos) < acertos:
            return False
    return True


ALVOS = [
    ("17-7", 17, 12, 11),
    ("18-12", 18, 12, 11),
]

for pid, n, saem, acertos in ALVOS:
    descartes = resolver(n, saem, acertos)
    if descartes is None:
        print(f"{pid}: nao foi possivel cobrir.")
        continue
    ok = conferir(n, descartes, saem, acertos)
    print(f'\n    "{pid}": {{')
    print(f'        "dezenas": {n},')
    print(f'        "descartes": {descartes},')
    print(f'        "garantias": [{{"saem": {saem}, "acertos": {acertos}}}],')
    print(f'    }},')
    print(f"    # {len(descartes)} jogos | conferido por forca bruta: "
          f"{'OK' if ok else 'FALHOU'}")
```

- [ ] **Step 2: Rodar o gerador**

Run: `python robo/gerar_padroes.py`
Expected: imprime dois blocos prontos para colar, cada um seguido de
`conferido por forca bruta: OK`. O `17-7` deve sair com 7 jogos e o `18-12`
com 12. Se algum imprimir `FALHOU`, **pare** — não cole nada e investigue.

- [ ] **Step 3: Colar os padrões em `robo/fechamento.py`**

Acrescente os dois blocos impressos ao dicionário `PADROES`, depois da entrada
`"18-6"`, mantendo o comentário explicativo acima de cada um:

```python
    # Sete descartes de dois, achados por busca gulosa (robo/gerar_padroes.py).
    # Não têm forma regular: a lista abaixo é uma constante congelada e
    # verificada, não uma regra que dê para deduzir de cabeça.
    "17-7": {  # ... cole aqui a saída do gerador
    },
    # Doze descartes de três. Garante prêmio quando só 12 das suas 18 saem —
    # o que acontece uma vez a cada quatro sorteios.
    "18-12": {  # ... cole aqui a saída do gerador
    },
```

Use exatamente os números impressos pelo gerador. Não invente nem reordene.

- [ ] **Step 4: Rodar os testes**

Run: `python robo/testar_fechamento.py`
Expected: PASSA. O teste percorre `PADROES` inteiro, então os dois padrões
novos ganham verificação de estrutura e de garantia automaticamente.

Rode também um confronto rápido do custo:

Run: `python -c "import sys; sys.path.insert(0,'robo'); import fechamento as F; print({k: (F.jogos_do_padrao(k), F.custo_do_padrao(k)) for k in F.PADROES})"`
Expected: `{'18-5': (5, 17.5), '18-6': (6, 21.0), '17-7': (7, 24.5), '18-12': (12, 42.0)}`

- [ ] **Step 5: Commit**

```bash
git add robo/gerar_padroes.py robo/fechamento.py
git commit -m "Padrões de fechamento 17-7 e 18-12

Achados por busca gulosa e congelados como constante. O gerador fica no
repositório para registrar de onde os números vieram; a garantia dos dois
é conferida por força bruta junto com os demais."
```

---

### Task 3: Sorteio auditável do lado aleatório

O controle aleatório precisa ser reproduzível por qualquer pessoa, em qualquer
linguagem, senão o experimento não vale nada — sempre caberia a suspeita de
que o palpite foi escolhido depois do sorteio. `random` do Python não serve:
a implementação pode mudar entre versões e não há equivalente idêntico em JS.

**Files:**
- Modify: `robo/fechamento.py`
- Modify: `robo/testar_fechamento.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `mulberry32(semente: int) -> Callable[[], float]`
  - `dezenas_aleatorias(semente: int, quantidade: int, lo: int, hi: int) -> list[int]`

- [ ] **Step 1: Escrever os testes que falham**

Acrescente a `robo/testar_fechamento.py`, antes do bloco `if __name__`:

```python
def testar_prng():
    a = F.mulberry32(3757)
    b = F.mulberry32(3757)
    checar([a() for _ in range(5)] == [b() for _ in range(5)],
           "mulberry32: mesma semente, mesma sequencia")

    c = F.mulberry32(3758)
    checar(F.mulberry32(3757)() != c(),
           "mulberry32: sementes diferentes, valores diferentes")

    valores = [F.mulberry32(1)() for _ in range(1)]
    checar(all(0.0 <= v < 1.0 for v in valores),
           "mulberry32: valores no intervalo [0, 1)")


def testar_dezenas_aleatorias():
    d = F.dezenas_aleatorias(3757, 18, 1, 25)
    checar(len(d) == 18, "sorteio: devolve 18 dezenas")
    checar(len(set(d)) == 18, "sorteio: sem repeticao")
    checar(d == sorted(d), "sorteio: vem ordenado")
    checar(all(1 <= n <= 25 for n in d), "sorteio: dentro de 1..25")
    checar(d == F.dezenas_aleatorias(3757, 18, 1, 25),
           "sorteio: mesma semente devolve o mesmo resultado")
    checar(d != F.dezenas_aleatorias(3758, 18, 1, 25),
           "sorteio: semente diferente devolve resultado diferente")
```

E acrescente as duas chamadas ao bloco `if __name__ == "__main__":`, depois de
`testar_avaliacao()`:

```python
    testar_prng()
    testar_dezenas_aleatorias()
```

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `python robo/testar_fechamento.py`
Expected: FALHA com `AttributeError: module 'fechamento' has no attribute 'mulberry32'`

- [ ] **Step 3: Implementar**

Acrescente a `robo/fechamento.py`, depois de `avaliar`:

```python
# ------------------------------------------------------- sorteio auditável

MASCARA = 0xFFFFFFFF


def mulberry32(semente):
    """PRNG de 32 bits, idêntico bit a bit ao de js/fechamento.js.

    Não usamos `random` da biblioteca padrão de propósito: a implementação
    pode mudar entre versões do Python e não existe equivalente em
    JavaScript. O lado aleatório do placar só tem valor se qualquer pessoa
    puder reproduzi-lo — por isso o algoritmo é explícito e está publicado
    na própria página.
    """
    estado = semente & MASCARA

    def proximo():
        nonlocal estado
        estado = (estado + 0x6D2B79F5) & MASCARA
        t = estado
        t = ((t ^ (t >> 15)) * (t | 1)) & MASCARA
        t = (t ^ (t + ((t ^ (t >> 7)) * (t | 61)) & MASCARA)) & MASCARA
        return ((t ^ (t >> 14)) & MASCARA) / 4294967296.0

    return proximo


def dezenas_aleatorias(semente, quantidade, lo, hi):
    """Embaralha lo..hi com Fisher-Yates e devolve as primeiras, ordenadas."""
    sortear = mulberry32(semente)
    baralho = list(range(lo, hi + 1))
    for i in range(len(baralho) - 1, 0, -1):
        j = int(sortear() * (i + 1))
        baralho[i], baralho[j] = baralho[j], baralho[i]
    return sorted(baralho[:quantidade])
```

- [ ] **Step 4: Rodar os testes**

Run: `python robo/testar_fechamento.py`
Expected: PASSA, incluindo as seis linhas novas de `sorteio:` e as três de
`mulberry32:`.

- [ ] **Step 5: Commit**

```bash
git add robo/fechamento.py robo/testar_fechamento.py
git commit -m "Sorteio auditável para o lado aleatório do placar

PRNG explícito em vez do random da biblioteca padrão. O controle só tem
valor como experimento se qualquer um puder reproduzir o palpite, e para
isso o algoritmo precisa ser o mesmo em Python e em JavaScript."
```

---

### Task 4: As 18 dezenas do jogo campeão

O `campeao.py` hoje devolve 15 dezenas para a Lotofácil. O fechamento precisa
de 18. A regra, que também será escrita na página: as 15 do campeão mais as
próximas do ranking de pontuação, até completar.

**Files:**
- Modify: `robo/campeao.py`
- Modify: `robo/testar_fechamento.py`

**Interfaces:**
- Consumes: `campeao.jogo_campeao`, `campeao._score`, `campeao.FICHAS`
- Produces: `campeao.pool_campeao(slug, concursos, tamanho) -> list[int]`

- [ ] **Step 1: Escrever o teste que falha**

Acrescente a `robo/testar_fechamento.py`, junto dos outros imports do topo:

```python
import json

import campeao
```

E a função de teste, antes do bloco `if __name__`:

```python
def testar_pool_campeao():
    caminho = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "dados", "lotofacil.json")
    with open(caminho, encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]

    quinze = campeao.jogo_campeao("lotofacil", concursos)
    dezoito = campeao.pool_campeao("lotofacil", concursos, 18)

    checar(len(dezoito) == 18, "pool: devolve 18 dezenas")
    checar(len(set(dezoito)) == 18, "pool: sem repeticao")
    checar(dezoito == sorted(dezoito), "pool: vem ordenado")
    checar(set(quinze) <= set(dezoito),
           "pool: contem as 15 do jogo campeao")
    checar(all(1 <= n <= 25 for n in dezoito), "pool: dentro de 1..25")
    checar(dezoito == campeao.pool_campeao("lotofacil", concursos, 18),
           "pool: e deterministico")
    checar(campeao.pool_campeao("lotofacil", concursos, 15) == sorted(quinze),
           "pool: para tamanho 15 devolve o proprio jogo campeao")
```

E a chamada no bloco `if __name__ == "__main__":`:

```python
    testar_pool_campeao()
```

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `python robo/testar_fechamento.py`
Expected: FALHA com `AttributeError: module 'campeao' has no attribute 'pool_campeao'`

- [ ] **Step 3: Implementar**

Acrescente ao final de `robo/campeao.py`:

```python
def pool_campeao(slug, concursos, tamanho):
    """As dezenas do jogo campeão mais as seguintes do ranking, até `tamanho`.

    Usado pelo fechamento, que precisa de mais dezenas do que cabem num jogo.
    Determinístico: mesma entrada, mesma saída, sempre. Para `tamanho` igual
    ao tamanho da aposta devolve o próprio jogo campeão.
    """
    base = sorted(jogo_campeao(slug, concursos))
    if tamanho <= len(base):
        return base
    cfg = FICHAS[slug]
    trincas = [(c[0], c[1], c[2]) for c in concursos]
    score, universo = _score(cfg, trincas)
    escolhidas = set(base)
    for n in sorted(universo, key=lambda x: (-score[x], x)):
        if len(escolhidas) >= tamanho:
            break
        escolhidas.add(n)
    return sorted(escolhidas)
```

- [ ] **Step 4: Rodar os testes**

Run: `python robo/testar_fechamento.py`
Expected: PASSA, com as sete linhas novas de `pool:`.

Confirme que o Desafio não mudou:

Run: `python robo/testar_motor.py`
Expected: imprime o campeão de cada loteria e `Gabarito salvo.` — o campeão da
Lotofácil deve ser o mesmo de antes desta tarefa.

- [ ] **Step 5: Commit**

```bash
git add robo/campeao.py robo/testar_fechamento.py
git commit -m "pool_campeao: as 18 dezenas do campeão para o fechamento

As 15 do jogo campeão mais as seguintes do ranking. O jogo campeão em si
não muda — o Desafio continua cravando exatamente o que cravava."
```

---

### Task 5: O robô confere e crava o fechamento

**Files:**
- Modify: `robo/atualizar.py`
- Create: `dados/fechamento.json` (gerado pela primeira execução)

**Interfaces:**
- Consumes: `fechamento.montar`, `fechamento.avaliar`,
  `fechamento.dezenas_aleatorias`, `fechamento.custo_do_padrao`,
  `campeao.pool_campeao`, `atualizar.buscar`
- Produces: `atualizar.atualizar_fechamento(concursos) -> bool`,
  `atualizar.rateio_do_concurso(numero) -> dict | None`

- [ ] **Step 1: Escrever o passo de rateio**

Em `robo/atualizar.py`, acrescente `import fechamento` junto do
`import campeao` que já existe no topo, e a constante junto de `ARQ_DESAFIO`:

```python
ARQ_FECHAMENTO = os.path.join(PASTA_DADOS, "fechamento.json")
PRESET_FECHAMENTO = "18-5"
```

Depois da função `buscar`, acrescente:

```python
def rateio_do_concurso(numero):
    """Valores reais de prêmio daquele concurso, vindos da API da Caixa.

    Devolve {"11": 7.0, "12": 14.0, ...} ou None se a API não trouxer.
    Nunca estima: sem rateio, o retorno fica em branco na página.
    """
    try:
        dados = buscar("lotofacil", numero)
    except Exception:
        return None
    tabela = {}
    for faixa in dados.get("listaRateioPremio", []):
        digitos = "".join(c for c in faixa.get("descricaoFaixa", "")
                          if c.isdigit())
        valor = faixa.get("valorPremio")
        if digitos and valor is not None:
            tabela[digitos] = float(valor)
    return tabela or None
```

- [ ] **Step 2: Escrever o passo do fechamento**

Ainda em `robo/atualizar.py`, depois de `atualizar_desafio`, acrescente:

```python
def atualizar_fechamento(concursos):
    """Desafio do Fechamento: confere o pendente e crava o próximo.

    Dois lados por sorteio, mesmo padrão e mesmo custo: um montado sobre as
    18 dezenas do jogo campeão, outro sobre 18 dezenas sorteadas com semente
    igual ao número do concurso. O placar existe para mostrar que os dois
    empatam.

    A conta acumulada não é gravada: gasto e retorno são recalculados a
    partir do histórico, aqui e na página.
    """
    if os.path.exists(ARQ_FECHAMENTO):
        with open(ARQ_FECHAMENTO, encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {"preset": PRESET_FECHAMENTO, "pendente": None,
                 "historico": []}
    dados["preset"] = PRESET_FECHAMENTO
    indice = {c[0]: c for c in concursos}
    tamanho = fechamento.PADROES[PRESET_FECHAMENTO]["dezenas"]
    mudou = False

    def cravar(apos):
        corte = [c for c in concursos if c[0] <= apos]
        alvo = apos + 1
        return {
            "apos": apos,
            "campeao": {"dezenas": campeao.pool_campeao("lotofacil", corte,
                                                        tamanho)},
            "aleatorio": {"dezenas": fechamento.dezenas_aleatorias(
                              alvo, tamanho, 1, 25),
                          "semente": alvo},
        }

    while dados["pendente"] and (dados["pendente"]["apos"] + 1) in indice:
        pendente = dados["pendente"]
        sorteio = indice[pendente["apos"] + 1]
        if len(sorteio[2]) != 15:
            break                      # concurso sem dezenas: espera a próxima rodada
        rateio = rateio_do_concurso(sorteio[0])
        linha = {"concurso": sorteio[0], "data": sorteio[1],
                 "resultado": sorteio[2], "rateio": rateio}
        for lado in ("campeao", "aleatorio"):
            dezenas = pendente[lado]["dezenas"]
            jogos = fechamento.montar(dezenas, PRESET_FECHAMENTO)
            nota = fechamento.avaliar(jogos, sorteio[2], rateio)
            linha[lado] = {"dezenas": dezenas, "acertos": nota["acertos"],
                           "retorno": nota["retorno"]}
        dados["historico"].append(linha)
        dados["pendente"] = cravar(sorteio[0])
        melhor_c = max(linha["campeao"]["acertos"])
        melhor_a = max(linha["aleatorio"]["acertos"])
        print(f"  Fechamento: concurso {sorteio[0]} conferido — "
              f"campeão {melhor_c}, aleatório {melhor_a}; próximo cravado.")
        mudou = True

    if not dados["pendente"]:
        dados["pendente"] = cravar(concursos[-1][0])
        print(f"  Fechamento: primeiro palpite cravado (após concurso "
              f"{concursos[-1][0]}).")
        mudou = True

    if mudou:
        with open(ARQ_FECHAMENTO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
    return mudou
```

- [ ] **Step 3: Ligar no laço principal**

Em `robo/atualizar.py`, dentro de `main()`, logo depois do bloco
`try/except` que chama `atualizar_desafio`, acrescente:

```python
            if cfg["slug"] == "lotofacil":
                try:
                    if atualizar_fechamento(concursos):
                        houve_novidade = True
                except Exception as erro:
                    print(f"{cfg['nome']}: fechamento falhou ({erro}).")
```

O `try/except` segue o tratamento que o arquivo já dá ao Desafio e ao CSV:
uma falha aqui não pode derrubar o resto da rodada.

- [ ] **Step 4: Rodar o robô e conferir o resultado**

Run: `python robo/atualizar.py`
Expected: entre as linhas normais, aparece
`Fechamento: primeiro palpite cravado (após concurso NNNN).`

Confira o arquivo gerado:

Run: `python -c "import json; d=json.load(open('dados/fechamento.json',encoding='utf-8')); print(json.dumps(d,ensure_ascii=False,indent=1))"`
Expected: `preset` igual a `18-5`; `pendente.apos` igual ao último concurso da
Lotofácil; `campeao.dezenas` e `aleatorio.dezenas` com 18 números cada,
ordenados e diferentes entre si; `aleatorio.semente` igual a `apos + 1`;
`historico` vazio.

Rode de novo para confirmar que é idempotente:

Run: `python robo/atualizar.py`
Expected: **nenhuma** linha de `Fechamento:` — não há concurso novo, nada muda.

- [ ] **Step 5: Commit**

```bash
git add robo/atualizar.py dados/fechamento.json
git commit -m "Robô crava e confere o Desafio do Fechamento

Dois fechamentos por sorteio, campeão contra aleatório, com os valores
reais de rateio da Caixa. A conta acumulada não é gravada: é recalculada
do histórico, porque total somado que fica guardado sempre diverge."
```

---

### Task 6: Motor de fechamento em JavaScript

Porte fiel do Python, no padrão já usado por `motor.js`. A paridade entre os
dois é testada — é o que impede que a página mostre uma coisa e o robô grave
outra.

**Files:**
- Create: `js/fechamento.js`
- Modify: `robo/testar_fechamento.py` (passa a gerar o gabarito)
- Modify: `teste.html`

**Interfaces:**
- Consumes: `fechamento.PADROES` (mesmos dados, transcritos)
- Produces: `window.SorteLabFechamento` com `PADROES`, `PRECO_JOGO`,
  `FAIXA_MINIMA`, `jogosDoPadrao`, `custoDoPadrao`, `montar`, `avaliar`,
  `mulberry32`, `dezenasAleatorias`, `contaAcumulada`

- [ ] **Step 1: Gerar o gabarito de paridade**

Acrescente ao final de `robo/testar_fechamento.py`, dentro do bloco
`if __name__ == "__main__":`, antes do `if falhas:`:

```python
    caminho_gabarito = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "dados", "gabarito_fechamento.json")
    dezenas = [2, 3, 5, 6, 9, 10, 11, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
    resultado = [1, 2, 3, 5, 6, 9, 10, 11, 13, 14, 15, 16, 19, 20, 24]
    rateio = {"11": 7.0, "12": 14.0, "13": 35.0, "14": 1341.42, "15": 565758.41}
    gabarito = {"padroes": {}, "sorteios": {}}
    for pid in F.PADROES:
        base = dezenas[:F.PADROES[pid]["dezenas"]]
        jogos = F.montar(base, pid)
        gabarito["padroes"][pid] = {
            "jogos": jogos,
            "custo": F.custo_do_padrao(pid),
            "avaliacao": F.avaliar(jogos, resultado, rateio),
        }
    for semente in (1, 3757, 99999):
        gabarito["sorteios"][str(semente)] = F.dezenas_aleatorias(
            semente, 18, 1, 25)
    with open(caminho_gabarito, "w", encoding="utf-8") as f:
        json.dump(gabarito, f, ensure_ascii=False)
    print("Gabarito de fechamento salvo.")
```

Run: `python robo/testar_fechamento.py`
Expected: PASSA e imprime `Gabarito de fechamento salvo.`

- [ ] **Step 2: Escrever o motor JS**

Crie `js/fechamento.js`:

```javascript
/* SorteLab — fechamento da Lotofácil (porte fiel de robo/fechamento.py).
 * Fechamento NÃO aumenta a chance de ganhar. Ele garante uma faixa mínima
 * quando você acerta o bastante, e concentra o retorno em vez de espalhar. */
"use strict";

(function () {
  const DEZENAS_POR_JOGO = 15;
  const PRECO_JOGO = 3.50;
  const FAIXA_MINIMA = 11;

  function triosConsecutivos(quantidade) {
    const fora = [];
    for (let i = 0; i < quantidade * 3; i += 3) fora.push([i, i + 1, i + 2]);
    return fora;
  }

  const PADROES = {
    "18-5": {
      dezenas: 18, descartes: triosConsecutivos(5),
      garantias: [{ saem: 13, acertos: 11 }, { saem: 14, acertos: 12 },
                  { saem: 15, acertos: 12 }]
    },
    "18-6": {
      dezenas: 18, descartes: triosConsecutivos(6),
      garantias: [{ saem: 13, acertos: 11 }, { saem: 14, acertos: 12 },
                  { saem: 15, acertos: 13 }]
    }
    // 17-7 e 18-12 entram aqui, transcritos de robo/fechamento.py.
  };

  function jogosDoPadrao(id) { return PADROES[id].descartes.length; }

  function custoDoPadrao(id) {
    return Math.round(jogosDoPadrao(id) * PRECO_JOGO * 100) / 100;
  }

  function montar(dezenas, id) {
    const padrao = PADROES[id];
    if (dezenas.length !== padrao.dezenas) {
      throw new Error("O padrão " + id + " precisa de exatamente " +
                      padrao.dezenas + " dezenas.");
    }
    if (new Set(dezenas).size !== dezenas.length) {
      throw new Error("Há dezenas repetidas na escolha.");
    }
    const base = dezenas.slice().sort((a, b) => a - b);
    return padrao.descartes.map(descarte => {
      const fora = new Set(descarte);
      return base.filter((_, i) => !fora.has(i));
    });
  }

  function avaliar(jogos, resultado, rateio) {
    const alvo = new Set(resultado);
    const acertos = jogos.map(j => j.filter(n => alvo.has(n)).length);
    const premios = {};
    acertos.forEach(a => {
      if (a >= FAIXA_MINIMA) premios[a] = (premios[a] || 0) + 1;
    });
    let retorno = null;
    if (rateio) {
      retorno = acertos.reduce((soma, a) =>
        a >= FAIXA_MINIMA ? soma + (Number(rateio[a]) || 0) : soma, 0);
      retorno = Math.round(retorno * 100) / 100;
    }
    return { acertos, premios, retorno };
  }

  // -------------------------------------------------- sorteio auditável

  function mulberry32(semente) {
    let estado = semente >>> 0;
    return function () {
      estado = (estado + 0x6D2B79F5) >>> 0;
      let t = estado;
      t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
      t = (t ^ (t + Math.imul(t ^ (t >>> 7), t | 61))) >>> 0;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function dezenasAleatorias(semente, quantidade, lo, hi) {
    const sortear = mulberry32(semente);
    const baralho = [];
    for (let n = lo; n <= hi; n++) baralho.push(n);
    for (let i = baralho.length - 1; i > 0; i--) {
      const j = Math.floor(sortear() * (i + 1));
      const troca = baralho[i]; baralho[i] = baralho[j]; baralho[j] = troca;
    }
    return baralho.slice(0, quantidade).sort((a, b) => a - b);
  }

  // -------------------------------------------------- conta acumulada

  function contaAcumulada(historico, id) {
    const custo = custoDoPadrao(id);
    const conta = { sorteios: historico.length, campeao: null, aleatorio: null };
    ["campeao", "aleatorio"].forEach(lado => {
      let retorno = 0, semRateio = 0;
      historico.forEach(linha => {
        if (linha[lado] && linha[lado].retorno === null) semRateio++;
        else if (linha[lado]) retorno += linha[lado].retorno;
      });
      const gasto = historico.length * custo;
      conta[lado] = {
        gasto: Math.round(gasto * 100) / 100,
        retorno: Math.round(retorno * 100) / 100,
        saldo: Math.round((retorno - gasto) * 100) / 100,
        semRateio
      };
    });
    return conta;
  }

  const raiz = (typeof window !== "undefined") ? window : globalThis;
  raiz.SorteLabFechamento = {
    PADROES, PRECO_JOGO, FAIXA_MINIMA, DEZENAS_POR_JOGO,
    jogosDoPadrao, custoDoPadrao, montar, avaliar,
    mulberry32, dezenasAleatorias, contaAcumulada
  };
})();
```

- [ ] **Step 3: Transcrever os padrões irregulares**

Copie as entradas `"17-7"` e `"18-12"` de `robo/fechamento.py` para o objeto
`PADROES` de `js/fechamento.js`, convertendo a sintaxe Python para JS:
`"dezenas": 17` vira `dezenas: 17`, e as listas ficam iguais.

Os números devem bater exatamente. O teste do próximo passo pega qualquer
divergência.

- [ ] **Step 4: Escrever o teste de paridade na página**

Em `teste.html`, acrescente `<script src="js/fechamento.js"></script>` logo
depois da linha do `motor.js`. Depois, dentro do `.then(async gabarito => {`,
antes da linha `const erros = ...`, acrescente:

```javascript
  const FZ = window.SorteLabFechamento;
  const gf = await fetch("dados/gabarito_fechamento.json").then(r => r.json());
  const dezenas = [2,3,5,6,9,10,11,13,14,15,16,19,20,21,22,23,24,25];
  const resultado = [1,2,3,5,6,9,10,11,13,14,15,16,19,20,24];
  const rateio = {11:7.0, 12:14.0, 13:35.0, 14:1341.42, 15:565758.41};

  for (const pid of Object.keys(gf.padroes)) {
    const esperado = gf.padroes[pid];
    const jogos = FZ.montar(dezenas.slice(0, FZ.PADROES[pid].dezenas), pid);
    log(JSON.stringify(jogos) === JSON.stringify(esperado.jogos),
        "fechamento " + pid + ": montagem bate com o Python");
    log(Math.abs(FZ.custoDoPadrao(pid) - esperado.custo) < 0.001,
        "fechamento " + pid + ": custo R$ " + FZ.custoDoPadrao(pid));
    const nota = FZ.avaliar(jogos, resultado, rateio);
    log(JSON.stringify(nota.acertos) === JSON.stringify(esperado.avaliacao.acertos),
        "fechamento " + pid + ": acertos batem com o Python");
    log(Math.abs(nota.retorno - esperado.avaliacao.retorno) < 0.001,
        "fechamento " + pid + ": retorno R$ " + nota.retorno);
  }

  for (const semente of Object.keys(gf.sorteios)) {
    const saiu = FZ.dezenasAleatorias(Number(semente), 18, 1, 25);
    log(JSON.stringify(saiu) === JSON.stringify(gf.sorteios[semente]),
        "sorteio semente " + semente + ": bate com o Python");
  }
```

- [ ] **Step 5: Rodar o teste no navegador**

Abra `teste.html` no navegador (o `Ver-Site.bat` sobe o servidor local).
Expected: o título da página mostra `TUDO OK` e aparecem quatro linhas verdes
por padrão de fechamento, mais três de `sorteio semente`.

Se alguma linha de `sorteio semente` der ERRO, o PRNG divergiu entre as
linguagens — confira as máscaras de 32 bits no lado Python.

- [ ] **Step 6: Commit**

```bash
git add js/fechamento.js teste.html robo/testar_fechamento.py dados/gabarito_fechamento.json
git commit -m "Motor de fechamento em JavaScript, com teste de paridade

Porte fiel do Python. O gabarito gerado pelo teste garante que a página
mostra exatamente o que o robô grava — inclusive o sorteio auditável."
```

---

### Task 7: A página

**Files:**
- Create: `fechamento.html`
- Create: `js/paginafechamento.js`
- Modify: `css/estilo.css`

**Interfaces:**
- Consumes: `window.SorteLabFechamento`, `dados/fechamento.json`,
  `dados/lotofacil.json`
- Produces: a página renderizada.

- [ ] **Step 1: Escrever o esqueleto da página**

Crie `fechamento.html` copiando o `<head>`, o `<header class="topo">` e o
`<footer class="rodape">` de `desafio.html` — mesmos `<link>` de fonte e CSS,
mesmo favicon SVG inline, mesmo script do GoatCounter no fim.

Ajuste:
- `<title>` para `Fechamento da Lotofácil — SorteLabs`
- `<link rel="canonical" href="https://sortelabs.com.br/fechamento.html">`
- `<meta name="description">` explicando fechamento em uma frase
- `<nav>` com `<a href="desafio.html">Desafio</a>` e
  `<a href="/">Todas as loterias</a>`

Os scripts no fim do `<body>`, nesta ordem:

```html
<script src="js/interface.js"></script>
<script src="js/fechamento.js"></script>
<script src="js/paginafechamento.js"></script>
<script data-goatcounter="https://sortelabs.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```

O corpo tem quatro `<section>`, nesta ordem, cada uma com um `id`:
`o-que-e`, `montador`, `placar`, `conta`.

Todas dentro de `<main class="miolo painel">`, como em `desafio.html`.
Cuidado para nenhum `id` de seção colidir com `id` de botão: o botão de
montar é `btn-montar`, a seção é `montador`.

- [ ] **Step 2: Escrever o bloco "o que é"**

HTML estático, sem JS — este bloco tem que continuar legível se o script
falhar. Dentro de `<section id="o-que-e" class="revelar">`:

```html
<h2>O que é um fechamento</h2>

<p>Na Lotofácil saem 15 números de 25. O seu jogo também tem 15. Ou seja:
você é obrigado a deixar 10 números de fora, e se deixar de fora os
errados, já era.</p>

<p>A ideia do fechamento é escolher <strong>18 números</strong> em vez de 15.
Aí você só deixa 7 de fora — bem mais seguro. O problema é que o volante
só aceita 15, então não cabem 18 num jogo só.</p>

<p>A solução é fazer vários jogos. <strong>Cada jogo pega 15 dos seus 18 e
descarta 3.</strong> E aqui está o pulo do gato: se cada jogo descartar um
trio diferente, os descartes ficam espalhados.</p>

<p>Suponha que dos seus 18 números, 13 vão sair e 5 são lixo. Você não sabe
quais são os 5 lixos. Mas <strong>é impossível 5 números se esconderem em
6 trios diferentes ao mesmo tempo</strong> — pelo menos um trio vai ter
lixo dentro. E o jogo que descarta esse trio está descartando lixo. Esse
é o seu jogo bom.</p>

<p>Não é sorte, é contagem. Dá para conferir cenário por cenário — e é
exatamente o que o teste automático deste site faz antes de qualquer
coisa ir ao ar.</p>

<h3>Os fechamentos que montamos aqui</h3>

<div class="rolagem-x">
<table class="tabela">
  <thead>
    <tr><th>Dezenas</th><th>Jogos</th><th>Custo</th><th>Garantia</th></tr>
  </thead>
  <tbody>
    <tr><td>18</td><td>5</td><td>R$ 17,50</td><td>11 acertos se 13 das suas saírem</td></tr>
    <tr><td>18</td><td>6</td><td>R$ 21,00</td><td>11 se 13 · 13 acertos se as 15 saírem</td></tr>
    <tr><td>17</td><td>7</td><td>R$ 24,50</td><td>11 acertos se 12 das suas saírem</td></tr>
    <tr><td>18</td><td>12</td><td>R$ 42,00</td><td>11 acertos se só 12 saírem</td></tr>
  </tbody>
</table>
</div>

<h3>Agora a parte que ninguém conta</h3>

<div class="aviso-obs"><strong>Fechamento não aumenta a sua chance de
ganhar. Nenhum método aumenta.</strong> Todo jogo de 15 dezenas acerta 9 números
em média, seja ele escolhido por estatística, por sonho ou por sorteio.
Isso é conta fechada, não opinião.</div>

<p>E a garantia soa melhor do que é. <strong>Garantir 11 acertos é garantir
uns R$ 7.</strong> Gastar R$ 17,50 para ter uma chance em 16 de ganhar
R$ 7 é péssimo negócio, e a gente não vai fingir o contrário.</p>

<p>O que o fechamento faz de verdade é <strong>concentrar</strong>. Jogo
espalhado raspa sempre e nunca acerta. Fechamento raspa pouco, mas quando
acerta, acerta em vários jogos de uma vez. Muda o formato do resultado,
não o tamanho da chance.</p>

<h3>Com que frequência cada faixa acontece</h3>

<div class="rolagem-x">
<table class="tabela">
  <thead><tr><th>Acertos</th><th>Acontece</th></tr></thead>
  <tbody>
    <tr><td>11</td><td>1 a cada 11 jogos</td></tr>
    <tr><td>12</td><td>1 a cada 60</td></tr>
    <tr><td>13</td><td>1 a cada 692</td></tr>
    <tr><td>14</td><td>1 a cada 21.792</td></tr>
    <tr><td>15</td><td>1 a cada 3.268.760</td></tr>
  </tbody>
</table>
</div>

<p>Se você costuma fazer 11 e 12 e sente que "faltou pouco": não faltou.
É assim que o jogo foi desenhado. A distância de 12 para 15 é de 60 para
3,2 milhões.</p>
```

- [ ] **Step 3: Escrever o formulário e a lógica**

Dentro de `<section id="montador" class="revelar">`, um formulário no padrão das
páginas de loteria (`.cartao form` já é `flex-direction: column; gap: 18px`).
Os `id` abaixo são consumidos pelo script do passo seguinte e precisam bater
exatamente:

```html
<h2>Monte o seu fechamento</h2>

<div class="cartao">
  <form onsubmit="return false">
    <div class="linha-campos">
      <div class="campo">
        <label for="padrao">Qual fechamento</label>
        <select id="padrao">
          <option value="18-5">18 dezenas em 5 jogos — R$ 17,50</option>
          <option value="18-6">18 dezenas em 6 jogos — R$ 21,00</option>
          <option value="17-7">17 dezenas em 7 jogos — R$ 24,50</option>
          <option value="18-12">18 dezenas em 12 jogos — R$ 42,00</option>
        </select>
      </div>
      <div class="campo">
        <label for="dezenas">Suas dezenas, separadas por espaço</label>
        <input type="text" id="dezenas" inputmode="numeric"
               autocomplete="off" placeholder="02 03 05 06 09 ...">
      </div>
    </div>
    <div class="botoes">
      <button class="botao" type="button" id="btn-montar">Montar fechamento</button>
      <button class="botao secundario" type="button" id="btn-usar-campeao">Usar as do campeão</button>
    </div>
  </form>

  <div id="saida-montagem"></div>
</div>

<p>As dezenas do campeão são as 15 do jogo campeão da Lotofácil mais as 3
seguintes do ranking. É a mesma regra que o robô usa para cravar o palpite
do placar aqui embaixo.</p>
```

Crie `js/paginafechamento.js`:

```javascript
/* SorteLab — página do fechamento da Lotofácil. */
"use strict";

(function () {
  const FZ = window.SorteLabFechamento;
  const PRESET_PLACAR = "18-5";

  const $ = id => document.getElementById(id);
  const dinheiro = v => "R$ " + v.toFixed(2).replace(".", ",");
  const dez = n => String(n).padStart(2, "0");

  let estado = { fechamento: null };

  function lerDezenas(texto) {
    const nums = (texto.match(/\d+/g) || []).map(Number);
    return Array.from(new Set(nums)).sort((a, b) => a - b);
  }

  function montarFechamento() {
    const id = $("padrao").value;
    const dezenas = lerDezenas($("dezenas").value);
    const saida = $("saida-montagem");
    try {
      const jogos = FZ.montar(dezenas, id);
      const p = FZ.PADROES[id];
      const garantias = p.garantias.map(g =>
        "<li>Se <strong>" + g.saem + "</strong> das suas " + p.dezenas +
        " saírem, você tem garantido um jogo com <strong>" + g.acertos +
        "</strong> acertos.</li>").join("");
      saida.innerHTML =
        "<p class='dica'><em>" + jogos.length + " jogos · " +
        dinheiro(FZ.custoDoPadrao(id)) + "</em></p><ul class='garantias'>" +
        garantias + "</ul><ol class='jogos'>" +
        jogos.map(j => "<li>" + j.map(dez).join(" ") + "</li>").join("") +
        "</ol>";
    } catch (e) {
      saida.innerHTML = "<p class='erro'>" + e.message + "</p>";
    }
  }

  function usarDoCampeao() {
    const pendente = estado.fechamento && estado.fechamento.pendente;
    if (!pendente) return;
    $("padrao").value = PRESET_PLACAR;
    $("dezenas").value = pendente.campeao.dezenas.map(dez).join(" ");
    montarFechamento();
  }

  function linhaPlacar(linha, lado) {
    const d = linha[lado];
    const melhor = Math.max.apply(null, d.acertos);
    const premiados = d.acertos.filter(a => a >= FZ.FAIXA_MINIMA).length;
    return "<td>" + melhor + "</td><td>" + premiados + "</td><td>" +
      (d.retorno === null ? "—" : dinheiro(d.retorno)) + "</td>";
  }

  function desenharPlacar() {
    const dados = estado.fechamento;
    if (!dados) return;
    const historico = dados.historico.slice().reverse();
    $("placar-corpo").innerHTML = historico.map(linha =>
      "<tr><td>" + linha.concurso + "</td><td>" + linha.data + "</td>" +
      linhaPlacar(linha, "campeao") + linhaPlacar(linha, "aleatorio") +
      "</tr>").join("") ||
      "<tr><td colspan='8'>Nenhum sorteio conferido ainda.</td></tr>";

    if (dados.pendente) {
      $("pendente").innerHTML =
        "<p>Cravado para o concurso <strong>" + (dados.pendente.apos + 1) +
        "</strong>, antes do sorteio:</p>" +
        "<p><strong>Campeão:</strong> " +
        dados.pendente.campeao.dezenas.map(dez).join(" ") + "</p>" +
        "<p><strong>Aleatório</strong> (semente " +
        dados.pendente.aleatorio.semente + "): " +
        dados.pendente.aleatorio.dezenas.map(dez).join(" ") + "</p>";
    }
  }

  function desenharConta() {
    const dados = estado.fechamento;
    if (!dados) return;
    const conta = FZ.contaAcumulada(dados.historico, dados.preset);
    const linha = (nome, c) =>
      "<tr><th>" + nome + "</th><td>" + dinheiro(c.gasto) + "</td><td>" +
      dinheiro(c.retorno) + "</td><td class='" +
      (c.saldo < 0 ? "negativo" : "positivo") + "'>" +
      dinheiro(c.saldo) + "</td></tr>";
    $("conta-corpo").innerHTML =
      linha("Campeão", conta.campeao) + linha("Aleatório", conta.aleatorio);
    $("conta-sorteios").textContent = conta.sorteios;

    // Concurso sem rateio entra no gasto mas não no retorno, o que puxa o
    // saldo para baixo. Melhor avisar do que mostrar um número torto calado.
    const semRateio = Math.max(conta.campeao.semRateio,
                               conta.aleatorio.semRateio);
    $("conta-ressalva").innerHTML = semRateio
      ? "Em <strong>" + semRateio + "</strong> " +
        (semRateio === 1 ? "sorteio" : "sorteios") + " a Caixa não publicou " +
        "os valores de prêmio. " + (semRateio === 1 ? "Ele conta" : "Eles contam") +
        " no gasto mas não no retorno, então o saldo real é um pouco melhor " +
        "do que o mostrado aqui."
      : "";
  }

  fetch("dados/fechamento.json")
    .then(r => r.json())
    .then(dados => {
      estado.fechamento = dados;
      desenharPlacar();
      desenharConta();
      usarDoCampeao();
    })
    .catch(() => {
      $("placar-corpo").innerHTML =
        "<tr><td colspan='8'>Não foi possível carregar o placar agora.</td></tr>";
    });

  $("btn-montar").addEventListener("click", montarFechamento);
  $("btn-usar-campeao").addEventListener("click", usarDoCampeao);
})();
```

- [ ] **Step 4: Escrever o placar e a conta em HTML**

Os `id` têm que bater exatamente com os que o script do passo anterior usa.

`<section id="placar" class="revelar">`:

```html
<h2>O placar público</h2>

<p>A cada sorteio o robô crava dois fechamentos de 18 dezenas em 5 jogos,
antes do resultado sair. Um monta as dezenas do jogo campeão; o outro,
18 dezenas sorteadas. Os dois gastam os mesmos R$ 17,50.</p>

<p>O placar existe para mostrar uma coisa: <strong>os dois empatam</strong>.
Se a estatística funcionasse, o campeão abriria vantagem. Acompanhe e
tire sua conclusão.</p>

<div class="cartao" id="pendente"></div>

<div class="rolagem-x">
<table class="tabela">
  <thead>
    <tr>
      <th rowspan="2">Concurso</th><th rowspan="2">Data</th>
      <th colspan="3">Campeão</th><th colspan="3">Aleatório</th>
    </tr>
    <tr>
      <th>Melhor</th><th>Premiados</th><th>Retorno</th>
      <th>Melhor</th><th>Premiados</th><th>Retorno</th>
    </tr>
  </thead>
  <tbody id="placar-corpo">
    <tr><td colspan="8">Carregando…</td></tr>
  </tbody>
</table>
</div>

<p>"Melhor" é quantos acertos fez o melhor dos 5 jogos. "Premiados" é
quantos dos 5 jogos bateram 11 acertos ou mais.</p>
```

`<section id="conta" class="revelar">`:

```html
<h2>A conta, sem maquiagem</h2>

<p>Somando tudo o que foi gasto e tudo o que voltou, ao longo de
<span id="conta-sorteios">0</span> sorteios:</p>

<div class="rolagem-x">
<table class="tabela">
  <thead>
    <tr><th>Lado</th><th>Gasto</th><th>Retorno</th><th>Saldo</th></tr>
  </thead>
  <tbody id="conta-corpo"></tbody>
</table>
</div>

<p id="conta-ressalva"></p>

<p>Os valores de prêmio são os oficiais da Caixa para cada concurso, não
estimativa. Quando a Caixa não publica o rateio, deixamos em branco em
vez de inventar.</p>

<h3>Como conferir o lado aleatório</h3>

<p>Um placar assim só vale se ninguém puder trapacear. As 18 dezenas do
lado aleatório são sorteadas com uma semente igual ao número do concurso
— para o concurso 3757, a semente é 3757. Qualquer pessoa reproduz e
confere que o palpite foi cravado antes, e não escolhido depois:</p>

<pre class="rolagem-x"><code>function mulberry32(semente) {
  let estado = semente &gt;&gt;&gt; 0;
  return function () {
    estado = (estado + 0x6D2B79F5) &gt;&gt;&gt; 0;
    let t = estado;
    t = Math.imul(t ^ (t &gt;&gt;&gt; 15), t | 1) &gt;&gt;&gt; 0;
    t = (t ^ (t + Math.imul(t ^ (t &gt;&gt;&gt; 7), t | 61))) &gt;&gt;&gt; 0;
    return ((t ^ (t &gt;&gt;&gt; 14)) &gt;&gt;&gt; 0) / 4294967296;
  };
}

// Embaralha 1..25 com Fisher-Yates e pega as 18 primeiras, ordenadas.
function dezenasAleatorias(semente) {
  const sortear = mulberry32(semente);
  const baralho = [];
  for (let n = 1; n &lt;= 25; n++) baralho.push(n);
  for (let i = baralho.length - 1; i &gt; 0; i--) {
    const j = Math.floor(sortear() * (i + 1));
    [baralho[i], baralho[j]] = [baralho[j], baralho[i]];
  }
  return baralho.slice(0, 18).sort((a, b) =&gt; a - b);
}</code></pre>
```

- [ ] **Step 5: Escrever o CSS**

Em `css/estilo.css`, acrescente ao final:

Só quatro classes novas. Tudo o mais reaproveita o que já existe: `.cartao`,
`.cartao.destaque`, `.botao`, `.botao.secundario`, `.botoes`, `.linha-campos`,
`.campo`, `.dica`, `.aviso-obs`, `.erro`, `.rolagem-x`, `table.tabela`,
`.revelar`. **Não crie equivalentes** — as tabelas usam `class="tabela"` e os
blocos roláveis usam `class="rolagem-x"`, que já estão no CSS.

```css
/* ---------------------------------------------- fechamento da Lotofácil */

.jogos {
  margin: 0; padding-left: 1.7em;
  font-family: var(--dados); font-size: .92rem; line-height: 1.9;
  font-variant-numeric: tabular-nums;
}

.garantias { margin: 0 0 16px; padding-left: 1.2em; font-size: .93rem; }
.garantias li { margin-bottom: 5px; }

.tabela td.negativo { color: var(--alerta); font-weight: 600; }
.tabela td.positivo { color: var(--cor); font-weight: 600; }
```

`--dados`, `--cor` e `--alerta` são tokens que já existem no arquivo; use-os
em vez de escrever cor ou fonte na mão.

- [ ] **Step 6: Conferir no navegador**

Rode `Ver-Site.bat` e abra `fechamento.html`.
Expected:
- Os quatro blocos aparecem na ordem certa
- O campo já vem preenchido com as 18 dezenas do campeão e a montagem já
  aparece
- Trocar o padrão e clicar em "Montar fechamento" muda a lista de jogos, o
  custo e as garantias
- Digitar 17 dezenas com o padrão `18-5` selecionado mostra a mensagem de erro
  em vez de quebrar
- Nenhuma barra de rolagem horizontal na página
- Em janela de 380 px de largura tudo continua legível

Desligue o JavaScript no navegador e recarregue.
Expected: o bloco "o que é", com toda a explicação e as tabelas, continua
visível e legível. Conteúdo não pode sumir quando o script falha.

- [ ] **Step 7: Commit**

```bash
git add fechamento.html js/paginafechamento.js css/estilo.css
git commit -m "Página do fechamento da Lotofácil

Explicação, ferramenta de montagem, placar público e a conta acumulada.
O aviso de que fechamento não aumenta a chance fica no mesmo bloco da
garantia, não em rodapé."
```

---

### Task 8: Publicação — links, sitemap e verificação no CI

**Files:**
- Modify: `robo/gerar_paginas.py`
- Modify: `index.html`
- Modify: `.github/workflows/atualizar.yml`

**Interfaces:**
- Consumes: tudo das tarefas anteriores.
- Produces: página no ar, no sitemap e com a garantia verificada a cada rodada.

- [ ] **Step 1: Incluir no sitemap e nos links**

Em `robo/gerar_paginas.py`, na linha que monta o sitemap, troque:

```python
    for u in ["", "desafio.html"] + urls:
```

por:

```python
    for u in ["", "desafio.html", "fechamento.html"] + urls:
```

Na mesma função, o `<nav>` do modelo de página (por volta da linha 70) passa a
incluir o link novo:

```python
    <nav><a href="desafio.html">Desafio</a><a href="fechamento.html">Fechamento</a><a href="/">Todas as loterias</a></nav>
```

Em `index.html`, acrescente um link para `fechamento.html` junto do link que
já existe para o Desafio, com uma frase curta dizendo o que é.

- [ ] **Step 2: Regerar as páginas**

Run: `python robo/gerar_paginas.py`
Expected: `OK sitemap.xml e robots.txt` e as oito páginas regeradas.

Confira:

Run: `grep -c "fechamento.html" sitemap.xml lotofacil.html index.html`
Expected: `sitemap.xml:1`, `lotofacil.html:1`, `index.html:1` (ou mais).

- [ ] **Step 3: Ligar a verificação no CI**

Em `.github/workflows/atualizar.yml`, acrescente um passo **antes** de
`Buscar concursos novos na API da Caixa`:

```yaml
      - name: Conferir as garantias do fechamento
        run: python robo/testar_fechamento.py
```

A garantia é uma afirmação pública. Se um padrão quebrar, a rodada para antes
de publicar qualquer coisa.

- [ ] **Step 4: Rodar a suíte inteira**

Run: `python robo/testar_fechamento.py`
Expected: PASSA, terminando em `Tudo certo.`

Run: `python robo/testar_motor.py`
Expected: imprime os campeões e `Gabarito salvo.`

Run: `python robo/atualizar.py`
Expected: roda sem erro; `Tudo em dia.` ou as novidades do dia.

Abra `teste.html` no navegador.
Expected: `TUDO OK` no título.

- [ ] **Step 5: Commit e publicar**

```bash
git add robo/gerar_paginas.py index.html lotofacil.html .github/workflows/atualizar.yml sitemap.xml
git commit -m "Fechamento no ar: links, sitemap e verificação no CI

A conferência das garantias roda antes da atualização dos dados. Padrão
que não passar na força bruta impede a publicação."
git push
```

- [ ] **Step 6: Conferir no ar**

Depois do deploy do GitHub Pages (leva 1 a 2 minutos):

Run: `curl -s -o /dev/null -w "%{http_code}" https://sortelabs.com.br/fechamento.html`
Expected: `200`

Abra a página no celular e confira que as tabelas rolam dentro do próprio
bloco, sem fazer a página inteira rolar de lado.

Peça a indexação de `https://sortelabs.com.br/fechamento.html` no Search
Console.

---

## Notas de execução

**Ordem.** As tarefas 1 a 5 são Python e formam uma corrente: cada uma depende
da anterior. A 6 depende da 1 a 3. A 7 depende da 6. A 8 depende de todas.
Não há tarefas paralelizáveis com segurança.

**O que não pode quebrar.** Depois de cada tarefa, `python robo/testar_motor.py`
tem que continuar imprimindo os mesmos campeões de antes. Se o campeão da
Lotofácil mudar, alguma coisa em `campeao.py` foi mexida indevidamente — o
Desafio do Campeão depende dele e cravou palpites em cima dele.

**Fim de linha.** O repositório tem `.gitattributes` com `dados/csv/*.csv -text`
por causa de conflito entre Windows e o runner Linux. Os JSON novos não
precisam de tratamento, mas se aparecer diff gigante em `dados/`, é isso.

**Primeira rodada do placar.** O histórico começa vazio e só ganha a primeira
linha depois do próximo sorteio da Lotofácil. A página precisa ficar
apresentável nesse estado — o passo 6 da Tarefa 7 cobre isso.
