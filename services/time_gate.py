# services/time_gate.py
import os
from datetime import datetime
from dateutil import tz

LOCAL_TZ = tz.gettz(os.getenv("TIMEZONE", "Pacific/Auckland"))
DIGEST_LOCAL_TIME = os.getenv("DIGEST_LOCAL_TIME", "19:00")  # HH:MM

def should_send_now() -> bool:
    return datetime.now(tz=LOCAL_TZ).strftime("%H:%M") == DIGEST_LOCAL_TIME
