import pytest
from unittest.mock import patch, MagicMock
from bot.services.whisper import transcribe_voice


def test_transcribe_voice_returns_text():
    mock_response = MagicMock()
    mock_response.text = "позвони Ивану завтра"
    with patch("bot.services.whisper.client.audio.transcriptions.create",
               return_value=mock_response):
        result = transcribe_voice(b"fake_audio_bytes")
    assert result == "позвони Ивану завтра"


def test_transcribe_voice_empty_audio_raises():
    with patch("bot.services.whisper.client.audio.transcriptions.create",
               side_effect=Exception("Audio too short")):
        with pytest.raises(Exception, match="Audio too short"):
            transcribe_voice(b"")
