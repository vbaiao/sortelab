/* SorteLab — motor estatístico (porte fiel do gerador_loterias.py)
 * Score por dezena: 50% frequência histórica + 35% recente + 15% atraso.
 * Nenhuma estatística aumenta a chance real de ganhar. Diversão apenas. */
"use strict";

(function () {
  const JANELA_RECENTE = 200;
  const MAX_TENTATIVAS = 2000;
  const MAX_COMBOS_CAMPEAO = 400000;
  const PESO_HISTORICO = 0.50, PESO_RECENTE = 0.35, PESO_ATRASO = 0.15;

  const LOTERIAS = {
    megasena: {
      slug: "megasena", nome: "Mega-Sena", lo: 1, hi: 60, sorteadas: 6,
      apostaMin: 6, apostaMax: 20, preco: 6.00, precoFixo: false,
      premios: { 4: "Quadra 🎉", 5: "Quina 🎉🎉", 6: "SENA!!! 💰💰💰" },
      obs: ""
    },
    lotofacil: {
      slug: "lotofacil", nome: "Lotofácil", lo: 1, hi: 25, sorteadas: 15,
      apostaMin: 15, apostaMax: 20, preco: 3.50, precoFixo: false,
      premios: { 11: "11 pontos 🎉", 12: "12 pontos 🎉", 13: "13 pontos 🎉🎉",
                 14: "14 pontos 💰", 15: "15 PONTOS!!! 💰💰💰" },
      obs: ""
    },
    quina: {
      slug: "quina", nome: "Quina", lo: 1, hi: 80, sorteadas: 5,
      apostaMin: 5, apostaMax: 15, preco: 3.00, precoFixo: false,
      premios: { 2: "Duque 🎉", 3: "Terno 🎉🎉", 4: "Quadra 💰",
                 5: "QUINA!!! 💰💰💰" },
      obs: ""
    },
    lotomania: {
      slug: "lotomania", nome: "Lotomania", lo: 0, hi: 99, sorteadas: 20,
      apostaMin: 50, apostaMax: 50, preco: 3.50, precoFixo: true,
      premios: { 0: "0 acertos — TAMBÉM PAGA! 💰", 15: "15 pontos 🎉",
                 16: "16 pontos 🎉", 17: "17 pontos 🎉🎉", 18: "18 pontos 💰",
                 19: "19 pontos 💰💰", 20: "20 PONTOS!!! 💰💰💰" },
      obs: ""
    },
    duplasena: {
      slug: "duplasena", nome: "Dupla Sena", lo: 1, hi: 50, sorteadas: 6,
      apostaMin: 6, apostaMax: 15, preco: 3.00, precoFixo: false,
      premios: { 3: "Terno 🎉", 4: "Quadra 🎉🎉", 5: "Quina 💰",
                 6: "SENA!!! 💰💰💰" },
      obs: "O histórico usa o 1º sorteio de cada concurso. Para conferir o " +
           "2º sorteio, confira de novo digitando as dezenas dele."
    },
    diadesorte: {
      slug: "diadesorte", nome: "Dia de Sorte", lo: 1, hi: 31, sorteadas: 7,
      apostaMin: 7, apostaMax: 15, preco: 3.00, precoFixo: false,
      premios: { 4: "4 acertos 🎉", 5: "5 acertos 🎉🎉", 6: "6 acertos 💰",
                 7: "7 ACERTOS!!! 💰💰💰" },
      obs: "O “Mês da Sorte” é marcado à parte no volante (não entra no " +
           "histórico de dezenas)."
    },
    timemania: {
      slug: "timemania", nome: "Timemania", lo: 1, hi: 80, sorteadas: 7,
      apostaMin: 10, apostaMax: 10, preco: 3.50, precoFixo: true,
      premios: { 3: "3 acertos 🎉", 4: "4 acertos 🎉", 5: "5 acertos 🎉🎉",
                 6: "6 acertos 💰", 7: "7 ACERTOS!!! 💰💰💰" },
      obs: "O “Time do Coração” é marcado à parte no volante."
    },
    maismilionaria: {
      slug: "maismilionaria", nome: "+Milionária", lo: 1, hi: 50, sorteadas: 6,
      apostaMin: 6, apostaMax: 12, preco: 6.00, precoFixo: false,
      premios: { 4: "4 acertos 🎉", 5: "5 acertos 💰", 6: "6 ACERTOS!!! 💰💰💰" },
      obs: "Os 2 trevos (1 a 6) são marcados à parte; o prêmio máximo exige " +
           "acertá-los também."
    }
  };

  // ---------------------------------------------------------- utilidades

  function comb(n, k) {                     // BigInt: aguenta C(100,20)
    if (k < 0 || k > n) return 0n;
    k = Math.min(k, n - k);
    let r = 1n;
    for (let i = 0; i < k; i++) {
      r = r * BigInt(n - i) / BigInt(i + 1);
    }
    return r;
  }

  function dinheiro(v) {
    return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  function inteiroBr(n) {
    return Number(n).toLocaleString("pt-BR");
  }

  function dez(n) { return String(n).padStart(2, "0"); }

  // ---------------------------------------------------------- estatística

  function calcularEstatisticas(cfg, concursos) {
    const total = concursos.length;
    const universo = [];
    for (let n = cfg.lo; n <= cfg.hi; n++) universo.push(n);

    const freq = {}, freqRec = {}, ultimoIndice = {};
    universo.forEach(n => { freq[n] = 0; freqRec[n] = 0; });
    concursos.forEach(([, , nums], i) => {
      nums.forEach(n => { freq[n]++; ultimoIndice[n] = i; });
    });
    concursos.slice(-JANELA_RECENTE).forEach(([, , nums]) => {
      nums.forEach(n => { freqRec[n]++; });
    });

    const atraso = {};
    universo.forEach(n => {
      atraso[n] = ultimoIndice[n] === undefined ? total : total - 1 - ultimoIndice[n];
    });

    const fs = universo.map(n => freq[n]);
    const rs = universo.map(n => freqRec[n]);
    const maxF = Math.max(...fs), minF = Math.min(...fs);
    const maxR = Math.max(...rs), minR = Math.min(...rs);
    const maxA = Math.max(...universo.map(n => atraso[n]));

    const score = {};
    universo.forEach(n => {
      const fN = maxF > minF ? (freq[n] - minF) / (maxF - minF) : 0.5;
      const rN = maxR > minR ? (freqRec[n] - minR) / (maxR - minR) : 0.5;
      const aN = maxA ? atraso[n] / maxA : 0;
      score[n] = PESO_HISTORICO * fN + PESO_RECENTE * rN + PESO_ATRASO * aN;
    });

    return { total, freq, freqRec, atraso, score, universo, concursos };
  }

  // ---------------------------------------------------------- perfil

  function parametrosFaixa(cfg) {
    const quantidade = cfg.hi - cfg.lo + 1;
    const tamanho = Math.ceil(quantidade / 6);
    const numFaixas = Math.ceil(quantidade / tamanho);
    return { tamanho, numFaixas };
  }

  function faixaDe(cfg, n) {
    return Math.floor((n - cfg.lo) / parametrosFaixa(cfg).tamanho);
  }

  /* Faixa de soma típica e faixa de pares aceita para um jogo de k dezenas —
     as mesmas usadas pelo filtro de perfil, expostas para a interface poder
     explicar os números ao usuário. */
  function perfilEsperado(cfg, k) {
    const quantidade = cfg.hi - cfg.lo + 1;
    const media = k * (cfg.lo + cfg.hi) / 2;
    const variancia = (quantidade * quantidade - 1) / 12;
    const desvio = Math.sqrt(k * variancia * (quantidade - k) / (quantidade - 1));
    const meio = Math.floor(k / 2);
    return {
      somaMedia: Math.round(media),
      somaMin: Math.ceil(media - 1.2 * desvio),
      somaMax: Math.floor(media + 1.2 * desvio),
      paresMin: Math.max(0, meio - 1),
      paresMax: Math.min(k, meio + 2)
    };
  }

  function jogoValido(cfg, jogo) {
    const k = jogo.length;
    const p = perfilEsperado(cfg, k);

    const soma = jogo.reduce((a, b) => a + b, 0);
    if (soma < p.somaMin || soma > p.somaMax) return false;

    const pares = jogo.filter(n => n % 2 === 0).length;
    if (pares < p.paresMin || pares > p.paresMax) return false;

    const { numFaixas } = parametrosFaixa(cfg);
    const porFaixa = {};
    jogo.forEach(n => {
      const f = faixaDe(cfg, n);
      porFaixa[f] = (porFaixa[f] || 0) + 1;
    });
    const distintas = Object.keys(porFaixa).length;
    if (distintas < Math.min(numFaixas, k) - 1) return false;
    if (Math.max(...Object.values(porFaixa)) > Math.ceil(k / numFaixas) + 1) {
      return false;
    }
    return true;
  }

  // ---------------------------------------------------------- geração

  function sortearJogo(cfg, score, k) {
    const nums = [];
    for (let n = cfg.lo; n <= cfg.hi; n++) nums.push(n);
    const pesos = nums.map(n => Math.pow(score[n] + 0.05, 2));
    const jogo = [];
    for (let j = 0; j < k; j++) {
      const soma = pesos.reduce((a, b) => a + b, 0);
      let alvo = Math.random() * soma;
      let i = 0;
      while (i < nums.length - 1 && (alvo -= pesos[i]) > 0) i++;
      jogo.push(nums[i]);
      nums.splice(i, 1);
      pesos.splice(i, 1);
    }
    return jogo.sort((a, b) => a - b);
  }

  function gerarJogos(cfg, stats, quantidade, k) {
    const jogos = [];
    for (let q = 0; q < quantidade; q++) {
      let melhor = null;
      for (let t = 0; t < MAX_TENTATIVAS; t++) {
        const jogo = sortearJogo(cfg, stats.score, k);
        const repetido = jogos.some(j => {
          const s = new Set(j);
          return jogo.filter(n => s.has(n)).length > k - 2;
        });
        if (repetido) continue;
        if (jogoValido(cfg, jogo)) { melhor = jogo; break; }
        if (melhor === null) melhor = jogo;
      }
      jogos.push(melhor);
    }
    return jogos;
  }

  function jogoCampeao(cfg, stats) {
    const score = stats.score;
    const k = cfg.apostaMin;
    const { numFaixas } = parametrosFaixa(cfg);
    const ranking = stats.universo.slice()
      .sort((a, b) => score[b] - score[a] || a - b);

    let tamanhoPool = k;
    while (tamanhoPool < ranking.length &&
           comb(tamanhoPool + 1, k) <= BigInt(MAX_COMBOS_CAMPEAO)) {
      tamanhoPool++;
    }
    const pool = new Set(ranking.slice(0, tamanhoPool));
    for (let f = 0; f < numFaixas; f++) {
      const daFaixa = ranking.find(n => faixaDe(cfg, n) === f);
      if (daFaixa !== undefined) pool.add(daFaixa);
    }
    const lista = [...pool].sort((a, b) => score[b] - score[a] || a - b);

    const alvoFaixas = Math.min(numFaixas, k);
    let melhor = null, melhorPontos = -1;

    // enumeração iterativa de combinações C(lista.length, k)
    const idx = [];
    for (let i = 0; i < k; i++) idx.push(i);
    const m = lista.length;
    if (m >= k) {
      while (true) {
        const combo = idx.map(i => lista[i]);
        const faixas = new Set(combo.map(n => faixaDe(cfg, n)));
        if (faixas.size >= alvoFaixas) {
          const jogo = combo.slice().sort((a, b) => a - b);
          if (jogoValido(cfg, jogo)) {
            const pontos = jogo.reduce((s, n) => s + score[n], 0);
            if (pontos > melhorPontos) { melhor = jogo; melhorPontos = pontos; }
          }
        }
        let i = k - 1;
        while (i >= 0 && idx[i] === m - k + i) i--;
        if (i < 0) break;
        idx[i]++;
        for (let j = i + 1; j < k; j++) idx[j] = idx[j - 1] + 1;
      }
    }
    return melhor || ranking.slice(0, k).sort((a, b) => a - b);
  }

  // ---------------------------------------------------------- preço/chance

  function custoAposta(cfg, k) {
    if (cfg.precoFixo) return cfg.preco;
    return Number(comb(k, cfg.apostaMin)) * cfg.preco;
  }

  function combinacoesCobertas(cfg, k) {
    return comb(k, cfg.sorteadas);
  }

  function totalCombinacoes(cfg) {
    return comb(cfg.hi - cfg.lo + 1, cfg.sorteadas);
  }

  function chanceUmEm(cfg, k, jogos) {
    const cobertas = combinacoesCobertas(cfg, k) * BigInt(jogos);
    if (cobertas <= 0n) return null;
    return Number(totalCombinacoes(cfg) / cobertas);
  }

  // ---------------------------------------------------------- parser/conferidor

  function lerLinhaJogo(cfg, linha, exato) {
    if (linha.includes(":")) linha = linha.slice(linha.lastIndexOf(":") + 1);
    const tokens = linha.replace(/[-,;]/g, " ").trim().split(/\s+/)
      .filter(t => t.length);
    if (!tokens.length) return null;
    const dezenas = new Set();
    for (const t of tokens) {
      if (!/^\d+$/.test(t)) return null;
      const n = parseInt(t, 10);
      if (n < cfg.lo || n > cfg.hi) return null;
      dezenas.add(n);
    }
    const minimo = exato || cfg.apostaMin;
    const maximo = exato || cfg.apostaMax;
    if (dezenas.size < minimo || dezenas.size > maximo) return null;
    return [...dezenas].sort((a, b) => a - b);
  }

  /* Selo do prêmio para exibir AO LADO do número de acertos: tira do rótulo
     o "N acertos/pontos" que repetiria o número já mostrado, mas preserva
     nomes de faixa ("Quadra", "Quina") e avisos ("TAMBÉM PAGA!"). */
  function seloPremio(cfg, acertos) {
    const bruto = cfg.premios[acertos];
    if (!bruto) return "";
    const limpo = bruto.replace(/^\d+\s*(acertos?|pontos?)!*\s*(—\s*)?/i, "").trim();
    return limpo || bruto;
  }

  function conferirJogos(cfg, resultado, jogos) {
    const alvo = new Set(resultado);
    return jogos.map(jogo => {
      const acertos = jogo.filter(n => alvo.has(n));
      return {
        jogo, acertos,
        premio: cfg.premios[acertos.length] || ""
      };
    });
  }

  // ---------------------------------------------------------- exporta

  const raiz = (typeof window !== "undefined") ? window : globalThis;
  raiz.SorteLab = {
    LOTERIAS, JANELA_RECENTE,
    comb, dinheiro, inteiroBr, dez,
    calcularEstatisticas, jogoValido, perfilEsperado, gerarJogos, jogoCampeao,
    custoAposta, combinacoesCobertas, totalCombinacoes, chanceUmEm,
    lerLinhaJogo, conferirJogos, seloPremio, faixaDe
  };
})();
