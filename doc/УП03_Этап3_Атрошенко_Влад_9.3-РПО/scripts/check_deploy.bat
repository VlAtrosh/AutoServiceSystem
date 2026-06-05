@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ========================================
echo  ПРОВЕРКА СТАТУСА РАЗВЕРТЫВАНИЯ
echo ========================================

echo.
echo [1/3] Статус контейнеров:
docker compose -f docker-compose.prod.yml ps

echo.
echo [2/3] Последние логи (50 строк):
docker compose -f docker-compose.prod.yml logs --tail=50

echo.
echo [3/3] Проверка доступности фронтенда:
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://80.78.247.163

echo.
echo ========================================
echo  ПРОВЕРКА ЗАВЕРШЕНА
echo ========================================
pause