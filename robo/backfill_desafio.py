# -*- coding: utf-8 -*-
"""Preenchimento retroativo do Desafio do Campeão (rodar uma vez).

Para cada um dos últimos 30 concursos de cada loteria, recalcula o jogo
campeão usando SOMENTE os dados anteriores àquele concurso (sem olhar o
futuro — o cálculo é determinístico e reproduzível) e registra os acertos.
As entradas ganham a marca "retro": true para o painel diferenciá-las das
cravadas ao vivo pelo robô.
"""

import json
import os

import campeao
from loterias import LOTERIAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
ARQ_DESAFIO = os.path.join(PASTA_DADOS, "desafio.json")
QUANTOS = 30

desafio = {}
for cfg in LOTERIAS:
    slug = cfg["slug"]
    with open(os.path.join(PASTA_DADOS, f"{slug}.json"), encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]
    historico = []
    inicio = max(1, len(concursos) - QUANTOS)
    for t in range(inicio, len(concursos)):
        jogo = campeao.jogo_campeao(slug, concursos[:t])
        alvo = concursos[t]
        acertos = len(set(jogo) & set(alvo[2]))
        historico.append({"concurso": alvo[0], "data": alvo[1], "jogo": jogo,
                          "resultado": alvo[2], "acertos": acertos,
                          "retro": True})
    pendente = {"apos": concursos[-1][0],
                "jogo": campeao.jogo_campeao(slug, concursos)}
    desafio[slug] = {"pendente": pendente, "historico": historico}
    media = sum(h["acertos"] for h in historico) / len(historico)
    print(f"{cfg['nome']}: {len(historico)} retroativos, média "
          f"{media:.2f} acerto(s); palpite cravado p/ o próximo concurso.")

with open(ARQ_DESAFIO, "w", encoding="utf-8") as f:
    json.dump(desafio, f, ensure_ascii=False, separators=(",", ":"))
print("OK dados/desafio.json")
