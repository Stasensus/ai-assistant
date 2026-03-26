import logging
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from bot.config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_ID
from bot.handlers.text import handle_text
from bot.handlers.voice import handle_voice
from bot.handlers.commands import cmd_today, cmd_done, cmd_snooze
from bot.services.scheduler import init_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    scheduler = init_scheduler(app, chat_id=ALLOWED_USER_ID)
    scheduler.start()

    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("snooze", cmd_snooze))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Bot started. Polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
