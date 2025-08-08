import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class _ENV:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_DB_ID: str = os.getenv("NOTION_DB_ID", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "Agent <no-reply@example.com>")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    CAL_TZ: str = os.getenv("CAL_TZ", "Pacific/Auckland")
    AGENT_BEARER: str = os.getenv("AGENT_BEARER", "")

ENV = _ENV()
