FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt /app/requirements.txt

# Установка зависимостей
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем приложение
COPY app.py /app/app.py

# Создаем директорию для данных
RUN mkdir -p /app/data && chmod 755 /app/data

# Запуск приложения
CMD ["python", "app.py"]

