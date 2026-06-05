# RELEASE_NOTES.md

## Версия 1.0.0 (03.06.2026)

### Что добавлено
- Развертывание на VPS (80.78.247.163)
- Docker Compose production конфигурация
- Nginx для статики фронтенда
- Автоматический перезапуск контейнеров (restart: unless-stopped)

### Как запустить
```bash
docker compose -f docker-compose.prod.yml up -d