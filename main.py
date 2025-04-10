# project/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, init_models
from app.api.base_router import base_router
import os

app = FastAPI(title="Website Parser API")

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base_router)

@app.on_event("startup")
async def startup_event():
    # Создаем директорию для данных, если ее нет
    from app.core.config import Settings
    os.makedirs(Settings.DATA_DIR, exist_ok=True)
    # Инициализируем базу данных
    await init_models()