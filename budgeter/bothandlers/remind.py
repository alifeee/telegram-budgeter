from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

USER_CONFIRMING_REMINDER = range(1)

async def ask_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        reminders_on = context.user_data["reminders"]
    except KeyError:
        reminders_on = False
    reminders_on_text = "on" if reminders_on else "off"
    await update.effective_message.reply_text(f"""
This bot can remind you at 10am every day to log the previous day's spending. It also prompts you to fill in any missed days.

Your reminders are currently {reminders_on_text}. What do you want to change?
    """,
        reply_markup=ReplyKeyboardMarkup(
            [["Remind me"], ["Don't remind me"]],
            is_persistent=True,
            resize_keyboard=True,
    )
    )
    return USER_CONFIRMING_REMINDER

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["reminders"] = True
    await update.effective_message.reply_text(
        "I'll remind you to log your spending every day at 10am. If you want to change this, use /remind",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def dont_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["reminders"] = False
    await update.effective_message.reply_text(
        "Okay! You won't be bothered. If you change your mind, use /remind",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

remind_handler = ConversationHandler(
    entry_points=[CommandHandler("remind", ask_remind)],
    states={
        USER_CONFIRMING_REMINDER: [
            MessageHandler(
                filters.Regex("^Remind me$"),
                remind
            ),
            MessageHandler(
                filters.Regex("^Don't remind me$"),
                dont_remind
            ),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", lambda *args: ConversationHandler.END),
    ],
)
