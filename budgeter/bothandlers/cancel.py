from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler

CANCEL_MESSAGE = """
Ok, cancelled.
"""


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


cancel_handler = CommandHandler("cancel", cancel)
