import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Вставьте здесь токен вашего бота
TOKEN = '7601337093:AAEPQpZicF5sJ0OtKg_UlEqCeBXSWgCT3lM'

# URL вашего веб-приложения
WEB_APP_URL = "https://crypto-coffee.netlify.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    keyboard = [
        [
            InlineKeyboardButton("Visit the 3D Coffee Shop", url=WEB_APP_URL)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to Crypto Coffee! Click the button below to visit your coffee shop:",
        reply_markup=reply_markup
    )

def main():
    """Запуск бота."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
