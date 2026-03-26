import io
from openai import OpenAI
from bot.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_voice(audio_bytes: bytes) -> str:
    """Transcribe OGG/OPUS audio bytes to text using Whisper API."""
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "voice.ogg"
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ru",
    )
    return response.text
