from ..spreadsheet import SpreadsheetCredentials, Spreadsheet
import telegram
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import pandas
from gspread.exceptions import APIError


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials):
    message = await update.message.reply_text("Getting stats...")
    try:
        SPREADSHEET_ID = context.user_data["spreadsheet_id"]
    except KeyError:
        await message.edit_text(
            "No spreadsheet ID found. Please create a spreadsheet first. /start",
        )
        return
    
    try:
        spreadsheet = Spreadsheet(spreadsheet_credentials, SPREADSHEET_ID)
    except APIError as e:
        await message.edit_text(
            f"""
Error getting spreadsheet with ID:
`{SPREADSHEET_ID}`
            
Check that the spreadsheet exists and that the bot has access to it\.

Change the spreadsheet ID with /start
""",
            parse_mode="MarkdownV2"
        )
        return
    cols = spreadsheet.get_cols([1, 2])
    df = pandas.DataFrame(cols[1:], columns=['Date', 'Spend'])
    df['Date'] = pandas.to_datetime(df['Date'], format='%d/%m/%Y')
    await message.edit_text(df.to_string())


def get_stats_handler(credentials: SpreadsheetCredentials):
    return CommandHandler(
        "stats",
        lambda update, context: stats(update, context, credentials)
    )
