/* SorteLab — página do fechamento da Lotofácil. */
"use strict";

(function () {
  const FZ = window.SorteLabFechamento;
  const PRESET_PLACAR = "18-5";

  const $ = id => document.getElementById(id);
  const dinheiro = v => (v < 0 ? "-R$ " : "R$ ") +
    Math.abs(v).toFixed(2).replace(".", ",");
  const dez = n => String(n).padStart(2, "0");

  let estado = { fechamento: null, ultimoConcurso: null };

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
    escreverDezenas(pendente.campeao.dezenas);
    montarFechamento();
  }

  function escreverDezenas(lista) {
    $("dezenas").value = lista.map(dez).join(" ");
  }

  /* Cada padrão pede uma quantidade fixa de dezenas. Trocar o padrão sem
     ajustar o campo deixava o visitante encarando "o padrão 17-7 precisa de
     exatamente 17 dezenas" e adivinhando qual apagar. Aqui a lista se ajusta
     sozinha: sobrando, corta as últimas; faltando, completa com as melhores
     do campeão e, se ainda faltar, com as menores dezenas livres. */
  function ajustarAoPadrao() {
    const alvo = FZ.PADROES[$("padrao").value].dezenas;
    const atuais = lerDezenas($("dezenas").value).filter(n => n >= 1 && n <= 25);
    const escolhidas = atuais.slice(0, alvo);

    if (escolhidas.length < alvo) {
      const pendente = estado.fechamento && estado.fechamento.pendente;
      const reserva = (pendente ? pendente.campeao.dezenas : [])
        .concat(Array.from({ length: 25 }, (_, i) => i + 1));
      for (const n of reserva) {
        if (escolhidas.length >= alvo) break;
        if (!escolhidas.includes(n)) escolhidas.push(n);
      }
    }
    escreverDezenas(escolhidas.sort((a, b) => a - b));
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
      const alvo = dados.pendente.apos + 1;
      /* O robô roda por cron do GitHub Actions, que descarta boa parte dos
         agendamentos — já medimos 6 execuções de 48 num dia. Então existe
         uma janela real, às vezes de horas, entre o resultado sair e o
         palpite ser conferido. Dizer "antes do sorteio" nessa janela é
         afirmar algo que o leitor sabe ser falso, justamente na página que
         pede confiança. Quando o sorteio já saiu, a página diz isso. */
      const jaSorteou = estado.ultimoConcurso !== null &&
                        estado.ultimoConcurso >= alvo;
      const situacao = jaSorteou
        ? "<p>O concurso <strong>" + alvo + "</strong> já foi sorteado. " +
          "Estas dezenas foram cravadas antes disso e continuam aqui, " +
          "intactas, esperando o robô conferir — ele roda de tempos em " +
          "tempos e a linha entra no placar assim que ele passar.</p>"
        : "<p>Cravado para o concurso <strong>" + alvo + "</strong>, que " +
          "ainda não foi sorteado:</p>";
      $("pendente").innerHTML = situacao +
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
    const linha = (nome, c) => {
      // Zero não é nem ganho nem perda — só vermelho quando saldo < 0 e só
      // verde quando saldo > 0. Colorir um "ainda não aconteceu nada" de
      // verde seria maquiagem, e esta página existe para não maquiar.
      const classe = c.saldo > 0 ? " class='positivo'" :
                     c.saldo < 0 ? " class='negativo'" : "";
      return "<tr><th>" + nome + "</th><td>" + dinheiro(c.gasto) + "</td><td>" +
        dinheiro(c.retorno) + "</td><td" + classe + ">" +
        dinheiro(c.saldo) + "</td></tr>";
    };
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

  // Se os dados não chegarem — o robô escreve este arquivo a cada sorteio,
  // então um 404 ou um JSON quebrado é uma possibilidade real, não só
  // teórica — as quatro áreas que dependem dele têm que dizer a mesma
  // coisa: que não deu para carregar agora. Uma tabela em branco ao lado
  // de "não carregou" pareceria "não há nada a mostrar", quando na
  // verdade é o oposto: os dados existem, só não chegaram.
  function mostrarFalhaDeCarga() {
    const msg = "Não foi possível carregar os dados agora.";
    $("pendente").innerHTML = "<p>" + msg + "</p>";
    $("placar-corpo").innerHTML = "<tr><td colspan='8'>" + msg + "</td></tr>";
    $("conta-corpo").innerHTML = "<tr><td colspan='4'>" + msg + "</td></tr>";
    $("conta-ressalva").textContent = msg + " Tente recarregar a página em instantes.";
  }

  /* Descobre o último concurso já sorteado, só para saber se o pendente está
     esperando conferência. Falha aqui não é problema: sem o número, a página
     simplesmente não afirma nada sobre o sorteio ter saído. */
  function buscarUltimoConcurso() {
    return fetch("dados/lotofacil.json")
      .then(r => (r.ok ? r.json() : null))
      .then(base => {
        const lista = base && base.concursos;
        estado.ultimoConcurso = lista && lista.length
          ? lista[lista.length - 1][0] : null;
      })
      .catch(() => { estado.ultimoConcurso = null; });
  }

  fetch("dados/fechamento.json")
    .then(r => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(dados => {
      estado.fechamento = dados;
      desenharConta();
      usarDoCampeao();
      // O placar depende do último concurso, então espera essa consulta.
      return buscarUltimoConcurso().then(desenharPlacar);
    })
    .catch(mostrarFalhaDeCarga);

  $("btn-montar").addEventListener("click", montarFechamento);
  $("btn-usar-campeao").addEventListener("click", usarDoCampeao);
  $("padrao").addEventListener("change", ajustarAoPadrao);
})();
