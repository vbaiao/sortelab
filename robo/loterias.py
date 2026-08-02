# -*- coding: utf-8 -*-
"""Fichas técnicas das loterias suportadas pelo SorteLab (lado robô)."""

LOTERIAS = [
    dict(slug="megasena", nome="Mega-Sena"),
    dict(slug="lotofacil", nome="Lotofácil"),
    dict(slug="quina", nome="Quina"),
    dict(slug="lotomania", nome="Lotomania"),
    dict(slug="duplasena", nome="Dupla Sena"),
    dict(slug="diadesorte", nome="Dia de Sorte"),
    dict(slug="timemania", nome="Timemania"),
    dict(slug="maismilionaria", nome="+Milionária"),
]

API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/"
