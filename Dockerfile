# Dockerfile

# --- Этап 1: Сборка фронтенда ---
FROM node:20-alpine as frontend-builder

WORKDIR /app

# Копируем файлы, необходимые для установки зависимостей
COPY package.json package-lock.json .env ./

# Устанавливаем npm зависимости
RUN npm install

# Копируем остальные файлы фронтенда
COPY frontend/ ./frontend/
COPY public/ ./public/
COPY tailwind.config.js postcss.config.js tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts ./

# Собираем фронтенд
RUN npm run build


# --- Этап 2: Сборка Python-приложения ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN addgroup --system app && adduser --system --group app

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код Django-приложения
COPY . .

# Копируем собранный фронтенд из первого этапа
COPY --from=frontend-builder /app/assets ./assets

# Устанавливаем права на скрипт запуска
COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/manage.py

RUN chown -R app:app /app

USER app

# Открываем порт, на котором будет работать Gunicorn
EXPOSE 8000

# Запускаем приложение через скрипт
ENTRYPOINT ["/entrypoint.sh"]