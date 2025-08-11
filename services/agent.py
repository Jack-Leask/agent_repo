# services/agent.py
# Agent orchestration with a 7:00 pm NZT digest gate.

import os
from datetime import datetime
from dateutil import tz

from .notion import get_today_tasks, mark_task_status, get_page_title, append_note
from .emailer import send_digest, send_kickoff_plan, send_wrap
from .env import ENV
from .time_gate import should_send_now  # make sure services/time_gate.py exists

# Local timezone for timestamps in subjects/logs
LOCAL_TZ = tz.gettz(os.getenv("TIMEZONE", "Pacific/Auckland"))

def kickoff_flow():
    tasks = get_today_tasks()
    return {"ok": True, "top": tasks}

def nudge_flow():
    return {"ok": True, "msg": "Keep going."}

def wrap_flow():
    send_wrap("Wrap complete.")
    return {"ok": True}

def _base():
    # Prefer APP_BASE_URL env; fallback to ENV.APP_BASE_URL if present
    return os.getenv("APP_BASE_URL") or getattr(ENV, "APP_BASE_URL", "")

def daily_digest():
    """
    Send the Notion digest whenever this endpoint is called.
    (No time gate. Use cron to control when it runs.)
    """
    tasks = get_today_tasks()
    send_digest(tasks, _base())
    return {"ok": True, "sent": len(tasks)}


def start_task(page_id: str):
    title = get_page_title(page_id)
    mark_task_status(page_id, "Doing")
    plan = [
        f"Define success for: {title}",
        "List 3 bullet points or metrics.",
        "Draft outline with 3-5 headings.",
        "Gather 3 sources/links.",
        "Ship a v0 in 45-60 minutes.",
    ]
    send_kickoff_plan(title, plan)
    return {"ok": True, "id": page_id, "status": "Doing"}

def complete_task(page_id: str):
    title = get_page_title(page_id)
    mark_task_status(page_id, "Done")
    append_note(page_id, "Marked Done via agent.")
    return {"ok": True, "id": page_id, "status": "Done"}
