import json
import os

STATE_FILE = "user_state.json"

# Завантажити стан
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        user_voices = json.load(f)
else:
    user_voices = {}

def get_user_model(user_id: int) -> str | None:
    return user_voices.get(str(user_id))

def set_user_model(user_id: int, model_name: str):
    user_voices[str(user_id)] = model_name
    save_state()

def save_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_voices, f, ensure_ascii=False, indent=2)
