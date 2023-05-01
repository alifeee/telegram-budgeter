from telegram import InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from ..spreadsheet import verifyurl

USER_CHOOSING_SHEET_MODE, USER_CONFIRMING_CREATION, USERGIVING_SPREADSHEET_URL = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html("""
Hi!

I help you log your daily spending over time. I can provide statistics as well as help keep the spreadsheet up to date.

To get started let's create a spreadsheet where we can store your data. Use /cancel to cancel at any time.

Created by @alifeeerenn. <a href="https://github.com/alifeee/telegram-budgeter">Source code</a>.
""",
        reply_markup=ReplyKeyboardMarkup(
            [["Create spreadsheet"], ["Use existing spreadsheet"]], one_time_keyboard=True,
            is_persistent=True,
            resize_keyboard=True,
        ),
        disable_web_page_preview=True,
    )
    return USER_CHOOSING_SHEET_MODE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Cancelled. Use /start to start again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def create_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_photo(
        "https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/new-google-sheet.png",
        caption="""
Let's get started! Create a new spreadsheet with <a href='https://sheets.google.com'>Google Sheets</a>.

I only use the columns A and B, so make sure they have a label, and you can do what you want with the rest of the spreadsheet. Feel free to fill in as much historical data as you want! I will only ask for spending data from the earliest date that you have filled in.
""",
    parse_mode="HTML"
    )
    await update.message.reply_media_group(
        [
            InputMediaPhoto("https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/1-click-share.png"),
            InputMediaPhoto("https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/2-enter-email.png"),
            InputMediaPhoto("https://raw.githubusercontent.com/alifeee/telegram-budgeter/master/budgeter/bothandlers/images/3-share.png"),
        ],
        caption="""
Now, to keep track of data I need access to the spreadsheet! Please share it by:

1. Clicking the "Share" button in the top right corner
2. Entering the email address of the bot 
    telegram-budgeter@telegram-budgeter.iam.gserviceaccount.com
3. Clicking "Share"
        """
    )
    await update.effective_message.reply_text(
        "Let me know when you're done!",
        reply_markup=ReplyKeyboardMarkup(
            [["I'm done"]], one_time_keyboard=True, is_persistent=True, resize_keyboard=True,
        ),
    )
    return USER_CONFIRMING_CREATION


async def use_existing_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Please send me the URL of the spreadsheet you want to use. Make sure it is shared with the me so I can edit it!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return USERGIVING_SPREADSHEET_URL


async def give_spreadsheet_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    spreadsheet_id = update.effective_message.text
    if not verifyurl(spreadsheet_id):
        await update.effective_message.reply_text(
            "That doesn't look like a Google Sheets URL to me. Please try again :) or /cancel"
        )
        return USERGIVING_SPREADSHEET_URL
    context.user_data["spreadsheet_url"] = spreadsheet_id
    await update.effective_message.reply_text("""
Thanks! To get started, try /stats

To get a daily prompt to log your spending, use /remind
"""
    )
    return ConversationHandler.END
    
start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        USER_CHOOSING_SHEET_MODE: [
            MessageHandler(
                filters.Regex("^Create spreadsheet$"), create_spreadsheet
            ),
            MessageHandler(
                filters.Regex(
                    "^Use existing spreadsheet$"), use_existing_spreadsheet
            ),
        ],
        USER_CONFIRMING_CREATION: [
            MessageHandler(
                filters.Regex("^I'm done$"),
                use_existing_spreadsheet
            ),
        ],
        USERGIVING_SPREADSHEET_URL: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, give_spreadsheet_id
            ),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        CommandHandler("cancel", cancel),
        ],
)
