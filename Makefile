.PHONY: help setup run check format docker-build docker-up docker-down logs clean

help:
	@echo "========================================="
	@echo "  Доступные команды:"
	@echo "========================================="
	@echo "  make setup        - Установка зависимостей"
	@echo "  make run          - Запуск проекта локально"
	@echo "  make check        - Проверка кода (линтер + тесты)"
	@echo "  make format       - Форматирование кода"
	@echo "  make docker-build - Сборка Docker образов"
	@echo "  make docker-up    - Запуск Docker контейнеров"
	@echo "  make docker-down  - Остановка Docker контейнеров"
	@echo "  make logs         - Просмотр логов"
	@echo "  make clean        - Очистка временных файлов"
	@echo "========================================="

setup:
	@echo "Install dependencies"
	cd backend && pip install -r requirements.txt
	@echo "Setup complete"

run:
	@echo "Run project locally"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

check:
	@echo "=== Running checks ==="
	cd backend && ruff check .
	cd backend && black --check .
#	cd backend && pytest tests/ -v 

format:
	@echo "=== Formatting code ==="
	cd backend && ruff check . --fix
	cd backend && black .

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

logs:
	docker compose logs -f

clean:
	@echo "Cleaning temporary files"
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"