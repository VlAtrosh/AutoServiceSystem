@echo off
chcp 65001 > nul
cd /d "%~dp0\..\backend"

echo ========================================
echo  Проверка качества кода
echo ========================================

echo [1/3] Ruff линтер...
ruff check .
if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Ruff нашел проблемы!
    pause
    exit /b %errorlevel%
)
echo [OK] Ruff проверка пройдена

echo.
echo [2/3] Black форматтер (проверка)...
black --check .
if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Неотформатированные файлы!
    echo Запусти scripts\format.bat для исправления
    pause
    exit /b %errorlevel%
)
echo [OK] Black проверка пройдена

echo.
echo [3/3] Запуск тестов...
pytest tests/ -v
if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Тесты не прошли!
    pause
    exit /b %errorlevel%
)
echo [OK] Все тесты пройдены

echo.
echo ========================================
echo [УСПЕХ] Все проверки пройдены!
echo ========================================
pause