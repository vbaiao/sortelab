@echo off
title SorteLab - servidor local
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  SorteLab rodando em http://localhost:8765
echo  (feche esta janela para parar)
echo.
start "" http://localhost:8765
python -m http.server 8765
