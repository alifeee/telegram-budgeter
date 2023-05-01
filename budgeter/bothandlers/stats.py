from ..spreadsheet import SpreadsheetCredentials, Spreadsheet
import telegram
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import pandas
from gspread.exceptions import APIError, NoValidUrlKeyFound
import re


def openSpreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials):
    try:
        SPREADSHEET_URL = context.user_data["spreadsheet_url"]
    except KeyError:
        return None, "No spreadsheet URL found. Please create or link a spreadsheet first. /start"
    
    try:
        spreadsheet = Spreadsheet(spreadsheet_credentials, SPREADSHEET_URL)
    except APIError as e:
        return None, f"""
I can't access the spreadsheet with the link:
<pre>{SPREADSHEET_URL}</pre>

Do I have access? If not, use /start for instructions on how to give me access.
"""
    return spreadsheet, None

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials):
    message = await update.message.reply_text("Getting stats...")
    spreadsheet, error = openSpreadsheet(update, context, spreadsheet_credentials)
    if error:
        await message.edit_text(error, parse_mode="HTML")
        return

    try:
        df = spreadsheet.get_parsed_data()
        average = df['Spend'].mean()
    except Exception as e:
        await message.edit_text(f"""
Error processing spreadsheet. Ask @alifeeerenn why. :)

(Error: {e})
        """
        )
        raise e
    
    await message.edit_text(f"Average spend: {average:.2f}")


def get_stats_handler(credentials: SpreadsheetCredentials):
    return CommandHandler(
        "stats",
        lambda update, context: stats(update, context, credentials)
    )
