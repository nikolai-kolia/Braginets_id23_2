# project/app/core/config.py
import os
from pathlib import Path

class Settings():
    # URL для подключения к базе данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    # URL для подключения к Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Секретный ключ для JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
    # Алгоритм шифрования JWT
    ALGORITHM = "HS256"
    # Время жизни access токена в минутах
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    # Директория для хранения графов
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))