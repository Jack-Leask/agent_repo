# Placeholder calendar integration. Replace with Outlook/Graph or Google Calendar API calls.
from datetime import datetime, timedelta
from .env import ENV

def create_block(title: str, minutes: int = 60, start: datetime | None = None):
    if not start:
        start = datetime.now()
    end = start + timedelta(minutes=minutes)
    return {"title": title, "start": start.isoformat(), "end": end.isoformat(), "tz": ENV.CAL_TZ}
