# -*- coding: utf-8 -*-
"""Gera as 8 páginas de loteria (megasena.html, ...), sitemap.xml e robots.txt
a partir do template embutido. Rodar sempre que o template mudar:
    python robo/gerar_paginas.py
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGINAS = [
    dict(slug="megasena", nome="Mega-Sena", cor="#209869",
         aposta="6 a 20 dezenas de 1 a 60 · sorteio de 6",
         descricao="Gerador estatístico, conferidor copia-e-cola e calculadora "
                   "de bolão com rateio para a Mega-Sena. Grátis e honesto: "
                   "nada aumenta sua chance, a gente só organiza a brincadeira.",
         intro="A Mega-Sena sorteia 6 dezenas de 60. Aqui você gera jogos com "
               "base na estatística de todos os concursos desde 1996, monta "
               "bolão com rateio pronto para o WhatsApp e confere vários "
               "jogos de uma vez."),
    dict(slug="lotofacil", nome="Lotofácil", cor="#930089",
         aposta="15 a 20 dezenas de 1 a 25 · sorteio de 15",
         descricao="Gerador estatístico, conferidor de vários jogos e bolão "
                   "com rateio para a Lotofácil. Ferramentas grátis do SorteLab.",
         intro="A Lotofácil sorteia 15 dezenas de 25 — a queridinha dos "
               "bolões. Gere jogos com o perfil típico dos sorteios, monte o "
               "bolão do grupo com rateio pronto para o WhatsApp e confira "
               "todos os jogos de uma vez."),
    dict(slug="quina", nome="Quina", cor="#260085",
         aposta="5 a 15 dezenas de 1 a 80 · sorteio de 5",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Quina. Ferramentas grátis do SorteLab.",
         intro="A Quina sorteia 5 dezenas de 80, todos os dias. Gere jogos "
               "guiados pela estatística do histórico completo, planeje o "
               "orçamento e confira seus jogos em segundos."),
    dict(slug="lotomania", nome="Lotomania", cor="#E07000",
         aposta="50 dezenas de 00 a 99 · sorteio de 20 · 0 acertos também paga",
         descricao="Gerador de 50 dezenas, conferidor e bolão com rateio para "
                   "a Lotomania. Ferramentas grátis do SorteLab.",
         intro="Na Lotomania você marca 50 dezenas de 100 e ganha com 15 a 20 "
               "acertos — ou com nenhum! Gere seu cartão com base na "
               "estatística e confira sem sofrimento (são muitas dezenas, "
               "deixa que a gente conta)."),
    dict(slug="duplasena", nome="Dupla Sena", cor="#A61324",
         aposta="6 a 15 dezenas de 1 a 50 · dois sorteios por concurso",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Dupla Sena. Ferramentas grátis do SorteLab.",
         intro="A Dupla Sena dá duas chances por concurso: dois sorteios de 6 "
               "dezenas de 50. O histórico aqui usa o 1º sorteio; para "
               "conferir o 2º, é só digitar as dezenas dele no conferidor."),
    dict(slug="diadesorte", nome="Dia de Sorte", cor="#CB852B",
         aposta="7 a 15 dezenas de 1 a 31 + Mês da Sorte",
         descricao="Gerador estatístico, conferidor e bolão com rateio para o "
                   "Dia de Sorte. Ferramentas grátis do SorteLab.",
         intro="O Dia de Sorte sorteia 7 dezenas de 31, mais o Mês da Sorte. "
               "Gere jogos com base no histórico e confira os seus — o mês "
               "você escolhe no volante, do seu jeito."),
    dict(slug="timemania", nome="Timemania", cor="#0E8A3E",
         aposta="10 dezenas fixas de 1 a 80 + Time do Coração",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Timemania. Ferramentas grátis do SorteLab.",
         intro="Na Timemania você marca 10 dezenas de 80 e o seu Time do "
               "Coração. Gere os números pela estatística — o time, claro, "
               "é questão de fé."),
    dict(slug="maismilionaria", nome="+Milionária", cor="#2E3078",
         aposta="6 a 12 dezenas de 1 a 50 + 2 trevos",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "+Milionária. Ferramentas grátis do SorteLab.",
         intro="A +Milionária sorteia 6 dezenas de 50 e 2 trevos de 6. As "
               "dezenas você gera aqui pela estatística; os trevos são "
               "marcados à parte no volante."),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{nome}: Gerador, Bolão com Rateio e Conferidor — SorteLab</title>
<meta name="description" content="{descricao}">
<meta property="og:title" content="{nome} — Gerador, Bolão e Conferidor | SorteLab">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Rubik:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/estilo.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='46' fill='%23C99011'/><text x='50' y='66' font-size='48' text-anchor='middle' font-family='Arial Black'>7</text></svg>">
<style>:root {{ --cor: {cor}; --cor-suave: {cor}14; }}</style>
</head>
<body>

<header class="topo">
  <div class="miolo">
    <a class="marca" href="index.html"><span class="bolinha-logo">7</span>SorteLab</a>
    <nav><a href="index.html">Todas as loterias</a></nav>
  </div>
</header>

<div class="faixa-loteria">
  <div class="miolo">
    <h1>{nome}</h1>
    <p class="sub">{aposta}</p>
    <div class="ultimo-resultado" id="ultimo-resultado">Carregando o último resultado…</div>
  </div>
</div>

<nav class="abas" aria-label="Ferramentas">
  <div class="miolo">
    <button class="aba" data-alvo="gerador" aria-selected="true">🎲 Gerador</button>
    <button class="aba" data-alvo="bolao" aria-selected="false">👥 Bolão</button>
    <button class="aba" data-alvo="orcamento" aria-selected="false">💰 Orçamento</button>
    <button class="aba" data-alvo="conferidor" aria-selected="false">✅ Conferidor</button>
    <button class="aba" data-alvo="estatisticas" aria-selected="false">📊 Estatísticas</button>
  </div>
</nav>

<main class="miolo painel">

  <p class="dica" style="margin-top:0">{intro}</p>
  <div class="anuncio" aria-hidden="true"><!-- espaço reservado: anúncio topo --></div>

  <section class="ferramenta" id="gerador">
    <div class="cartao">
      <h2>Gerar jogos</h2>
      <p class="dica">Sorteio ponderado: dezenas com melhor score no histórico
      têm mais chance de entrar, e todo jogo respeita o perfil típico dos
      sorteios (soma, pares/ímpares e espalhamento).</p>
      <form id="form-gerador">
        <div class="linha-campos">
          <div class="campo">
            <label for="ger-qtd">Quantos jogos?</label>
            <input type="number" id="ger-qtd" min="1" max="100" value="5">
          </div>
        </div>
        <div class="botoes">
          <button class="botao" type="submit">Gerar jogos</button>
          <button class="botao secundario" type="button" id="btn-campeao">Gerar o jogo campeão</button>
          <button class="botao secundario" type="button" id="btn-copiar-jogos" hidden>Copiar jogos</button>
        </div>
      </form>
      <div id="ger-saida"></div>
      <div class="caixa-resumo" id="ger-resumo" hidden></div>
      {obs_html}
    </div>
  </section>

  <section class="ferramenta" id="bolao" hidden>
    <div class="cartao">
      <h2>Montar bolão</h2>
      <p class="dica">Gere os jogos do grupo, faça o rateio e copie a mensagem
      pronta para o WhatsApp.</p>
      <form id="form-bolao">
        <div class="linha-campos">
          <div class="campo">
            <label for="bol-jogos">Jogos</label>
            <input type="number" id="bol-jogos" min="1" max="50" value="4">
          </div>
          {campo_dezenas}
          <div class="campo">
            <label for="bol-pessoas">Pessoas</label>
            <input type="number" id="bol-pessoas" min="1" max="100" value="4">
          </div>
          <div class="campo">
            <label for="bol-valor">Valor total (R$) — vazio usa o custo oficial</label>
            <input type="text" id="bol-valor" inputmode="decimal" placeholder="ex.: 120,00">
          </div>
        </div>
        <button class="botao" type="submit">Montar bolão</button>
      </form>
      <div id="bol-saida"></div>
      <div class="caixa-resumo" id="bol-rateio" hidden></div>
      <div class="msg-whats" id="bol-msg" hidden></div>
      <div class="botoes">
        <button class="botao" type="button" id="btn-copiar-whats" hidden>Copiar mensagem</button>
        <a class="botao secundario" id="btn-abrir-whats" hidden target="_blank" rel="noopener">Abrir no WhatsApp</a>
      </div>
      {obs_html}
    </div>
  </section>

  <section class="ferramenta" id="orcamento" hidden>
    <div class="cartao">
      <h2>Planejar pelo orçamento</h2>
      <p class="dica">Diga quanto o grupo tem e veja todas as formas de gastar
      — com a chance real de cada uma, sem promessa milagrosa.</p>
      <form id="form-orcamento">
        <div class="linha-campos">
          <div class="campo">
            <label for="orc-valor">Quanto vocês têm? (R$)</label>
            <input type="text" id="orc-valor" inputmode="decimal" placeholder="ex.: 100">
          </div>
          <div class="campo">
            <label for="orc-pessoas">Pessoas</label>
            <input type="number" id="orc-pessoas" min="1" max="100" value="1">
          </div>
        </div>
        <button class="botao" type="submit">Ver possibilidades</button>
      </form>
      <p class="erro" id="orc-erro" hidden></p>
      <div id="orc-tabela" style="margin-top:14px"></div>
      <div id="orc-saida" hidden style="margin-top:18px"></div>
    </div>
  </section>

  <section class="ferramenta" id="conferidor" hidden>
    <div class="cartao">
      <h2>Conferir jogos</h2>
      <p class="dica">Informe o resultado, cole seus jogos (um por linha, em
      qualquer formato: 05-10-22, 5 10 22, ou linhas copiadas daqui) e veja os
      acertos marcados.</p>
      <form id="form-conferidor">
        <div class="linha-campos">
          <div class="campo" style="flex:2">
            <label for="conf-resultado">Resultado sorteado</label>
            <input type="text" id="conf-resultado" inputmode="numeric" placeholder="dezenas do sorteio">
          </div>
          <div class="campo" style="justify-content:flex-end">
            <button class="botao secundario" type="button" id="btn-ultimo">Usar último resultado</button>
          </div>
        </div>
        <div class="campo">
          <label for="conf-jogos">Seus jogos (um por linha)</label>
          <textarea id="conf-jogos" placeholder="Jogo 1: ..."></textarea>
        </div>
        <button class="botao" type="submit" style="margin-top:12px">Conferir</button>
      </form>
      <p class="erro" id="conf-erro" hidden></p>
      <div id="conf-saida" hidden style="margin-top:14px"></div>
      {obs_html}
    </div>
  </section>

  <section class="ferramenta" id="estatisticas" hidden>
    <p class="dica" id="atualizado-em"></p>
    <div id="est-conteudo"></div>
    <div class="aviso-obs">Curiosidade honesta: essas listas descrevem o
    passado, não preveem o futuro. Cada dezena tem exatamente a mesma chance
    em todo sorteio — o globo não tem memória.</div>
  </section>

  <div class="anuncio" aria-hidden="true"><!-- espaço reservado: anúncio rodapé --></div>
</main>

<footer class="rodape">
  <div class="miolo">
    <div class="selo-honesto"><strong>O selo honesto do SorteLab:</strong>
    nenhuma estatística aumenta sua chance de ganhar — e quem prometer o
    contrário está te enganando. Nossas ferramentas organizam a brincadeira:
    jogos com perfil de sorteio real, bolão sem briga na hora do rateio e
    conferência sem dor de cabeça. Jogue por diversão e com moderação. Proibido
    para menores de 18 anos.</div>
    <p>SorteLab — ferramentas gratuitas para loterias ·
    <a href="index.html">todas as loterias</a> · dados oficiais da Caixa,
    atualizados todo dia após os sorteios. Este site não tem vínculo com a
    Caixa Econômica Federal e não vende apostas.</p>
  </div>
</footer>

<script>window.PAGINA = {{ slug: "{slug}" }};</script>
<script src="js/motor.js"></script>
<script src="js/app.js"></script>
</body>
</html>
"""

CAMPO_DEZENAS_VARIAVEL = """<div class="campo">
            <label for="bol-dezenas">Dezenas por jogo</label>
            <select id="bol-dezenas">{opcoes}</select>
          </div>"""


def gerar():
    # importa as fichas do motor JS? Não: usa limites conhecidos por slug.
    limites = {
        "megasena": (6, 20), "lotofacil": (15, 20), "quina": (5, 15),
        "lotomania": (50, 50), "duplasena": (6, 15), "diadesorte": (7, 15),
        "timemania": (10, 10), "maismilionaria": (6, 12),
    }
    observacoes = {
        "duplasena": "O histórico usa o 1º sorteio de cada concurso; para "
                     "conferir o 2º, digite as dezenas dele no conferidor.",
        "diadesorte": "O “Mês da Sorte” é marcado à parte no volante.",
        "timemania": "O “Time do Coração” é marcado à parte no volante.",
        "maismilionaria": "Os 2 trevos (1 a 6) são marcados à parte no volante.",
        "lotomania": "Na Lotomania, 0 acertos também paga prêmio!",
    }
    urls = []
    for pagina in PAGINAS:
        minimo, maximo = limites[pagina["slug"]]
        if minimo == maximo:
            campo = ""
        else:
            opcoes = "".join(f'<option value="{k}">{k}</option>'
                             for k in range(minimo, maximo + 1))
            campo = CAMPO_DEZENAS_VARIAVEL.format(opcoes=opcoes)
        obs = observacoes.get(pagina["slug"], "")
        obs_html = (f'<div class="aviso-obs">ℹ️ {obs}</div>' if obs else "")
        html = TEMPLATE.format(campo_dezenas=campo, obs_html=obs_html, **pagina)
        destino = os.path.join(RAIZ, f"{pagina['slug']}.html")
        with open(destino, "w", encoding="utf-8") as f:
            f.write(html)
        urls.append(f"{pagina['slug']}.html")
        print(f"OK {destino}")

    with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in ["index.html"] + urls:
            f.write(f"  <url><loc>https://vbaiao.github.io/sortelab/{u}"
                    f"</loc></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n"
                "Sitemap: https://vbaiao.github.io/sortelab/sitemap.xml\n")
    print("OK sitemap.xml e robots.txt")


if __name__ == "__main__":
    gerar()
