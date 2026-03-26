from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ALLOWED_USER_ID
from bot.services.leantime import get_leantime
from bot.handlers.text import _format_today


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    tasks = get_leantime().get_today_tasks()
    await update.message.reply_text(_format_today(tasks), parse_mode="Markdown")


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    lt = get_leantime()
    task = lt.get_last_active_task()
    if task:
        lt.complete_task(task["id"])
        await update.message.reply_text(f"✅ Выполнено: {task['headline']}")
    else:
        await update.message.reply_text("Активных задач не найдено.")


async def cmd_snooze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    context.user_data["awaiting_snooze"] = True
    await update.message.reply_text(
        "На сколько отложить? Напиши: 'на 30 минут' или 'на завтра'"
    )
