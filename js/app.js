/* SorteLab — lógica das páginas de loteria (usa js/motor.js). */
"use strict";

(function () {
  const SL = window.SorteLab;
  const slug = window.PAGINA && window.PAGINA.slug;
  if (!slug) return;
  const cfg = SL.LOTERIAS[slug];
  let stats = null;

  const $ = (sel) => document.querySelector(sel);

  // ---------------------------------------------------------- helpers de UI

  function bolas(nums, marcados, mini, animar) {
    const marca = marcados || new Set();
    const div = document.createElement("div");
    div.className = "bolas" + (animar ? " anima" : "");
    nums.forEach(n => {
      const b = document.createElement("span");
      b.className = "bola" + (marca.has(n) ? " acerto" : "") + (mini ? " mini" : "");
      b.textContent = SL.dez(n);
      div.appendChild(b);
    });
    return div;
  }

  function linhaJogo(rotuloTexto, jogo, extras, animar) {
    const linha = document.createElement("div");
    linha.className = "jogo-gerado";
    const rotulo = document.createElement("span");
    rotulo.className = "num";
    rotulo.textContent = rotuloTexto;
    linha.appendChild(rotulo);
    linha.appendChild(bolas(jogo, null, jogo.length > 10, animar));
    if (extras) {
      const info = document.createElement("span");
      info.className = "info";
      info.textContent = extras;
      linha.appendChild(info);
    }
    return linha;
  }

  function limpar(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  function textoJogos(jogos) {
    return jogos.map((j, i) =>
      "Jogo " + (i + 1) + ": " + j.map(SL.dez).join("-")).join("\n");
  }

  function mostrarErro(el, msg) {
    el.textContent = msg;
    el.hidden = !msg;
  }

  // ---------------------------------------------------------- abas

  document.querySelectorAll(".aba").forEach(botao => {
    botao.addEventListener("click", () => {
      document.querySelectorAll(".aba").forEach(b =>
        b.setAttribute("aria-selected", b === botao ? "true" : "false"));
      document.querySelectorAll(".ferramenta").forEach(sec =>
        sec.hidden = sec.id !== botao.dataset.alvo);
    });
  });

  // ---------------------------------------------------------- carga de dados

  fetch("dados/" + slug + ".json")
    .then(r => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(base => {
      stats = SL.calcularEstatisticas(cfg, base.concursos);
      prepararPagina();
    })
    .catch(() => {
      const alvo = $("#ultimo-resultado");
      if (alvo) alvo.textContent =
        "Não consegui carregar o histórico agora. Recarregue a página.";
    });

  function ultimoConcurso() {
    return stats.concursos[stats.concursos.length - 1];
  }

  function prepararPagina() {
    const [num, data, dezenas] = ultimoConcurso();
    const alvo = $("#ultimo-resultado");
    limpar(alvo);
    const rotulo = document.createElement("span");
    rotulo.className = "rotulo";
    rotulo.textContent = "Último resultado — concurso " + num + " (" + data + ")";
    alvo.appendChild(rotulo);
    alvo.appendChild(bolas(dezenas, null, dezenas.length > 10));

    const marcaAtualizado = $("#atualizado-em");
    if (marcaAtualizado) {
      marcaAtualizado.textContent = stats.total.toLocaleString("pt-BR") +
        " concursos analisados, do primeiro sorteio até " + data + ".";
    }
    prepararEstatisticas();
  }

  // ---------------------------------------------------------- gerador

  const formGerador = $("#form-gerador");
  if (formGerador) {
    formGerador.addEventListener("submit", (ev) => {
      ev.preventDefault();
      gerar(false);
    });
    $("#btn-campeao").addEventListener("click", () => gerar(true));
  }

  function gerar(campeao) {
    if (!stats) return;
    const saida = $("#ger-saida");
    const resumo = $("#ger-resumo");
    limpar(saida);
    let jogos;
    if (campeao) {
      jogos = [SL.jogoCampeao(cfg, stats)];
    } else {
      const qtd = Math.min(100, Math.max(1, parseInt($("#ger-qtd").value, 10) || 1));
      jogos = SL.gerarJogos(cfg, stats, qtd, cfg.apostaMin);
    }

    const perfil = SL.perfilEsperado(cfg, cfg.apostaMin);
    jogos.forEach((j, i) => {
      const soma = j.reduce((a, b) => a + b, 0);
      const pares = j.filter(n => n % 2 === 0).length;
      saida.appendChild(linhaJogo("Jogo " + (i + 1), j,
        "soma " + soma + " · " + pares + " pares · perfil típico", true));
    });

    const legenda = document.createElement("p");
    legenda.className = "dica";
    legenda.style.margin = "12px 0 0";
    legenda.innerHTML = "<strong>O que são esses números:</strong> a " +
      "<em>soma</em> é o total das dezenas do jogo e os <em>pares</em> são " +
      "quantas delas são números pares. Servem para você conferir que o jogo " +
      "tem a cara de um sorteio real: na " + cfg.nome + ", a soma costuma cair " +
      "entre <strong>" + perfil.somaMin + " e " + perfil.somaMax + "</strong> " +
      "(média " + perfil.somaMedia + ") e os pares entre <strong>" +
      perfil.paresMin + " e " + perfil.paresMax + "</strong>. Todo jogo gerado " +
      "aqui já passou por esse filtro. " +
      "<em>Nem soma nem pares mudam sua chance de ganhar</em>: eles só evitam " +
      "combinações de cara estranha, como dezenas em sequência, que muita " +
      "gente joga e dividiriam o prêmio com mais pessoas.";
    saida.appendChild(legenda);

    const custo = jogos.length * cfg.preco;
    resumo.innerHTML = (campeao
      ? "<strong>Este é o jogo campeão:</strong> entre todas as combinações " +
        "possíveis, é a de maior pontuação no nosso score — e continuará sendo " +
        "exatamente esta até sair o próximo concurso. "
      : "") +
      "Custo na lotérica: <strong>" + SL.dinheiro(custo) + "</strong>" +
      (jogos.length > 1 ? " (" + jogos.length + " × " + SL.dinheiro(cfg.preco) + ")" : "") + ".";
    resumo.hidden = false;
    $("#btn-copiar-jogos").hidden = false;
    $("#btn-copiar-jogos").onclick = () => copiar(textoJogos(jogos), $("#btn-copiar-jogos"));
  }

  function copiar(texto, botao) {
    navigator.clipboard.writeText(texto).then(() => {
      const original = botao.textContent;
      botao.textContent = "Copiado";
      setTimeout(() => { botao.textContent = original; }, 1600);
    });
  }

  // ---------------------------------------------------------- bolão

  const formBolao = $("#form-bolao");
  if (formBolao) {
    formBolao.addEventListener("submit", (ev) => {
      ev.preventDefault();
      montarBolao();
    });
  }

  function montarBolao() {
    if (!stats) return;
    const jogosQtd = Math.min(50, Math.max(1, parseInt($("#bol-jogos").value, 10) || 1));
    const k = cfg.apostaMin === cfg.apostaMax
      ? cfg.apostaMin
      : parseInt($("#bol-dezenas").value, 10);
    const pessoas = Math.min(100, Math.max(1, parseInt($("#bol-pessoas").value, 10) || 1));
    const valorBruto = ($("#bol-valor").value || "").replace(/\./g, "").replace(",", ".");
    const custoOficial = jogosQtd * SL.custoAposta(cfg, k);
    const valor = parseFloat(valorBruto) > 0 ? parseFloat(valorBruto) : custoOficial;

    const jogos = SL.gerarJogos(cfg, stats, jogosQtd, k);
    const saida = $("#bol-saida");
    limpar(saida);
    jogos.forEach((j, i) => saida.appendChild(linhaJogo("Jogo " + (i + 1), j, "", true)));

    const cota = valor / pessoas;
    const chance = SL.chanceUmEm(cfg, k, jogosQtd);
    $("#bol-rateio").innerHTML =
      "Custo oficial estimado: <strong>" + SL.dinheiro(custoOficial) + "</strong> · " +
      "Valor do bolão: <strong>" + SL.dinheiro(valor) + "</strong> · " +
      pessoas + " pessoa(s) · Cota: <strong>" + SL.dinheiro(cota) + "</strong>" +
      (chance ? " · Chance do prêmio máximo: 1 em " + SL.inteiroBr(chance) : "");
    $("#bol-rateio").hidden = false;

    const msg = "*Bolão " + cfg.nome + " — SorteLabs*\n" +
      jogosQtd + " jogo(s) de " + k + " dezenas\n\n" +
      textoJogos(jogos) + "\n\n" +
      "Total: " + SL.dinheiro(valor) + "  |  " + pessoas + " pessoa(s)\n" +
      "Cota por pessoa: " + SL.dinheiro(cota) + "\n" +
      "Quem tá dentro?\n" +
      "Confira depois em https://sortelabs.com.br/" + slug + ".html";
    const caixaMsg = $("#bol-msg");
    caixaMsg.textContent = msg;
    caixaMsg.hidden = false;
    const btnCopiar = $("#btn-copiar-whats");
    btnCopiar.hidden = false;
    btnCopiar.onclick = () => copiar(msg, btnCopiar);
    const btnAbrir = $("#btn-abrir-whats");
    btnAbrir.hidden = false;
    btnAbrir.href = "https://wa.me/?text=" + encodeURIComponent(msg);
  }

  // ---------------------------------------------------------- orçamento

  const formOrcamento = $("#form-orcamento");
  if (formOrcamento) {
    formOrcamento.addEventListener("submit", (ev) => {
      ev.preventDefault();
      planejar();
    });
  }

  function planejar() {
    if (!stats) return;
    const valorBruto = ($("#orc-valor").value || "").replace(/\./g, "").replace(",", ".");
    const valor = parseFloat(valorBruto) || 0;
    const pessoas = Math.min(100, Math.max(1, parseInt($("#orc-pessoas").value, 10) || 1));
    const erro = $("#orc-erro");
    const area = $("#orc-tabela");
    limpar(area);
    $("#orc-saida").hidden = true;

    const opcoes = [];
    for (let k = cfg.apostaMin; k <= cfg.apostaMax; k++) {
      const custoJogo = SL.custoAposta(cfg, k);
      if (custoJogo > valor) break;
      const maxJogos = Math.floor(valor / custoJogo);
      opcoes.push({
        k, custoJogo, maxJogos,
        gasto: maxJogos * custoJogo,
        chance: SL.chanceUmEm(cfg, k, maxJogos)
      });
    }
    if (!opcoes.length) {
      mostrarErro(erro, "Com " + SL.dinheiro(valor) + " não dá para a aposta mínima da " +
        cfg.nome + " (" + SL.dinheiro(SL.custoAposta(cfg, cfg.apostaMin)) + "). Junte mais gente.");
      return;
    }
    mostrarErro(erro, "");

    const tabela = document.createElement("table");
    tabela.className = "tabela";
    tabela.innerHTML = "<thead><tr><th>Dezenas</th><th>Custo/jogo</th>" +
      "<th>Jogos</th><th>Gasto</th><th>Sobra</th><th>Chance máx.</th>" +
      "<th>Cota</th><th></th></tr></thead>";
    const corpo = document.createElement("tbody");
    opcoes.forEach(op => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + op.k + "</td>" +
        "<td>" + SL.dinheiro(op.custoJogo) + "</td>" +
        "<td>" + op.maxJogos + "</td>" +
        "<td>" + SL.dinheiro(op.gasto) + "</td>" +
        "<td>" + SL.dinheiro(valor - op.gasto) + "</td>" +
        "<td>1 em " + SL.inteiroBr(op.chance) + "</td>" +
        "<td>" + SL.dinheiro(op.gasto / pessoas) + "</td>";
      const td = document.createElement("td");
      const botao = document.createElement("button");
      botao.className = "botao mini";
      botao.type = "button";
      botao.textContent = "Gerar";
      botao.addEventListener("click", () => {
        corpo.querySelectorAll("tr").forEach(l => l.classList.remove("escolhida"));
        tr.classList.add("escolhida");
        gerarDoOrcamento(op, pessoas, valor);
      });
      td.appendChild(botao);
      tr.appendChild(td);
      corpo.appendChild(tr);
    });
    tabela.appendChild(corpo);
    const rolagem = document.createElement("div");
    rolagem.className = "rolagem-x";
    rolagem.appendChild(tabela);
    area.appendChild(rolagem);

    if (opcoes.length > 1) {
      const nota = document.createElement("p");
      nota.className = "dica";
      nota.style.marginTop = "10px";
      nota.textContent = "Leitura honesta: com o mesmo orçamento, a chance " +
        "depende só do total apostado — as opções quase empatam, muda a sobra. " +
        "Jogos com mais dezenas concentram prêmios; mais jogos espalham dezenas.";
      area.appendChild(nota);
    }
  }

  function gerarDoOrcamento(op, pessoas, valor) {
    const quantidade = Math.min(op.maxJogos, 100);
    const jogos = SL.gerarJogos(cfg, stats, quantidade, op.k);
    const saida = $("#orc-saida");
    limpar(saida);
    const titulo = document.createElement("h2");
    titulo.textContent = quantidade + " jogo(s) de " + op.k + " dezenas";
    saida.appendChild(titulo);
    if (quantidade < op.maxJogos) {
      const nota = document.createElement("p");
      nota.className = "dica";
      nota.textContent = op.maxJogos + " jogos é muita coisa — gerei os primeiros 100.";
      saida.appendChild(nota);
    }
    jogos.forEach((j, i) => saida.appendChild(linhaJogo("Jogo " + (i + 1), j, "", true)));
    const resumo = document.createElement("div");
    resumo.className = "caixa-resumo";
    resumo.innerHTML = "Gasto: <strong>" + SL.dinheiro(op.gasto) + "</strong> " +
      "(sobra " + SL.dinheiro(valor - op.gasto) + ") · Cota por pessoa (" +
      pessoas + "): <strong>" + SL.dinheiro(op.gasto / pessoas) + "</strong>";
    saida.appendChild(resumo);
    const botao = document.createElement("button");
    botao.className = "botao secundario mini";
    botao.style.marginTop = "12px";
    botao.type = "button";
    botao.textContent = "Copiar jogos";
    botao.addEventListener("click", () => copiar(textoJogos(jogos), botao));
    saida.appendChild(botao);
    saida.hidden = false;
    saida.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ---------------------------------------------------------- conferidor

  const formConferidor = $("#form-conferidor");
  if (formConferidor) {
    $("#btn-ultimo").addEventListener("click", () => {
      const [, , dezenas] = ultimoConcurso();
      $("#conf-resultado").value = dezenas.map(SL.dez).join(" ");
    });
    formConferidor.addEventListener("submit", (ev) => {
      ev.preventDefault();
      conferir();
    });
  }

  function conferir() {
    if (!stats) return;
    const erro = $("#conf-erro");
    const resultado = SL.lerLinhaJogo(cfg, $("#conf-resultado").value, cfg.sorteadas);
    if (!resultado) {
      mostrarErro(erro, "O resultado precisa ter exatamente " + cfg.sorteadas +
        " dezenas entre " + SL.dez(cfg.lo) + " e " + cfg.hi +
        ". Use o botão “Usar último resultado” ou confira a digitação.");
      return;
    }
    const linhas = $("#conf-jogos").value.split("\n").map(l => l.trim()).filter(l => l);
    const jogos = [], ignoradas = [];
    linhas.forEach(l => {
      const jogo = SL.lerLinhaJogo(cfg, l);
      if (jogo) jogos.push(jogo); else ignoradas.push(l);
    });
    if (!jogos.length) {
      mostrarErro(erro, "Cole pelo menos um jogo (de " + cfg.apostaMin + " a " +
        cfg.apostaMax + " dezenas por linha).");
      return;
    }
    mostrarErro(erro, "");

    const saida = $("#conf-saida");
    limpar(saida);
    const alvo = new Set(resultado);
    const cabecalho = document.createElement("div");
    cabecalho.className = "jogo-gerado";
    const rotulo = document.createElement("span");
    rotulo.className = "num";
    rotulo.textContent = "Sorteio";
    cabecalho.appendChild(rotulo);
    cabecalho.appendChild(bolas(resultado, alvo, resultado.length > 10, true));
    saida.appendChild(cabecalho);

    const conferidos = SL.conferirJogos(cfg, resultado, jogos);
    let premiados = 0;
    conferidos.forEach((c, i) => {
      const linha = linhaJogo("Jogo " + (i + 1), [],
        c.acertos.length + " acerto(s)");
      linha.querySelector(".bolas").replaceWith(bolas(c.jogo, alvo, c.jogo.length > 10, true));
      if (c.premio) {
        premiados++;
        const selo = document.createElement("span");
        selo.className = "premio";
        selo.textContent = SL.seloPremio(cfg, c.acertos.length);
        linha.appendChild(selo);
      }
      saida.appendChild(linha);
    });

    const resumo = document.createElement("div");
    resumo.className = "caixa-resumo";
    resumo.innerHTML = "<strong>" + jogos.length + " jogo(s) conferido(s).</strong> " +
      (premiados ? premiados + " jogo(s) premiado(s)."
                 : "Nenhum premiado desta vez.") +
      (ignoradas.length ? "<br>" + ignoradas.length +
        " linha(s) ignorada(s) por não parecerem um jogo." : "");
    saida.appendChild(resumo);
    saida.hidden = false;
  }

  // ---------------------------------------------------------- estatísticas

  function prepararEstatisticas() {
    const area = $("#est-conteudo");
    if (!area) return;
    limpar(area);

    const blocos = [
      ["Mais sorteadas (histórico completo)",
        stats.universo.slice().sort((a, b) => stats.freq[b] - stats.freq[a]).slice(0, 10)
          .map(n => [n, stats.freq[n] + "×"])],
      ["Mais quentes (últimos " + SL.JANELA_RECENTE + " concursos)",
        stats.universo.slice().sort((a, b) => stats.freqRec[b] - stats.freqRec[a]).slice(0, 10)
          .map(n => [n, stats.freqRec[n] + "×"])],
      ["Mais atrasadas",
        stats.universo.slice().sort((a, b) => stats.atraso[b] - stats.atraso[a]).slice(0, 10)
          .map(n => [n, stats.atraso[n] + " concursos sem sair"])]
    ];

    blocos.forEach(([titulo, itens]) => {
      const cartao = document.createElement("div");
      cartao.className = "cartao";
      const h = document.createElement("h2");
      h.textContent = titulo;
      cartao.appendChild(h);
      const lista = document.createElement("ul");
      lista.className = "lista-rank";
      itens.forEach(([n, valor]) => {
        const li = document.createElement("li");
        li.appendChild(bolas([n], null, true));
        const span = document.createElement("span");
        span.className = "valor";
        span.textContent = valor;
        li.appendChild(span);
        lista.appendChild(li);
      });
      cartao.appendChild(lista);
      area.appendChild(cartao);
    });

    const ultimos = document.createElement("div");
    ultimos.className = "cartao";
    ultimos.innerHTML = "<h2>Últimos 5 resultados</h2>";
    stats.concursos.slice(-5).reverse().forEach(([num, data, dezenas]) => {
      ultimos.appendChild(linhaJogo("Conc. " + num + " · " + data, [], ""));
      ultimos.lastChild.querySelector(".num").style.minWidth = "130px";
      ultimos.lastChild.querySelector(".bolas").replaceWith(bolas(dezenas, null, dezenas.length > 10));
    });
    area.appendChild(ultimos);
  }
})();
