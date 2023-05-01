from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = os.environ["ADMIN_USER_ID"]

async def remind(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="Wanna get spammed?"
    )
