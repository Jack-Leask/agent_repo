# services/notion.py – Notion API version
import os, requests, datetime
from .env import ENV

BASE = "https://api.notion.com/v1"
NOTION_TOKEN = os.getenv("NOTION_API_KEY") or ENV.NOTION_TOKEN
DB_ID = os.getenv("NOTION_DB_ID") or os.getenv("NOTION_DATABASE_ID") or ENV.NOTION_DB_ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def _query(payload):
    r = requests.post(f"{BASE}/databases/{DB_ID}/query", headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def _page_props(page):
    p = page.get("properties", {})
    title = p.get("Task", {}).get("title", [{}])[0].get("plain_text", "")
    day = p.get("Day", {}).get("number")
    week = p.get("Week", {}).get("number")
    status = (p.get("Status", {}).get("select") or {}).get("name")
    return {"id": page["id"], "Task": title, "Day": day, "Week": week, "Status": status}

def get_today_tasks():
    today = datetime.datetime.now().day
    # Try: Day == today & Status == Todo
    payload = {
        "filter": {
            "and": [
                {"property": "Status", "select": {"equals": "Todo"}},
                {"property": "Day", "number": {"equals": today}},
            ]
        },
        "sorts": [{"property": "Day", "direction": "ascending"}],
        "page_size": 3,
    }
    data = _query(payload)
    results = data.get("results", [])
    if not results:
        # Fallback: any Todo, earliest Day first
        payload = {
            "filter": {"property": "Status", "select": {"equals": "Todo"}},
            "sorts": [{"property": "Day", "direction": "ascending"}],
            "page_size": 3,
        }
        results = _query(payload).get("results", [])
    return [_page_props(p) for p in results]

def mark_task_status(page_id: str, status: str):
    r = requests.patch(
        f"{BASE}/pages/{page_id}",
        headers=HEADERS,
        json={"properties": {"Status": {"select": {"name": status}}}},
        timeout=20,
    )
    r.raise_for_status()
    return True
