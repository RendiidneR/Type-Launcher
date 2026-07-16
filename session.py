import os
import json

# Папка для настроек нашего лаунчера в AppData (для Windows)
LAUNCHER_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), '.my_launcher')
CONFIG_FILE = os.path.join(LAUNCHER_DIR, 'session.json')


def save_session(username: str, uuid: str, token: str):
    """Сохраняет данные сессии в файл"""
    if not os.path.exists(LAUNCHER_DIR):
        os.makedirs(LAUNCHER_DIR)

    data = {
        "username": username,
        "uuid": uuid,
        "accessToken": token
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_session() -> dict:
    """Загружает сохраненную сессию, если она есть"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def clear_session():
    """Удаляет сессию при выходе из аккаунта"""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)