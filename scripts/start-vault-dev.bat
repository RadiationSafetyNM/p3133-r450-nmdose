@echo off
title ▶ Vault Dev Background Starter

:: Vault 실행 여부 확인
tasklist | find /i "vault.exe" >nul
if %errorlevel%==0 (
    echo Vault already running.
    goto :end
)

:: 최소화 상태로 Vault 실행
start /min "Vault Dev Server" cmd /k "vault server -dev"

timeout /t 2 >nul

set VAULT_ADDR=http://127.0.0.1:8200
set VAULT_TOKEN=hvs.your_token_here
echo Vault dev server started in background.

:end
