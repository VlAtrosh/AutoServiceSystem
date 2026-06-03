@echo off
chcp 65001 > nul
cd /d "%~dp0\..\backend"

echo ========================================
echo  Запуск сервера
echo ========================================

echo Запуск на http://localhost:8000
uvicorn app.main:app --reload --port 8000

pause