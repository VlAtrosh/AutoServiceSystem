@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ========================================
echo  ПЕРЕЗАПУСК СЕРВИСОВ
echo ========================================

echo Перезапуск контейнеров...
docker compose -f docker-compose.prod.yml restart

echo.
echo Текущий статус:
docker compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo  ПЕРЕЗАПУСК ВЫПОЛНЕН
echo ========================================
pause