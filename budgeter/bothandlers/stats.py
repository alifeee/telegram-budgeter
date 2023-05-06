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

Or maybe this will help:
(Error: {})
"""
STATISTICS_MESSAGE = """
<b>All time ({totaldays:.0f} days)</b>:
  Total spend: £{total:,.2f}
  Average spend: £{average:,.2f}
  {avg_prog}
  Median spend: £{median:,.2f}
  {med_prog}

<b>Last 30 days</b>:
  Total spend: £{last30total:,.2f}
  Average spend: £{last30average:,.2f}
  {last30avg_prog}
  Median spend: £{last30median:,.2f}
  {last30med_prog}
"""


def num_to_progress_bar(num: float, max: float) -> str:
    """Converts a number to a progress bar.

    Args:
        num (float): The number to convert.
        max (float): The maximum value of the progress bar.

    Returns:
        str: The progress bar.
    """
    TOTAL_BARS = 20
    num_bars = int(num / max * TOTAL_BARS)
    return "▓" * num_bars + "░" * (TOTAL_BARS - num_bars)


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = await update.message.reply_text("Getting stats...")
    spreadsheet_client = context.bot_data["spreadsheet_client"]

    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await message.edit_text(NO_SPREADSHEET_URL_MESSAGE)
        return

    spreadsheet = Spreadsheet(spreadsheet_client, spreadsheet_url)

    try:
        df = spreadsheet.get_spending_dataframe()
    except Exception as e:
        await message.edit_text(ERROR_PROCESSING_SPREADSHEET_MESSAGE.format(e))
        return

    totaldays = (df["Date"].max() - df["Date"].min()).days
    total = df["Spend"].sum()
    average = df["Spend"].mean()
    median = df["Spend"].median()

    last30total = df.tail(30)["Spend"].sum()
    last30average = df.tail(30)["Spend"].mean()
    last30median = df.tail(30)["Spend"].median()

    max_avg = max(average, last30average, median, last30median)

    await message.edit_text(
        STATISTICS_MESSAGE.format(
            totaldays=totaldays,
            total=total,
            average=average,
            median=median,
            last30total=last30total,
            last30average=last30average,
            last30median=last30median,
            avg_prog=num_to_progress_bar(average, max_avg),
            med_prog=num_to_progress_bar(median, max_avg),
            last30avg_prog=num_to_progress_bar(last30average, max_avg),
            last30med_prog=num_to_progress_bar(last30median, max_avg),
        ),
        parse_mode="HTML",
    )


stats_handler = CommandHandler("stats", stats)
