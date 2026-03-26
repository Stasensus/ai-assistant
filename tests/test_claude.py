import pytest
import json
from unittest.mock import patch, MagicMock
from bot.services.claude import classify_message


def make_mock_response(json_str):
    mock = MagicMock()
    mock.content = [MagicMock(text=json_str)]
    return mock


def test_classify_new_task():
    response_json = json.dumps({
        "intent": "new_task",
        "title": "Позвонить Ивану",
        "description": "",
        "project": "Бизнес / Курс для помогающих профессий",
        "priority": "medium",
        "due_date": None,
        "subtasks": [],
        "tags": []
    })
    with patch("bot.services.claude.client.messages.create",
               return_value=make_mock_response(response_json)):
        result = classify_message("позвони Ивану по курсу")
    assert result["intent"] == "new_task"
    assert result["title"] == "Позвонить Ивану"


def test_classify_complete():
    response_json = json.dumps({"intent": "complete"})
    with patch("bot.services.claude.client.messages.create",
               return_value=make_mock_response(response_json)):
        result = classify_message("сделал")
    assert result["intent"] == "complete"


def test_classify_query_today():
    response_json = json.dumps({"intent": "query_today"})
    with patch("bot.services.claude.client.messages.create",
               return_value=make_mock_response(response_json)):
        result = classify_message("что у меня сегодня?")
    assert result["intent"] == "query_today"
