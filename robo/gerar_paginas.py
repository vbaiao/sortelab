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
                   "com rateio para a Lotofácil. Ferramentas grátis do SorteLabs.",
         intro="A Lotofácil sorteia 15 dezenas de 25 — a queridinha dos "
               "bolões. Gere jogos com o perfil típico dos sorteios, monte o "
               "bolão do grupo com rateio pronto para o WhatsApp e confira "
               "todos os jogos de uma vez."),
    dict(slug="quina", nome="Quina", cor="#260085",
         aposta="5 a 15 dezenas de 1 a 80 · sorteio de 5",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Quina. Ferramentas grátis do SorteLabs.",
         intro="A Quina sorteia 5 dezenas de 80, todos os dias. Gere jogos "
               "guiados pela estatística do histórico completo, planeje o "
               "orçamento e confira seus jogos em segundos."),
    dict(slug="lotomania", nome="Lotomania", cor="#E07000",
         aposta="50 dezenas de 00 a 99 · sorteio de 20 · 0 acertos também paga",
         descricao="Gerador de 50 dezenas, conferidor e bolão com rateio para "
                   "a Lotomania. Ferramentas grátis do SorteLabs.",
         intro="Na Lotomania você marca 50 dezenas de 100 e ganha com 15 a 20 "
               "acertos — ou com nenhum! Gere seu cartão com base na "
               "estatística e confira sem sofrimento (são muitas dezenas, "
               "deixa que a gente conta)."),
    dict(slug="duplasena", nome="Dupla Sena", cor="#A61324",
         aposta="6 a 15 dezenas de 1 a 50 · dois sorteios por concurso",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Dupla Sena. Ferramentas grátis do SorteLabs.",
         intro="A Dupla Sena dá duas chances por concurso: dois sorteios de 6 "
               "dezenas de 50. O histórico aqui usa o 1º sorteio; para "
               "conferir o 2º, é só digitar as dezenas dele no conferidor."),
    dict(slug="diadesorte", nome="Dia de Sorte", cor="#CB852B",
         aposta="7 a 15 dezenas de 1 a 31 + Mês da Sorte",
         descricao="Gerador estatístico, conferidor e bolão com rateio para o "
                   "Dia de Sorte. Ferramentas grátis do SorteLabs.",
         intro="O Dia de Sorte sorteia 7 dezenas de 31, mais o Mês da Sorte. "
               "Gere jogos com base no histórico e confira os seus — o mês "
               "você escolhe no volante, do seu jeito."),
    dict(slug="timemania", nome="Timemania", cor="#0E8A3E",
         aposta="10 dezenas fixas de 1 a 80 + Time do Coração",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "Timemania. Ferramentas grátis do SorteLabs.",
         intro="Na Timemania você marca 10 dezenas de 80 e o seu Time do "
               "Coração. Gere os números pela estatística — o time, claro, "
               "é questão de fé."),
    dict(slug="maismilionaria", nome="+Milionária", cor="#2E3078",
         aposta="6 a 12 dezenas de 1 a 50 + 2 trevos",
         descricao="Gerador estatístico, conferidor e bolão com rateio para a "
                   "+Milionária. Ferramentas grátis do SorteLabs.",
         intro="A +Milionária sorteia 6 dezenas de 50 e 2 trevos de 6. As "
               "dezenas você gera aqui pela estatística; os trevos são "
               "marcados à parte no volante."),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="1ASDodTUQNNEFQTdYF4TCvACuHrtQRBXcfsDynb9Msk" />
<title>{nome}: Gerador, Bolão com Rateio e Conferidor — SorteLabs</title>
<meta name="description" content="{descricao}">
<meta property="og:title" content="{nome} — Gerador, Bolão e Conferidor | SorteLabs">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<link rel="canonical" href="https://sortelabs.com.br/{slug}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/estilo.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%230A0D12'/><rect x='18' y='18' width='26' height='26' rx='6' fill='%23CF9F3F'/><rect x='56' y='18' width='26' height='26' rx='6' fill='%23222A35'/><rect x='18' y='56' width='26' height='26' rx='6' fill='%23222A35'/><rect x='56' y='56' width='26' height='26' rx='6' fill='%23CF9F3F'/></svg>">
<style>:root {{ --cor: {cor}; }}</style>
</head>
<body>

<header class="topo">
  <div class="miolo">
    <a class="marca" href="index.html"><span class="sorte">Sorte</span><span class="labs">Labs</span></a>
    <nav><a href="desafio.html">Desafio</a><a href="index.html">Todas as loterias</a></nav>
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
    <button class="aba" data-alvo="gerador" aria-selected="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.7 4.8L18.5 9.5 13.7 11.2 12 16l-1.7-4.8L5.5 9.5l4.8-1.7z"/><path d="M18 15l.7 1.8 1.8.7-1.8.7L18 20l-.7-1.8-1.8-.7 1.8-.7z"/></svg><span>Gerador</span></button>
    <button class="aba" data-alvo="bolao" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 19.5c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M16.5 5.4a3.2 3.2 0 0 1 0 6.2"/><path d="M17.5 14.8c2.1.5 3.5 2.3 3.5 4.7"/></svg><span>Bolão</span></button>
    <button class="aba" data-alvo="orcamento" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v5M18 9.5v5"/></svg><span>Orçamento</span></button>
    <button class="aba" data-alvo="conferidor" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 11.2V12a8.5 8.5 0 1 1-5-7.8"/><path d="M8.5 11.5l3 3 9-9"/></svg><span>Conferidor</span></button>
    <button class="aba" data-alvo="estatisticas" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 20.5h17"/><rect x="5" y="12" width="3.6" height="6"/><rect x="10.2" y="7.5" width="3.6" height="10.5"/><rect x="15.4" y="4" width="3.6" height="14"/></svg><span>Estatísticas</span></button>
  </div>
</nav>

<main class="miolo painel">

  <p class="dica" style="margin-top:0">{intro}</p>
  <div class="anuncio" aria-hidden="true"><!-- espaço reservado: anúncio topo --></div>

  <section class="ferramenta" id="gerador">
    <div class="cartao">
      <h2>Gerar jogos</h2>
      <p class="dica">Cada dezena recebe uma nota (o <em>score</em>): 50% da
      frequência em todo o histórico, 35% da frequência nos últimos 200
      concursos e 15% do atraso, que é há quantos concursos ela não sai. As
      dezenas com nota melhor entram com mais facilidade no sorteio dos seus
      jogos — mas há aleatoriedade, então cada clique traz jogos diferentes.</p>
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
      <p class="dica" style="margin:12px 0 0">
      <strong>Jogo campeão:</strong> em vez de sortear, ele testa as
      combinações das dezenas mais bem pontuadas e devolve a de maior nota
      total — um único jogo, sempre o mesmo, até sair um novo concurso e as
      notas mudarem. É o palpite que usamos no
      <a href="desafio.html">Desafio do Campeão</a>, onde registramos em
      público quantos acertos ele faz a cada sorteio.</p>
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
            <label for="bol-valor">Valor total (R$)</label>
            <input type="text" id="bol-valor" inputmode="decimal" placeholder="ex.: 120,00">
            <small class="ajuda">Em branco, usamos o custo oficial.</small>
          </div>
        </div>
        <div class="botoes">
          <button class="botao" type="submit">Montar bolão</button>
          <button class="botao secundario" type="button" id="btn-copiar-whats" hidden>Copiar mensagem</button>
          <a class="botao secundario" id="btn-abrir-whats" hidden target="_blank" rel="noopener">Abrir no WhatsApp</a>
        </div>
      </form>
      <div id="bol-saida"></div>
      <div class="caixa-resumo" id="bol-rateio" hidden></div>
      <div class="msg-whats" id="bol-msg" hidden></div>
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
            <label for="orc-valor">Orçamento (R$)</label>
            <input type="text" id="orc-valor" inputmode="decimal" placeholder="ex.: 100">
          </div>
          <div class="campo">
            <label for="orc-pessoas">Pessoas</label>
            <input type="number" id="orc-pessoas" min="1" max="100" value="1">
          </div>
        </div>
        <div class="botoes">
          <button class="botao" type="submit">Ver possibilidades</button>
        </div>
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
          <div class="campo">
            <label for="conf-resultado">Resultado sorteado</label>
            <input type="text" id="conf-resultado" inputmode="numeric" placeholder="dezenas do sorteio">
            <small class="ajuda">Separe por espaço, traço ou vírgula.</small>
          </div>
        </div>
        <div class="linha-campos">
          <div class="campo">
            <label for="conf-jogos">Seus jogos (um por linha)</label>
            <textarea id="conf-jogos" placeholder="Cole aqui, um jogo por linha"></textarea>
          </div>
        </div>
        <div class="botoes">
          <button class="botao" type="submit">Conferir</button>
          <button class="botao secundario" type="button" id="btn-ultimo">Usar último resultado</button>
        </div>
      </form>
      <p class="erro" id="conf-erro" hidden></p>
      <div id="conf-saida" hidden style="margin-top:14px"></div>
      {obs_html}
    </div>
  </section>

  <section class="ferramenta" id="estatisticas" hidden>
    <p class="dica" id="atualizado-em"></p>
    <div id="est-conteudo"></div>
    <div class="cartao">
      <h2>Baixar o histórico completo</h2>
      <p class="dica">Todos os concursos da {nome} desde o primeiro sorteio, num
      arquivo só e atualizado junto com o site. O CSV abre direto no Excel (dois
      cliques) com uma dezena por coluna; o JSON é o mesmo dado para quem quiser
      usar em programação. Pode usar como quiser — são dados públicos da Caixa.</p>
      <div class="botoes">
        <a class="botao" href="dados/csv/{slug}.csv" download>Baixar CSV (Excel)</a>
        <a class="botao secundario" href="dados/{slug}.json" download>Baixar JSON</a>
      </div>
    </div>
    <div class="aviso-obs">Curiosidade honesta: essas listas descrevem o
    passado, não preveem o futuro. Cada dezena tem exatamente a mesma chance
    em todo sorteio — o globo não tem memória.</div>
  </section>

  <div class="anuncio" aria-hidden="true"><!-- espaço reservado: anúncio rodapé --></div>
</main>

<footer class="rodape">
  <div class="miolo">
    <div class="selo-honesto"><strong>O selo honesto do SorteLabs:</strong>
    nenhuma estatística aumenta sua chance de ganhar — e quem prometer o
    contrário está te enganando. Nossas ferramentas organizam a brincadeira:
    jogos com perfil de sorteio real, bolão sem briga na hora do rateio e
    conferência sem dor de cabeça. Jogue por diversão e com moderação. Proibido
    para menores de 18 anos.</div>
    <p>SorteLabs — ferramentas gratuitas para loterias ·
    <a href="index.html">todas as loterias</a> · dados oficiais da Caixa,
    atualizados todo dia após os sorteios. Este site não tem vínculo com a
    Caixa Econômica Federal e não vende apostas.</p>
  </div>
</footer>

<script>window.PAGINA = {{ slug: "{slug}" }};</script>
<script src="js/interface.js"></script>
<script src="js/motor.js"></script>
<script src="js/app.js"></script>
<script data-goatcounter="https://sortelabs.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
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
        for u in ["index.html", "desafio.html"] + urls:
            f.write(f"  <url><loc>https://sortelabs.com.br/{u}"
                    f"</loc></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n"
                "Sitemap: https://sortelabs.com.br/sitemap.xml\n")
    print("OK sitemap.xml e robots.txt")


if __name__ == "__main__":
    gerar()
