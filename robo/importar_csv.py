# -*- coding: utf-8 -*-
"""Importação inicial (rodar uma única vez, localmente).

Lê os CSVs `{slug}-download-resultados.csv` de uma pasta e cria os
`dados/{slug}.json` que o site consome. Depois disso quem mantém os JSONs
em dia é o robô (atualizar.py).

Uso: python importar_csv.py <pasta_com_os_csvs>
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone

from loterias import LOTERIAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")


def importar(pasta_csv):
    os.makedirs(PASTA_DADOS, exist_ok=True)
    for cfg in LOTERIAS:
        caminho = os.path.join(pasta_csv, f"{cfg['slug']}-download-resultados.csv")
        if not os.path.exists(caminho):
            print(f"AVISO: {caminho} não encontrado — pulando {cfg['nome']}.")
            continue
        concursos = []
        with open(caminho, encoding="utf-8-sig") as f:
            leitor = csv.reader(f)
            next(leitor)
            for linha in leitor:
                if len(linha) < 3:
                    continue
                try:
                    numero = int(linha[0])
                    dezenas = sorted(int(x) for x in linha[2:] if x.strip())
                except ValueError:
                    continue
                if dezenas:
                    concursos.append([numero, linha[1], dezenas])
        concursos.sort(key=lambda c: c[0])
        destino = os.path.join(PASTA_DADOS, f"{cfg['slug']}.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump({"loteria": cfg["slug"], "nome": cfg["nome"],
                       "atualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "concursos": concursos},
                      f, ensure_ascii=False, separators=(",", ":"))
        print(f"{cfg['nome']}: {len(concursos)} concursos -> {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    importar(sys.argv[1])
