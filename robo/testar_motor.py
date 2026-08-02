# -*- coding: utf-8 -*-
"""Teste do motor JS sem Node: roda motor.js num mini-interpretador? Não —
compara o RESULTADO determinístico do motor Python de referência com o que o
navegador calculará, gerando um gabarito em JSON que a página de teste lê.

Gera dados/gabarito_teste.json com, por loteria: jogo campeão esperado e
alguns valores de custo/chance. A página teste.html compara e mostra OK/ERRO.
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, ".."))

from gerador_loterias import (LOTERIAS, calcular_estatisticas, custo_aposta,
                              jogo_campeao, total_combinacoes,
                              combinacoes_cobertas)

PASTA_DADOS = os.path.join(RAIZ, "dados")

gabarito = {}
for cfg in LOTERIAS:
    with open(os.path.join(PASTA_DADOS, f"{cfg['slug']}.json"),
              encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]
    sorteios = [(c[0], c[1], c[2]) for c in concursos]
    stats = calcular_estatisticas(cfg, sorteios)
    k = cfg["aposta_min"]
    gabarito[cfg["slug"]] = {
        "campeao": jogo_campeao(cfg, stats),
        "custo_minimo": custo_aposta(cfg, k),
        "chance_um_em": total_combinacoes(cfg) // combinacoes_cobertas(cfg, k),
        "total": stats["total"],
    }
    print(f"{cfg['nome']}: campeão {gabarito[cfg['slug']]['campeao']}")

with open(os.path.join(PASTA_DADOS, "gabarito_teste.json"), "w",
          encoding="utf-8") as f:
    json.dump(gabarito, f, ensure_ascii=False)
print("Gabarito salvo.")
