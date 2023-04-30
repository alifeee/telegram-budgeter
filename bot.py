"""Telegram bot to log daily spending"""
import os
from dotenv import load_dotenv
import logging
import pandas
from telegram.ext import *
import telegram.ext.filters as filters
from telegram import *
from budgeter.spreadsheet import SpreadsheetCredentials
from budgeter.bothandlers.help import help_handler
from budgeter.bothandlers.start import start_handler
from budgeter.bothandlers.stats import get_stats_handler

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


async def get_spreadsheet_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        spreadsheet_id = context.user_data["spreadsheet_id"]
        await update.effective_message.reply_text(
            f"Spreadsheet ID: {spreadsheet_id}",
        )
    except KeyError:
        await update.effective_message.reply_text(
            "No spreadsheet ID found. Please create a spreadsheet first. /start",
        )
        return


def main():
    CREDENTIALS_PATH = "google_credentials.json"
    credentials = SpreadsheetCredentials(CREDENTIALS_PATH)

    persistent_data = PicklePersistence(filepath="bot_data.pickle")
    application = Application.builder().token(
        API_KEY).persistence(persistent_data).build()

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    stats_handler = get_stats_handler(credentials)
    application.add_handler(stats_handler)
    application.add_handler(CommandHandler(
        "get_spreadsheet_id", get_spreadsheet_id)
    )
    application.run_polling()


if __name__ == "__main__":
    main()
