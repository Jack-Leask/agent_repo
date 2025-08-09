# services/notion.py — Notion API integration (production-ready)
# Reads tasks from a Notion database and updates Status.
# Expects env vars:
#   NOTION_API_KEY or NOTION_TOKEN
#   NOTION_DB_ID or NOTION_DATABASE_ID
#
# Required Notion properties (exact names/types):
#   Task (Title), Week (Number), Day (Number), Status (Select with option "Todo")

from __future__ import annotations
import os
import datetime as dt
import requests
from typing import Any, Dict, List

# --- Env / Config -------------------------------------------------------------

NOTION_TOKEN = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN", "")
DB_ID = os.getenv("NOTION_DB_ID") or os.getenv("NOTION_DATABASE_ID", "")

NOTION_VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# --- Utilities ----------------------------------------------------------------

def _notion_request(method: str, path: str, json: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Thin wrapper around requests with better logs for debugging."""
    url = f"{BASE}{path}"
    try:
        r = requests.request(method, url, headers=HEADERS, json=json, timeout=20)
        if not r.ok:
            print(f"[notion] HTTP {r.status_code} on {path}: {r.text[:500]}")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Bubble up so FastAPI returns 500 and Railway logs show this line.
        print(f"[notion] Exception {method} {path}: {e}")
        raise

def _get_first_plain_text(rich_text: List[Dict[str, Any]] | None) -> str:
    if not rich_text:
        return ""
    item = rich_text[0]
    return (item.get("plain_text") or
            (item.get("text") or {}).get("content") or
            "")

def _page_props(page: Dict[str, Any]) -> Dict[str, Any]:
    """Extract our known properties safely."""
    props = page.get("properties", {})
    title = _get_first_plain_text(props.get("Task", {}).get("title"))
    day = props.get("Day", {}).get("number")
    week = props.get("Week", {}).get("number")
    status = (props.get("Status", {}).get("select") or {}).get("name")
    return {
        "id": page.get("id"),
        "Task": title,
        "Day": day,
        "Week": week,
        "Status": status,
    }

# --- Public API ---------------------------------------------------------------

def get_today_tasks() -> List[Dict[str, Any]]:
    """
    Returns up to 3 Todo items ordered by Day ascending.
    (We do NOT filter by calendar date to avoid mismatches with a 1–30 plan.)
    """
    if not NOTION_TOKEN or not DB_ID:
        print("[notion] Missing NOTION_API_KEY/NOTION_TOKEN or NOTION_DB_ID/NOTION_DATABASE_ID.")
        return []

    payload = {
        "filter": {"property": "Status", "select": {"equals": "Todo"}},
        "sorts": [{"property": "Day", "direction": "ascending"}],
        "page_size": 3,
    }
    data = _notion_request("POST", f"/databases/{DB_ID}/query", json=payload)
    results = data.get("results", [])
    tasks = [_page_props(p) for p in results]

    if not tasks:
        print("[notion] No Todo tasks returned. Check property names/types and ensure at least one row has Status=Todo.")
    else:
        print(f"[notion] Fetched {len(tasks)} task(s). First: {tasks[0].get('Task')} (Day {tasks[0].get('Day')})")

    return tasks

def mark_task_status(page_id: str, status: str) -> bool:
    """
    Update a Notion page's Status select to the given value (e.g., 'Done', 'Doing').
    """
    if not NOTION_TOKEN:
        print("[notion] Missing NOTION_API_KEY/NOTION_TOKEN.")
        return False

    body = {"properties": {"Status": {"select": {"name": status}}}}
    _notion_request("PATCH", f"/pages/{page_id}", json=body)
    print(f"[notion] Updated {page_id} -> Status='{status}'")
    return True

# Optional helper you can call elsewhere if needed
def list_todos(limit: int = 10) -> List[Dict[str, Any]]:
    """List Todo items (useful for debugging)."""
    payload = {
        "filter": {"property": "Status", "select": {"equals": "Todo"}},
        "sorts": [{"property": "Day", "direction": "ascending"}],
        "page_size": max(1, min(limit, 100)),
    }
    data = _notion_request("POST", f"/databases/{DB_ID}/query", json=payload)
    return [_page_props(p) for p in data.get("results", [])]
def get_page_title(page_id: str) -> str:
    r = requests.get(f"{BASE}/pages/{page_id}", headers=HEADERS, timeout=20)
    r.raise_for_status()
    p = r.json().get("properties", {})
    return _get_first_plain_text(p.get("Task", {}).get("title"))

def append_note(page_id: str, text: str) -> bool:
    r = requests.patch(
        f"{BASE}/pages/{page_id}",
        headers=HEADERS,
        json={"properties": {
            "Notes/Links": {"rich_text": [{"text": {"content": text}}]}
        }},
        timeout=20,
    )
    r.raise_for_status()
    return True

