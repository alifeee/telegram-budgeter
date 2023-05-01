from telegram import Update
from telegram.ext import ContextTypes
import os
import logging

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    try:
        ADMIN_ID = os.environ["ADMIN_USER_ID"]
    except KeyError as e:
        raise ValueError(
            "ADMIN_USER_ID environment variable not set."
        ) from e
    try:
        user = update.effective_user
        chat = update.effective_chat
    except AttributeError:
        user = "unknown"
        chat = "unknown"
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""
Error!

User: {user}

Chat: {chat}

Update: {update}

Error: {context.error}
        """
    )
    print(context)
    logger = logging.getLogger(__name__)
    logger.error(
        f"Update {update.update_id} caused error {context.error}"
    )
    # raise context.error
