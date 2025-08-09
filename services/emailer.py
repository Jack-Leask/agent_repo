# top of file
EMAIL_TO   = os.getenv("EMAIL_TO") or os.getenv("EMAIL_USER")

def _send_mail(subject: str, html: str, to: str = None):
    to = to or EMAIL_TO   # use EMAIL_TO first, fallback to EMAIL_USER
    ...

import smtplib, ssl, os
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
FROM_NAME  = os.getenv("FROM_NAME", "Newsletter Agent")
TOKEN = os.getenv("AGENT_BEARER")  # add near top

def _send_mail(subject: str, html: str, to: str = None):
    to = to or EMAIL_USER
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{EMAIL_USER}>"
    msg["To"] = to
    msg.set_content("HTML only")
    msg.add_alternative(html, subtype="html")
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(context=ctx)
        s.login(EMAIL_USER, EMAIL_PASS)
        s.send_message(msg)

def send_digest(tasks, base_url: str):
    def row(t):
        return f"""
        <tr>
          <td>{t.get('Task')}</td>
          <td>Day {t.get('Day')}</td>
          <td><a href="{base_url}/hook/start?id={t.get('id')}">Start</a> |
              <a href="{base_url}/hook/done?id={t.get('id')}">Done</a></td>
        </tr>"""
    rows = "".join(row(t) for t in tasks) or "<tr><td colspan=3>No tasks</td></tr>"
    html = f"""
    <h3>Tonight’s top tasks</h3>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Task</th><th>When</th><th>Actions</th></tr>
      {rows}
    </table>"""
    _send_mail("NZ Energy — Tonight’s tasks", html)

def send_kickoff_plan(title: str, plan: list[str]):
    li = "".join(f"<li>{p}</li>" for p in plan)
    html = f"<h3>Kickoff: {title}</h3><ol>{li}</ol>"
    _send_mail(f"Kickoff plan — {title}", html)

def send_wrap(text: str):
    _send_mail("Wrap", f"<p>{text}</p>")

def _send_mail(subject: str, html: str, to: str = None):
    to = to or EMAIL_USER
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{EMAIL_USER}>"
    msg["To"] = to
    msg.set_content("HTML only")
    msg.add_alternative(html, subtype="html")
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(EMAIL_USER, EMAIL_PASS)
            s.send_message(msg)
    except Exception as e:
        print(f"[email] send failed: {e}")

def send_digest(tasks, base_url: str):
    def row(t):
        return f"""
        <tr>
          <td>{t.get('Task')}</td>
          <td>Day {t.get('Day')}</td>
          <td><a href="{base_url}/hook/start?id={t.get('id')}&k={TOKEN}">Start</a> |
              <a href="{base_url}/hook/done?id={t.get('id')}&k={TOKEN}">Done</a></td>
        </tr>"""
    ...

print(f"[email] sending to {to} via {SMTP_HOST}:{SMTP_PORT} as {EMAIL_USER}")
with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
    s.starttls(context=ctx)
    s.login(EMAIL_USER, EMAIL_PASS)
    s.send_message(msg)
print("[email] sent ok")
