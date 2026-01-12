# Выбираем базоый образ
FROM python:3.11.14-slim

# Создаем отдельного пользователя для работы внутри контейнера
RUN groupadd -r groupdocker && useradd -r -g groupdocker userdocker

# Переменные окружения по умолчанию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app


# Копируем файл с зависимостями в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt


# Копируем исходный код приложения в контейнер ( предполагается, что код находится в папке web, можно просто COPY . . )
# Не забывать про файл .dockerignore чтобы не копировать лишние файлы
COPY web/ ./web/


RUN mkdir -p web/staticfiles web/media

EXPOSE 8000

USER userdocker

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]