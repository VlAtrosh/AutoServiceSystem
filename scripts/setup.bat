@echo off
chcp 65001 > nul
cd /d "%~dp0\..\backend"

echo ========================================
echo  Установка зависимостей
echo ========================================

echo [1/2] Установка пакетов...
pip install --force-reinstall -r requirements.txt

echo.
echo [2/2] Проверка версий...
python -c "import pydantic; assert pydantic.__version__ == '2.5.0', f'pydantic version {pydantic.__version__} != 2.5.0'"
if errorlevel 1 (
    echo.
    echo    ОШИБКА: Неправильная версия pydantic!
    echo    Требуется: 2.5.0
    echo    Попробуйте удалить venv и запустить setup.bat заново
    pause
    exit /b 1
)

echo.
echo  Зависимости установлены корректно
pause