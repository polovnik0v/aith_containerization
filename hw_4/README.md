# ЛР 4. Развертывание собственного сервиса в Kubernetes

## Описание

Развернут сервис из двух Deployment'ов с кастомным образом:
- **demo-api** — кастомный FastAPI сервис (собран из Dockerfile)
- **redis** — кэш/база данных для demo-api

## Архитектура

### 1. Deployment: `demo-api`
- **Кастомный образ**: `demo-api:latest` (собран из `Dockerfile`)
- **Init контейнер**: `wait-for-redis` — ждет готовности Redis перед запуском основного контейнера
- **Volume**: `emptyDir` для хранения данных приложения (`/app/data`)
- **ConfigMap**: `demo-api-configmap` — несекретные настройки (APP_MESSAGE, REDIS_HOST, REDIS_PORT)
- **Secret**: `demo-api-secret` — пароль для Redis
- **Liveness/Readiness пробы**: HTTP проверка на `/health`
- **Лейблы**: `app: demo-api`, `tier: backend`, `lab: hw4`, `version: v1`

### 2. Deployment: `redis`
- **Образ**: `redis:7-alpine` (публичный)
- **ConfigMap/Secret**: Использует Secret для пароля
- **Liveness/Readiness пробы**: `redis-cli ping`
- **Лейблы**: `app: redis`, `tier: cache`, `lab: hw4`, `component: database`

### 3. Services
- **demo-api-service**: NodePort на порту 30080
- **redis-service**: ClusterIP для внутреннего доступа

## Выполнение требований

✅ **Минимум 2 Deployment**: `demo-api` и `redis`  
✅ **Кастомный образ**: `demo-api` собран из `Dockerfile`  
✅ **Init контейнер**: В `demo-api` есть `wait-for-redis`  
✅ **Volume**: `emptyDir` в `demo-api`  
✅ **ConfigMap и Secret**: Используются в обоих Deployment'ах  
✅ **Service**: `demo-api-service` и `redis-service`  
✅ **Liveness/Readiness пробы**: В обоих Deployment'ах  
✅ **Лейблы**: Дополнительные лейблы помимо обязательных (`tier`, `lab`, `version`, `component`)

## Развертывание

### 1. Сборка кастомного образа в Minikube

```bash
# Убедитесь, что Minikube запущен
minikube status

# Настроить Docker на использование Minikube
eval $(minikube docker-env)

# Собрать образ
cd hw_4
docker build -t demo-api:latest .
```

### 2. Применение манифестов

```bash
# В правильном порядке (зависимости сначала)
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f redis-service.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f demo-api-service.yaml
kubectl apply -f demo-api-deployment.yaml
```

### 3. Проверка статуса

```bash
# Проверить поды
kubectl get pods -l lab=hw4

# Проверить сервисы
kubectl get services -l lab=hw4

# Проверить логи demo-api
kubectl logs -l app=demo-api

# Проверить логи redis
kubectl logs -l app=redis
```

### 4. Доступ к сервису

Для доступа к сервису используем URL, который возвращает Minikube:

```bash
# Получить URL через Minikube (локально)
minikube service demo-api-service --url
# Пример вывода: http://127.0.0.1:57544
```
### Swagger UI (удобное тестирование эндпоинтов)
```bash
<YOUR_MINIKUBE_URL>/docs
```
### Тестирование API
```bash
# Главная страница
curl <YOUR_MINIKUBE_URL>/

# Health check
curl <YOUR_MINIKUBE_URL>/health

# Сохранить значение в Redis
curl -X POST "<YOUR_MINIKUBE_URL>/redis/test-key?value=test-value"

# Получить значение из Redis
curl <YOUR_MINIKUBE_URL>/redis/test-key

# Статистика Redis
curl <YOUR_MINIKUBE_URL>/stats
```

## Очистка

```bash
kubectl delete -f demo-api-deployment.yaml
kubectl delete -f demo-api-service.yaml
kubectl delete -f redis-deployment.yaml
kubectl delete -f redis-service.yaml
kubectl delete -f configmap.yaml
kubectl delete -f secret.yaml
```

Или все сразу:
```bash
kubectl delete -f .
```

