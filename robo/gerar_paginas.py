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
         descricao="Monte jogos da Mega-Sena, organize o bolão com a divisão pronta e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="A Mega-Sena sorteia 6 dezenas entre 1 e 60. Aqui você monta seus jogos, organiza o bolão do grupo e confere tudo de uma vez. Usamos todos os sorteios desde 1996."),
    dict(slug="lotofacil", nome="Lotofácil", cor="#930089",
         aposta="15 a 20 dezenas de 1 a 25 · sorteio de 15",
         descricao="Monte jogos da Lotofácil, organize o bolão do grupo e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="A Lotofácil sorteia 15 dezenas entre 1 e 25. É a loteria preferida dos bolões, porque acertar 11 números já paga. Monte seus jogos, divida o bolão e confira tudo aqui."),
    dict(slug="quina", nome="Quina", cor="#260085",
         aposta="5 a 15 dezenas de 1 a 80 · sorteio de 5",
         descricao="Monte jogos da Quina, organize o bolão do grupo e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="A Quina sorteia 5 dezenas entre 1 e 80, quase todo dia. Acertar 2 números já paga prêmio. Monte seus jogos, planeje quanto gastar e confira os resultados."),
    dict(slug="lotomania", nome="Lotomania", cor="#E07000",
         aposta="50 dezenas de 00 a 99 · sorteio de 20 · 0 acertos também paga",
         descricao="Monte seu cartão de 50 dezenas da Lotomania, organize o bolão e confira sem contar na mão. Grátis e sem cadastro.",
         intro="Na Lotomania você marca 50 dezenas entre 00 e 99, e o sorteio tira 20. Ganha quem acerta de 15 a 20 — ou quem não acerta nenhuma! Aqui você monta o cartão e confere sem contar na mão."),
    dict(slug="duplasena", nome="Dupla Sena", cor="#A61324",
         aposta="6 a 15 dezenas de 1 a 50 · dois sorteios por concurso",
         descricao="Monte jogos da Dupla Sena, organize o bolão do grupo e confira os dois sorteios do concurso. Grátis e sem cadastro.",
         intro="A Dupla Sena sorteia 6 dezenas entre 1 e 50, duas vezes no mesmo concurso. São duas chances por aposta. Aqui você monta os jogos e confere os dois sorteios."),
    dict(slug="diadesorte", nome="Dia de Sorte", cor="#CB852B",
         aposta="7 a 15 dezenas de 1 a 31 + Mês da Sorte",
         descricao="Monte jogos do Dia de Sorte, organize o bolão do grupo e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="O Dia de Sorte sorteia 7 dezenas entre 1 e 31, mais um mês da sorte. A gente cuida das dezenas; o mês você escolhe no volante."),
    dict(slug="timemania", nome="Timemania", cor="#0E8A3E",
         aposta="10 dezenas fixas de 1 a 80 + Time do Coração",
         descricao="Monte jogos da Timemania, organize o bolão do grupo e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="Na Timemania você marca 10 dezenas entre 1 e 80, mais o seu time do coração. A gente ajuda com os números. O time, claro, é você quem escolhe."),
    dict(slug="maismilionaria", nome="+Milionária", cor="#2E3078",
         aposta="6 a 12 dezenas de 1 a 50 + 2 trevos",
         descricao="Monte jogos da +Milionária, organize o bolão do grupo e confira vários jogos de uma vez. Grátis e sem cadastro.",
         intro="A +Milionária sorteia 6 dezenas entre 1 e 50, mais 2 trevos. Aqui você monta as dezenas; os trevos você marca no volante."),
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
    <a class="marca" href="/"><span class="sorte">Sorte</span><span class="labs">Labs</span></a>
    <nav><a href="desafio.html">Desafio</a><a href="/">Todas as loterias</a></nav>
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
      <p class="dica">Damos uma nota para cada dezena. A nota olha três coisas. Quantas
      vezes a dezena já saiu. Quantas vezes ela saiu nos últimos 200 sorteios.
      E há quanto tempo ela não sai. As dezenas com nota alta aparecem
      mais nos seus jogos. Mas tem sorteio no meio: cada vez que você clica,
      saem jogos diferentes.</p>
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
      <strong>E o botão "jogo campeão"?</strong> Ele não sorteia: ele monta o
      jogo com as dezenas de nota mais alta. É um jogo só, e ele fica o mesmo
      até sair o próximo sorteio. É esse jogo que usamos no
      <a href="desafio.html">Desafio do Campeão</a>, onde mostramos quantos
      números ele acerta toda vez.</p>
      <div id="ger-saida"></div>
      <div class="caixa-resumo" id="ger-resumo" hidden></div>
      {obs_html}
    </div>
  </section>

  <section class="ferramenta" id="bolao" hidden>
    <div class="cartao">
      <h2>Montar bolão</h2>
      <p class="dica">Monte os jogos do grupo, veja quanto cada pessoa paga e
      copie a mensagem pronta para mandar no WhatsApp.</p>
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
      <p class="dica">Diga quanto vocês têm para gastar. Mostramos as opções de
      jogo que cabem nesse dinheiro, quanto sobra e a chance de cada uma.</p>
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
      <p class="dica">Primeiro coloque o resultado do sorteio. Depois cole seus
      jogos, um em cada linha. Pode colar do jeito que estiver: 05-10-22 ou
      5 10 22. Vamos marcar os números que você acertou.</p>
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
      <p class="dica">Baixe todos os sorteios da {nome}, desde o primeiro. O
      arquivo CSV abre no Excel com dois cliques, com uma dezena em cada coluna.
      O JSON é para quem programa. É de graça e você pode usar como quiser.</p>
      <div class="botoes">
        <a class="botao" href="dados/csv/{slug}.csv" download>Baixar CSV (Excel)</a>
        <a class="botao secundario" href="dados/{slug}.json" download>Baixar JSON</a>
      </div>
    </div>
    <div class="aviso-obs">Atenção: estas listas mostram o que já aconteceu.
    Elas não adivinham o próximo sorteio. Em todo sorteio, cada dezena tem a
    mesma chance de sair — não importa se ela saiu muito ou pouco antes.</div>
  </section>

  <div class="anuncio" aria-hidden="true"><!-- espaço reservado: anúncio rodapé --></div>
</main>

<footer class="rodape">
  <div class="miolo">
    <div class="selo-honesto"><strong>O selo honesto do SorteLabs.</strong>
    Nenhuma conta aumenta a sua chance de ganhar na loteria. Quem promete isso
    está te enganando. O que a gente faz é organizar a brincadeira: montar os
    jogos, dividir o bolão sem briga e conferir tudo rápido. Jogue por diversão
    e só o quanto puder gastar. Proibido para menores de 18 anos.</div>
    <p>SorteLabs — ferramentas gratuitas para loterias ·
    <a href="/">todas as loterias</a> · dados oficiais da Caixa,
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
        # A home entra como "/" e não "/index.html": mandar o arquivo fazia o
        # Google tratá-lo como página alternativa da raiz, e ele avisava
        # "página alternativa com tag canônica adequada".
        for u in ["", "desafio.html"] + urls:
            f.write(f"  <url><loc>https://sortelabs.com.br/{u}"
                    f"</loc></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n"
                "Sitemap: https://sortelabs.com.br/sitemap.xml\n")
    print("OK sitemap.xml e robots.txt")


if __name__ == "__main__":
    gerar()
