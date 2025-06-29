from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from .whitelist import is_authorized
from .voice_utils import process_voice
from sirenmask.rvc_engine.model_manager import get_available_models
from sirenmask.bot.state import get_user_model, set_user_model, set_user_settings
from sirenmask.bot.state import get_user_settings, reset_user_settings

default_settings = {
    "f0_up_key": 2,
    "index_rate": 0.8,
    "filter_radius": 7,
    "resample_sr": 48000,
    "rms_mix_rate": 0.25,
    "protect": 0.5
}


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
    settings = get_user_settings(user_id)
    output_path = await process_voice(voice_file, model, settings)
    await update.message.reply_voice(voice=open(output_path, "rb"))


def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("select_voice", select_voice))
    app.add_handler(CallbackQueryHandler(set_voice))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CommandHandler("voice_settings", voice_settings))


async def voice_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return

    args = context.args
    if not args:
        # показати поточні
        current = get_user_settings(user_id) or default_settings
        text = "🎛 Поточні параметри:\n" + "\n".join(
            f"{k}: {v}" for k, v in current.items()
        )
        text += "\n\nЩоб змінити: /voice_settings f0_up_key=3"
        text += "\nЩоб скинути до стандартних: /voice_settings reset"
        await update.message.reply_text(text)
        return

    if args[0] == "reset":
        reset_user_settings(user_id)
        await update.message.reply_text("✅ Параметри скинуто до стандартних.")
        return

    # зміна параметра
    try:
        key, value = args[0].split("=")
        if key not in default_settings:
            await update.message.reply_text("⛔ Невідомий параметр.")
            return
        value = type(default_settings[key])(value)
        current = get_user_settings(user_id) or default_settings.copy()
        current[key] = value
        set_user_settings(user_id, current)
        await update.message.reply_text(f"✅ Параметр {key} встановлено в {value}")
    except Exception as e:
        await update.message.reply_text("⚠️ Помилка зміни параметра.")