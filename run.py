from telegram.ext import ApplicationBuilder
from sirenmask.bot.handlers import register_handlers
from sirenmask.config import TELEGRAM_TOKEN, TEMP_PATH
from sirenmask.setup.download_models import download_all
from pathlib import Path

def main():
    Path(TEMP_PATH).mkdir(parents=True, exist_ok=True)

    download_all()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()
