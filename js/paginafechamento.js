/* SorteLab — página do fechamento da Lotofácil. */
"use strict";

(function () {
  const FZ = window.SorteLabFechamento;
  const PRESET_PLACAR = "18-5";

  const $ = id => document.getElementById(id);
  const dinheiro = v => "R$ " + v.toFixed(2).replace(".", ",");
  const dez = n => String(n).padStart(2, "0");

  let estado = { fechamento: null };

  function lerDezenas(texto) {
    const nums = (texto.match(/\d+/g) || []).map(Number);
    return Array.from(new Set(nums)).sort((a, b) => a - b);
  }

  function montarFechamento() {
    const id = $("padrao").value;
    const dezenas = lerDezenas($("dezenas").value);
    const saida = $("saida-montagem");
    try {
      // montar() valida a quantidade e repetições, mas não a faixa de cada
      // dezena — sem esta checagem, um "30" digitado por engano vira um
      // jogo malformado em silêncio em vez de dar erro.
      const foraDaFaixa = dezenas.some(n => n < 1 || n > 25);
      if (foraDaFaixa) {
        throw new Error("As dezenas têm que estar entre 01 e 25. Confira o " +
                        "que você digitou.");
      }
      const jogos = FZ.montar(dezenas, id);
      const p = FZ.PADROES[id];
      const garantias = p.garantias.map(g =>
        "<li>Se <strong>" + g.saem + "</strong> das suas " + p.dezenas +
        " saírem, você tem garantido um jogo com <strong>" + g.acertos +
        "</strong> acertos.</li>").join("");
      saida.innerHTML =
        "<p class='dica'><em>" + jogos.length + " jogos · " +
        dinheiro(FZ.custoDoPadrao(id)) + "</em></p><ul class='garantias'>" +
        garantias + "</ul><ol class='jogos'>" +
        jogos.map(j => "<li>" + j.map(dez).join(" ") + "</li>").join("") +
        "</ol>";
    } catch (e) {
      saida.innerHTML = "<p class='erro'>" + e.message + "</p>";
    }
  }

  function usarDoCampeao() {
    const pendente = estado.fechamento && estado.fechamento.pendente;
    if (!pendente) return;
    $("padrao").value = PRESET_PLACAR;
    $("dezenas").value = pendente.campeao.dezenas.map(dez).join(" ");
    montarFechamento();
  }

  function linhaPlacar(linha, lado) {
    const d = linha[lado];
    const melhor = Math.max.apply(null, d.acertos);
    const premiados = d.acertos.filter(a => a >= FZ.FAIXA_MINIMA).length;
    return "<td>" + melhor + "</td><td>" + premiados + "</td><td>" +
      (d.retorno === null ? "—" : dinheiro(d.retorno)) + "</td>";
  }

  function desenharPlacar() {
    const dados = estado.fechamento;
    if (!dados) return;
    const historico = dados.historico.slice().reverse();
    $("placar-corpo").innerHTML = historico.map(linha =>
      "<tr><td>" + linha.concurso + "</td><td>" + linha.data + "</td>" +
      linhaPlacar(linha, "campeao") + linhaPlacar(linha, "aleatorio") +
      "</tr>").join("") ||
      "<tr><td colspan='8'>Nenhum sorteio conferido ainda.</td></tr>";

    if (dados.pendente) {
      $("pendente").innerHTML =
        "<p>Cravado para o concurso <strong>" + (dados.pendente.apos + 1) +
        "</strong>, antes do sorteio:</p>" +
        "<p><strong>Campeão:</strong> " +
        dados.pendente.campeao.dezenas.map(dez).join(" ") + "</p>" +
        "<p><strong>Aleatório</strong> (semente " +
        dados.pendente.aleatorio.semente + "): " +
        dados.pendente.aleatorio.dezenas.map(dez).join(" ") + "</p>";
    }
  }

  function desenharConta() {
    const dados = estado.fechamento;
    if (!dados) return;
    const conta = FZ.contaAcumulada(dados.historico, dados.preset);
    const linha = (nome, c) =>
      "<tr><th>" + nome + "</th><td>" + dinheiro(c.gasto) + "</td><td>" +
      dinheiro(c.retorno) + "</td><td class='" +
      (c.saldo < 0 ? "negativo" : "positivo") + "'>" +
      dinheiro(c.saldo) + "</td></tr>";
    $("conta-corpo").innerHTML =
      linha("Campeão", conta.campeao) + linha("Aleatório", conta.aleatorio);
    $("conta-sorteios").textContent = conta.sorteios;

    // Concurso sem rateio entra no gasto mas não no retorno, o que puxa o
    // saldo para baixo. Melhor avisar do que mostrar um número torto calado.
    const semRateio = Math.max(conta.campeao.semRateio,
                               conta.aleatorio.semRateio);
    $("conta-ressalva").innerHTML = semRateio
      ? "Em <strong>" + semRateio + "</strong> " +
        (semRateio === 1 ? "sorteio" : "sorteios") + " a Caixa não publicou " +
        "os valores de prêmio. " + (semRateio === 1 ? "Ele conta" : "Eles contam") +
        " no gasto mas não no retorno, então o saldo real é um pouco melhor " +
        "do que o mostrado aqui."
      : (conta.sorteios === 0
        ? "Ainda não fechou nenhum sorteio. O placar acima já está de pé, " +
          "esperando o primeiro resultado para começar a somar."
        : "");
  }

  fetch("dados/fechamento.json")
    .then(r => r.json())
    .then(dados => {
      estado.fechamento = dados;
      desenharPlacar();
      desenharConta();
      usarDoCampeao();
    })
    .catch(() => {
      $("placar-corpo").innerHTML =
        "<tr><td colspan='8'>Não foi possível carregar o placar agora.</td></tr>";
    });

  $("btn-montar").addEventListener("click", montarFechamento);
  $("btn-usar-campeao").addEventListener("click", usarDoCampeao);
})();
