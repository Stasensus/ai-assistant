import pickle
import os
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from bot.config import GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_ID

TOKEN_PATH = os.path.join(os.path.dirname(GOOGLE_CREDENTIALS_FILE), "google_token.pickle")
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
    if not creds or not creds.valid:
        raise RuntimeError("Google Calendar token missing or invalid. Re-authorize locally.")
    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(hours: int = 24) -> list:
    """Return events from now until now+hours."""
    service = _get_service()
    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=hours)
    result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=now.isoformat(),
        timeMax=until.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=10,
    ).execute()
    return result.get("items", [])


def get_event_start(event: dict) -> datetime | None:
    """Parse event start time, return aware datetime or None for all-day."""
    start = event.get("start", {})
    if "dateTime" in start:
        return datetime.fromisoformat(start["dateTime"])
    return None  # all-day event, no specific time


def format_event(event: dict) -> str:
    title = event.get("summary", "Без названия")
    start = event.get("start", {})
    if "dateTime" in start:
        dt = datetime.fromisoformat(start["dateTime"])
        time_str = dt.strftime("%H:%M")
        return f"📅 {time_str} — {title}"
    return f"📅 {title} (весь день)"
