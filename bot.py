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
from budgeter.bothandlers.privacy import privacy_handler
from budgeter.bothandlers.spreadsheet import spreadsheet_handler
from budgeter.bothandlers.errorHandler import error_handler
from budgeter.bothandlers.remind import remind_handler
from budgeter.bothandlers.unknown import unknown_handler
import asyncio
from budgeter.remind import remind

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




def main():
    CREDENTIALS_PATH = "google_credentials.json"
    credentials = SpreadsheetCredentials(CREDENTIALS_PATH)

    persistent_data = PicklePersistence(filepath="bot_data.pickle")

    # user data
    loop = asyncio.new_event_loop()
    user_data = loop.run_until_complete(persistent_data.get_user_data())
    loop.close()

    application = Application.builder().token(
        API_KEY).persistence(persistent_data).build()

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    stats_handler = get_stats_handler(credentials)
    application.add_handler(stats_handler)
    application.add_handler(spreadsheet_handler)
    application.add_handler(remind_handler)
    application.add_handler(privacy_handler)

    application.add_handler(unknown_handler)
    application.add_error_handler(error_handler)

    for user, data in user_data.items():
        try:
            sheet_url = data['spreadsheet_url']
            reminders_on = data['reminders']
        except KeyError:
            continue
        if reminders_on:
            application.job_queue.run_repeating(
                remind,
                interval=3000,
                first = 1
            )

    application.run_polling()


if __name__ == "__main__":
    main()
