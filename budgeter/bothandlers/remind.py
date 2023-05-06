from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from ..remind import queue_reminder, cancel_reminder
from .cancel import cancel_handler

ASK_REMINDER_MESSAGE = """
This bot can remind you at 11am every day to log the previous day's spending. It also prompts you to fill in any missed days.

Your reminders are currently %s. What do you want to change?
"""
DO_REMIND_CHOICE = "Remind me"
DONT_REMIND_CHOICE = "Don't remind me"

DO_REMIND_MESSAGE = """
I'll remind you to log your spending every day at 10am. If you want to change this, use /remind
"""

DONT_REMIND_MESSAGE = """
Okay! You won't be bothered. If you change your mind, use /remind
"""

USER_CONFIRMING_REMINDER = range(1)


async def ask_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        reminders_on = context.user_data["reminders"]
    except KeyError:
        reminders_on = False
    reminders_on_text = "on" if reminders_on else "off"
    await update.effective_message.reply_html(
        ASK_REMINDER_MESSAGE % reminders_on_text,
        reply_markup=ReplyKeyboardMarkup(
            [[DO_REMIND_CHOICE], [DONT_REMIND_CHOICE]],
            is_persistent=True,
            resize_keyboard=True,
        ),
    )
    return USER_CONFIRMING_REMINDER


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["reminders"] = True
    queue_reminder(context.job_queue, update.effective_user.id)
    await update.effective_message.reply_text(
        DO_REMIND_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def dont_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["reminders"] = False
    cancel_reminder(context.job_queue, update.effective_user.id)
    await update.effective_message.reply_text(
        DONT_REMIND_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


remind_handler = ConversationHandler(
    entry_points=[CommandHandler("remind", ask_remind)],
    states={
        USER_CONFIRMING_REMINDER: [
            MessageHandler(filters.Regex(f"^({DO_REMIND_CHOICE})$"), remind),
            MessageHandler(filters.Regex(f"^({DONT_REMIND_CHOICE})$"), dont_remind),
        ],
    },
    fallbacks=[cancel_handler],
)
