@echo off
chcp 65001 > nul
cd /d "%~dp0\..\backend"

echo ========================================
echo  Форматирование кода
echo ========================================

echo [1/2] Ruff автоисправление...
ruff check . --fix
if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Ruff не смог исправить все ошибки
    pause
    exit /b %errorlevel%
)
echo [OK] Ruff исправления применены

echo.
echo [2/2] Black форматирование...
black .
if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Black не смог отформатировать файлы
    pause
    exit /b %errorlevel%
)
echo [OK] Black форматирование применено

echo.
echo ========================================
echo [УСПЕХ] Форматирование завершено!
echo ========================================
pause