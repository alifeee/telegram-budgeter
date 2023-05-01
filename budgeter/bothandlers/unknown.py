from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "That's not a command I know!",
    )

unknown_handler = MessageHandler(filters.COMMAND, unknown)
