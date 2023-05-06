from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from ..spreadsheet import Spreadsheet
import datetime
import pandas
import numpy
from .cancel import cancel_handler

USER_GIVING_DATA = range(1)

SPREADSHEET_NOT_SET_UP_MESSAGE = """
You haven't set up a spreadsheet yet! Use /start to set one up.
"""

SPREADSHEET_BADLY_FORMATTED_MESSAGE = """
The spreadsheet appears to be broken. Try /start.
"""

UP_TO_DATE_MESSAGE = """
You're up to date. Try /stats to see insights
"""

SPENDING_DATA_MISSING_MESSAGE = """
Spending data missing for {}. How much did you spend on this day? ({})
"""

NOT_A_NUMBER_MESSAGE = """
That doesn't look like a number. Try again?
"""

DATA_NOT_ADDED_MESSAGE = """
Data not added. Ask @alifeeerenn why. :)

Or maybe this will help:
(Error: {})
"""

RECORDED_FINAL_SPEND_MESSAGE = """
Recorded £{:.2f}! You're up to date.

Average spend over the last 30 days: 
£{:.2f} ({} £{:.2f})

Use /stats for more
"""

RECORDED_INTERMEDIATE_SPEND_MESSAGE = """
Recorded £{:.2f}! Spending data missing for {}. How much did you spend on this day? ({})
"""


async def spend(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = await update.message.reply_text("Loading...")
    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await message.edit_text(SPREADSHEET_NOT_SET_UP_MESSAGE)
        return ConversationHandler.END

    spreadsheet_client = context.bot_data["spreadsheet_client"]
    spreadsheet = Spreadsheet(spreadsheet_client, spreadsheet_url)
    try:
        df = spreadsheet.get_spending_dataframe()
    except Exception as e:
        await message.edit_text(SPREADSHEET_BADLY_FORMATTED_MESSAGE)
        return ConversationHandler.END

    next_date = df["Date"].max() + datetime.timedelta(days=1)
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if next_date >= today:
        await message.edit_text(UP_TO_DATE_MESSAGE)
        return ConversationHandler.END

    context.user_data["date"] = next_date
    date = next_date.strftime("%d/%m/%Y")
    dayofweek = next_date.strftime("%A")
    daysago = (datetime.datetime.now() - next_date).days
    if daysago == 1:
        daysagotext = "yesterday"
    else:
        daysagotext = f"{daysago} days ago"

    await message.edit_text(
        SPENDING_DATA_MISSING_MESSAGE.format(f"{dayofweek} {date}", daysagotext)
    )
    return USER_GIVING_DATA


async def give_data(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = await update.message.reply_text("Loading...")
    try:
        amount = float(update.message.text)
    except ValueError:
        await message.edit_text(NOT_A_NUMBER_MESSAGE)
        return USER_GIVING_DATA

    spreadsheet_url = context.user_data["spreadsheet_url"]
    spreadsheet_client = context.bot_data["spreadsheet_client"]
    spreadsheet = Spreadsheet(spreadsheet_client, spreadsheet_url)
    data_added, why_not = spreadsheet.add_data(context.user_data["date"], amount)
    if not data_added:
        await message.edit_text(DATA_NOT_ADDED_MESSAGE.format(why_not))
        return ConversationHandler.END

    df = spreadsheet.get_spending_dataframe()

    next_date = df["Date"].max() + datetime.timedelta(days=1)
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if next_date >= today:
        avg30d = df["Spend"].tail(30).mean()
        avgdiff = df["Spend"].tail(31).head(30).mean() - avg30d
        avgarrow = "⬆️" if avgdiff > 0 else "⬇️" if avgdiff < 0 else "➡️"
        await message.edit_text(
            RECORDED_FINAL_SPEND_MESSAGE.format(amount, avg30d, avgarrow, abs(avgdiff))
        )
        return ConversationHandler.END
    elif next_date < datetime.datetime.now():
        context.user_data["date"] = next_date
        date = next_date.strftime("%d/%m/%Y")
        dayofweek = next_date.strftime("%A")
        daysago = (datetime.datetime.now() - next_date).days
        if daysago == 1:
            daysagotext = "yesterday"
        else:
            daysagotext = f"{daysago} days ago"

        await message.edit_text(
            RECORDED_INTERMEDIATE_SPEND_MESSAGE.format(
                amount, f"{dayofweek} {date}", daysagotext
            )
        )
        return USER_GIVING_DATA


spend_handler = ConversationHandler(
    entry_points=[CommandHandler("spend", spend)],
    states={
        USER_GIVING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_data)]
    },
    fallbacks=[cancel_handler],
)
