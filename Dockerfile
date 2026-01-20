FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# базовые пакеты, нужные для сборки некоторых зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

# uv как менеджер зависимостей
RUN pip install --no-cache-dir uv

# сначала lock-файлы (чтобы работал docker cache)
COPY pyproject.toml uv.lock ./

# ставим зависимости строго по lock
RUN uv sync --frozen --no-dev

# копируем исходники
COPY . .

# создаем непривилегированного пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# ВАЖНО: правильный модуль (у тебя FastAPI app в application/main.py)
CMD ["uv", "run", "uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]
