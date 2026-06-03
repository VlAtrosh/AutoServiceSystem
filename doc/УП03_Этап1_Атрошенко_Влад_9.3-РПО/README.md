
#  AutoServiceSystem: Система автоматизации ремонтов и заказ-нарядов

AutoServiceSystem — это веб-приложение для автоматизации работы автосервиса (СТО). Система позволяет управлять заказ-нарядами, клиентами, автомобилями, справочниками работ и запчастей, а также формировать отчёты по выручке. Проект демонстрирует возможности FastAPI для создания REST API, интеграцию с базой данных (в памяти), современный фронтенд с адаптивным дизайном и полный цикл тестирования (модульные и интеграционные тесты).

Проект создан для наглядной демонстрации возможностей FastAPI: REST API, авторизация через JWT-токены, статусная модель заказов, уведомления (SMS), отчёты и интерактивный интерфейс.

##  Моё мнение о FastAPI

FastAPI — это современный и быстрый фреймворк для создания API на Python. Он сочетает в себе простоту Flask и мощь асинхронности, автоматически генерирует документацию Swagger UI, валидирует данные через Pydantic и работает на скорости Starlette (практически догоняет Node.js и Go).

Вместо того чтобы вручную писать валидацию запросов, документацию и сериализацию, FastAPI всё делает за вас. Достаточно описать модели через Pydantic — и вы получаете:

- Автоматическую валидацию входных данных
- Документацию API (Swagger UI и ReDoc)
- Автодополнение в IDE
- Асинхронную обработку запросов

Для production-проектов FastAPI незаменим. Он отлично подходит для микросервисов, бэкенда мобильных приложений, систем реального времени и машинного обучения. Проект демонстрирует, что создание профессионального API может быть быстрым, простым и даже увлекательным.

##  Быстрый старт

### Требования

- Python 3.8+
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/VlAtrosh/car-service.git
cd auto_service


# Windows
python -m venv venv
venv\Scripts\activate
```

### Создайте виртуальное окружение (рекомендуется):
```
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

```
### Установите зависимости:
```
pip install -r requirements.txt
```

### Запустите сервер:
```
cd backend
uvicorn app.main:app --reload --port 8000
```

### Откройте в браузере:
```
http://localhost:8000
```

## Справка по командам

```
# Запуск сервера в режиме разработки
uvicorn app.main:app --reload --port 8000

# Запуск в PRODUCTION режиме
set APP_ENV=production && uvicorn app.main:app --reload --port 8000

# Запуск в DEBUG режиме (отключена проверка токенов)
set APP_ENV=debug && uvicorn app.main:app --reload --port 8000

# Запуск в TEST режиме (заглушка для SMS)
set APP_ENV=test && uvicorn app.main:app --reload --port 8000

# Проверка качества кода Ruff
ruff check .

# Авто-исправление Ruff
ruff check . --fix

# Форматирование кода Black
black .

# Проверка форматирования Black
black --check .

# Запуск модульных тестов
pytest tests/ -v

# Запуск интеграционных тестов
pytest tests/test_integration.py -v -s

# Открыть Swagger документацию
# http://localhost:8000/docs
```

## Примеры вывода

Главная страница (фронтенд)

```
<img width="1200" height="700" alt="Главная страница" src="https://user-images.githubusercontent.com/placeholder/autoservice-main.png" />
```

## Авторизация

```
POST /api/v1/user/login
Content-Type: application/json

{
  "email": "test@mail.ru",
  "password": "123"
}
```

Ответ:
```
{
  "access_token": "87dccd9a-3c63-4ab1-bb19-f60f9eb0e84f",
  "token_type": "bearer"
}
```


Создание заказа:

```
POST /api/v1/order/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "client_id": "client1",
  "car_info": "BMW X5 2022"
}
```
Ответ:
```
{
  "order_id": "8fefec3e",
  "order_number": "ЗН-8fefec3e",
  "status": "accepted"
}
```


Смена статуса заказа

```
PUT /api/v1/order/8fefec3e/status?new_status=ready
Authorization: Bearer <token>
```

Ответ:
```
{
  "status": "ready"
}
```

SMS в консоли сервера:

```
[SMS] -> +79123456789: Your order ЗН-8fefec3e is ready for pickup
```

## Интерфейс

```
<img width="1200" height="500" alt="Заказ-наряды" src="https://github.com/user-attachments/assets/placeholder-orders.png" /
```

Карточки заказ-нарядов с цветовой индикацией статусов

```
<img width="1200" height="400" alt="Выпадающее меню пользователя" src="https://github.com/user-attachments/assets/placeholder-menu.png" />
```


<img width="1920" height="1030" alt="Снимок экрана (1388)" src="https://github.com/user-attachments/assets/a2277dda-cb59-4756-a0e8-588b2cf146e4" />

<img width="1920" height="1038" alt="Снимок экрана (1390)" src="https://github.com/user-attachments/assets/51fa7df6-d3f7-4035-a286-ed996e2dc076" />

<img width="1920" height="1033" alt="Снимок экрана (1398)" src="https://github.com/user-attachments/assets/18106d4b-28de-464a-b011-eed66e8b45da" />




## Структура проекта

```
auto_service/
│
├── README.md
├── requirements.txt
│
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # Точка входа (FastAPI)
│       ├── config.py               # Конфигурация (PRODUCTION/DEBUG/TEST)
│       │
│       ├── core/                   # Общие компоненты
│       │   ├── __init__.py
│       │   ├── database.py         # База данных в памяти
│       │   ├── dependencies.py     # get_current_user, HTTPBearer
│       │   ├── exceptions.py       # Кастомные исключения
│       │   └── file_storage.py     # Работа с JSON файлами
│       │
│       ├── modules/
│       │   ├── __init__.py
│       │   │
│       │   ├── user/               # Модуль пользователей
│       │   │   ├── __init__.py
│       │   │   ├── models.py       # User, UserRole
│       │   │   ├── schemas.py      # Pydantic схемы
│       │   │   ├── api.py          # Эндпоинты (login, register, me)
│       │   │   ├── service.py      # Бизнес-логика
│       │   │   └── utils.py        # Хэширование
│       │   │
│       │   ├── cars/               # Модуль автомобилей
│       │   │   ├── __init__.py
│       │   │   ├── models.py       # Car
│       │   │   ├── schemas.py      # CarCreate, CarUpdate, CarResponse
│       │   │   ├── api.py          # CRUD эндпоинты
│       │   │   └── service.py      # Бизнес-логика
│       │   │
│       │   ├── order/              # Модуль заказ-нарядов
│       │   │   ├── __init__.py
│       │   │   ├── models.py       # Order, OrderStatus, OrderItem
│       │   │   ├── schemas.py      # CreateOrderRequest, AddWorkRequest
│       │   │   ├── api.py          # Эндпоинты
│       │   │   ├── service.py      # Бизнес-логика
│       │   │   └── status_machine.py # Логика переходов статусов
│       │   │
│       │   ├── reference/          # Модуль справочных данных
│       │   │   ├── __init__.py
│       │   │   ├── models.py       # Work, Part
│       │   │   ├── schemas.py      # WorkResponse, PartResponse
│       │   │   ├── api.py          # Эндпоинты (works, parts)
│       │   │   └── service.py      # Бизнес-логика
│       │   │
│       │   ├── report/             # Модуль отчетности
│       │   │   ├── __init__.py
│       │   │   ├── schemas.py      # RevenueReportResponse
│       │   │   ├── api.py          # Эндпоинт revenue
│       │   │   └── service.py      # Бизнес-логика
│       │   │
│       │   └── integration/        # Модуль интеграции
│       │       ├── __init__.py
│       │       ├── api.py          # Эндпоинт export-excel
│       │       ├── service.py      # Бизнес-логика
│       │       ├── excel_export.py # Экспорт в Excel
│       │       ├── pdf_export.py   # Экспорт в PDF
│       │       └── print_service.py # Печать
│       │
│       └── utils/
│           ├── __init__.py
│           └── logger.py
│
├── frontend/
│   └── web/
│       ├── index.html
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
│
├── data/
│   └── cars.json                   # Хранилище автомобилей
│
└── tests/
    ├── __init__.py
    ├── test_user.py
    ├── test_order.py
    └── test_integration.py
```

## Назначение файлов

| Файл | Что делает |
|------|------------|
| `backend/app/main.py` | Точка входа, подключение роутеров, CORS, раздача статики |
| `backend/app/config.py` | Конфигурация с режимами PRODUCTION/DEBUG/TEST |
| `backend/app/modules/user/` | Регистрация, авторизация, JWT-токены, роли |
| `backend/app/modules/order/` | Заказ-наряды, статусная модель, расчёт стоимости |
| `backend/app/modules/reference/` | Справочники работ и запчастей |
| `backend/app/modules/notification/` | Отправка SMS (заглушка) |
| `backend/app/modules/report/` | Отчёты по выручке |
| `backend/app/modules/integration/` | Экспорт в Excel/PDF |
| `frontend/web/` | HTML/CSS/JS интерфейс |
| `tests/` | Модульные и интеграционные тесты |


## Ключевые концепции

Авторизация через Bearer Token

```
# dependencies.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = db.tokens.get(token)
    return db.users.get(user_id)
```

Статусная модель заказа

```
status_machine.py
_transitions = {
    OrderStatus.ACCEPTED: [OrderStatus.DIAGNOSTICS],
    OrderStatus.DIAGNOSTICS: [OrderStatus.WAITING_APPROVAL, OrderStatus.IN_PROGRESS],
    OrderStatus.IN_PROGRESS: [OrderStatus.READY],
    OrderStatus.READY: [OrderStatus.COMPLETED],
}
```

Три режима сборки (PRODUCTION/DEBUG/TEST)

```
# config.py
import os

class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"

class DebugConfig(Config):
    DEBUG = True
    ENV = "debug"

class TestConfig(Config):
    DEBUG = False
    ENV = "test"
    TESTING = True
```

Модульные тесты (pytest)

```
def test_add_part_with_zero_quantity(self):
    order = OrderService.create_order("client1", "BMW X5")
    updated_order = OrderService.add_part(order.id, "p1", 0)
    assert len(updated_order.items) == 0  # Не добавляется
```

## Обработка ошибок

| Ситуация | Сообщение |
|----------|-----------|
| Неверный email или пароль | `{"detail": "Invalid email or password"}` |
| Токен не предоставлен | `{"detail": "Token not provided"}` |
| Неверный токен | `{"detail": "Invalid token"}` |
| Недостаточно прав (роль не та) | `{"detail": "Not enough rights"}` |
| Заказ не найден | `{"detail": "Order not found"}` |
| Невозможно изменить статус | `{"detail": "Cannot change status"}` |
| Сервер не запущен | `Ошибка подключения к серверу` |

## ⚙️ Коды возврата API

| Код | Значение |
|-----|----------|
| 200 | Успешное выполнение |
| 400 | Ошибка валидации / неверный запрос |
| 401 | Не авторизован (токен не предоставлен или неверен) |
| 403 | Доступ запрещён (недостаточно прав) |
| 404 | Объект не найден |
| 422 | Ошибка валидации Pydantic |
| 500 | Внутренняя ошибка сервера |

## Результаты тестирования

<img width="1920" height="860" alt="Снимок экрана (1371)" src="https://github.com/user-attachments/assets/58bbceff-48d1-4ff2-b1b4-a3233c9ec81a" />\


## Заключение

AutoServiceSystem — это пример того, как с помощью FastAPI можно организовать полноценную систему автоматизации автосервиса. Вместо того чтобы писать все с нуля, проект использует готовые, проверенные инструменты:

- FastAPI — быстрый и современный фреймворк для API

- Pydantic — валидация данных

- Uvicorn — ASGI-сервер

- Pytest — тестирование

- Ruff / Black — качество кода

Этот подход:

- Ускоряет разработку — не нужно изобретать велосипед

- Повышает надёжность — автоматическая валидация и документация

- Обеспечивает масштабируемость — легко добавить новые модули

- Дает прозрачность — Swagger документация готова сразу


