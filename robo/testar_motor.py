# -*- coding: utf-8 -*-
"""Gera o gabarito que teste.html usa para conferir o motor em JavaScript.

Não dá para rodar js/motor.js aqui — não há Node. Então o Python calcula os
mesmos valores, grava em dados/gabarito_teste.json, e a página de teste
compara no navegador e mostra OK ou ERRO.

Este script roda no robô, DEPOIS de buscar os resultados novos: o gabarito é
derivado de dados/*.json, então gerá-lo antes o deixaria velho na mesma
execução. Sem isso ele ia ficando para trás a cada rodada e teste.html
acusava erro em loterias que estavam perfeitamente corretas.

Tudo aqui usa só o que está dentro do repositório. A versão anterior
importava gerador_loterias.py da pasta acima — o programa de linha de
comando, que nunca foi versionado — e por isso funcionava na máquina do
autor e quebrava o robô no GitHub Actions.
"""

import json
import os
import sys
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import campeao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")

NOMES = {
    "megasena": "Mega-Sena", "lotofacil": "Lotofácil", "quina": "Quina",
    "lotomania": "Lotomania", "duplasena": "Dupla Sena",
    "diadesorte": "Dia de Sorte", "timemania": "Timemania",
    "maismilionaria": "+Milionária",
}


def chance_um_em(ficha):
    """Uma aposta mínima cobre quantas das combinações possíveis do sorteio."""
    universo = ficha["hi"] - ficha["lo"] + 1
    return comb(universo, ficha["sorteadas"]) // comb(ficha["k"],
                                                      ficha["sorteadas"])


gabarito = {}
for slug, ficha in campeao.FICHAS.items():
    caminho = os.path.join(PASTA_DADOS, f"{slug}.json")
    if not os.path.exists(caminho):
        print(f"{NOMES[slug]}: sem dados, pulando.")
        continue
    with open(caminho, encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]

    gabarito[slug] = {
        "campeao": campeao.jogo_campeao(slug, concursos),
        # A aposta mínima é uma combinação só, então custa o preço cheio.
        "custo_minimo": ficha["preco"],
        "chance_um_em": chance_um_em(ficha),
        "total": len(concursos),
    }
    print(f"{NOMES[slug]}: campeão {gabarito[slug]['campeao']}")

with open(os.path.join(PASTA_DADOS, "gabarito_teste.json"), "w",
          encoding="utf-8") as f:
    json.dump(gabarito, f, ensure_ascii=False)
print("Gabarito salvo.")
