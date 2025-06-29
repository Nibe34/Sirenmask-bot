from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from .whitelist import is_authorized
from .voice_utils import process_voice
from sirenmask.rvc_engine.model_manager import get_available_models
from sirenmask.bot.state import get_user_model, set_user_model


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 Доступ обмежено.")
        return
    await update.message.reply_text("Привіт! Обери голос через /select_voice, потім надішли voice.")


async def select_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    models = get_available_models()
    if not models:
        await update.message.reply_text("⚠️ Немає доступних голосів.")
        return

    keyboard = [
        [InlineKeyboardButton(model_name, callback_data=model_name)]
        for model_name in models
    ]

    await update.message.reply_text(
        "🎙️ Обери голос:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def set_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    model_name = query.data

    set_user_model(user_id, model_name)  # ✅ збереження в файл

    await query.answer()
    await query.edit_message_text(f"✅ Голос встановлено: {model_name}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return

    model = get_user_model(user_id)  # ✅ отримуємо збережену модель
    if not model:
        await update.message.reply_text("Спочатку оберіть голос через /select_voice")
        return

    voice_file = await update.message.voice.get_file()
    output_path = await process_voice(voice_file, model)
    await update.message.reply_voice(voice=open(output_path, "rb"))


def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("select_voice", select_voice))
    app.add_handler(CallbackQueryHandler(set_voice))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
