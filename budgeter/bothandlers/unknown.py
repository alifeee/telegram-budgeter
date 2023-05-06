from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

COMMAND_UNKOWN_MESSAGE = """
That's not a command I know!
"""


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(COMMAND_UNKOWN_MESSAGE)


unknown_handler = MessageHandler(filters.COMMAND, unknown)
