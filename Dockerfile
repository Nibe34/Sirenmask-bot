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

# Клонуємо RVC репозиторій одразу сюди
RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git rvc_lib

# Копіюємо локальні файли (після клону!)
COPY . .

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Додаємо PYTHONPATH
ENV PYTHONPATH="/app"

# Порт
EXPOSE 5000

# Запуск
CMD ["python3", "run.py"]
