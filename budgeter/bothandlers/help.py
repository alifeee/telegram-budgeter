from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/help currently does nothing :). See https://github.com/alifeee/telegram-budgeter if you want to run this bot yourself."
    )

help_handler = CommandHandler("help", help)
