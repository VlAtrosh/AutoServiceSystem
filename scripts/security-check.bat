@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ========================================
echo Проверка секретов в проекте
echo ========================================
echo.

git grep -n -i -E "password|secret|token|api_key|jwt|smtp|database_url" -- . ":!docs" ":!screenshots" ":!*.md" ":!backups"

echo.
dir /s .env* 2>nul

echo.
echo ========================================
echo Если найдены реальные секреты - удалить!
echo ========================================
pause