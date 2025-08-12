import os
import traceback
from typing import Optional

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To
except Exception:
    SendGridAPIClient = None  # type: ignore

SG_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "").strip()  # must be a verified Single Sender
SENDER_NAME = os.getenv("SENDER_NAME", "Agent Mailer").strip()

sg: Optional[SendGridAPIClient] = None
if SG_API_KEY and SendGridAPIClient:
    try:
        sg = SendGridAPIClient(SG_API_KEY)
        print("[email] SendGrid mailer loaded")
    except Exception as e:
        print(f"[email] Failed to init SendGrid: {e}")
else:
    print("[email] SendGrid not configured; set SENDGRID_API_KEY")

def _log_resp(prefix: str, resp) -> None:
    try:
        print(f"[email] {prefix} status={resp.status_code}")
    except Exception:
        # Keep logs safe even if resp isn't what we expect
        print(f"[email] {prefix} sent (no status available)")

def _send(subject: str, html: str, to_email: str) -> bool:
    """Send an HTML email via SendGrid Single Sender."""
    if not sg:
        print("[email] SendGrid client not available")
        return False
    if not SENDER_EMAIL:
        print("[email] SENDER_EMAIL missing (needs to be a verified Single Sender)")
        return False
    try:
        msg = Mail(
            from_email=Email(SENDER_EMAIL, SENDER_NAME),
            to_emails=[To(to_email)],
            subject=subject,
            html_content=html,
        )
        resp = sg.send(msg)
        _log_resp("send", resp)
        return 200 <= getattr(resp, "status_code", 500) < 300
    except Exception as e:
        print(f"[email] send failed: {e}\n{traceback.format_exc()}")
        return False

# Public helpers your agent calls
def send_digest(to_email: str, subject: str, html: str) -> bool:
    return _send(subject, html, to_email)

def send_kickoff_plan(to_email: str, subject: str, html: str) -> bool:
    return _send(subject, html, to_email)

def send_wrap(to_email: str, subject: str, html: str) -> bool:
    return _send(subject, html, to_email)
