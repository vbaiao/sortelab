/* SorteLabs — painel do Desafio do Campeão.
 *
 * Os palpites são cravados pelo robô ANTES de cada sorteio e ficam salvos em
 * dados/desafio.json. Se o robô atrasar, esta página confere sozinha o palpite
 * pendente contra o resultado oficial da Caixa — o palpite já estava publicado,
 * então conferir aqui não muda nada, só mostra antes. */
"use strict";

(function () {
  const SL = window.SorteLab;
  const API_CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/";
  const CORES = {
    megasena: "#209869", lotofacil: "#930089", quina: "#260085",
    lotomania: "#E07000", duplasena: "#A61324", diadesorte: "#CB852B",
    timemania: "#0E8A3E", maismilionaria: "#2E3078"
  };
  const ORDEM = ["megasena", "lotofacil", "quina", "lotomania", "duplasena",
                 "diadesorte", "timemania", "maismilionaria"];

  function bolas(nums) {
    const div = document.createElement("div");
    div.className = "bolas";
    nums.forEach(n => {
      const b = document.createElement("span");
      b.className = "bola mini";
      b.textContent = SL.dez(n);
      div.appendChild(b);
    });
    return div;
  }

  function montarSecao(slug, d) {
    const cfg = SL.LOTERIAS[slug];
    const sec = document.createElement("section");
    sec.className = "secao-loteria";
    sec.dataset.slug = slug;
    sec.style.setProperty("--cor", CORES[slug]);

    const hist = d.historico || [];
    const media = hist.length
      ? hist.reduce((s, h) => s + h.acertos, 0) / hist.length : 0;
    const esperado = cfg.apostaMin * cfg.sorteadas / (cfg.hi - cfg.lo + 1);
    const melhor = hist.length ? Math.max(...hist.map(h => h.acertos)) : 0;
    const premiados = hist.filter(h => cfg.premios[h.acertos]).length;

    const cab = document.createElement("header");
    cab.innerHTML = "<span>" + cfg.nome + "</span>" +
      "<span class='medias'>média " + media.toFixed(2) +
      " · esperado pelo acaso " + esperado.toFixed(2) +
      " · melhor: " + melhor +
      (premiados ? " · prêmios: " + premiados : "") + "</span>";
    sec.appendChild(cab);

    const corpo = document.createElement("div");
    corpo.className = "corpo";

    if (d.pendente) {
      const crav = document.createElement("div");
      crav.className = "cravado";
      const rot = document.createElement("div");
      rot.className = "rotulo-cravado";
      rot.textContent = "Cravado para o próximo sorteio (depois do concurso " +
        d.pendente.apos + ")";
      crav.appendChild(rot);
      crav.appendChild(bolas(d.pendente.jogo));
      corpo.appendChild(crav);
    } else {
      const aviso = document.createElement("p");
      aviso.className = "dica";
      aviso.style.margin = "0 0 14px";
      aviso.textContent = "O próximo palpite é cravado assim que o robô roda.";
      corpo.appendChild(aviso);
    }

    const tabela = document.createElement("table");
    tabela.className = "hist";
    tabela.innerHTML = "<thead><tr><th>Sorteio</th><th>Data</th>" +
      "<th>Acertos</th><th>Números que acertou</th></tr></thead>";
    const tb = document.createElement("tbody");
    hist.slice(-15).reverse().forEach(h => {
      const alvo = new Set(h.resultado);
      const certas = h.jogo.filter(n => alvo.has(n));
      const selo = SL.seloPremio(cfg, h.acertos);
      /* Duas situações, e só duas: ou o palpite já estava publicado aqui
         antes do sorteio, ou foi recalculado depois com os dados da véspera.
         Quem fez a conferência (robô ou a página) não muda nada para quem lê. */
      const marca = h.retro
        ? "<span class='tag-refeito'>refeito depois</span>"
        : "<span class='tag-antes'>salvo antes</span>";
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + h.concurso + marca + "</td>" +
        "<td>" + h.data + "</td>" +
        "<td class='num-acertos'>" + h.acertos +
          (selo ? " <span class='premio'>" + selo + "</span>" : "") + "</td>" +
        "<td>" + (certas.length ? certas.map(SL.dez).join(" - ") : "—") + "</td>";
      tb.appendChild(tr);
    });
    tabela.appendChild(tb);
    const rolagem = document.createElement("div");
    rolagem.className = "rolagem-x";
    rolagem.appendChild(tabela);
    corpo.appendChild(rolagem);

    sec.appendChild(corpo);
    return sec;
  }

  function buscarConcurso(slug, numero) {
    const controle = new AbortController();
    const prazo = setTimeout(() => controle.abort(), 8000);
    return fetch(API_CAIXA + slug + "/" + numero, { signal: controle.signal })
      .then(r => {
        if (!r.ok) throw new Error("indisponível");
        return r.json();
      })
      .then(d => ({
        concurso: Number(d.numero),
        data: d.dataApuracao,
        resultado: d.listaDezenas.map(Number).sort((a, b) => a - b)
      }))
      .finally(() => clearTimeout(prazo));
  }

  /* Confere o palpite pendente contra um resultado já sorteado.
     Devolve a entrada de histórico pronta, ou null se ainda não dá. */
  function conferirPendente(pendente, sorteio) {
    if (!pendente || !sorteio || sorteio.concurso !== pendente.apos + 1) return null;
    if (!sorteio.resultado.length) return null;
    const alvo = new Set(sorteio.resultado);
    return {
      concurso: sorteio.concurso,
      data: sorteio.data,
      jogo: pendente.jogo,
      resultado: sorteio.resultado,
      acertos: pendente.jogo.filter(n => alvo.has(n)).length,
      aoVivo: true
    };
  }

  window.DesafioSorteLabs = { conferirPendente };   // exposto para teste

  const raiz = document.getElementById("conteudo");
  if (!raiz) return;

  fetch("dados/desafio.json").then(r => r.json()).then(desafio => {
    raiz.textContent = "";
    ORDEM.forEach(slug => {
      if (desafio[slug] && SL.LOTERIAS[slug]) {
        raiz.appendChild(montarSecao(slug, desafio[slug]));
      }
    });

    // Robô atrasado? A página confere o palpite pendente por conta própria.
    ORDEM.forEach(slug => {
      const d = desafio[slug];
      if (!d || !d.pendente || !SL.LOTERIAS[slug]) return;
      buscarConcurso(slug, d.pendente.apos + 1)
        .then(sorteio => {
          const entrada = conferirPendente(d.pendente, sorteio);
          if (!entrada) return;
          d.historico.push(entrada);
          d.pendente = null;
          const antiga = raiz.querySelector('[data-slug="' + slug + '"]');
          if (antiga) antiga.replaceWith(montarSecao(slug, d));
        })
        .catch(() => {});   // sorteio ainda não saiu: nada a fazer
    });
  }).catch(() => {
    raiz.innerHTML = "<p class='dica'>Não consegui carregar o desafio agora. " +
      "Recarregue a página.</p>";
  });
})();
