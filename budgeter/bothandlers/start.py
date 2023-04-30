from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters


CHOOSING_SHEET_MODE, CONFIRMING, GIVING_SPREADSHEET_ID = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Hi! I'm a bot that logs your daily spending. To get started, please create a spreadsheet.",
        reply_markup=ReplyKeyboardMarkup(
            [["Create spreadsheet"], ["Use existing spreadsheet"]], one_time_keyboard=True,
            is_persistent=True,
            resize_keyboard=True,
        ),
    )
    return CHOOSING_SHEET_MODE


async def create_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Please create a spreadsheet and confirm when you're done.",
        reply_markup=ReplyKeyboardMarkup(
            [["Confirm"]], one_time_keyboard=True, is_persistent=True, resize_keyboard=True,
        ),
    )
    return CONFIRMING


async def use_existing_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Please enter the spreadsheet URL.",
    )
    return GIVING_SPREADSHEET_ID


async def give_spreadsheet_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    spreadsheet_id = update.effective_message.text
    context.user_data["spreadsheet_url"] = spreadsheet_id
    await update.effective_message.reply_text(
        "Spreadsheet URL received! You can now start logging your spending.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_SHEET_MODE: [
            MessageHandler(
                filters.Regex("^Create spreadsheet$"), create_spreadsheet
            ),
            MessageHandler(
                filters.Regex(
                    "^Use existing spreadsheet$"), use_existing_spreadsheet
            ),
        ],
        CONFIRMING: [
            MessageHandler(
                filters.Regex("^Confirm$"),
                use_existing_spreadsheet
            ),
        ],
        GIVING_SPREADSHEET_ID: [
            MessageHandler(
                filters.TEXT, give_spreadsheet_id
            ),
        ],
    },
    fallbacks=[CommandHandler("start", start)],
)
