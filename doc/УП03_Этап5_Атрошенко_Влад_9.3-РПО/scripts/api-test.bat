@echo off
cd /d "%~dp0\.."
echo ========== ПРОВЕРКА API ==========
echo.
echo 1. Health check:
curl -s http://localhost:8000/health
echo.
echo 2. Регистрация:
curl -s -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d "{\"username\":\"testuser\",\"email\":\"test@mail.ru\",\"last_name\":\"Тестов\",\"first_name\":\"Тест\",\"password\":\"123456\",\"phone\":\"+79123456789\",\"role\":\"client\"}"
echo.
echo 3. Логин:
curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"testuser\",\"password\":\"123456\"}"
echo.
echo 4. Ошибочный логин:
curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"wrong\",\"password\":\"wrong\"}"
echo.
echo ========== ПРОВЕРКА ЗАВЕРШЕНА ==========
pause