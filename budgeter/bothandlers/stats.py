from ..spreadsheet import Spreadsheet
import telegram
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import pandas
from gspread.exceptions import APIError, NoValidUrlKeyFound
from gspread.client import Client
import re

NO_SPREADSHEET_URL_MESSAGE = """
No spreadsheet URL found. Please create or link a spreadsheet first. /start
"""
NO_SPREADSHEET_ACCESS_MESSAGE = """
I can't access the spreadsheet with the link:
{}

Do I have access? If not, use /start for instructions on how to give me access.
"""
ERROR_PROCESSING_SPREADSHEET_MESSAGE = """
Error processing spreadsheet. Ask @alifeeerenn why. :)

(Error: {})
"""
STATISTICS_MESSAGE = """
Average spend: £{:.2f}
"""


def openSpreadsheet(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        SPREADSHEET_URL = context.user_data["spreadsheet_url"]
    except KeyError:
        return None, NO_SPREADSHEET_URL_MESSAGE

    try:
        spreadsheet_client = context.bot_data["spreadsheet_client"]
        spreadsheet = Spreadsheet(spreadsheet_client, SPREADSHEET_URL)
    except APIError as e:
        return (
            None,
            NO_SPREADSHEET_ACCESS_MESSAGE.format(SPREADSHEET_URL),
        )

    return spreadsheet, None


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = await update.message.reply_text("Getting stats...")
    spreadsheet_client = context.bot_data["spreadsheet_client"]
    spreadsheet, error = openSpreadsheet(update, context)
    if error:
        await message.edit_text(error, parse_mode="HTML")
        return

    try:
        df = spreadsheet.get_parsed_data()
        average = df["Spend"].mean()
    except Exception as e:
        await message.edit_text(ERROR_PROCESSING_SPREADSHEET_MESSAGE.format(e))
        raise e

    await message.edit_text(STATISTICS_MESSAGE.format(average))


stats_handler = CommandHandler("stats", stats)
