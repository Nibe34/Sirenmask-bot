from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from .whitelist import is_authorized
from .voice_utils import process_voice
from sirenmask.rvc_engine.model_manager import get_available_models
from sirenmask.bot.state import get_user_model, set_user_model, set_user_settings, get_user_menu, set_user_menu
from sirenmask.bot.state import get_user_settings, reset_user_settings
from telegram.ext import filters
from telegram import ReplyKeyboardMarkup, KeyboardButton

"""
default_settings = {
    "f0_up_key": 2,
    "index_rate": 0.8,
    "filter_radius": 7,
    "resample_sr": 48000,
    "rms_mix_rate": 0.25,
    "protect": 0.5
}
"""

default_settings = {
    "f0_up_key": 2,
    "index_rate": 0.8,
    "filter_radius": 7,
    "rms_mix_rate": 0.25,
    "protect": 0.5
}

PARAM_OPTIONS = {
    "f0_up_key": [-12, -6, -3, 0, 3, 6, 12],
    "index_rate": [0.0, 0.25, 0.5, 0.8, 1.0],
    "filter_radius": [0, 3, 7],
    "rms_mix_rate": [0.0, 0.25, 0.5, 0.75, 1.0],
    "protect": [0.0, 0.33, 0.5, 0.7, 1.0],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 Доступ обмежено.")
        return

    set_user_menu(update.effective_user.id, "main")
    await update.message.reply_text("Привіт! Обери дію через меню нижче.", reply_markup=get_main_keyboard())



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

def format_settings_text(settings):
    return "🌛 Поточні параметри:\n" + "\n".join(
        f"{k}: {settings.get(k, default_settings[k])}" for k in default_settings
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


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 Доступ обмежено.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎙 Обрати голос", callback_data="menu_select_voice")],
        [InlineKeyboardButton("🎛 Налаштування", callback_data="menu_settings")],
        [InlineKeyboardButton("🔄 Скинути параметри", callback_data="menu_reset_settings")],
    ])

    await update.message.reply_text("Меню:", reply_markup=keyboard)

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not is_authorized(user_id):
        await query.answer("🚫 Доступ обмежено", show_alert=True)
        return

    data = query.data

    if data == "menu_select_voice":
        await query.answer()
        await select_voice(update, context)
    elif data == "menu_settings":
        await query.answer()
        current = get_user_settings(user_id) or default_settings
        text = "🎛 Поточні параметри:\n" + "\n".join(
            f"{k}: {v}" for k, v in current.items()
        )
        await query.edit_message_text(text)
    elif data == "menu_reset_settings":
        reset_user_settings(user_id)
        await query.answer("✅ Скинуто")
        await query.edit_message_text("✅ Параметри скинуто до стандартних.")
    else:
        await query.answer("❓ Невідомий вибір")


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🎙 Обрати голос")],
            [KeyboardButton("🎛 Налаштування"), KeyboardButton("🔄 Скинути параметри")],
        ],
        resize_keyboard=True,  # адаптує під екран
        one_time_keyboard=False
    )

def get_settings_description_text():
    return (
        "📘 *Пояснення параметрів:*\n\n"
        "*f0_up_key* — транспозиція голосу (в півтонах).\n"
        "   Напр.: `+12` — вищий голос, `-12` — нижчий.\n\n"
        "*index_rate* — наскільки сильно враховується індексна модель (0.0–1.0).\n"
        "   Вищі значення = більше схожості з оригінальним голосом.\n\n"
        "*filter_radius* — ступінь згладжування f0 (0 = вимкнено, 3–7 = більше згладжування).\n\n"
        "*rms_mix_rate* — міксинг гучності оригіналу (0.0–1.0).\n"
        "   1.0 — зберігати гучність оригіналу повністю, 0.0 — ігнорувати.\n\n"
        "*protect* — наскільки сильно захищати нестабільні частоти (0.0–1.0).\n"
        "   Вищі значення = менше спотворень у 'шепітних' або 'повітряних' звуках.\n"
    )

def get_settings_main_keyboard():
    from sirenmask.bot.handlers import default_settings

    keys = list(default_settings.keys())
    keyboard = []

    for i in range(0, len(keys), 2):
        row = [KeyboardButton(keys[i])]
        if i + 1 < len(keys):
            row.append(KeyboardButton(keys[i + 1]))
        keyboard.append(row)

    keyboard.append([KeyboardButton("🔄 Скинути параметри")])
    keyboard.append([KeyboardButton("ℹ️ Пояснення параметрів")])
    keyboard.append([KeyboardButton("🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_parameter_values_keyboard(param_name):
    from sirenmask.bot.handlers import PARAM_OPTIONS
    options = PARAM_OPTIONS.get(param_name, [])

    keyboard = []

    for i in range(0, len(options), 2):
        row = []
        row.append(KeyboardButton(str(options[i])))
        if i + 1 < len(options):
            row.append(KeyboardButton(str(options[i + 1])))
        keyboard.append(row)

    keyboard.append([
        KeyboardButton("➖ Зменшити"),
        KeyboardButton("➕ Збільшити")
    ])

    keyboard.append([KeyboardButton("🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sirenmask.bot.handlers import default_settings, PARAM_OPTIONS
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return

    text = update.message.text.strip()
    menu = get_user_menu(user_id)
    current_settings = get_user_settings(user_id) or default_settings.copy()

    def format_settings(settings):
        return "🎛 Поточні параметри:\n" + "\n".join(f"{k}: {v}" for k, v in settings.items())

    # --- MAIN MENU ---
    if menu == "main":
        if text == "🎙 Обрати голос":
            set_user_menu(user_id, "voice_select")
            await update.message.reply_text("🎙 Обери голос:", reply_markup=get_voice_select_keyboard())
        elif text == "🎛 Налаштування":
            set_user_menu(user_id, "settings_main")
            await update.message.reply_text(format_settings(current_settings))
            await update.message.reply_text("⚙️ Обери параметр для зміни:", reply_markup=get_settings_main_keyboard())
        elif text == "🔄 Скинути параметри":
            reset_user_settings(user_id)
            await update.message.reply_text("✅ Параметри скинуто до стандартних.", reply_markup=get_main_keyboard())

    # --- VOICE SELECTION ---
    elif menu == "voice_select":
        if text == "🔙 Назад":
            set_user_menu(user_id, "main")
            await update.message.reply_text("↩️ Назад до головного меню", reply_markup=get_main_keyboard())
        else:
            from sirenmask.rvc_engine.model_manager import get_available_models
            if text in get_available_models():
                set_user_model(user_id, text)
                set_user_menu(user_id, "main")
                await update.message.reply_text(f"✅ Голос встановлено: {text}", reply_markup=get_main_keyboard())
            else:
                await update.message.reply_text("⚠️ Невідомий голос.")

    # --- SETTINGS MENU ---
    elif menu == "settings_main":
        if text == "🔙 Назад":
            set_user_menu(user_id, "main")
            await update.message.reply_text("↩️ Назад до головного меню", reply_markup=get_main_keyboard())

        elif text == "🔄 Скинути параметри":
            reset_user_settings(user_id)
            current_settings = get_user_settings(user_id) or default_settings.copy()
            await update.message.reply_text("✅ Параметри скинуто до стандартних.")
            await update.message.reply_text(format_settings(current_settings), reply_markup=get_settings_main_keyboard())

        elif text in default_settings:
            set_user_menu(user_id, f"settings_param_{text}")
            await update.message.reply_text(format_settings(current_settings))
            await update.message.reply_text(
                f"🔧 Обери нове значення для `{text}`:",
                reply_markup=get_parameter_values_keyboard(text),
                parse_mode="Markdown"
            )
        elif text == "ℹ️ Пояснення параметрів":
            await update.message.reply_text(get_settings_description_text(), parse_mode="Markdown")


        else:
            await update.message.reply_text("❓ Невідомий параметр.")

    # --- PARAM VALUE MENU ---
    elif menu.startswith("settings_param_"):
        param = menu.replace("settings_param_", "")
        if param not in default_settings:
            await update.message.reply_text("❌ Помилка параметра.")
            return

        value = current_settings.get(param, default_settings[param])
        delta = {
            "f0_up_key": 1,
            "index_rate": 0.05,
            "filter_radius": 1,
            "rms_mix_rate": 0.05,
            "protect": 0.05,
        }.get(param, 1)

        if text == "🔙 Назад":
            set_user_menu(user_id, "settings_main")
            await update.message.reply_text(format_settings(current_settings))
            await update.message.reply_text("⚙️ Обери параметр:", reply_markup=get_settings_main_keyboard())

        elif text == "➕ Збільшити":
            new_value = round(value + delta, 3)
            current_settings[param] = new_value
            set_user_settings(user_id, current_settings)
            await update.message.reply_text(f"✅ {param} збільшено до {new_value}")
            await update.message.reply_text(format_settings(current_settings), reply_markup=get_parameter_values_keyboard(param))

        elif text == "➖ Зменшити":
            new_value = round(value - delta, 3)
            current_settings[param] = new_value
            set_user_settings(user_id, current_settings)
            await update.message.reply_text(f"✅ {param} зменшено до {new_value}")
            await update.message.reply_text(format_settings(current_settings), reply_markup=get_parameter_values_keyboard(param))

        else:
            try:
                typed = type(default_settings[param])(text)
                current_settings[param] = typed
                set_user_settings(user_id, current_settings)
                set_user_menu(user_id, "settings_main")
                await update.message.reply_text(f"✅ Параметр {param} оновлено до {typed}")
                await update.message.reply_text(format_settings(current_settings), reply_markup=get_settings_main_keyboard())
            except:
                await update.message.reply_text("⚠️ Неправильне значення.")




def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🎙 Обрати голос")],
            [KeyboardButton("🎛 Налаштування")],
        ],
        resize_keyboard=True
    )

def get_voice_select_keyboard():
    from sirenmask.rvc_engine.model_manager import get_available_models
    models = get_available_models()

    keyboard = [[KeyboardButton(name)] for name in models]
    keyboard.append([KeyboardButton("🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)












def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("select_voice", select_voice))
    app.add_handler(CommandHandler("voice_settings", voice_settings))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(handle_menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(set_voice))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))




