import pytest
from unittest.mock import MagicMock, patch
from bot.services.scheduler import BotScheduler


def test_add_reminder_stores_job():
    mock_app = MagicMock()
    sched = BotScheduler(mock_app, chat_id=123)
    with patch.object(sched.scheduler, "add_job") as mock_add:
        sched.add_one_time_reminder(
            chat_id=123,
            text="Тест",
            remind_at="2026-03-28T10:00:00"
        )
    mock_add.assert_called_once()


def test_scheduler_starts_without_error():
    mock_app = MagicMock()
    sched = BotScheduler(mock_app, chat_id=123)
    sched.scheduler.start()
    assert sched.scheduler.running
    sched.scheduler.shutdown()
