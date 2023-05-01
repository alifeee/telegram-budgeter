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

def jobname(user: int) -> str:
    return f"reminder-{user}"

def queue_reminder(job_queue: JobQueue, user: int, run_now: bool = False):
    already_a_job = job_queue.get_jobs_by_name(jobname(user))
    if already_a_job:
        return
    job_queue.run_daily(
        remind,
        time=datetime.time(hour=10, minute=0),
        chat_id=user,
        name=jobname(user),
    )
    if run_now:
        job_queue.run_once(
            remind,
            when=0,
            chat_id=user,
        )

def cancel_reminder(job_queue: JobQueue, user: int):
    jobs = job_queue.get_jobs_by_name(jobname(user))
    for job in jobs:
        job.schedule_removal()

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
