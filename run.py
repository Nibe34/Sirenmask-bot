from telegram.ext import ApplicationBuilder
from sirenmask.bot.handlers import register_handlers
from sirenmask.config import TELEGRAM_TOKEN

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()
