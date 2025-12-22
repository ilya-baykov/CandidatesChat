# Используем официальный Python
FROM python:3.11-slim

# ------------------------------
# System settings
# ------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ------------------------------
# Workdir
# ------------------------------
WORKDIR /app

# ------------------------------
# System dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential \
    curl \
    ca-certificates \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Устанавливаем Poetry
# ------------------------------
RUN pip install --no-cache-dir poetry

# ------------------------------
# Копируем файлы проекта
# ------------------------------
# Сначала копируем только файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости (без создания виртуального окружения)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# ------------------------------
# Копируем остальной код
# ------------------------------
COPY . .

# ------------------------------
# Создаем необходимые директории
# ------------------------------
RUN mkdir -p web/staticfiles web/media

# ------------------------------
# Рабочая директория для web
# ------------------------------
WORKDIR /app/web

# ------------------------------
# Default command
# ------------------------------
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]