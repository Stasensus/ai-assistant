from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import ALLOWED_USER_ID
from bot.services.claude import classify_message
from bot.services.leantime import get_leantime
from bot.services.scheduler import get_scheduler


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    text = update.message.text
    if context.user_data.pop("awaiting_snooze", False):
        await _handle_snooze_duration(update, context, text)
        return
    await _process_message(update, context, text)


async def _handle_snooze_duration(update, context, duration_text: str):
    """Process snooze duration reply and reschedule last active reminder."""
    from datetime import datetime, timedelta
    import re
    now = datetime.now()
    match_min = re.search(r"(\d+)\s*минут", duration_text)
    match_hour = re.search(r"(\d+)\s*час", duration_text)
    if "завтра" in duration_text:
        remind_at = (now + timedelta(days=1)).replace(hour=9, minute=0).isoformat()
        label = "завтра в 9:00"
    elif match_min:
        minutes = int(match_min.group(1))
        remind_at = (now + timedelta(minutes=minutes)).isoformat()
        label = f"через {minutes} минут"
    elif match_hour:
        hours = int(match_hour.group(1))
        remind_at = (now + timedelta(hours=hours)).isoformat()
        label = f"через {hours} часа"
    else:
        await update.message.reply_text("Не понял время. Попробуй: 'на 30 минут' или 'на завтра'.")
        return
    get_scheduler().add_one_time_reminder(
        chat_id=update.effective_chat.id,
        text="🔔 Напоминание (отложено)",
        remind_at=remind_at,
    )
    await update.message.reply_text(f"⏰ Напомню {label}.")


async def _process_message(update, context, text: str):
    try:
        intent = classify_message(text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Не смог разобрать сообщение: {e}")
        return

    lt = get_leantime()

    if intent["intent"] == "new_task":
        try:
            task_id = lt.create_task(
                title=intent["title"],
                description=intent.get("description", ""),
                priority=intent.get("priority", "medium"),
                due_date=intent.get("due_date"),
                tags=intent.get("tags", []),
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Задача не сохранилась в Leantime: {e}")
            return

        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            intent.get("priority", "medium"), "🟡"
        )
        title = intent["title"]
        project = intent.get("project", "Входящие")
        priority = intent.get("priority", "medium")
        msg = f"📋 {title}\n   Проект: {project}\n   Приоритет: {priority_emoji} {priority}"
        if intent.get("due_date"):
            msg += f"\n   Срок: {intent['due_date']}"
        if intent.get("subtasks"):
            msg += "\n   Подзадачи:\n" + "\n".join(f"   • {s}" for s in intent["subtasks"])

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Добавлено", callback_data=f"confirm_{task_id}"),
        ]])
        await update.message.reply_text(msg, reply_markup=keyboard)

    elif intent["intent"] == "complete":
        task = lt.get_last_active_task()
        if task:
            lt.complete_task(task["id"])
            await update.message.reply_text(f"✅ Выполнено: {task['headline']}")
        else:
            await update.message.reply_text("Активных задач не найдено.")

    elif intent["intent"] == "query_today":
        tasks = lt.get_today_tasks()
        await update.message.reply_text(_format_today(tasks), parse_mode="Markdown")

    elif intent["intent"] == "reminder":
        sched = get_scheduler()
        sched.add_one_time_reminder(
            chat_id=update.effective_chat.id,
            text=f"🔔 {intent['text']}",
            remind_at=intent.get("remind_at", ""),
        )
        await update.message.reply_text(f"🔔 Напоминание поставлено: {intent['text']}")

    elif intent["intent"] == "waiting":
        task = lt.get_last_active_task()
        if task:
            lt.set_waiting(task["id"], intent.get("waiting_for", ""))
            await update.message.reply_text(
                f"⏳ Жду ответа от {intent.get('waiting_for', '?')}: {task['headline']}"
            )
        else:
            await update.message.reply_text("Нет активной задачи для ожидания.")

    elif intent["intent"] == "reschedule":
        task = lt.get_last_active_task()
        if task:
            lt.reschedule_task(task["id"], intent["due_date"])
            await update.message.reply_text(
                f"📅 Перенесено на {intent['due_date']}: {task['headline']}"
            )

    elif intent["intent"] == "clarify":
        await update.message.reply_text(intent["question"])


def _format_today(tasks: list) -> str:
    if not tasks:
        return "📭 На сегодня задач нет. Отличный день!"
    priority_tasks = [t for t in tasks if t.get("priority") in ("3", "high")]
    other_tasks = [t for t in tasks if t not in priority_tasks]
    lines = [f"☀️ *Твой день — {len(tasks)} задачи:*\n"]
    if priority_tasks:
        lines.append(f"⭐ Приоритет: {priority_tasks[0]['headline']}")
    if other_tasks:
        others = " / ".join(t["headline"] for t in other_tasks[:3])
        lines.append(f"📋 Ещё: {others}")
    return "\n".join(lines)
