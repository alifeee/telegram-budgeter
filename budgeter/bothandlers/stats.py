from ..spreadsheet import SpreadsheetCredentials, Spreadsheet
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import pandas


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials):
    message = await update.message.reply_text("Getting stats...")
    SPREADSHEET_ID = "18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0"
    spreadsheet = Spreadsheet(spreadsheet_credentials, SPREADSHEET_ID)
    cols = spreadsheet.get_cols([1, 2])
    df = pandas.DataFrame(cols[1:], columns=['Date', 'Spend'])
    df['Date'] = pandas.to_datetime(df['Date'], format='%d/%m/%Y')
    await message.edit_text(df.to_string())


def get_stats_handler(credentials: SpreadsheetCredentials):
    return CommandHandler(
        "stats",
        lambda update, context: stats(update, context, credentials)
    )
