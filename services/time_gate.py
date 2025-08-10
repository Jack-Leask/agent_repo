# time_gate.py
import os
from datetime import datetime
from dateutil import tz

# Use TIMEZONE from Railway env, or default to Pacific/Auckland
LOCAL_TZ = tz.gettz(os.getenv("TIMEZONE", "Pacific/Auckland"))

# Time to send the digest (HH:MM in local time)
DIGEST_LOCAL_TIME = os.getenv("DIGEST_LOCAL_TIME", "19:00")

def should_send_now() -> bool:
    """Return True if the current local time matches the scheduled digest time."""
    now_str = datetime.now(tz=LOCAL_TZ).strftime("%H:%M")
    return now_str == DIGEST_LOCAL_TIME
