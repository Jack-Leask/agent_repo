# Newsletter Agent (Option B) – Starter

Minimal scaffold for an evening AI agent that helps you complete tasks from your Notion 30‑day plan, emails you a plan, creates calendar blocks, and follows up until tasks are Done.

## What’s inside
- `main.py` – FastAPI app with 4 endpoints: kickoff, nudge, wrap, weekly_reset
- `services/` – helpers for Notion, Email, Calendar, and the Agent logic
- `.env.example` – fill with your keys
- `requirements.txt` – install deps
- `notion_mapping.json` – map your Notion database property names/IDs

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # add your tokens

uvicorn main:app --reload --port 8080
```

## Endpoints
- `POST /hook/kickoff`  → fetch today’s tasks, pick top 1–3, send plan email, optionally create calendar blocks
- `POST /hook/nudge`    → if nothing is Done, suggest smallest next action and offer a 25‑min block
- `POST /hook/wrap`     → move unfinished tasks to tomorrow, log blockers, summarize
- `POST /hook/weekly_reset` → Sunday planning workflow

All endpoints expect a bearer token (see `.env`).

## Deploy
- Railway, Render, Fly.io, or Azure Container Apps.
- Add cron jobs (platform schedulers) to hit the endpoints at 19:05, 20:00, 21:15 NZ time.
