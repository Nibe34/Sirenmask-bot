FROM python:3.10-slim

# Залежності
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    git \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Клонуємо RVC-репозиторій і додаємо __init__.py
RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git rvc_lib \
 && touch rvc_lib/__init__.py \
 && touch rvc_lib/infer/__init__.py \
 && touch rvc_lib/infer/modules/__init__.py \
 && touch rvc_lib/infer/modules/vc/__init__.py

# Копіюємо локальний проєкт
COPY . .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Додаємо rvc_lib до PYTHONPATH
ENV PYTHONPATH="/app:/app/rvc_lib"

# Порт
EXPOSE 5000

# Запуск
CMD ["python3", "run.py"]
