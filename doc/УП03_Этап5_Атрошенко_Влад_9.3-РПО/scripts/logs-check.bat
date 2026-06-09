@echo off
cd /d "%~dp0\.."
echo ========== ПРОВЕРКА ЛОГОВ ==========
docker logs autoservice-backend --tail 50 > reports\logs_tail.txt
type reports\logs_tail.txt
echo.
echo ========== ПРОВЕРКА ЗАВЕРШЕНА ==========
pause