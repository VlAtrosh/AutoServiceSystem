@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ========================================
echo  ЗАПУСК PRODUCTION РАЗВЕРТЫВАНИЯ
echo ========================================

echo [1/3] Остановка старых контейнеров...
docker compose -f docker-compose.prod.yml down

echo [2/3] Сборка и запуск...
docker compose -f docker-compose.prod.yml up --build -d

echo [3/3] Проверка статуса...
docker compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo  ГОТОВО!
echo  Проект доступен по адресу: http://80.78.247.163
echo ========================================
pause