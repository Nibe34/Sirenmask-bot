FROM python:3.10-slim

# ffmpeg і системні залежності
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    git \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Копіюємо залежності
COPY requirements.txt .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь проєкт
COPY . .

# Порт, який слухає додаток
EXPOSE 5000

# Запуск бота
CMD ["python3", "run.py"]
