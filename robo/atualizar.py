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
from loterias import API_BASE, LOTERIAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
ARQ_DESAFIO = os.path.join(PASTA_DADOS, "desafio.json")
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


def buscar(slug, numero=None, timeout=20):
    url = API_BASE + slug + ("" if numero is None else f"/{numero}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (SorteLab; +https://github.com)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dados = json.load(resp)
    return (int(dados["numero"]), dados["dataApuracao"],
            sorted(int(x) for x in dados["listaDezenas"]))


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
    if verificadas == 0:
        print("Nenhuma loteria pôde ser verificada.")
        sys.exit(1)
    print("Novidades!" if houve_novidade else "Tudo em dia.")


if __name__ == "__main__":
    main()
