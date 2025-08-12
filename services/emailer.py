"""
emailer.py — SendGrid Single Sender
- No SMTP. No Outlook.
- Uses SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, SENDGRID_TO_EMAIL.
- Optional: FROM_NAME, REPLY_TO, APP_BASE_URL, AGENT_BEARER.
"""

import os
from html import escape
from typing import Iterable, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# --- Env ---
SG_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL", FROM_EMAIL).strip()
FROM_NAME = os.getenv("FROM_NAME", "Newsletter Agent").strip()
REPLY_TO = os.getenv("REPLY_TO", "").strip()

APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")
AGENT_BEARER = os.getenv("AGENT_BEARER", "").strip()

# Debug banner so you can see the right module loaded
print("[email] SendGrid mailer loaded")

# --- Helpers ---
def _require_env():
    missing = []
    if not SG_API_KEY:   missing.append("SENDGRID_API_KEY")
    if not FROM_EMAIL:   missing.append("SENDGRID_FROM_EMAIL")
    if not TO_EMAIL:     missing.append("SENDGRID_TO_EMAIL")
    if missing:
        raise RuntimeError(f"[email] Missing env var(s): {', '.join(missing)}")

def _sg():
    _require_env()
    return SendGridAPIClient(SG_API_KEY)

def _plain_from_html(html: str) -> str:
    # quick text fallback
    import re
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</(p|div|li|tr|h\d)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

def send_email(subject: str, html: str, to_email: Optional[str] = None) -> bool:
    """Send an email via SendGrid Single Sender."""
    try:
        client = _sg()
        msg = Mail(
            from_email=Email(FROM_EMAIL, FROM_NAME),
            to_emails=To(to_email or TO_EMAIL),
            subject=subject,
            html_content=Content("text/html", html),
        )
        # add plain text fallback
        msg.add_content(Content("text/plain", _plain_from_html(html)))
        if REPLY_TO:
            msg.reply_to = Email(REPLY_TO)

        client.send(msg)
        print(f"[email] sent via SendGrid as {FROM_EMAIL}")
        return True
    except Exception as e:
        print(f"[email] send failed: {e}")
        return False
    resp = client.send(msg)
print(f"[email] SG status={resp.status_code}, body={resp.body}, headers={resp.headers}")


# --- Domain-specific helpers you’re calling from the agent ---

def _row(task: dict) -> str:
    """Build one row for the digest table."""
    title = escape(str(task.get("Task") or task.get("title") or "(untitled)"))
    day = escape(str(task.get("Day") or task.get("due") or ""))
    url = escape(str(task.get("url") or ""))

    # Action links (optional, only shown if APP_BASE_URL and AGENT_BEARER are set)
    actions = ""
    if APP_BASE_URL and AGENT_BEARER and task.get("id"):
        tid = escape(str(task["id"]))
        start = f'{APP_BASE_URL}/hook/start?id={tid}&k={AGENT_BEARER}'
        done  = f'{APP_BASE_URL}/hook/done?id={tid}&k={AGENT_BEARER}'
        actions = f'<a href="{start}">Start</a> | <a href="{done}">Done</a>'

    link = f' <a href="{url}">🔗</a>' if url else ""
    when = f"Day {day}" if day else ""
    return f"""
      <tr>
        <td>{title}{link}</td>
        <td>{when}</td>
        <td>{actions}</td>
      </tr>
    """

def send_digest(tasks: Iterable[dict], base_url: Optional[str] = None) -> bool:
    """Send the Notion digest email (HTML table)."""
    rows = "".join(_row(t) for t in tasks) if tasks else ""
    if not rows:
        rows = '<tr><td colspan="3">No tasks</td></tr>'

    # Allow runtime override of base URL for this call
    bu = (base_url or APP_BASE_URL).rstrip("/") if (base_url or APP_BASE_URL) else ""
    if bu and bu != APP_BASE_URL:
        print(f"[email] using base_url override: {bu}")

    html = f"""
    <h3>Tonight’s top tasks</h3>
    <table border="1" cellpadding="6" cellspacing="0">
      <thead><tr><th>Task</th><th>When</th><th>Actions</th></tr></thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    """
    return send_email("NZ Energy — Tonight’s tasks", html)

def send_kickoff_plan(title: str, plan: Iterable[str]) -> bool:
    items = "".join(f"<li>{escape(p)}</li>" for p in plan)
    html = f"<h3>Kickoff: {escape(title)}</h3><ol>{items}</ol>"
    return send_email(f"Kickoff plan — {title}", html)

def send_wrap(text: str) -> bool:
    html = f"<p>{escape(text)}</p>"
    return send_email("Wrap", html)
