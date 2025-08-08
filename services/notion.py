# Placeholder Notion service. Replace with real Notion SDK calls.
# For now reads a local CSV exported from Notion to simulate tasks.

import csv
from datetime import datetime
from .env import ENV

CSV_PATH = "/mnt/data/NZ_Energy_Newsletter_30Day_Tasks.csv"

def _read_rows():
    rows = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for i, r in enumerate(csv.DictReader(f)):
                r["id"] = str(i+1)
                r["Day"] = int(r["Day"])
                r["Week"] = int(r["Week"])
                rows.append(r)
    except FileNotFoundError:
        pass
    return rows

def get_today_tasks():
    rows = _read_rows()
    # simple demo: return first 3 TODOs
    todays = [r for r in rows if r.get("Status","") == "Todo"]
    return todays[:3]

def mark_task_status(task_id: str, status: str):
    # Placeholder: no writeback in this scaffold.
    return True
