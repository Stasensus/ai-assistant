from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ALLOWED_USER_ID
from bot.services.whisper import transcribe_voice
from bot.handlers.text import _process_message


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    audio_bytes = await file.download_as_bytearray()
    text = transcribe_voice(bytes(audio_bytes))
    await update.message.reply_text(f"🎙️ _{text}_", parse_mode="Markdown")
    await _process_message(update, context, text)
