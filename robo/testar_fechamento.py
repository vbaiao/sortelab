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
