"""In-memory data store.

Loads the mock customers and products, and keeps per-customer session state
(the pending suggestion, a staged action awaiting consent) plus a running
audit log. In a real deployment these would be backed by the bank's systems;
here they are simple JSON files so the demo runs with zero setup.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> Any:
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


class Store:
    def __init__(self) -> None:
        self.customers = {c["id"]: c for c in _load("customers.json")}
        self.products = {p["code"]: p for p in _load("products.json")}
        # session[customer_id] = {"pending": product_code, "staged": action}
        self.sessions: dict[str, dict] = {}
        # audit[customer_id] = [ {ts, action, detail}, ... ]
        self.audit: dict[str, list] = {}

    # ---- customers / products -------------------------------------------
    def customer(self, cid: str) -> dict:
        if cid not in self.customers:
            raise KeyError(f"unknown customer {cid}")
        return self.customers[cid]

    def product(self, code: str) -> dict | None:
        return self.products.get(code)

    # ---- session state ---------------------------------------------------
    def session(self, cid: str) -> dict:
        return self.sessions.setdefault(cid, {"pending": None, "staged": None})

    def set_pending(self, cid: str, code: str | None) -> None:
        self.session(cid)["pending"] = code

    def stage(self, cid: str, action: dict) -> None:
        self.session(cid)["staged"] = action

    def clear_session(self, cid: str) -> None:
        self.sessions[cid] = {"pending": None, "staged": None}

    # ---- audit trail -----------------------------------------------------
    def log(self, cid: str, action: str, detail: str) -> None:
        self.audit.setdefault(cid, []).append(
            {"ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
             "action": action, "detail": detail}
        )

    def audit_log(self, cid: str) -> list:
        return self.audit.get(cid, [])
