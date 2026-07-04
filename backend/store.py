"""In-memory data store (read-only).

Loads the mock customers and products from JSON. Kept deliberately stateless so
it works unchanged on a serverless platform like Vercel: there is no per-request
session memory here. The small amount of conversation state (which suggestion is
pending, which action is staged) is carried by the client and passed back in,
and the audit trail is assembled client-side. In a real deployment these read
from the bank's systems.
"""

from __future__ import annotations

import json
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

    def customer(self, cid: str) -> dict:
        if cid not in self.customers:
            raise KeyError(f"unknown customer {cid}")
        return self.customers[cid]

    def product(self, code: str) -> dict | None:
        return self.products.get(code)
