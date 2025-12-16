from fastapi import FastAPI
import os
import redis
import json
from datetime import datetime

app = FastAPI()

# Получаем конфигурацию из переменных окружения
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
APP_MESSAGE = os.getenv("APP_MESSAGE", "Hello from Demo API!")

# Подключение к Redis
try:
    if REDIS_PASSWORD:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    else:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
    redis_client.ping()
except Exception as e:
    redis_client = None
    print(f"Redis connection failed: {e}")


@app.get("/")
def read_root():
    """Главная страница"""
    return {
        "message": APP_MESSAGE,
        "timestamp": datetime.now().isoformat(),
        "service": "demo-api"
    }


@app.get("/health")
def health_check():
    """Health check endpoint для liveness/readiness проб"""
    redis_status = "connected" if redis_client else "disconnected"
    try:
        if redis_client:
            redis_client.ping()
    except:
        redis_status = "error"
    
    return {
        "status": "healthy" if redis_status == "connected" else "degraded",
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/redis/{key}")
def get_redis_value(key: str):
    """Получить значение из Redis"""
    if not redis_client:
        return {"error": "Redis not available"}
    try:
        value = redis_client.get(key)
        return {"key": key, "value": value}
    except Exception as e:
        return {"error": str(e)}


@app.post("/redis/{key}")
def set_redis_value(key: str, value: str):
    """Установить значение в Redis"""
    if not redis_client:
        return {"error": "Redis not available"}
    try:
        redis_client.set(key, value)
        return {"key": key, "value": value, "status": "saved"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/stats")
def get_stats():
    """Получить статистику"""
    if not redis_client:
        return {"error": "Redis not available"}
    try:
        info = redis_client.info()
        return {
            "redis_keys": redis_client.dbsize(),
            "redis_memory": info.get("used_memory_human", "N/A"),
            "redis_connected_clients": info.get("connected_clients", 0)
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

