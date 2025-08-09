from fastapi import FastAPI, Request, HTTPException
from services.agent import kickoff_flow, nudge_flow, wrap_flow, start_task, complete_task, daily_digest
from services.env import ENV

app = FastAPI()

def _auth(req: Request):
    if req.headers.get("authorization") != f"Bearer {ENV.AGENT_BEARER}":
        raise HTTPException(status_code=401, detail="unauthorized")

@app.post("/hook/kickoff")
def kickoff(request: Request):
    _auth(request); return kickoff_flow()

@app.post("/hook/nudge")
def nudge(request: Request):
    _auth(request); return nudge_flow()

@app.post("/hook/wrap")
def wrap(request: Request):
    _auth(request); return wrap_flow()

@app.post("/hook/digest")
def digest(request: Request):
    _auth(request); return daily_digest()

@app.post("/hook/start")
def start(request: Request, id: str):
    _auth(request); return start_task(id)

@app.post("/hook/done")
def done(request: Request, id: str):
    _auth(request); return complete_task(id)

from fastapi import Header, HTTPException
import os

@app.post("/ping")
def ping(authorization: str = Header(...)):
    expected = f"Bearer {os.environ.get('AGENT_BEARER')}"
    if authorization.strip() == expected:
        return {"ok": True, "message": "Bearer token accepted"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

def _auth(req: Request):
    # Accept header OR ?k= query (for email links)
    auth = req.headers.get("authorization")
    key = req.query_params.get("k")
    if auth == f"Bearer {ENV.AGENT_BEARER}" or key == ENV.AGENT_BEARER:
        return
    raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/hook/start")
def start_get(request: Request, id: str):
    _auth(request); return start_task(id)

@app.get("/hook/done")
def done_get(request: Request, id: str):
    _auth(request); return complete_task(id)
