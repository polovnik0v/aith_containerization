# ЛР 2. Docker Compose на примере Apache Airflow

## Описание docker-compose.yml

Проект состоит из трех сервисов, работающих в единой сети `airflow-lab2-network`:

### 1. `airflow-init` (Init сервис)
- **Назначение**: Одноразовая инициализация базы данных Airflow
- **Контейнер**: `airflow-init-container`
- **Команда**: Инициализирует БД и создает административного пользователя
- **Restart**: `no`
- **Volumes**: 
  - `airflow-db-volume` - для хранения SQLite БД
  - `./dags` - монтирование DAG файлов
  - `./logs` - логи Airflow

### 2. `airflow-webserver` (App сервис)
- **Назначение**: Веб-интерфейс Airflow
- **Контейнер**: `airflow-webserver-container`
- **Образ**: `airflow-lab2:latest` (собирается из `Dockerfile.good`)
- **Порт**: `8080` (через `AIRFLOW_WEBSERVER_PORT` из `.env`)
- **Command**: `airflow webserver`
- **Depends_on**: `airflow-init` (condition: service_completed_successfully)
- **Healthcheck**: Проверяет доступность через curl
- **Volumes**: `airflow-db-volume`, `./dags`, `./logs`

### 3. `airflow-scheduler` (App сервис)
- **Назначение**: Планировщик задач Airflow
- **Контейнер**: `airflow-scheduler-container`
- **Образ**: `airflow-lab2:latest`
- **Command**: `airflow scheduler`
- **Depends_on**: 
  - `airflow-init` (condition: service_completed_successfully)
  - `airflow-webserver` (condition: service_healthy)
- **Healthcheck**: Проверяет наличие процесса scheduler
- **Volumes**: `airflow-db-volume`, `./dags`, `./logs`

## Особенности реализации

✅ Автоматическая сборка образа из `Dockerfile.good`  
✅ Жесткое именование контейнеров  
✅ `depends_on` с условиями  
✅ Volumes (именованные тома и bind mounts)  
✅ Прокидывание порта наружу (8080)  
✅ `command` для каждого сервиса  
✅ `healthcheck` для webserver и scheduler  
✅ Переменные окружения в `.env` файле  
✅ Явная сеть `airflow-lab2-network`

## Запуск

```bash
docker-compose up -d
```

Airflow доступен по адресу: http://localhost:8080  
Логин: `admin` / Пароль: `admin`

## Остановка

```bash
docker-compose down
```

Полная очистка с удалением volumes:
```bash
docker-compose down -v
```

## Ответы на вопросы

### 1. Можно ли ограничивать ресурсы (память или CPU) для сервисов в docker-compose.yml?

**Да, можно.** В docker-compose.yml можно ограничивать ресурсы через секцию `deploy.resources`:

```yaml
services:
  airflow-webserver:
    # ... другие настройки
    deploy:
      resources:
        limits:
          cpus: '1.0'      # Максимум 1 CPU
          memory: 512M      # Максимум 512 МБ памяти
        reservations:
          cpus: '0.5'      # Минимум 0.5 CPU
          memory: 256M     # Минимум 256 МБ памяти
```

**Важно:** Секция `deploy` работает только в режиме Swarm (docker stack deploy). Для обычного `docker-compose up` нужно использовать:

```yaml
services:
  airflow-webserver:
    # ... другие настройки
    mem_limit: 512m        # Лимит памяти
    cpus: 1.0              # Лимит CPU
```

Или через `mem_limit` и `cpu_count` (устаревший способ, но работает).

**Зачем ограничивать ресурсы:**
- Предотвращение перегрузки хоста
- Гарантия доступности ресурсов для других сервисов
- Контроль потребления ресурсов

### 2. Как можно запустить только определенный сервис из docker-compose.yml?

**Способ 1:** Указать имя сервиса при запуске:

```bash
docker-compose up -d airflow-webserver
```

Это запустит только `airflow-webserver` и все его зависимости (согласно `depends_on`).

**Способ 2:** Использовать `--no-deps` для запуска без зависимостей:

```bash
docker-compose up -d --no-deps airflow-scheduler
```

Это запустит только `airflow-scheduler`, игнорируя зависимости.
