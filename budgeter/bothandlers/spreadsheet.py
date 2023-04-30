from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from gspread.utils import extract_id_from_url
from gspread.exceptions import NoValidUrlKeyFound

async def get_spreadsheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        spreadsheet_url = context.user_data["spreadsheet_url"]
    except KeyError:
        await update.effective_message.reply_text(
            "It doesn't look like you've linked a spreadsheet! Try /start",
        )
        return
    
    try:
        _ = extract_id_from_url(spreadsheet_url)
    except NoValidUrlKeyFound:
        await update.message.reply_html(
            f"""
Your link doesn't look like a Google Sheets link.

Your link:
<pre>{spreadsheet_url}</pre>

To change it, use /start
            """
        )
        return
    
    await update.message.reply_html(
        f"""
Your spreadsheet is:

<a href="{spreadsheet_url}">{spreadsheet_url}</a>
        """
    )
    
spreadsheet_handler = CommandHandler("spreadsheet", get_spreadsheet_url)
