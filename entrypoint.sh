#!/bin/bash
set -e

# Инициализируем БД
airflow db init

# Создаём пользователя, если не существует
airflow users create \
    --username "${AIRFLOW_USERNAME:-admin}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password "${AIRFLOW_PASSWORD:-admin}" || true

airflow scheduler &

# Запускаем Airflow Webserver
exec airflow webserver
