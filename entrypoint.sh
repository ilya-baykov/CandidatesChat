#!/bin/bash
set -euo pipefail

echo "Запуск Django entrypoint..."

# Все команды manage.py указываем с полным путём
echo "Применяем миграции..."
python /app/web/manage.py migrate --noinput

# Суперюзер (если переменные заданы)
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && \
   [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && \
   [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "Создаём/обновляем суперюзера..."
  python /app/web/manage.py createsuperuser --noinput || true
else
  echo "Переменные суперюзера не заданы → пропускаем создание"
fi

# Если нужно collectstatic (в dev можно закомментировать или оставить)
# python /app/web/manage.py collectstatic --noinput --clear || true

echo "Запускаем приложение..."
exec "$@"