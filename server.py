import os
import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

# Чтение ключей из переменных окружения
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ДИАГНОСТИКА: выводим в логи Render, видит ли скрипт переменные
print("=== ДИАГНОСТИКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===")
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY получен: {'ДА' if SUPABASE_KEY else 'НЕТ'}")
if SUPABASE_KEY:
    print(f"Длина SUPABASE_KEY: {len(SUPABASE_KEY)} символов")
print("========================================")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Критическая ошибка: Переменные SUPABASE_URL или SUPABASE_KEY не найдены в системе! "
        "Убедись, что они добавлены в панели Render во вкладке Environment."
    )

# Инициализируем клиент Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[CRITICAL] Ошибка при вызове create_client: {e}")
    raise e

app = FastAPI(title="Type-Launcher API")