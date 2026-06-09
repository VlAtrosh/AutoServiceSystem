@echo off
cd /d "%~dp0\.."
echo ========== ОБЩАЯ ПРОВЕРКА КАЧЕСТВА ==========
call scripts\test.bat
call scripts\api-test.bat
echo ========== ПРОВЕРКА ЗАВЕРШЕНА ==========
pause