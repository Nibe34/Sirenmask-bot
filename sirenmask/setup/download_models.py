import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Список моделей або файлів для завантаження
FILES_TO_DOWNLOAD = {
    "assets/hubert/hubert_base.pt": os.getenv("HUBERT_URL"),
    "models/QOP/QOP.pth": os.getenv("VOICE_MODEL_QOP_PTH"),
    "models/QOP/QOP.index.pkl": os.getenv("VOICE_MODEL_QOP_INDEX"),
}

def download_file(url, path):
    path = Path(path)
    if path.exists():
        print(f"[✓] {path} вже існує")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[⬇️] Завантаження: {url}")
    r = requests.get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"[✅] Завантажено: {path}")

def download_all():
    for path, url in FILES_TO_DOWNLOAD.items():
        if not url:
            print(f"[⚠️] Пропущено: {path} — немає URL")
            continue
        download_file(url, path)

if __name__ == "__main__":
    download_all()
