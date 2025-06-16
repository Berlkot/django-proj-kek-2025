# nginx/Dockerfile
FROM nginx:1.25-alpine

# Удаляем стандартную конфигурацию Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем нашу конфигурацию в образ.
# Docker сам выставит корректные права доступа.
COPY nginx.conf /etc/nginx/conf.d/default.conf