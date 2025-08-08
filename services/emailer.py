import smtplib, ssl
from email.mime.text import MIMEText
from .env import ENV

def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = ENV.EMAIL_FROM
    msg['To'] = ENV.EMAIL_TO

    if not ENV.SMTP_HOST or not ENV.SMTP_USER:
        print("[DEV] Email would send:\n", subject, "\n", body)
        return True

    context = ssl.create_default_context()
    with smtplib.SMTP(ENV.SMTP_HOST, ENV.SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(ENV.SMTP_USER, ENV.SMTP_PASS)
        server.sendmail(ENV.EMAIL_FROM, [ENV.EMAIL_TO], msg.as_string())
    return True
