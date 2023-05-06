"""Telegram bot to log daily spending"""
import os
from dotenv import load_dotenv
import logging
import pandas
from telegram.ext import *
import telegram.ext.filters as filters
from telegram import *
from budgeter.bothandlers.help import help_handler
from budgeter.bothandlers.start import start_handler
from budgeter.bothandlers.stats import stats_handler
from budgeter.bothandlers.spend import spend_handler
from budgeter.bothandlers.privacy import privacy_handler
from budgeter.bothandlers.spreadsheet import spreadsheet_handler
from budgeter.bothandlers.errorHandler import error_handler
from budgeter.bothandlers.remind import remind_handler
from budgeter.bothandlers.unknown import unknown_command_handler
import asyncio
from budgeter.remind import queue_reminder
import gspread

load_dotenv()
try:
    API_KEY = os.environ["TELEGRAM_BOT_ACCESS_TOKEN"]
except KeyError as e:
    raise ValueError(
        "Please set the TELEGRAM_BOT_ACCESS_TOKEN environment variable."
    ) from e

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    # user data
    persistent_data = PicklePersistence(
        filepath="bot_data.pickle",
        store_data=PersistenceInput(
            user_data=True,
            bot_data=False,
        ),
    )
    loop = asyncio.new_event_loop()
    all_user_data = loop.run_until_complete(persistent_data.get_user_data())
    loop.close()

    # spreadsheet authentication
    CREDENTIALS_PATH = "google_credentials.json"
    spreadsheet_client = gspread.service_account(filename=CREDENTIALS_PATH)

    async def add_client_to_application(application: Application) -> None:
        application.bot_data["spreadsheet_client"] = spreadsheet_client
        bot: Bot = application.bot
        await bot.set_my_commands(
            [
                ("stats", "Get spending statistics"),
                ("spreadsheet", "Get spreadsheet URL"),
                ("spend", "Set a day's spend"),
                ("remind", "Set reminders on/off"),
                ("start", "Set spreadsheet"),
                ("help", "See help"),
                ("privacy", "See privacy information"),
                ("cancel", "Cancel the current operation"),
            ]
        )

    # application
    application = (
        Application.builder()
        .token(API_KEY)
        .persistence(persistent_data)
        .post_init(add_client_to_application)
        .build()
    )

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(stats_handler)
    application.add_handler(spreadsheet_handler)
    application.add_handler(remind_handler)
    application.add_handler(spend_handler)
    application.add_handler(privacy_handler)

    application.add_handler(unknown_command_handler)
    application.add_error_handler(error_handler)

    for user_id, user_data in all_user_data.items():
        try:
            sheet_url = user_data["spreadsheet_url"]
            reminders_on = user_data["reminders"]
        except KeyError:
            continue
        if reminders_on:
            queue_reminder(application.job_queue, user_id)

    application.run_polling()


if __name__ == "__main__":
    main()
