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


def testar_valores_congelados():
    """Verifica valores congelados da geradora — o contrato com o JS e o placar.

    A semente determina a sequência de números, e o lado aleatório do placar é
    uma aposta pública: comparamos seu desempenho com o fechamento estatístico
    jogo a jogo. Se este teste falha, ou o gerador mudou, ou a porta JavaScript
    divergiu — e em ambos os casos o histórico já publicado na página está em
    risco. Por isso estes valores não podem mudar sem justificativa externalizada.
    """
    checar(F.dezenas_aleatorias(1, 18, 1, 25) ==
           [2, 3, 4, 5, 7, 8, 9, 10, 11, 14, 15, 17, 18, 19, 20, 23, 24, 25],
           "sorteio: semente=1 gera [2, 3, 4, 5, 7, 8, 9, 10, 11, 14, 15, 17, 18, 19, 20, 23, 24, 25]")
    checar(F.dezenas_aleatorias(3757, 18, 1, 25) ==
           [1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24, 25],
           "sorteio: semente=3757 gera [1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24, 25]")
    checar(F.dezenas_aleatorias(99999, 18, 1, 25) ==
           [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 20, 21, 22, 23, 24],
           "sorteio: semente=99999 gera [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 20, 21, 22, 23, 24]")


if __name__ == "__main__":
    testar_estrutura()
    testar_montagem()
    testar_montagem_recusa_entrada_ruim()
    testar_avaliacao()
    testar_prng()
    testar_dezenas_aleatorias()
    testar_valores_congelados()
    testar_garantias()
    print()
    if falhas:
        print(f"{len(falhas)} FALHA(S).")
        sys.exit(1)
    print("Tudo certo.")
