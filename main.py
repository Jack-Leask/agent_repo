from fastapi import FastAPI, Header, HTTPException
from services.env import ENV
from services.agent import kickoff_flow, nudge_flow, wrap_flow, weekly_reset_flow

app = FastAPI(title="Newsletter Agent", version="0.1.0")

def auth(bearer: str | None):
    if not bearer or bearer != f"Bearer {ENV.AGENT_BEARER}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/hook/kickoff")
def kickoff(authorization: str | None = Header(None)):
    auth(authorization)
    return kickoff_flow()

@app.post("/hook/nudge")
def nudge(authorization: str | None = Header(None)):
    auth(authorization)
    return nudge_flow()

@app.post("/hook/wrap")
def wrap(authorization: str | None = Header(None)):
    auth(authorization)
    return wrap_flow()

@app.post("/hook/weekly_reset")
def weekly_reset(authorization: str | None = Header(None)):
    auth(authorization)
    return weekly_reset_flow()
