from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

HELP_MESSAGE = """
This bot helps you keep track of your expenses in a Google Sheets spreadsheet.

Commands (these are also buttons in the bot menu)
/start - start the bot
/help - this message
/privacy - privacy information
/spreadsheet - get a link to your spreadsheet
/spend - check if you're up to date with logging your daily spending
/reminder - toggle daily reminders to log your spending
/stats - get some statistics about your spending
/cancel - cancel the current operation

Source code for the bot:
https://github.com/alifeee/telegram-budgeter
"""


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        HELP_MESSAGE,
    )


help_handler = CommandHandler("help", help)
