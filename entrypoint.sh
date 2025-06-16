#!/bin/sh

# Выход при любой ошибке
set -e

echo "Running entrypoint script..."

# Собираем все статические файлы (включая собранный Vite бандл) в /staticfiles
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Применяем миграции базы данных
echo "Applying database migrations..."
python manage.py migrate

# Запускаем Gunicorn WSGI сервер
# Он будет слушать на порту 8000 и обслуживать запросы
echo "Starting Gunicorn..."
exec gunicorn animals.wsgi:application --bind 0.0.0.0:8000 --workers 3