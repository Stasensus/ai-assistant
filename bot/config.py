import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

LEANTIME_URL = os.environ["LEANTIME_URL"]
LEANTIME_API_KEY = os.environ["LEANTIME_API_KEY"]
LEANTIME_INBOX_PROJECT_ID = int(os.environ.get("LEANTIME_INBOX_PROJECT_ID", "1"))

MORNING_BRIEFING_HOUR = int(os.environ.get("MORNING_BRIEFING_HOUR", "9"))
MORNING_BRIEFING_MINUTE = int(os.environ.get("MORNING_BRIEFING_MINUTE", "0"))
KAIZEN_REMINDER_DAY = int(os.environ.get("KAIZEN_REMINDER_DAY", "1"))

LEANTIME_DASHBOARD_URL = os.environ.get("LEANTIME_DASHBOARD_URL", "http://localhost")

GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "/app/google_credentials.json")

PROJECTS = [
    "Личностное развитие",
    "Семья",
    "Бизнес / Курс для помогающих профессий",
    "Бизнес / Мастер-группы (GPT, Midjourney)",
    "Бизнес / Консультации",
    "Бизнес / SMM и личный бренд",
    "Бизнес / B2B и партнёрства",
    "Общественные дела",
    "Хобби",
    "Входящие",
]
