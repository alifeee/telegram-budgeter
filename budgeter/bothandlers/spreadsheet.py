from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from ..spreadsheet import verifyurl

async def get_spreadsheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await update.effective_message.reply_text(
            "It doesn't look like you've linked a spreadsheet! Try /start",
        )
        return
    
    await update.message.reply_html(
        f"""
Your spreadsheet is:

<a href="{spreadsheet_url}">{spreadsheet_url}</a>
        """
    )
    
spreadsheet_handler = CommandHandler("spreadsheet", get_spreadsheet_url)
