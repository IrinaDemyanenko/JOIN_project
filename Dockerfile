# Используем официальный образ Python (можете выбрать нужную версию)
FROM python:3.11-slim

# Отключаем запись pyc-файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создать директорию вашего приложения и сразу делаем её рабочей
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Копируем весь проект в контейнер
#COPY . /app/
# Скопировать содержимое директории /join/ c локального компьютера
# в директорию /app.
COPY join/ /app/


# Собираем статические файлы (для продакшена)
#RUN python manage.py collectstatic --noinput

# Применяем миграции (опционально можно запускать через docker-compose command)
# RUN python manage.py migrate

# Запускаем сервер Gunicorn при старте контейнера.(в продакшене не рекомендуется использовать runserver)
CMD ["gunicorn", "join.wsgi:application", "--bind", "0.0.0.0:8000"]
