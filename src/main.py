"""Telegram bot to log daily spending"""
import os
from dotenv import load_dotenv
import logging
from telegram.ext import *
from telegram import *

load_dotenv()
try:
    API_KEY = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
except KeyError as e:
    raise ValueError(
        "Please set the TELEGRAM_BOT_ACCESS_TOKEN environment variable."
    ) from e

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/help currently does nothing :). See https://github.com/alifeee/telegram-budgeter if you want to run this bot yourself."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start currently does nothing :). See https://github.com/alifeee/telegram-budgeter if you want to run this bot yourself."
    )


def main():
    application = Application.builder().token(API_KEY).build()
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
