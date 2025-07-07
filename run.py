from telegram.ext import ApplicationBuilder
from sirenmask.bot.handlers import register_handlers
from sirenmask.config import TELEGRAM_TOKEN, TEMP_PATH
from sirenmask.setup.download_models import download_all
from pathlib import Path

def main():
    print("🔧 Запуск main()")
    Path(TEMP_PATH).mkdir(parents=True, exist_ok=True)
    print("📁 TEMP_PATH створено:", TEMP_PATH)

    print("⬇️ Завантаження моделей...")
    download_all()
    print("✅ Моделі завантажено")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    print("🤖 Telegram бот створено")

    register_handlers(app)
    print("📦 Хендлери зареєстровано")

    print("🚀 Бот стартує")
    app.run_polling()

if __name__ == "__main__":
    main()
