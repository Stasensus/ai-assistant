from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from bot.config import (
    MORNING_BRIEFING_HOUR, MORNING_BRIEFING_MINUTE,
    KAIZEN_REMINDER_DAY, LEANTIME_DASHBOARD_URL,
)


class BotScheduler:
    def __init__(self, app, chat_id: int):
        self.app = app
        self.chat_id = chat_id
        self.scheduler = AsyncIOScheduler()
        self._register_recurring()

    def _register_recurring(self):
        self.scheduler.add_job(
            self._send_morning_briefing,
            CronTrigger(hour=MORNING_BRIEFING_HOUR, minute=MORNING_BRIEFING_MINUTE),
            id="morning_briefing",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._send_kaizen_reminder,
            CronTrigger(day=KAIZEN_REMINDER_DAY, hour=10, minute=0),
            id="kaizen_monthly",
            replace_existing=True,
        )

    async def _send_morning_briefing(self):
        from bot.services.leantime import get_leantime
        from bot.handlers.text import _format_today
        from bot.services.calendar import get_upcoming_events, format_event
        tasks = get_leantime().get_today_tasks()
        text = _format_today(tasks)
        try:
            events = get_upcoming_events(hours=24)
            if events:
                text += "\n\n📅 Встречи сегодня:\n" + "\n".join(format_event(e) for e in events)
        except Exception:
            pass  # Calendar unavailable — skip silently
        await self.app.bot.send_message(chat_id=self.chat_id, text=text)

    async def _send_kaizen_reminder(self):
        text = (
            f"📅 Время месячного Кайдзен-планирования!\n"
            f"Открой дашборд: {LEANTIME_DASHBOARD_URL}"
        )
        await self.app.bot.send_message(chat_id=self.chat_id, text=text)

    def add_one_time_reminder(self, chat_id: int, text: str, remind_at: str):
        """Schedule a one-time reminder. remind_at is ISO datetime string."""
        try:
            run_time = datetime.fromisoformat(remind_at)
        except (ValueError, TypeError):
            run_time = datetime.now() + timedelta(hours=1)

        async def _send():
            await self.app.bot.send_message(chat_id=chat_id, text=text)

        self.scheduler.add_job(_send, DateTrigger(run_date=run_time))

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()


_scheduler: BotScheduler | None = None


def init_scheduler(app, chat_id: int) -> BotScheduler:
    global _scheduler
    _scheduler = BotScheduler(app, chat_id)
    return _scheduler


def get_scheduler() -> BotScheduler:
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    return _scheduler
