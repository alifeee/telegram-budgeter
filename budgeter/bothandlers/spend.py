from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from ..spreadsheet import Spreadsheet, SpreadsheetCredentials
import datetime
import pandas
import numpy

USER_GIVING_DATA = range(1)

def get_first_day_without_data(dataframe: pandas.DataFrame) -> datetime:
    """
    Given a dataframe with "Date" and "Spend" columns, returns the first date where there is no spend data.

    If there is no missing data, returns the date one day after the last date in the dataframe.
    """
    if len(dataframe) == 0:
        return datetime.datetime.today() - datetime.timedelta(days=1)
    first_empty_spend = dataframe[dataframe["Spend"].isna()]["Date"]
    if len(first_empty_spend) > 0:
        return first_empty_spend.min()
    elif len(first_empty_spend) == 0:
        return dataframe["Date"].max() + datetime.timedelta(days=1)
    
def get_30d_avg(dataframe: pandas.DataFrame) -> float:
    """
    Given a dataframe with "Date" and "Spend" columns, returns the average spend over the last 30 days.
    """
    last_30_days = dataframe.tail(30)
    return last_30_days["Spend"].mean()

def get_avg_diff(dataframe: pandas.DataFrame) -> float:
    """
    Given a dataframe with "Date" and "Spend" columns, returns the difference between the average spend over the last 30 days the average spend from N-1 to N-31 days.
    """
    old_30_days = dataframe.tail(31).head(30)
    last_30_days = dataframe.tail(30)
    return last_30_days["Spend"].mean() - old_30_days["Spend"].mean()
    

async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials) -> None:
    message = await update.message.reply_text("Loading...")
    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await message.edit_text("You haven't set up a spreadsheet yet! Try /start")
        return ConversationHandler.END
    
    context.user_data["spreadsheet_url"] = spreadsheet_url
    spreadsheet = Spreadsheet(spreadsheet_credentials, spreadsheet_url)
    df = spreadsheet.get_parsed_data()

    first_no_data = get_first_day_without_data(df)
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if first_no_data >= today:
        await message.edit_text("You're up to date. Try /stats to see insights")
        return ConversationHandler.END
    
    context.user_data["date"] = first_no_data
    date = first_no_data.strftime("%d/%m/%Y")
    dayofweek = first_no_data.strftime("%A")
    daysago = (datetime.datetime.now() - first_no_data).days
    if daysago == 1:
        daysagotext = "yesterday"
    else:
        daysagotext = f"{daysago} days ago"

    await message.edit_text(f"Spending data missing for {dayofweek} {date}. How much did you spend on this day? ({daysagotext})")
    return USER_GIVING_DATA

async def give_data(update: Update, context: ContextTypes.DEFAULT_TYPE, spreadsheet_credentials: SpreadsheetCredentials) -> None:
    message = await update.message.reply_text("Loading...")
    try:
        amount = float(update.message.text)
    except ValueError:
        await message.edit_text("That doesn't look like a number. Try again?")
        return USER_GIVING_DATA
    
    spreadsheet_url = context.user_data["spreadsheet_url"]
    spreadsheet = Spreadsheet(spreadsheet_credentials, spreadsheet_url)
    df = spreadsheet.add_data(context.user_data["date"], amount)
    first_no_data = get_first_day_without_data(df)
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if first_no_data >= today:
        avg30d = get_30d_avg(df)
        avgdiff = get_avg_diff(df)
        avgarrow = "⬆️" if avgdiff > 0 else "⬇️" if avgdiff < 0 else "➡️"
        await message.edit_text(f"""
Recorded £{amount}... you're up to date!
        
Average spend over the last 30 days: £ {avg30d:.2f} ({avgarrow} £{abs(avgdiff):.2f})

Use /stats for more
        """)
        return ConversationHandler.END
    elif first_no_data < datetime.datetime.now():
        context.user_data["date"] = first_no_data
        date = first_no_data.strftime("%d/%m/%Y")
        dayofweek = first_no_data.strftime("%A")
        daysago = (datetime.datetime.now() - first_no_data).days
        if daysago == 1:
            daysagotext = "yesterday"
        else:
            daysagotext = f"{daysago} days ago"

        await message.edit_text(f"Recorded {amount}! Spending data missing for {dayofweek} {date}. How much did you spend on this day? ({daysagotext})")
        return USER_GIVING_DATA
    
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Ok, cancelled.")
    return ConversationHandler.END

def get_spend_handler(credentials: SpreadsheetCredentials):
    spend_credded = lambda u, c: spend(u, c, credentials)
    give_data_credded = lambda u, c: give_data(u, c, credentials)
    return ConversationHandler(
        entry_points=[CommandHandler("spend", spend_credded)],
        states={
            USER_GIVING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_data_credded)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ]
    )
