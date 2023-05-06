from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from ..spreadsheet import verifyurl

NO_LINKED_SPREADSHEET_MESSAGE = """
It doesn't look like you've linked a spreadsheet! Try /start
"""

SPREADSHEET_LINKED_MESSAGE = """
Your spreadsheet is:

{}
"""


async def get_spreadsheet_url(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await update.effective_message.reply_text(NO_LINKED_SPREADSHEET_MESSAGE)
        return

    await update.message.reply_text(SPREADSHEET_LINKED_MESSAGE.format(spreadsheet_url))


spreadsheet_handler = CommandHandler("spreadsheet", get_spreadsheet_url)
