from telegram import Update
from telegram.ext import ContextTypes, JobQueue
import random
import datetime

greetings = [
    "Sup",
    "Hi",
    "Hey",
    "Hello",
    "Howdy",
    "Salutations",
    "Greetings",
    "Yo",
    "What's up",
    "How's it going",
    "Bot here",
]

def queue_reminder(job_queue: JobQueue, user: int, run_now: bool = False):
    job_queue.run_daily(
        remind,
        time=datetime.time(hour=10, minute=0),
        chat_id=user,
    )
    if run_now:
        job_queue.run_once(
            remind,
            when=0,
            chat_id=user,
        )

async def remind(context: ContextTypes.DEFAULT_TYPE):
    try:
        user = context.job.chat_id
    except KeyError as e:
        raise ValueError(
            "user not set in reminder"
        ) from e
    
    greeting = random.choice(greetings)
    await context.bot.send_message(
        chat_id=user,
        text=f"""
{greeting}! How much did you spend yesterday?
/spend

(to disable these reminders, use /remind)
"""
    )
