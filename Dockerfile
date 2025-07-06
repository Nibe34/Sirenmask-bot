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

# rvc_lib
RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git

# Копіюємо залежності
COPY requirements.txt .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Явно копіюємо rvc_lib
COPY rvc_lib ./rvc_lib

# Копіюємо увесь проєкт
COPY . .

# Порт, який слухає додаток
EXPOSE 5000

# Запуск бота
CMD ["python3", "run.py"]
