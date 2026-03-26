import pytest
from unittest.mock import patch, MagicMock
from bot.services.leantime import LeantimeClient


@pytest.fixture
def client():
    return LeantimeClient("http://localhost", "test_key", inbox_project_id=1)


def test_create_task_returns_id(client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"result": {"id": 42}, "error": None}
    mock_resp.raise_for_status = MagicMock()
    with patch("bot.services.leantime.requests.post", return_value=mock_resp):
        task_id = client.create_task(
            title="Позвонить Ивану",
            project_id=1,
            priority="high",
            due_date="2026-03-28"
        )
    assert task_id == 42


def test_get_today_tasks_returns_list(client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "result": [
            {"id": 1, "headline": "Задача 1", "priority": "high", "status": "inprogress"},
            {"id": 2, "headline": "Задача 2", "priority": "medium", "status": "new"},
        ],
        "error": None
    }
    mock_resp.raise_for_status = MagicMock()
    with patch("bot.services.leantime.requests.post", return_value=mock_resp):
        tasks = client.get_today_tasks()
    assert len(tasks) == 2
    assert tasks[0]["headline"] == "Задача 1"
