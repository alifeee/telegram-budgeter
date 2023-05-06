import datetime
import pandas
from ..spreadsheet import Spreadsheet
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import matplotlib.pyplot as plt
import io


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

NOT_ENOUGH_DATA_FOR_ROLLING_MESSAGE = """
When you have more than 30 days of data, I'll show you a rolling average ;).
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

    graph_message = await update.message.reply_text("Generating graph...")
    try:
        figure = plt.figure()
        ax = figure.add_subplot(111)

        df.plot(
            x="Date",
            y="Spend",
            ax=ax,
        )

        last_date = df["Date"].max()
        days_ago_30 = last_date - datetime.timedelta(days=30)
        ax.vlines(
            days_ago_30,
            0,
            df["Spend"].max(),
            color="red",
            linestyle=":",
            alpha=0.5,
            label="30d ago",
        )

        rolling_spends_7d = df["Spend"].rolling(7).mean()
        rolling_spends_7d_df = pandas.concat([df["Date"], rolling_spends_7d], axis=1)
        rolling_spends_7d_df.columns = ["Date", "7d rolling average"]
        rolling_spends_7d_df = rolling_spends_7d_df.dropna()
        rolling_spends_7d_df.plot(
            x="Date",
            y="7d rolling average",
            ax=ax,
            linestyle="dashed",
        )

        ax.legend()
        ax.set_ylabel("Spend (£)")
        ax.set_xlabel("Date")
        ax.set_title("Daily Spend")
        ax.grid()
        ax.set_ylim(bottom=0)
        figure.tight_layout()

        buf = io.BytesIO()
        figure.savefig(buf, format="png")
        buf.seek(0)

        await update.message.reply_photo(buf)
        await graph_message.delete()
    except Exception as e:
        await graph_message.edit_text("Error generating graph: {}".format(e))

    # rolling average (only if there are more than 30 days of data)
    if len(df) < 40:
        await update.message.reply_text(NOT_ENOUGH_DATA_FOR_ROLLING_MESSAGE)

    rolling_average_message = await update.message.reply_text(
        "Generating rolling average graph..."
    )
    try:
        figure = plt.figure()
        ax = figure.add_subplot(111)

        rolling_spends_30d = df["Spend"].rolling(30).mean()
        rolling_spends_30d_df = pandas.concat([df["Date"], rolling_spends_30d], axis=1)
        rolling_spends_30d_df.columns = ["Date", "30d rolling average"]
        rolling_spends_30d_df = rolling_spends_30d_df.dropna()
        rolling_spends_30d_df.plot(
            x="Date",
            y="30d rolling average",
            ax=ax,
        )

        ax.set_ylabel("Spend (£)")
        ax.set_xlabel("End Date")
        ax.set_title("30 day rolling average")
        ax.grid()
        ax.set_ylim(bottom=0)
        figure.tight_layout()

        buf = io.BytesIO()
        figure.savefig(buf, format="png")
        buf.seek(0)

        await update.message.reply_photo(buf)
        await rolling_average_message.delete()
    except Exception as e:
        await rolling_average_message.edit_text(
            "Error generating rolling average graph: {}".format(e)
        )


stats_handler = CommandHandler("stats", stats)
