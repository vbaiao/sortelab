# SorteLab — Design aprovado (01/08/2026)

## O que é
Site estático de ferramentas para as loterias da Caixa, baseado no motor
estatístico do `gerador_loterias.py` (score 50% frequência histórica + 35%
recente + 15% atraso, filtros de perfil de sorteio). Português, mobile-first,
tom honesto: nenhuma estatística aumenta chance real; entretenimento, +18.

## Escopo v1
8 loterias: Mega-Sena, Lotofácil, Quina, Lotomania, Dupla Sena, Dia de Sorte,
Timemania, +Milionária. Cada uma com 5 ferramentas em abas:
1. Gerador (ponderado + jogo campeão determinístico)
2. Bolão com rateio + mensagem pronta para WhatsApp (diferencial nº 1)
3. Planejador de orçamento (tabela de possibilidades com chance)
4. Conferidor copia-e-cola (diferencial nº 2)
5. Estatísticas (mais sorteados, atrasados, últimos resultados)

Fora da v1: páginas navegáveis de resultados (SEO de guerra), Super Sete /
Federal / Loteca (mecânica diferente), contas de usuário.

## Arquitetura
- Site 100% estático, sem build tools: HTML + CSS + JS puro.
- `index.html` (home) + uma página por loteria (`megasena.html`, ...) para SEO.
- `js/motor.js`: todo o motor portado do Python; `js/app.js`: UI das abas.
- `dados/{slug}.json`: histórico compacto `{atualizado, concursos: [[n, data, [dezenas]], ...]}`.
- Rodapé honesto em todas as páginas; blocos reservados para AdSense futuro.

## Robô de atualização
- `robo/atualizar.py`: consulta a API oficial da Caixa
  (`servicebus2.caixa.gov.br/portaldeloterias/api/{slug}`) para as 8 loterias,
  completa os JSONs sem interação e sai com código 0 sempre que possível.
- `.github/workflows/atualizar.yml`: cron diário 21h30 BRT + repescagem 23h30,
  commita apenas quando há concurso novo; GitHub Pages republica sozinho.

## Publicação
Local primeiro (`Ver-Site.bat` com `python -m http.server`); depois conta
GitHub do usuário (a criar, com guia), repo `sortelab`, GitHub Pages.
Domínio próprio e AdSense ficam para depois do site no ar.

## Decisões do usuário
- Nome: **SorteLab**. Hospedagem: GitHub (conta a criar). Escopo: 8 loterias.
