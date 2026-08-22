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
