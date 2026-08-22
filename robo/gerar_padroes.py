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
