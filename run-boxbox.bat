@echo off
setlocal
cd /d "%~dp0"
title Box Box - Servidor local

echo [Box Box] Preparando o sistema...
where python >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao foi encontrado. Instale Python 3.12 ou superior e marque "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Criando ambiente virtual...
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo [2/4] Verificando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/4] Atualizando o banco sem apagar dados...
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto :error

echo [4/4] Box Box disponivel em http://127.0.0.1:8000/
echo Feche esta janela ou pressione Ctrl+C para parar.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
if errorlevel 1 goto :error
exit /b 0

:error
echo.
echo ERRO: nao foi possivel iniciar o Box Box. Leia a mensagem acima.
pause
exit /b 1
