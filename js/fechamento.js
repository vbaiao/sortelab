/* SorteLab — fechamento da Lotofácil (porte fiel de robo/fechamento.py).
 * Fechamento NÃO aumenta a chance de ganhar. Ele garante uma faixa mínima
 * quando você acerta o bastante, e concentra o retorno em vez de espalhar. */
"use strict";

(function () {
  const DEZENAS_POR_JOGO = 15;
  const PRECO_JOGO = 3.50;
  const FAIXA_MINIMA = 11;        // menor faixa que paga na Lotofácil

  function triosConsecutivos(quantidade) {
    const fora = [];
    for (let i = 0; i < quantidade * 3; i += 3) fora.push([i, i + 1, i + 2]);
    return fora;
  }

  const PADROES = {
    // Cinco trios disjuntos cobrindo as posições 0..14. As posições 15, 16 e
    // 17 nunca são descartadas — entram em todos os jogos. Por isso este
    // padrão trava em 12 acertos mesmo quando as 15 saem dentro das suas 18.
    "18-5": {
      dezenas: 18,
      descartes: triosConsecutivos(5),
      garantias: [{ saem: 13, acertos: 11 },
                  { saem: 14, acertos: 12 },
                  { saem: 15, acertos: 12 }]
    },
    // Seis trios disjuntos cobrindo todas as 18 posições. Custa R$ 3,50 a
    // mais que o 18-5 e chega a 13 acertos quando as 15 saem dentro das
    // suas 18.
    "18-6": {
      dezenas: 18,
      descartes: triosConsecutivos(6),
      garantias: [{ saem: 13, acertos: 11 },
                  { saem: 14, acertos: 12 },
                  { saem: 15, acertos: 13 }]
    },
    // Sete descartes de dois, achados por busca gulosa (robo/gerar_padroes.py).
    // Não têm forma regular: a lista abaixo é uma constante congelada e
    // verificada, não uma regra que dê para deduzir de cabeça.
    "17-7": {
      dezenas: 17,
      descartes: [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [0, 12]],
      garantias: [{ saem: 12, acertos: 11 }]
    },
    // Doze descartes de três. Garante prêmio quando só 12 das suas 18 saem —
    // o que acontece uma vez a cada quatro sorteios.
    "18-12": {
      dezenas: 18,
      descartes: [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14],
                  [15, 16, 17], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 1, 5],
                  [0, 1, 8], [2, 3, 4]],
      garantias: [{ saem: 12, acertos: 11 }]
    }
  };

  function jogosDoPadrao(id) { return PADROES[id].descartes.length; }

  function custoDoPadrao(id) {
    return Math.round(jogosDoPadrao(id) * PRECO_JOGO * 100) / 100;
  }

  function montar(dezenas, id) {
    const padrao = PADROES[id];
    if (dezenas.length !== padrao.dezenas) {
      throw new Error("O padrão " + id + " precisa de exatamente " +
                      padrao.dezenas + " dezenas.");
    }
    if (new Set(dezenas).size !== dezenas.length) {
      throw new Error("Há dezenas repetidas na escolha.");
    }
    const base = dezenas.slice().sort((a, b) => a - b);
    return padrao.descartes.map(descarte => {
      const fora = new Set(descarte);
      return base.filter((_, i) => !fora.has(i));
    });
  }

  // Cada jogo é uma aposta independente e paga por si: três jogos de 11
  // acertos recebem três vezes o rateio de 11. O retorno soma por JOGO
  // premiado, não por faixa. Sem rateio, o retorno fica null — a página
  // mostra os acertos e omite o valor, em vez de inventar um.
  function avaliar(jogos, resultado, rateio) {
    const alvo = new Set(resultado);
    const acertos = jogos.map(j => j.filter(n => alvo.has(n)).length);
    const premios = {};
    acertos.forEach(a => {
      if (a >= FAIXA_MINIMA) premios[a] = (premios[a] || 0) + 1;
    });
    let retorno = null;
    if (rateio) {
      retorno = acertos.reduce((soma, a) =>
        a >= FAIXA_MINIMA ? soma + (Number(rateio[a]) || 0) : soma, 0);
      retorno = Math.round(retorno * 100) / 100;
    }
    return { acertos, premios, retorno };
  }

  // -------------------------------------------------- sorteio auditável

  function mulberry32(semente) {
    /* PRNG de 32 bits, idêntico bit a bit ao de robo/fechamento.py. Não
     * usamos Math.random de propósito: o lado aleatório do placar só tem
     * valor se qualquer pessoa puder reproduzi-lo — por isso o algoritmo é
     * explícito e está publicado na própria página. */
    let estado = semente >>> 0;
    return function () {
      estado = (estado + 0x6D2B79F5) >>> 0;
      let t = estado;
      t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
      t = (t ^ (t + Math.imul(t ^ (t >>> 7), t | 61))) >>> 0;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function dezenasAleatorias(semente, quantidade, lo, hi) {
    // Embaralha lo..hi com Fisher-Yates e devolve as primeiras, ordenadas.
    const sortear = mulberry32(semente);
    const baralho = [];
    for (let n = lo; n <= hi; n++) baralho.push(n);
    for (let i = baralho.length - 1; i > 0; i--) {
      const j = Math.floor(sortear() * (i + 1));
      const troca = baralho[i]; baralho[i] = baralho[j]; baralho[j] = troca;
    }
    return baralho.slice(0, quantidade).sort((a, b) => a - b);
  }

  // -------------------------------------------------- conta acumulada

  // Soma gasto/retorno de um histórico (campeão vs. aleatório) e conta, à
  // parte, quantos concursos ficaram sem rateio publicado — para a página
  // nunca mostrar um saldo distorcido em silêncio.
  function contaAcumulada(historico, id) {
    const custo = custoDoPadrao(id);
    const conta = { sorteios: historico.length, campeao: null, aleatorio: null };
    ["campeao", "aleatorio"].forEach(lado => {
      let retorno = 0, semRateio = 0;
      historico.forEach(linha => {
        if (linha[lado] && linha[lado].retorno === null) semRateio++;
        else if (linha[lado]) retorno += linha[lado].retorno;
      });
      const gasto = historico.length * custo;
      conta[lado] = {
        gasto: Math.round(gasto * 100) / 100,
        retorno: Math.round(retorno * 100) / 100,
        saldo: Math.round((retorno - gasto) * 100) / 100,
        semRateio
      };
    });
    return conta;
  }

  const raiz = (typeof window !== "undefined") ? window : globalThis;
  raiz.SorteLabFechamento = {
    PADROES, PRECO_JOGO, FAIXA_MINIMA, DEZENAS_POR_JOGO,
    jogosDoPadrao, custoDoPadrao, montar, avaliar,
    mulberry32, dezenasAleatorias, contaAcumulada
  };
})();
