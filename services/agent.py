from .notion import get_today_tasks, mark_task_status
from .emailer import send_email
from .calendar import create_block
from datetime import datetime, timedelta
from .env import ENV

def pick_top_tasks(tasks, k=3):
    # naive selection: first k todos
    return tasks[:k]

def smallest_next_action(task_title: str):
    return f"Open the source links and draft 3 bullet points for: {task_title}"

def kickoff_flow():
    tasks = get_today_tasks()
    top = pick_top_tasks(tasks)
    if not top:
        body = "No tasks scheduled today. I will roll forward the next incomplete day."
    else:
        lines = [f"• {t['Task']} (Day {t['Day']}, Week {t['Week']})" for t in top]
        body = "Tonight’s plan (60–90 min):\n" + "\n".join(lines) + "\n\nReply START to block 60 min for the first task."
    send_email(subject="Tonight’s plan", body=body)
    return {"ok": True, "top": top}

def nudge_flow():
    tasks = get_today_tasks()
    done = [t for t in tasks if t.get("Status") == "Done"]
    if done:
        send_email(subject="Progress check", body="Nice. At least one task is Done. Keep going if you have time.")
        return {"ok": True, "status": "has_done"}
    if tasks:
        s = smallest_next_action(tasks[0]["Task"])
        send_email(subject="Mid-session nudge", body=f"Try this smallest next action: {s}\nBlock 25 min?")
    else:
        send_email(subject="Mid-session nudge", body="No tasks loaded for today.")
    return {"ok": True}

def wrap_flow():
    tasks = get_today_tasks()
    # naive: mark first task done if anything exists (placeholder logic)
    if tasks:
        mark_task_status(tasks[0]["id"], "Done")
    send_email(subject="Wrap-up", body="Mark remaining tasks Done if finished. I will roll leftovers to tomorrow.")
    return {"ok": True}

def weekly_reset_flow():
    send_email(subject="Weekly reset", body="Pick the top 3 tasks for the coming week. I can pre-block time on the calendar.")
    return {"ok": True}
