# Ozon Posting Processor — Ozon Webhook Service

## Назначение проекта

**Ozon Posting Processor** — backend‑сервис на Python, предназначенный для приёма webhook‑уведомлений от **Ozon Seller API**, получения расширенных данных о заказах через API Ozon, сохранения их в PostgreSQL и дальнейшего использования (аналитика, синхронизация, уведомления и т.п.).

Сервис спроектирован как **production‑ready webhook‑consumer**:

* устойчив к повторам уведомлений;
* строго следует контракту ответов Ozon;
* разворачивается через Docker Compose;
* изолирует HTTP‑слой от бизнес‑логики.

---

## Архитектурная идея

Проект следует принципу:

> **Webhook ≠ бизнес‑логика**

HTTP‑endpoint отвечает только за:

* приём уведомления;
* валидацию формы данных;
* возврат корректного HTTP‑ответа Ozon.

Вся остальная логика вынесена в сервисный слой.

### Общий поток данных

1. Ozon отправляет webhook (POST)
2. FastAPI endpoint принимает JSON
3. Payload валидируется (Pydantic DTO)
4. По `posting_number` выполняется запрос в Ozon API
5. Данные трансформируются в доменные модели
6. Записываются в PostgreSQL
7. Endpoint возвращает ответ по контракту Ozon

---

## Технологический стек

* **Python 3.13**
* **FastAPI** (ASGI)
* **Pydantic v2** — DTO и валидация
* **SQLAlchemy (async)** — ORM
* **asyncpg** — PostgreSQL драйвер
* **Alembic** — миграции БД
* **PostgreSQL 16**
* **Docker / Docker Compose**
* **uv** — менеджер зависимостей

---

## Структура проекта

```
.
├── application/
│   ├── main.py                # Точка входа FastAPI
│   ├── config.py              # Конфигурация (env)
│   ├── db.py                  # Async SQLAlchemy engine/session
│   └── orders/
│       ├── router.py          # Webhook endpoints
│       ├── schemas/           # Pydantic DTO
│       ├── services/
│       │   ├── use_case.py    # Бизнес‑сценарии
│       │   ├── manage_repo.py
│       │   └── manage_transformation.py
│       ├── integrations/
│       │   └── market/        # Ozon API client
│       └── repo/              # Репозитории БД
│
├── migrations/                # Alembic migrations
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Контракт webhook (Ozon)

### Endpoint

```
POST /webhook/notification
```

### Успешный ответ

```json
{
  "result": true
}
```

HTTP status: **200**

### Ответ при ошибке

```json
{
  "error": {
    "code": "ERROR_UNKNOWN",
    "message": "Описание ошибки",
    "details": null
  }
}
```

HTTP status: **4xx / 5xx**

Коды ошибок соответствуют документации Ozon:

* `ERROR_PARAMETER_VALUE_MISSED`
* `ERROR_REQUEST_DUPLICATED`
* `ERROR_UNKNOWN`

---

## Переменные окружения

Все конфигурации задаются через environment variables.

### Обязательные

```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname
CLIENT_ID=***        # Ozon Seller API client_id
API_KEY=***          # Ozon Seller API key
```

### Для Docker Compose (пример)

```env
POSTGRES_DB=ozon_1
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
DATABASE_URL=postgresql+asyncpg://postgres:1234@postgres:5432/ozon_1
```

---

## Локальный запуск (Docker)

### Требования

* Docker
* Docker Compose v2

### Запуск

```bash
docker compose up -d --build
```

Проверка состояния:

```bash
docker compose ps
docker compose logs -f app
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Миграции базы данных

Миграции применяются автоматически сервисом `migrate` при запуске `docker compose`.

Ручной запуск:

```bash
docker compose run --rm migrate
```

---

## Production‑развёртывание

Рекомендуемая схема:

* VPS (Ubuntu 22.04+)
* Docker Compose
* Reverse proxy (Caddy или Nginx)
* HTTPS (Let’s Encrypt)
* Закрытый порт 8000 (доступ только через proxy)


## Нефункциональные гарантии

* Идемпотентность по `posting_number`
* Отсутствие бизнес‑логики в HTTP‑слое
* Явные коды ошибок
* Асинхронная работа с БД
* Готовность к масштабированию
* Архитектурные паттерны, гарантирующие надежность транзакций


---

## Ограничения и допущения

* Сервис предполагает, что Ozon может присылать повторные webhook‑уведомления
* Потеря уведомлений предотвращается корректным HTTP‑контрактом
* Реализация очередей/streaming не входит в текущую версию

---

## Roadmap (планируемо)

* Inbox‑таблица для webhook‑событий
* Асинхронный воркер обработки
* Метрики (Prometheus)
* Structured logging
* Авторизация webhook (если будет поддержана Ozon)
* Добавлении работы с гугл таблицами для отчетности

---

## Автор

Проект разрабатывается как production‑ориентированный backend‑сервис для интеграции с маркетплейсом Ozon.
