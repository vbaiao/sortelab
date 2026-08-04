/* SorteLabs — comportamentos visuais compartilhados:
   o volante que se preenche (assinatura da marca) e a revelação
   das seções ao rolar. Ambos silenciam com prefers-reduced-motion. */
"use strict";

(function () {
  const semMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- volante: 60 células, algumas marcadas em ciclo ---------- */
  const volante = document.querySelector(".volante");
  if (volante) {
    const TOTAL = 60, MARCADAS = 13;
    const sorteadas = new Set();
    while (sorteadas.size < MARCADAS) {
      sorteadas.add(Math.floor(Math.random() * TOTAL));
    }
    for (let i = 0; i < TOTAL; i++) {
      const celula = document.createElement("i");
      if (sorteadas.has(i)) {
        celula.className = "marcada";
        if (!semMovimento) {
          celula.style.animationDelay = (Math.random() * 5.5).toFixed(2) + "s";
        }
      }
      volante.appendChild(celula);
    }
  }

  /* ---------- revelação ao rolar ---------- */
  const alvos = document.querySelectorAll(".revelar");
  if (!alvos.length) return;
  if (semMovimento || !("IntersectionObserver" in window)) {
    alvos.forEach(el => el.classList.add("visivel"));
    return;
  }
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach(entrada => {
      if (entrada.isIntersecting) {
        entrada.target.classList.add("visivel");
        observador.unobserve(entrada.target);
      }
    });
  }, { rootMargin: "0px 0px -12% 0px", threshold: .08 });
  alvos.forEach(el => observador.observe(el));
})();
