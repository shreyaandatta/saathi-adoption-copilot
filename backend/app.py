"""FastAPI app: serves the chat UI and the Saathi API.

Run:  uvicorn backend.app:app --reload
Then open http://localhost:8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import agent
from .store import Store

app = FastAPI(title="Saathi", description="Agentic adoption copilot (prototype)")
store = Store()

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


class ChatIn(BaseModel):
    customer_id: str
    message: str


class ConfirmIn(BaseModel):
    customer_id: str
    otp: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/customers")
def customers() -> list[dict]:
    return [
        {"id": c["id"], "name": c["name"], "language": c["language"],
         "occupation": c["occupation"], "savings_balance": c["savings_balance"]}
        for c in store.customers.values()
    ]


@app.get("/api/customer/{cid}")
def customer(cid: str) -> dict:
    try:
        return store.customer(cid)
    except KeyError:
        raise HTTPException(404, "unknown customer")


@app.post("/api/chat")
def chat(body: ChatIn) -> dict:
    try:
        return agent.handle(store, body.customer_id, body.message)
    except KeyError:
        raise HTTPException(404, "unknown customer")


@app.post("/api/confirm")
def confirm(body: ConfirmIn) -> dict:
    return agent.confirm(store, body.customer_id, body.otp)


@app.get("/api/audit/{cid}")
def audit(cid: str) -> list:
    return store.audit_log(cid)
