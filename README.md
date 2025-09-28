# FastAPI + Aiogram + Postgres + Redis

Этот проект состоит из:
- **FastAPI** — backend API
- **Aiogram** — Telegram-бот
- **Postgres** — база данных
- **Redis** — кэш / FSM для бота
- **Ruff** — линтер для проверки кода

---

## 🚀 Установка и запуск

### 1. Клонируем проект
```bash
git clone https://github.com/Solva-technology/solva-tasks-Kilotas.git
cd app

Создаём .env

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres_db:5432/postgres

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=postgres_db


SECRET_KEY="KSEUtdh6od27s5hNBWyoMvpyZI7qQ07fq8eyC6HQx1eI5NY1T9v4Jcp5gc1p56Ra2nwwXKjmS85N5LSj-2py1Q"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

BOT_TOKEN=8078022129:AAHDt3NFMZtvUawb8CQyp14H7CWYfpjg_BA
BOT_SECRET=super-strong-random-secret


REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=ceiPNogfzO4GJ8vd7c1V40zHn0WkSxhP
REDIS_SSL=false

Запуск контейнеров
docker compose up --build


Будут подняты сервисы:

app → FastAPI на http://localhost:8000

bot → Aiogram-бот

postgres → база на порту 5434

redis → Redis на порту 13284


Проверка работы

FastAPI docs: http://localhost:8000/docs
