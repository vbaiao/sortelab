/* SorteLab — página do fechamento da Lotofácil. */
"use strict";

(function () {
  const FZ = window.SorteLabFechamento;
  const PRESET_PLACAR = "18-5";
  const API_CAIXA =
    "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/";

  const $ = id => document.getElementById(id);
  const dinheiro = v => (v < 0 ? "-R$ " : "R$ ") +
    Math.abs(v).toFixed(2).replace(".", ",");
  const dez = n => String(n).padStart(2, "0");

  let estado = { fechamento: null, aoVivo: null, buscaFalhou: false };

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

  /* Sorteia dezenas para o visitante brincar. Aqui usamos Math.random de
     propósito, e não o mulberry32 do placar: aquele existe para ser
     reproduzível por terceiros, o que só importa quando a gente precisa
     provar que não trapaceou. Num botão que a pessoa clica quantas vezes
     quiser, semente fixa daria sempre o mesmo jogo — o contrário do que ela
     espera. */
  function sortearDezenas() {
    const alvo = FZ.PADROES[$("padrao").value].dezenas;
    const baralho = [];
    for (let n = 1; n <= 25; n++) baralho.push(n);
    for (let i = baralho.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const troca = baralho[i]; baralho[i] = baralho[j]; baralho[j] = troca;
    }
    escreverDezenas(baralho.slice(0, alvo).sort((a, b) => a - b));
    montarFechamento();
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

  /* O histórico gravado mais, se houver, a linha que a página conferiu
     sozinha. Placar e conta usam as duas juntas — mostrar o resultado na
     tabela e deixá-lo fora da soma daria dois números que se contradizem
     na mesma tela. */
  function todasAsLinhas() {
    const gravado = estado.fechamento ? estado.fechamento.historico : [];
    return estado.aoVivo ? gravado.concat([estado.aoVivo]) : gravado;
  }

  function linhaPlacar(linha, lado) {
    const d = linha[lado];
    const melhor = Math.max.apply(null, d.acertos);
    const premiados = d.acertos.filter(a => a >= FZ.FAIXA_MINIMA).length;
    return "<td>" + melhor + "</td><td>" + premiados + "</td><td>" +
      (d.retorno === null ? "—" : dinheiro(d.retorno)) + "</td>";
  }

  /* O que já dá para mostrar do próximo concurso, e o que não dá.

     O lado ALEATÓRIO sai na hora: ele é função pura do número do concurso.
     Semente 3773 devolve sempre as mesmas 18 dezenas, e o algoritmo está
     publicado logo abaixo nesta página. Não há nada a cravar — qualquer
     pessoa roda, antes ou depois do sorteio, e chega no mesmo resultado.
     Esconder isso até o robô passar seria esconder o que já é público.

     O lado CAMPEÃO não sai. Ele depende de QUAIS concursos entraram na
     conta: calculado com o histórico até o 3772 dá um jogo, com o 3773
     incluído dá outro — e esse segundo seria trapaça. O que o robô grava
     não é o número, é o corte. Por isso ele espera. */
  function proximoPalpite(proximo) {
    let aleatorio;
    try {
      aleatorio = FZ.dezenasAleatorias(proximo, 18, 1, 25).map(dez).join(" ");
    } catch (e) {
      return "";
    }
    return "<hr>" +
      "<p class='dica'><em>Próximo concurso: " + proximo + "</em></p>" +
      "<p><strong>Aleatório</strong> (semente " + proximo + "): " +
      aleatorio + "</p>" +
      "<p>Este lado não precisa esperar o robô: ele é só uma conta em cima " +
      "do número do concurso, e o código está aqui na página. Rode você " +
      "mesmo — tem que dar exatamente estas dezenas.</p>" +
      "<p><strong>Campeão:</strong> sai quando o robô cravar. Este depende " +
      "de quais concursos entraram na conta — feito com o histórico até o " +
      "<strong>" + (proximo - 1) + "</strong> dá um jogo, feito depois do " +
      "sorteio daria outro. O que fica registrado não é o número, é o " +
      "corte. Por isso ele espera, e o aleatório não.</p>";
  }

  /* Deixa qualquer pessoa conferir a regra do lado aleatório sem abrir
     console nenhum. Não substitui a auditoria de verdade — o código roda
     desta própria página — mas mostra o que importa para quem só quer
     entender: o mesmo concurso devolve sempre as mesmas dezenas. O passo a
     passo para conferir por fora fica logo abaixo, na página. */
  function mostrarDezenasDaSemente() {
    const saida = $("saida-semente");
    const n = parseInt($("semente").value, 10);
    if (!n || n < 1) {
      saida.innerHTML = "<p class='erro'>Digite o número de um concurso, " +
        "como 3773.</p>";
      return;
    }
    const dezenas = FZ.dezenasAleatorias(n, 18, 1, 25).map(dez).join(" ");
    saida.innerHTML =
      "<p class='dica'><em>Concurso " + n + " · semente " + n + "</em></p>" +
      "<p class='jogos-semente'>" + dezenas + "</p>";
  }

  function desenharPlacar() {
    const dados = estado.fechamento;
    if (!dados) return;
    const historico = todasAsLinhas().slice().reverse();
    $("placar-corpo").innerHTML = historico.map(linha =>
      "<tr><td>" + linha.concurso +
      (linha.aoVivo ? " <span class='ao-vivo'>ao vivo</span>" : "") +
      "</td><td>" + linha.data + "</td>" +
      linhaPlacar(linha, "campeao") + linhaPlacar(linha, "aleatorio") +
      "</tr>").join("") ||
      "<tr><td colspan='8'>Nenhum sorteio conferido ainda.</td></tr>";

    if (dados.pendente) {
      const alvo = dados.pendente.apos + 1;
      const dezenasDe = lado =>
        "<p><strong>" + (lado === "campeao" ? "Campeão" : "Aleatório") +
        "</strong>" + (lado === "aleatorio"
          ? " (semente " + dados.pendente.aleatorio.semente + ")" : "") +
        ": " + dados.pendente[lado].dezenas.map(dez).join(" ") + "</p>";

      /* Três estados, e a página precisa dizer a verdade nos três. O robô
         roda por cron do GitHub Actions, que descarta boa parte dos
         agendamentos — já medimos 6 execuções de 48 num dia. Então a janela
         entre o resultado sair e o palpite ser gravado é real e às vezes
         dura horas. */
      if (estado.aoVivo) {
        /* Depois de conferido, este palpite NÃO está mais em aberto: ele já
           correu e o resultado está na tabela. Continuar apresentando as
           mesmas dezenas como se fossem a aposta da vez faz o leitor
           procurar o concurso seguinte e não achar.

           E a página não pode cravar o próximo por conta própria. Não é
           limitação técnica — é o que dá valor ao painel: um palpite só
           prova alguma coisa se estiver publicado, com data, ANTES do
           sorteio. Calculado no navegador depois, não provaria nada. */
        $("pendente").innerHTML =
          "<p class='dica'><em>Este palpite já correu.</em></p>" +
          "<p>Estas são as dezenas que estavam cravadas para o concurso " +
          "<strong>" + alvo + "</strong>, publicadas aqui antes do sorteio. " +
          "Ele já saiu, e a conferência está no placar abaixo marcada como " +
          "<strong>ao vivo</strong> — foi esta página que fez a conta, " +
          "buscando o resultado direto na Caixa.</p>" +
          dezenasDe("campeao") + dezenasDe("aleatorio") +
          proximoPalpite(alvo + 1);
      } else if (estado.buscaFalhou) {
        $("pendente").innerHTML =
          "<p>Cravado para o concurso <strong>" + alvo + "</strong>. Não " +
          "deu para consultar a Caixa agora, então não dá para dizer daqui " +
          "se o sorteio já saiu:</p>" +
          dezenasDe("campeao") + dezenasDe("aleatorio");
      } else {
        /* Não dizer "ainda não foi sorteado". A página só sabe o que a API
           da Caixa conta, e ela atrasa: já vimos o resultado circulando na
           imprensa horas antes de aparecer ali. Afirmar que o sorteio não
           aconteceu, quando aconteceu, é dar por certeza o que é só o
           limite do que a página enxerga. */
        $("pendente").innerHTML =
          "<p>Cravado para o concurso <strong>" + alvo + "</strong>. A " +
          "Caixa ainda não publicou o resultado dele no sistema de onde a " +
          "gente lê. Assim que publicar, a conferência aparece aqui " +
          "sozinha — mesmo que o robô demore:</p>" +
          dezenasDe("campeao") + dezenasDe("aleatorio");
      }
    }
  }

  function desenharConta() {
    const dados = estado.fechamento;
    if (!dados) return;
    const conta = FZ.contaAcumulada(todasAsLinhas(), dados.preset);
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

  /* Pergunta o concurso direto à Caixa, e não a dados/lotofacil.json.
     Parece um detalhe e não é: os dois arquivos locais são gravados pela
     MESMA rodada do robô, então ficam velhos juntos. Comparar um com o
     outro nunca acusaria atraso — os dois estariam igualmente parados no
     passado. Só uma fonte de fora enxerga que o sorteio aconteceu.
     Falha aqui não quebra nada: sem resposta, a página só não afirma que
     o sorteio saiu. */
  function pedirCaixa(caminho) {
    const controle = new AbortController();
    const prazo = setTimeout(() => controle.abort(), 8000);
    return fetch(API_CAIXA + caminho, { signal: controle.signal })
      .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .finally(() => clearTimeout(prazo));
  }

  function lerSorteio(d) {
    const dezenas = (d.listaDezenas || []).map(Number).sort((a, b) => a - b);
    if (dezenas.length !== FZ.DEZENAS_POR_JOGO) return null;
    const rateio = {};
    (d.listaRateioPremio || []).forEach(f => {
      const faixa = String(f.descricaoFaixa || "").replace(/\D/g, "");
      if (faixa && f.valorPremio != null) rateio[faixa] = Number(f.valorPremio);
    });
    // Mesma guarda do robô: a faixa de 11 sempre tem milhares de ganhadores,
    // então zero ali quer dizer rateio ainda não liquidado — não que ninguém
    // ganhou. Sem ele o retorno fica em branco em vez de virar R$ 0,00.
    const liquidado = Number(rateio[FZ.FAIXA_MINIMA]) > 0;
    return { concurso: Number(d.numero), data: d.dataApuracao,
             resultado: dezenas, rateio: liquidado ? rateio : null };
  }

  /* Descobre a situação do concurso pendente.

     Pergunta DIRETO pelo concurso alvo, e não pelo endpoint do "último".
     Parece a ordem errada e não é: o endpoint do último atrasa. Neste
     momento ele responde 3769 enquanto /lotofacil/3770 devolve o 3770
     completo, com as 15 dezenas. Confiar nele faria a página jurar que o
     sorteio não saiu tendo o resultado a uma chamada de distância.

     A ambiguidade que sobra: para um concurso inexistente a API devolve
     HTTP 500 — o mesmo de uma pane. Aí sim o "último" serve, como
     desempate: se ele responde, a API está de pé e o 500 no alvo significa
     "ainda não existe"; se ele também falha, é indisponibilidade mesmo. */
  function situacaoDoPendente(alvo) {
    return pedirCaixa(alvo)
      .then(d => {
        const s = lerSorteio(d);
        return s ? { estado: "saiu", sorteio: s } : { estado: "aguardando" };
      })
      .catch(() => pedirCaixa("")
        .then(() => ({ estado: "aguardando" }))
        .catch(() => ({ estado: "indisponivel" })));
  }

  /* Confere o pendente contra um sorteio recém-saído, com o mesmo motor que
     o robô usa. Não grava nada: é só a página adiantando o que o robô vai
     registrar quando passar. */
  function conferirAoVivo(pendente, sorteio) {
    const linha = { concurso: sorteio.concurso, data: sorteio.data,
                    resultado: sorteio.resultado, rateio: sorteio.rateio,
                    aoVivo: true };
    ["campeao", "aleatorio"].forEach(lado => {
      const dezenas = pendente[lado].dezenas;
      const jogos = FZ.montar(dezenas, estado.fechamento.preset);
      const nota = FZ.avaliar(jogos, sorteio.resultado, sorteio.rateio);
      linha[lado] = { dezenas: dezenas, acertos: nota.acertos,
                      retorno: nota.retorno };
    });
    return linha;
  }

  fetch("dados/fechamento.json")
    .then(r => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(dados => {
      estado.fechamento = dados;
      usarDoCampeao();
      if (!dados.pendente) {
        desenharPlacar();
        desenharConta();
        return;
      }
      // Desenha já com o que temos e melhora depois: a consulta à Caixa
      // pode demorar ou falhar, e a página não deve ficar em branco por isso.
      desenharPlacar();
      desenharConta();
      return situacaoDoPendente(dados.pendente.apos + 1).then(r => {
        if (r.estado === "saiu") {
          estado.aoVivo = conferirAoVivo(dados.pendente, r.sorteio);
        } else if (r.estado === "indisponivel") {
          estado.buscaFalhou = true;
        }
        desenharPlacar();
        desenharConta();
      });
    })
    .catch(mostrarFalhaDeCarga);

  $("btn-montar").addEventListener("click", montarFechamento);
  $("btn-usar-campeao").addEventListener("click", usarDoCampeao);
  $("btn-sortear").addEventListener("click", sortearDezenas);
  $("padrao").addEventListener("change", ajustarAoPadrao);
  $("btn-semente").addEventListener("click", mostrarDezenasDaSemente);
  mostrarDezenasDaSemente();
})();
