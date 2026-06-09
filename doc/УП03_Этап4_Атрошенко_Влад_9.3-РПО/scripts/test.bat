@echo off
cd /d "%~dp0\..\backend"
echo ========== ЗАПУСК ТЕСТОВ ==========
pytest tests/ -v
pause