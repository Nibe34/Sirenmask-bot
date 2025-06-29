import json
import os

STATE_FILE = "user_state.json"

# Завантаження стану з підтримкою старого формату
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        user_state = json.load(f)
    # 🔄 Міграція зі старого формату: якщо значення — рядок, обгортаємо в словник
    for uid, value in list(user_state.items()):
        if isinstance(value, str):
            user_state[uid] = {"model": value}
    # зберігаємо одразу, якщо була міграція
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_state, f, ensure_ascii=False, indent=2)
else:
    user_state = {}

def save_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_state, f, ensure_ascii=False, indent=2)

def get_user_model(user_id: int) -> str | None:
    return user_state.get(str(user_id), {}).get("model")

def set_user_model(user_id: int, model_name: str):
    uid = str(user_id)
    if uid not in user_state:
        user_state[uid] = {}
    user_state[uid]["model"] = model_name
    save_state()

def get_user_settings(user_id: int) -> dict:
    return user_state.get(str(user_id), {}).get("settings", {})

def set_user_settings(user_id: int, settings: dict):
    uid = str(user_id)
    if uid not in user_state:
        user_state[uid] = {}
    user_state[uid]["settings"] = settings
    save_state()

def reset_user_settings(user_id: int):
    uid = str(user_id)
    if uid in user_state and "settings" in user_state[uid]:
        del user_state[uid]["settings"]
        save_state()
