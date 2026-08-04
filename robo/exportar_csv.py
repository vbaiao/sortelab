# -*- coding: utf-8 -*-
"""Exporta o histórico de cada loteria em CSV para download no site.

Formato pensado para abrir direto no Excel brasileiro: separador ponto e
vírgula e BOM UTF-8 (acentos corretos ao dar dois cliques no arquivo).
Cada dezena vai em sua própria coluna, como número, para facilitar
fórmulas e tabelas dinâmicas.
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_CSV = os.path.join(RAIZ, "dados", "csv")


def exportar(slug, concursos):
    """Grava dados/csv/{slug}.csv. Retorna True se o arquivo mudou."""
    os.makedirs(PASTA_CSV, exist_ok=True)
    largura = max(len(c[2]) for c in concursos)
    linhas = ["Concurso;Data;" + ";".join(f"D{i}" for i in range(1, largura + 1))]
    for numero, data, dezenas in concursos:
        celulas = [str(d) for d in dezenas] + [""] * (largura - len(dezenas))
        linhas.append(f"{numero};{data};" + ";".join(celulas))
    conteudo = "\r\n".join(linhas) + "\r\n"

    # newline="" na leitura: sem isso o Python converte os \r\n do arquivo em
    # \n, a comparação nunca bate e o CSV é reescrito a cada rodada — o que
    # enchia o repositório de commits idênticos.
    destino = os.path.join(PASTA_CSV, f"{slug}.csv")
    if os.path.exists(destino):
        with open(destino, encoding="utf-8-sig", newline="") as f:
            if f.read() == conteudo:
                return False
    with open(destino, "w", encoding="utf-8-sig", newline="") as f:
        f.write(conteudo)
    return True
