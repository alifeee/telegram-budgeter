"""Telegram bot to log daily spending"""
import os
from dotenv import load_dotenv
import logging
import pandas
from telegram.ext import *
from telegram import *
from spreadsheet import Spreadsheet, SpreadsheetCredentials

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

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials):
    message = await update.message.reply_text("Getting stats...")
    SPREADSHEET_ID = "18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0"
    spreadsheet = Spreadsheet(spreadsheet_credentials, SPREADSHEET_ID)
    cols = spreadsheet.get_cols([1, 2])
    df = pandas.DataFrame(cols[1:], columns=['Date', 'Spend'])
    df['Date'] = pandas.to_datetime(df['Date'], format='%d/%m/%Y')
    await message.edit_text(df.to_string())


def main():
    CREDENTIALS_PATH = "google_credentials.json"

    credentials = SpreadsheetCredentials(CREDENTIALS_PATH)

    application = Application.builder().token(API_KEY).build()
    application.add_handler(CommandHandler("help", help))
    application.add_handler(
        CommandHandler(
            "stats",
            lambda update, context: stats(update, context, credentials)
        )
    )
    application.run_polling()


if __name__ == "__main__":
    main()
