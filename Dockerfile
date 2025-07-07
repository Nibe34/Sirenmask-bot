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
RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git rvc_lib


# Копіюємо залежності
COPY requirements.txt .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь проєкт
COPY . .

# Додаємо rvc_lib до PYTHONPATH
ENV PYTHONPATH="/app"

# Порт, який слухає додаток
EXPOSE 5000

# Запуск бота
CMD ["python3", "run.py"]
