"""
Functions for:
- enabling/disabling daily reminders to log spending.
- sending the daily reminder.
"""
import random
import datetime
from telegram.ext import ContextTypes, JobQueue

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
    """Turns a user id into a unique job name for the reminder job.
    Then, when we want to cancel the job, we can just use the job name.

    Args:
        user (int): user id

    Returns:
        str: job name
    """
    return f"reminder-{user}"


def queue_reminder(job_queue: JobQueue, user: int, run_now: bool = False):
    """Queues a daily reminder for a user.

    Args:
        job_queue (JobQueue): the job queue (usually context.job_queue)
        user (int): user id
        run_now (bool, optional): whether to run the reminder immediately. Defaults to False.

    Returns:
        str: "success" if successful, "already_in_queue" if already in queue
    """
    already_a_job = job_queue.get_jobs_by_name(jobname(user))
    if already_a_job:
        return "already_in_queue"
    job_queue.run_daily(
        remind,
        time=datetime.time(hour=9, minute=0),
        chat_id=user,
        name=jobname(user),
    )
    return "success"


def cancel_reminder(job_queue: JobQueue, user: int):
    """Cancels a daily reminder for a user.

    Args:
        job_queue (JobQueue): the job queue (usually context.job_queue)
        user (int): user id

    Returns:
        str: "success" if successful
    """
    jobs = job_queue.get_jobs_by_name(jobname(user))
    if not jobs:
        return "not_in_queue"
    for job in jobs:
        job.schedule_removal()
    return "success"


async def remind(context: ContextTypes.DEFAULT_TYPE):
    """Sends a daily reminder to log spending.

    Args:
        context: the context passed by the job queue

    Raises:
        ValueError: if the user id is not set in the context
    """
    try:
        user = context.job.chat_id
    except KeyError as error:
        raise ValueError("user not set in reminder") from error

    greeting = random.choice(greetings)
    await context.bot.send_message(
        chat_id=user,
        text=f"""
{greeting}! How much did you spend yesterday?
/spend

(to disable these reminders, use /remind)
""",
    )
