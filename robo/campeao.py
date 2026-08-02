# -*- coding: utf-8 -*-
"""Jogo campeão determinístico — mesma regra do motor do site (js/motor.js).

Usado pelo robô para "cravar" um palpite antes de cada sorteio no
Desafio do Campeão (dados/desafio.json).
"""

from collections import Counter
from itertools import combinations
from math import ceil, comb, sqrt

JANELA_RECENTE = 200
MAX_COMBOS = 400_000
PESOS = (0.50, 0.35, 0.15)   # histórico, recente, atraso

FICHAS = {
    "megasena":       dict(lo=1, hi=60, sorteadas=6,  k=6),
    "lotofacil":      dict(lo=1, hi=25, sorteadas=15, k=15),
    "quina":          dict(lo=1, hi=80, sorteadas=5,  k=5),
    "lotomania":      dict(lo=0, hi=99, sorteadas=20, k=50),
    "duplasena":      dict(lo=1, hi=50, sorteadas=6,  k=6),
    "diadesorte":     dict(lo=1, hi=31, sorteadas=7,  k=7),
    "timemania":      dict(lo=1, hi=80, sorteadas=7,  k=10),
    "maismilionaria": dict(lo=1, hi=50, sorteadas=6,  k=6),
}


def _score(cfg, concursos):
    universo = list(range(cfg["lo"], cfg["hi"] + 1))
    total = len(concursos)
    freq = Counter()
    for _, _, nums in concursos:
        freq.update(nums)
    freq_rec = Counter()
    for _, _, nums in concursos[-JANELA_RECENTE:]:
        freq_rec.update(nums)
    ultimo = {}
    for i, (_, _, nums) in enumerate(concursos):
        for n in nums:
            ultimo[n] = i
    atraso = {n: total - 1 - ultimo.get(n, -1) for n in universo}

    fs = [freq[n] for n in universo]
    rs = [freq_rec.get(n, 0) for n in universo]
    max_f, min_f = max(fs), min(fs)
    max_r, min_r = max(rs), min(rs)
    max_a = max(atraso.values())
    ph, pr, pa = PESOS
    score = {}
    for n in universo:
        f = (freq[n] - min_f) / (max_f - min_f) if max_f > min_f else 0.5
        r = (freq_rec.get(n, 0) - min_r) / (max_r - min_r) if max_r > min_r else 0.5
        a = atraso[n] / max_a if max_a else 0
        score[n] = ph * f + pr * r + pa * a
    return score, universo


def _faixa(cfg, n, tamanho):
    return (n - cfg["lo"]) // tamanho


def _parametros_faixa(cfg):
    quantidade = cfg["hi"] - cfg["lo"] + 1
    tamanho = ceil(quantidade / 6)
    return tamanho, ceil(quantidade / tamanho)


def _valido(cfg, jogo):
    k = len(jogo)
    quantidade = cfg["hi"] - cfg["lo"] + 1
    media = k * (cfg["lo"] + cfg["hi"]) / 2
    desvio = sqrt(k * ((quantidade ** 2 - 1) / 12) * (quantidade - k) / (quantidade - 1))
    if not (media - 1.2 * desvio) <= sum(jogo) <= (media + 1.2 * desvio):
        return False
    pares = sum(1 for n in jogo if n % 2 == 0)
    if not (k // 2 - 1) <= pares <= (k // 2 + 2):
        return False
    tamanho, num_faixas = _parametros_faixa(cfg)
    faixas = Counter(_faixa(cfg, n, tamanho) for n in jogo)
    if len(faixas) < min(num_faixas, k) - 1:
        return False
    if max(faixas.values()) > ceil(k / num_faixas) + 1:
        return False
    return True


def jogo_campeao(slug, concursos):
    """Concursos: lista [[numero, data, [dezenas]], ...] em ordem crescente."""
    cfg = FICHAS[slug]
    trincas = [(c[0], c[1], c[2]) for c in concursos]
    score, universo = _score(cfg, trincas)
    k = cfg["k"]
    tamanho, num_faixas = _parametros_faixa(cfg)
    ranking = sorted(universo, key=lambda n: (-score[n], n))

    pool_n = k
    while pool_n < len(ranking) and comb(pool_n + 1, k) <= MAX_COMBOS:
        pool_n += 1
    pool = set(ranking[:pool_n])
    for f in range(num_faixas):
        topo = next((n for n in ranking if _faixa(cfg, n, tamanho) == f), None)
        if topo is not None:
            pool.add(topo)
    lista = sorted(pool, key=lambda n: (-score[n], n))

    alvo_faixas = min(num_faixas, k)
    melhor, melhor_pontos = None, -1.0
    for combo in combinations(lista, k):
        if len({_faixa(cfg, n, tamanho) for n in combo}) < alvo_faixas:
            continue
        jogo = sorted(combo)
        if not _valido(cfg, jogo):
            continue
        pontos = sum(score[n] for n in jogo)
        if pontos > melhor_pontos:
            melhor, melhor_pontos = jogo, pontos
    return melhor or sorted(ranking[:k])
