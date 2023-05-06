from telegram import InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from ..spreadsheet import verifyurl
from .cancel import cancel_handler

USER_CHOOSING_SHEET_MODE, USER_CONFIRMING_CREATION, USERGIVING_SPREADSHEET_URL = range(
    3
)

START_MESSAGE = """
Hi!

I help you log your daily spending over time. I can provide statistics as well as help keep the spreadsheet up to date.

To get started let's create a spreadsheet where we can store your data. Use /cancel to cancel at any time.

Created by @alifeeerenn. <a href="https://github.com/alifeee/telegram-budgeter">Source code</a>.
"""

CREATE_SHEET_OPTION = "Create spreadsheet"
USE_EXISTING_SHEET_OPTION = "Use existing spreadsheet"

CREATE_SPREADSHEET_IMAGE = "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/new-google-sheet.png"
CREATE_SPREADSHEET_MESSAGE = """
Let's get started! Create a new spreadsheet with <a href='https://sheets.google.com'>Google Sheets</a>.

I only use the columns A and B, so make sure they have a label, and you can do what you want with the rest of the spreadsheet. Feel free to fill in as much historical data as you want! I will only ask for spending data from the earliest date that you have filled in.
"""

EDIT_SPREADSHEET_PERMISSIONS_IMAGES = [
    "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/1-click-share.png",
    "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/2-enter-email.png",
    "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/3-share.png",
]
EDIT_SPREADSHEET_PERMISSIONS_MESSAGE = """
Now, to keep track of data I need access to the spreadsheet! Please share it by:

1. Clicking the "Share" button in the top right corner
2. Entering the email address of the bot 
    telegram-budgeter@telegram-budgeter.iam.gserviceaccount.com
3. Clicking "Share"
"""

QUERY_IF_DONE_MESSAGE = """
Let me know when you're done!
"""
IS_DONE_OPTION = "I'm done"

USE_EXISTING_SPREADSHEET_MESSAGE = """
Please send me the URL of the spreadsheet you want to use. Make sure it is shared with the me so I can edit it!
"""
NOT_A_SPREADSHEET_URL_MESSAGE = """
That doesn't look like a Google Sheets URL to me. Please try again :) or /cancel
"""
SPREADSHEET_URL_ACCEPTED_MESSAGE = """
Thanks! To get started, try /stats

To get a daily prompt to log your spending, use /remind
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(
        START_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            [[CREATE_SHEET_OPTION], [USE_EXISTING_SHEET_OPTION]],
            one_time_keyboard=True,
            is_persistent=True,
            resize_keyboard=True,
        ),
        disable_web_page_preview=True,
    )
    return USER_CHOOSING_SHEET_MODE


async def create_spreadsheet(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_photo(
        CREATE_SPREADSHEET_IMAGE,
        caption=CREATE_SPREADSHEET_MESSAGE,
        parse_mode="HTML",
    )
    await update.message.reply_media_group(
        [InputMediaPhoto(img) for img in EDIT_SPREADSHEET_PERMISSIONS_IMAGES],
        caption=EDIT_SPREADSHEET_PERMISSIONS_MESSAGE,
    )
    await update.effective_message.reply_text(
        QUERY_IF_DONE_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            [[IS_DONE_OPTION]],
            one_time_keyboard=True,
            is_persistent=True,
            resize_keyboard=True,
        ),
    )
    return USER_CONFIRMING_CREATION


async def use_existing_spreadsheet(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.effective_message.reply_text(
        USE_EXISTING_SPREADSHEET_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    return USERGIVING_SPREADSHEET_URL


async def give_spreadsheet_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    spreadsheet_id = update.effective_message.text
    if not verifyurl(spreadsheet_id):
        await update.effective_message.reply_text(NOT_A_SPREADSHEET_URL_MESSAGE)
        return USERGIVING_SPREADSHEET_URL
    context.user_data["spreadsheet_url"] = spreadsheet_id
    await update.effective_message.reply_text(SPREADSHEET_URL_ACCEPTED_MESSAGE)
    return ConversationHandler.END


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        USER_CHOOSING_SHEET_MODE: [
            MessageHandler(
                filters.Regex(f"^({CREATE_SHEET_OPTION})$"), create_spreadsheet
            ),
            MessageHandler(
                filters.Regex(f"^({USE_EXISTING_SHEET_OPTION})$"),
                use_existing_spreadsheet,
            ),
        ],
        USER_CONFIRMING_CREATION: [
            MessageHandler(
                filters.Regex(f"^({IS_DONE_OPTION})$"), use_existing_spreadsheet
            )
        ],
        USERGIVING_SPREADSHEET_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, give_spreadsheet_id),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        cancel_handler,
    ],
)
