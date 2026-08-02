# SorteLabs

Ferramentas gratuitas e honestas para 8 loterias da Caixa: gerador
estatístico, bolão com rateio pronto para o WhatsApp, conferidor de vários
jogos de uma vez e planejador de orçamento.

**A promessa honesta:** nenhuma estatística aumenta a chance de ganhar.
O SorteLabs organiza a brincadeira — não vende milagre.

## Como funciona

- Site 100% estático: HTML + CSS + JavaScript puro, sem servidor.
- `dados/*.json`: histórico completo de cada loteria.
- `js/motor.js`: o motor estatístico (score por dezena + filtros de perfil).
- `robo/atualizar.py`: consulta a API oficial da Caixa e completa os JSONs.
- `.github/workflows/atualizar.yml`: roda o robô todo dia e publica sozinho.

## Rodar localmente

Dê dois cliques em `Ver-Site.bat` (Windows) ou rode:

    python -m http.server 8765

e abra <http://localhost:8765>. A página `teste.html` valida o motor JS
contra o gabarito gerado pelo motor Python de referência.

## Manutenção

- Template das páginas de loteria: `robo/gerar_paginas.py` (edite e rode).
- Preços das apostas: em `js/motor.js` (LOTERIAS) — atualizar quando a Caixa
  reajustar.
- Importação inicial de históricos: `robo/importar_csv.py`.
