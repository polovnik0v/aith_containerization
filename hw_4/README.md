# ЛР 4. Развертывание собственного сервиса в Kubernetes
- Запуск minicube
<img width="962" height="468" alt="image" src="https://github.com/user-attachments/assets/ddfcff40-2a47-4e4d-9add-a77a206aa8e2" />

- Проверка

<img width="841" height="309" alt="image" src="https://github.com/user-attachments/assets/ad456e5a-f773-47f6-96aa-9a8c9a4abd5c" />
<img width="780" height="135" alt="image" src="https://github.com/user-attachments/assets/c83ca088-2e71-44aa-bdfe-84da90e68932" />

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
- Пример результатов
<img width="910" height="368" alt="image" src="https://github.com/user-attachments/assets/e92d03de-cb62-43a2-8080-c435ae8a89e1" />
<img width="901" height="198" alt="image" src="https://github.com/user-attachments/assets/252ac48b-a05e-4ea7-8410-23ff90cf458a" />

- Ручки в сваггере
<img width="1526" height="336" alt="image" src="https://github.com/user-attachments/assets/98a6914e-7b23-4ff1-9163-595faa565bd3" />

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

