from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

PRIVACY_MESSAGE = """
Your spreadsheet with your data is edited by a Google service account. This is a Google account that is not associated with any person and cannot be logged into normally. @alifeeerenn could create an elaborate python script to view the spreadsheet, but...

@alifeeerenn says: "I made this for myself. I don't care about your data".

Source code for the bot: <a href="https://github.com/alifeee/telegram-budgeter">alifeee/telegram-budgeter on GitHub</a>
"""

SHARE_SPREADSHEET_PHOTO = "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/sheets-sharing.png"
SHARE_SPREADSHEET_MESSAGE = """
Ultimately, sharing the spreadsheet with this bot is akin to sharing it with a person.
"""


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(PRIVACY_MESSAGE, disable_web_page_preview=True)
    await update.message.reply_photo(
        SHARE_SPREADSHEET_PHOTO,
        caption=SHARE_SPREADSHEET_MESSAGE,
    )


privacy_handler = CommandHandler("privacy", privacy)
