import os
import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

# Чтение ключей из переменных окружения (для безопасности на Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[WARNING] SUPABASE_URL или SUPABASE_KEY не заданы в переменных окружения!")

# Инициализируем клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Type-Launcher API")


# Схема данных, которую мы ждём от Flet-клиента
class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    username: str  # Здесь может быть email
    password: str


# Функция хэширования пароля
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# Функция проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.post("/api/register")
def register_user(data: RegisterSchema):
    try:
        # 1. Хэшируем пароль для безопасности
        hashed_pw = hash_password(data.password)

        # 2. Пытаемся вставить данные в Supabase таблицу profiles
        new_profile = {
            "username": data.username,
            "email": data.email,
            "password_hash": hashed_pw
        }

        response = supabase.table("profiles").insert(new_profile).execute()
        return {"status": "success", "message": "Пользователь успешно зарегистрирован!"}

    except Exception as e:
        # Выводим реальную ошибку в логи Render
        print(f"[ERROR] Ошибка регистрации: {e}")
        # Проверяем на дубликаты
        err_msg = str(e)
        if "unique" in err_msg or "already exists" in err_msg:
            raise HTTPException(status_code=400, detail="Этот никнейм или email уже зарегистрированы.")
        raise HTTPException(status_code=400, detail="Ошибка при записи в базу данных.")


@app.post("/api/login")
def login_user(data: LoginSchema):
    try:
        # Ищем пользователя по email или по username
        response = supabase.table("profiles") \
            .select("id, username, password_hash") \
            .or_(f"email.eq.{data.username},username.eq.{data.username}") \
            .execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Неверный логин или пароль.")

        user = response.data[0]

        # Проверяем хэш пароля
        if not verify_password(data.password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Неверный логин или пароль.")

        # Генерируем фейковый accessToken для примера (в будущем можно делать JWT)
        import uuid
        new_token = str(uuid.uuid4())

        # Записываем токен сессии обратно в базу, чтобы лаунчер мог авторизоваться
        supabase.table("profiles").update({"access_token": new_token}).eq("id", user["id"]).execute()

        return {
            "username": user["username"],
            "uuid": user["id"],
            "accessToken": new_token
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ERROR] Ошибка авторизации: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")


if __name__ == "__main__":
    import uvicorn

    # Локальный запуск (Render проигнорирует этот блок и запустит через Procfile)
    uvicorn.run(app, host="127.0.0.1", port=8000)