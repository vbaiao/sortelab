# -*- coding: utf-8 -*-
"""Testes do motor de fechamento.

A garantia de faixa é uma afirmação pública. Aqui ela é conferida por força
bruta, cenário por cenário — se um padrão falhar, o teste quebra e a
publicação para.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import campeao
import fechamento as F

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def testar_pool_campeao():
    caminho = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "dados", "lotofacil.json")
    with open(caminho, encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]

    quinze = campeao.jogo_campeao("lotofacil", concursos)
    dezoito = campeao.pool_campeao("lotofacil", concursos, 18)

    checar(len(dezoito) == 18, "pool: devolve 18 dezenas")
    checar(len(set(dezoito)) == 18, "pool: sem repeticao")
    checar(dezoito == sorted(dezoito), "pool: vem ordenado")
    checar(set(quinze) <= set(dezoito),
           "pool: contem as 15 do jogo campeao")
    checar(all(1 <= n <= 25 for n in dezoito), "pool: dentro de 1..25")
    checar(dezoito == campeao.pool_campeao("lotofacil", concursos, 18),
           "pool: e deterministico")
    checar(campeao.pool_campeao("lotofacil", concursos, 15) == sorted(quinze),
           "pool: para tamanho 15 devolve o proprio jogo campeao")


def testar_pool_campeao_segue_o_ranking():
    """As dezenas extras do pool são as melhores do ranking, não quaisquer.

    O esperado é recalculado aqui, não congelado num valor fixo:
    dados/lotofacil.json ganha concursos novos toda semana, o que muda os
    escores e portanto quais dezenas entram no pool. Um valor fixo quebraria
    sozinho na próxima rodada do robô. Por isso o teste refaz o mesmo ranking
    que pool_campeao usa por dentro (mesmo _score, mesmo critério de
    desempate) e confere que as dezenas acrescentadas são exatamente o topo
    desse ranking.
    """
    caminho = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "dados", "lotofacil.json")
    with open(caminho, encoding="utf-8") as f:
        concursos = json.load(f)["concursos"]

    quinze = campeao.jogo_campeao("lotofacil", concursos)
    cfg = campeao.FICHAS["lotofacil"]
    trincas = [(c[0], c[1], c[2]) for c in concursos]
    score, universo = campeao._score(cfg, trincas)
    fora_do_campeao = sorted(
        (n for n in universo if n not in set(quinze)),
        key=lambda n: (-score[n], n))

    dezoito = campeao.pool_campeao("lotofacil", concursos, 18)
    extras_18 = sorted(set(dezoito) - set(quinze))
    esperado_18 = sorted(fora_do_campeao[:3])
    checar(len(extras_18) == 3,
           f"pool18: acrescenta exatamente 3 dezenas "
           f"(esperado 3, veio {len(extras_18)}: {extras_18})")
    checar(extras_18 == esperado_18,
           f"pool18: as extras sao as 3 melhores do ranking fora do campeao "
           f"(esperado {esperado_18}, veio {extras_18})")

    dezesseis = campeao.pool_campeao("lotofacil", concursos, 16)
    extras_16 = sorted(set(dezesseis) - set(quinze))
    esperado_16 = sorted(fora_do_campeao[:1])
    checar(len(extras_16) == 1,
           f"pool16: acrescenta exatamente 1 dezena "
           f"(esperado 1, veio {len(extras_16)}: {extras_16})")
    checar(extras_16 == esperado_16,
           f"pool16: a extra e a melhor do ranking fora do campeao "
           f"(esperado {esperado_16}, veio {extras_16})")


def _ler_padroes_do_js():
    """Extrai a tabela PADROES de js/fechamento.js lendo o arquivo como texto.

    Não há Node aqui, então não dá para executar o JS. Mas a tabela é dado
    literal, e ler dado literal é trabalho de leitor de texto. Se o formato
    do arquivo mudar a ponto desta leitura falhar, o teste quebra — o que é
    o comportamento certo: quebrar alto é melhor que aprovar no escuro.
    """
    with open(os.path.join(RAIZ, "js", "fechamento.js"), encoding="utf-8") as f:
        texto = f.read()

    ids = list(F.PADROES)
    tabela = {}
    for pid in ids:
        marca = '"%s":' % pid
        if marca not in texto:
            raise ValueError(f"padrão {pid} não existe em js/fechamento.js")
        ini = texto.index(marca)
        fim = min([texto.index('"%s":' % o) for o in ids
                   if o != pid and texto.find('"%s":' % o, ini + 1) != -1
                   and texto.index('"%s":' % o, ini + 1) > ini]
                  + [len(texto)])
        bloco = texto[ini:fim]

        dezenas = int(re.search(r"dezenas:\s*(\d+)", bloco).group(1))
        cru = bloco[bloco.index("descartes:") + 10:bloco.index("garantias:")]
        trios = re.search(r"triosConsecutivos\((\d+)\)", cru)
        if trios:
            n = int(trios.group(1))
            descartes = [[i, i + 1, i + 2] for i in range(0, n * 3, 3)]
        else:
            descartes = [[int(x) for x in re.findall(r"\d+", grupo)]
                         for grupo in re.findall(r"\[([^\[\]]+)\]", cru)]
        garantias = [{"saem": int(s), "acertos": int(a)} for s, a in
                     re.findall(r"saem:\s*(\d+),\s*acertos:\s*(\d+)", bloco)]
        tabela[pid] = {"dezenas": dezenas, "descartes": descartes,
                       "garantias": garantias}
    return texto, tabela


def testar_paridade_com_o_js():
    """A garantia é provada em Python, mas quem a mostra ao leitor é o JS.

    teste.html já compara os dois, só que ele depende de alguém abrir uma
    página no navegador. Este teste roda no CI e pega a divergência antes
    de ela virar promessa publicada.
    """
    try:
        texto, js = _ler_padroes_do_js()
    except Exception as erro:
        checar(False, f"paridade: nao consegui ler js/fechamento.js ({erro})")
        return

    checar(set(js) == set(F.PADROES),
           f"paridade: os dois lados tem os mesmos padroes ({sorted(js)})")
    for pid in sorted(set(js) & set(F.PADROES)):
        py = F.PADROES[pid]
        checar(js[pid]["dezenas"] == py["dezenas"],
               f"paridade {pid}: dezenas ({js[pid]['dezenas']})")
        checar(js[pid]["descartes"] == py["descartes"],
               f"paridade {pid}: descartes batem")
        checar(js[pid]["garantias"] == py["garantias"],
               f"paridade {pid}: garantias batem")

    preco = re.search(r"PRECO_JOGO\s*=\s*([\d.]+)", texto)
    faixa = re.search(r"FAIXA_MINIMA\s*=\s*(\d+)", texto)
    checar(preco and abs(float(preco.group(1)) - F.PRECO_JOGO) < 1e-9,
           f"paridade: PRECO_JOGO ({preco.group(1) if preco else '?'})")
    checar(faixa and int(faixa.group(1)) == F.FAIXA_MINIMA,
           f"paridade: FAIXA_MINIMA ({faixa.group(1) if faixa else '?'})")


if __name__ == "__main__":
    testar_estrutura()
    testar_montagem()
    testar_montagem_recusa_entrada_ruim()
    testar_avaliacao()
    testar_prng()
    testar_dezenas_aleatorias()
    testar_valores_congelados()
    testar_garantias()
    testar_pool_campeao()
    testar_pool_campeao_segue_o_ranking()
    testar_paridade_com_o_js()

    # Gabarito de paridade: js/fechamento.js roda os mesmos dados em teste.html
    # e compara resultado a resultado. Sem isso a porta poderia divergir em
    # silêncio.
    caminho_gabarito = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "dados", "gabarito_fechamento.json")
    dezenas = [2, 3, 5, 6, 9, 10, 11, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
    resultado = [1, 2, 3, 5, 6, 9, 10, 11, 13, 14, 15, 16, 19, 20, 24]
    rateio = {"11": 7.0, "12": 14.0, "13": 35.0, "14": 1341.42, "15": 565758.41}
    gabarito = {"padroes": {}, "sorteios": {}}
    for pid in F.PADROES:
        base = dezenas[:F.PADROES[pid]["dezenas"]]
        jogos = F.montar(base, pid)
        gabarito["padroes"][pid] = {
            "jogos": jogos,
            "custo": F.custo_do_padrao(pid),
            "avaliacao": F.avaliar(jogos, resultado, rateio),
            # A garantia e o texto que a pagina publica; sem isso no
            # gabarito, a copia em JS poderia divergir da garantia provada
            # por forca bruta em robo/fechamento.py sem nada acusar.
            "garantias": F.PADROES[pid]["garantias"],
        }
    for semente in (1, 3757, 99999):
        gabarito["sorteios"][str(semente)] = F.dezenas_aleatorias(
            semente, 18, 1, 25)

    # Por padrão CONFERE, não reescreve. Antes este bloco regravava o arquivo
    # a cada execução — inclusive no CI, que roda este script e depois faz
    # `git add dados/`. Ou seja: mudar o motor em Python fazia o gabarito se
    # ajustar sozinho ao motor novo e ser commitado, e a divergência com o JS
    # só apareceria se alguém abrisse teste.html por conta própria. Uma
    # fixture que nunca falha não é fixture.
    # Para regravar de propósito: python robo/testar_fechamento.py --gabarito
    novo = json.dumps(gabarito, ensure_ascii=False)
    if "--gabarito" in sys.argv:
        with open(caminho_gabarito, "w", encoding="utf-8") as f:
            f.write(novo)
        print("Gabarito de fechamento REGRAVADO (--gabarito).")
    elif not os.path.exists(caminho_gabarito):
        checar(False, "gabarito: dados/gabarito_fechamento.json nao existe "
                      "(gere com --gabarito)")
    else:
        with open(caminho_gabarito, encoding="utf-8") as f:
            gravado = f.read()
        checar(gravado == novo,
               "gabarito: o arquivo commitado bate com o motor de hoje"
               + ("" if gravado == novo else
                  " — o motor mudou; confira js/fechamento.js e regrave com "
                  "--gabarito"))

    print()
    if falhas:
        print(f"{len(falhas)} FALHA(S).")
        sys.exit(1)
    print("Tudo certo.")
