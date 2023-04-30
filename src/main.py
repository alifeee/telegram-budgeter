"""Telegram bot to log daily spending"""
import os
from dotenv import load_dotenv
import logging
import pandas
from telegram.ext import *
import telegram.ext.filters as filters
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

CHOOSING_SHEET_MODE, CONFIRMING, GIVING_SPREADSHEET_ID = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Hi! I'm a bot that logs your daily spending. To get started, please create a spreadsheet.",
        reply_markup=ReplyKeyboardMarkup(
            [["Create spreadsheet"], ["Use existing spreadsheet"]], one_time_keyboard=True,
            is_persistent=True,
            resize_keyboard=True,
        ),
    )
    return CHOOSING_SHEET_MODE


async def create_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Please create a spreadsheet and confirm when you're done.",
        reply_markup=ReplyKeyboardMarkup(
            [["Confirm"]], one_time_keyboard=True, is_persistent=True, resize_keyboard=True,
        ),
    )
    return CONFIRMING


async def use_existing_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Please enter the spreadsheet ID.",
    )
    return GIVING_SPREADSHEET_ID


async def give_spreadsheet_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    spreadsheet_id = update.effective_message.text
    await update.effective_message.reply_text(
        "Spreadsheet ID received! You can now start logging your spending. Your spreadsheet ID is: " + spreadsheet_id,
    )
    return ConversationHandler.END


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

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_SHEET_MODE: [
                MessageHandler(
                    filters.Regex("^Create spreadsheet$"), create_spreadsheet
                ),
                MessageHandler(
                    filters.Regex(
                        "^Use existing spreadsheet$"), use_existing_spreadsheet
                ),
            ],
            CONFIRMING: [
                MessageHandler(
                    filters.Regex("^Confirm$"),
                    use_existing_spreadsheet
                ),
            ],
            GIVING_SPREADSHEET_ID: [
                MessageHandler(
                    filters.TEXT, give_spreadsheet_id
                ),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conversation_handler)

    application.add_handler(
        CommandHandler(
            "stats",
            lambda update, context: stats(update, context, credentials)
        )
    )
    application.run_polling()


if __name__ == "__main__":
    main()
