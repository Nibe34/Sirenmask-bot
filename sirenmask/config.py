import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split(",")))
VOICE_MODELS_PATH = os.getenv("VOICE_MODELS_PATH", "models")
TEMP_PATH = "temp/"
