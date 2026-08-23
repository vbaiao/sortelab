# -*- coding: utf-8 -*-
"""Robô de atualização do SorteLab.

Para cada loteria, consulta a API oficial da Caixa, baixa os concursos que
faltam em dados/{slug}.json e regrava o arquivo. Sem interação: feito para
rodar no GitHub Actions (ou manualmente: python robo/atualizar.py).

Códigos de saída: 0 = ok (com ou sem novidades); 1 = nenhuma loteria pôde
ser verificada (API indisponível).
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

import campeao
import exportar_csv
import fechamento
from loterias import API_BASE, LOTERIAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
ARQ_DESAFIO = os.path.join(PASTA_DADOS, "desafio.json")
ARQ_FECHAMENTO = os.path.join(PASTA_DADOS, "fechamento.json")
PRESET_FECHAMENTO = "18-5"
MAX_POR_EXECUCAO = 120   # limite de concursos baixados por loteria por rodada


def atualizar_desafio(slug, concursos):
    """Desafio do Campeão: confere o palpite cravado contra os resultados
    novos e crava o próximo. Determinístico e sem olhar o futuro."""
    if os.path.exists(ARQ_DESAFIO):
        with open(ARQ_DESAFIO, encoding="utf-8") as f:
            desafio = json.load(f)
    else:
        desafio = {}
    d = desafio.setdefault(slug, {"pendente": None, "historico": []})
    indice = {c[0]: c for c in concursos}
    mudou = False

    while d["pendente"] and (d["pendente"]["apos"] + 1) in indice:
        alvo = indice[d["pendente"]["apos"] + 1]
        jogo = d["pendente"]["jogo"]
        acertos = len(set(jogo) & set(alvo[2]))
        d["historico"].append({"concurso": alvo[0], "data": alvo[1],
                               "jogo": jogo, "resultado": alvo[2],
                               "acertos": acertos})
        corte = [c for c in concursos if c[0] <= alvo[0]]
        d["pendente"] = {"apos": alvo[0],
                         "jogo": campeao.jogo_campeao(slug, corte)}
        print(f"  Desafio: concurso {alvo[0]} conferido — {acertos} acerto(s); "
              f"novo palpite cravado.")
        mudou = True

    if not d["pendente"]:
        d["pendente"] = {"apos": concursos[-1][0],
                         "jogo": campeao.jogo_campeao(slug, concursos)}
        print(f"  Desafio: primeiro palpite cravado (após concurso "
              f"{concursos[-1][0]}).")
        mudou = True

    if mudou:
        with open(ARQ_DESAFIO, "w", encoding="utf-8") as f:
            json.dump(desafio, f, ensure_ascii=False, separators=(",", ":"))
    return mudou


def atualizar_fechamento(concursos):
    """Desafio do Fechamento: confere o pendente e crava o próximo.

    Dois lados por sorteio, mesmo padrão e mesmo custo: um montado sobre as
    18 dezenas do jogo campeão, outro sobre 18 dezenas sorteadas com semente
    igual ao número do concurso. O placar existe para mostrar que os dois
    empatam.

    A conta acumulada não é gravada: gasto e retorno são recalculados a
    partir do histórico, aqui e na página.
    """
    if os.path.exists(ARQ_FECHAMENTO):
        with open(ARQ_FECHAMENTO, encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {"preset": PRESET_FECHAMENTO, "pendente": None,
                 "historico": []}
    dados["preset"] = PRESET_FECHAMENTO
    indice = {c[0]: c for c in concursos}
    tamanho = fechamento.PADROES[PRESET_FECHAMENTO]["dezenas"]
    mudou = False

    def cravar(apos):
        corte = [c for c in concursos if c[0] <= apos]
        alvo = apos + 1
        return {
            "apos": apos,
            "campeao": {"dezenas": campeao.pool_campeao("lotofacil", corte,
                                                        tamanho)},
            "aleatorio": {"dezenas": fechamento.dezenas_aleatorias(
                              alvo, tamanho, 1, 25),
                          "semente": alvo},
        }

    while dados["pendente"] and (dados["pendente"]["apos"] + 1) in indice:
        pendente = dados["pendente"]
        sorteio = indice[pendente["apos"] + 1]
        if len(sorteio[2]) != 15:
            print(f"  Fechamento: concurso {sorteio[0]} ainda sem dezenas; "
                  f"aguardando.")
            break                      # concurso sem dezenas: espera a próxima rodada
        rateio = rateio_do_concurso(sorteio[0])
        linha = {"concurso": sorteio[0], "data": sorteio[1],
                 "resultado": sorteio[2], "rateio": rateio}
        for lado in ("campeao", "aleatorio"):
            dezenas = pendente[lado]["dezenas"]
            jogos = fechamento.montar(dezenas, PRESET_FECHAMENTO)
            nota = fechamento.avaliar(jogos, sorteio[2], rateio)
            linha[lado] = {"dezenas": dezenas, "acertos": nota["acertos"],
                           "retorno": nota["retorno"]}
        dados["historico"].append(linha)
        dados["pendente"] = cravar(sorteio[0])
        melhor_c = max(linha["campeao"]["acertos"])
        melhor_a = max(linha["aleatorio"]["acertos"])
        print(f"  Fechamento: concurso {sorteio[0]} conferido — "
              f"campeão {melhor_c}, aleatório {melhor_a}; próximo cravado.")
        mudou = True

    if not dados["pendente"]:
        dados["pendente"] = cravar(concursos[-1][0])
        print(f"  Fechamento: primeiro palpite cravado (após concurso "
              f"{concursos[-1][0]}).")
        mudou = True

    if mudou:
        with open(ARQ_FECHAMENTO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
    return mudou


def buscar(slug, numero=None, timeout=20, bruto=False):
    """Consulta um concurso na API da Caixa.

    Por padrão devolve só (numero, data, dezenas) — o suficiente para os
    chamadores existentes. Com bruto=True devolve o JSON completo, porque
    rateio_do_concurso precisa da tabela de prêmios que esse recorte descarta.
    """
    url = API_BASE + slug + ("" if numero is None else f"/{numero}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (SorteLab; +https://github.com)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dados = json.load(resp)
    if bruto:
        return dados
    return (int(dados["numero"]), dados["dataApuracao"],
            sorted(int(x) for x in dados["listaDezenas"]))


def rateio_do_concurso(numero):
    """Valores reais de prêmio daquele concurso, vindos da API da Caixa.

    Devolve {"11": 7.0, "12": 14.0, ...} ou None se a API não trouxer.
    Nunca estima: sem rateio, o retorno fica em branco na página.
    """
    time.sleep(0.4)   # educação com a API
    try:
        dados = buscar("lotofacil", numero, bruto=True)
    except Exception:
        return None
    tabela = {}
    for faixa in dados.get("listaRateioPremio", []):
        digitos = "".join(c for c in faixa.get("descricaoFaixa", "")
                          if c.isdigit())
        valor = faixa.get("valorPremio")
        if digitos and valor is not None:
            tabela[digitos] = float(valor)
    return tabela or None


def atualizar_loteria(cfg):
    caminho = os.path.join(PASTA_DADOS, f"{cfg['slug']}.json")
    if not os.path.exists(caminho):
        print(f"{cfg['nome']}: sem JSON base — rode importar_csv.py antes.")
        return None
    with open(caminho, encoding="utf-8") as f:
        base = json.load(f)
    concursos = base["concursos"]
    ultimo_local = concursos[-1][0]

    try:
        ultimo_api, _, _ = buscar(cfg["slug"])
    except Exception as erro:
        print(f"{cfg['nome']}: API indisponível ({erro}).")
        return None

    # O endpoint "último" da Caixa às vezes fica defasado (aponta para um
    # concurso antigo mesmo com o novo já publicado). Sonda adiante para
    # descobrir o último concurso que existe de verdade.
    ultimo_real = max(ultimo_api, ultimo_local)
    for _ in range(10):
        try:
            proximo = buscar(cfg["slug"], ultimo_real + 1)
        except Exception:
            break
        ultimo_real = proximo[0]
        time.sleep(0.3)

    if ultimo_real <= ultimo_local:
        print(f"{cfg['nome']}: em dia (concurso {ultimo_local}).")
        return False

    inicio = ultimo_local + 1
    fim = min(ultimo_real, ultimo_local + MAX_POR_EXECUCAO)
    novos = []
    for n in range(inicio, fim + 1):
        try:
            info = buscar(cfg["slug"], n)
        except Exception as erro:
            print(f"{cfg['nome']}: falha no concurso {n} ({erro}); "
                  f"salvando o que veio.")
            break
        novos.append([info[0], info[1], info[2]])
        time.sleep(0.4)   # educação com a API

    if not novos:
        return False
    concursos.extend(novos)
    base["atualizado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{cfg['nome']}: +{len(novos)} concurso(s) "
          f"(até {novos[-1][0]} de {novos[-1][1]}).")
    return True


def main():
    verificadas = 0
    houve_novidade = False
    for cfg in LOTERIAS:
        resultado = atualizar_loteria(cfg)
        if resultado is not None:
            verificadas += 1
        if resultado:
            houve_novidade = True
        caminho = os.path.join(PASTA_DADOS, f"{cfg['slug']}.json")
        if os.path.exists(caminho):
            with open(caminho, encoding="utf-8") as f:
                concursos = json.load(f)["concursos"]
            try:
                if atualizar_desafio(cfg["slug"], concursos):
                    houve_novidade = True
            except Exception as erro:
                print(f"{cfg['nome']}: desafio falhou ({erro}).")
            if cfg["slug"] == "lotofacil":
                try:
                    if atualizar_fechamento(concursos):
                        houve_novidade = True
                except Exception as erro:
                    print(f"{cfg['nome']}: fechamento falhou ({erro}).")
            try:
                if exportar_csv.exportar(cfg["slug"], concursos):
                    print(f"  CSV de download atualizado.")
                    houve_novidade = True
            except Exception as erro:
                print(f"{cfg['nome']}: exportação CSV falhou ({erro}).")
    if verificadas == 0:
        print("Nenhuma loteria pôde ser verificada.")
        sys.exit(1)
    print("Novidades!" if houve_novidade else "Tudo em dia.")


if __name__ == "__main__":
    main()
