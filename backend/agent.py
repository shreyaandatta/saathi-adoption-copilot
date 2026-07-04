"""The orchestrator (stateless).

Turns a customer message into a reply and, when appropriate, a staged action.
It plans the conversation and translates jargon; it does not decide products
(rules.py) or invent numbers (journey.py).

State handling: the tiny bit of conversation state — which suggestion is
"pending" a yes/no — is passed in and returned, so the caller (the client) owns
it. This keeps the backend fully stateless and safe on serverless platforms.
Intent detection is a small keyword parser so the demo runs offline; the
natural-language re-voicing is the optional Claude layer in llm.py.
"""

from __future__ import annotations

from . import journey, llm, rules
from .store import Store

CONFIRM = {"yes", "yeah", "ok", "okay", "haan", "han", "karo", "kardo", "sure",
           "go ahead", "do it", "proceed", "set it up", "theek hai", "confirm"}
BALANCE = {"balance", "kitna", "how much", "paisa hai"}
FD_WORDS = {"fd", "fixed deposit", "deposit"}
SIP_WORDS = {"sip", "invest", "mutual", "grow my money", "systematic"}
INS_WORDS = {"insurance", "term", "cover", "family", "suraksha"}
EXPLORE = {"idle", "sitting", "what can i do", "options", "suggest", "kya karu",
           "kya karun", "money", "savings", "extra", "spare"}
GREET = {"hi", "hello", "hey", "namaste", "namaskar"}


def _has(text: str, words: set[str]) -> bool:
    return any(w in text for w in words)


def _explain_and_offer(customer: dict, product: dict) -> dict:
    """Explain a product with a grounded illustration and offer to set it up."""
    ill = journey.build_illustration(customer, product)
    base = (
        f"{product['one_liner']} {ill['illustration']} "
        f"Shall I set up your {ill['summary'].lower()}? Just say yes."
    )
    return {"reply": llm.rephrase(base, customer["language"]),
            "proposal": None, "pending": product["code"]}


def handle(store: Store, cid: str, message: str, pending: str | None = None) -> dict:
    customer = store.customer(cid)
    text = message.lower().strip()

    # 1) The customer is confirming a suggestion we already made.
    if _has(text, CONFIRM) and pending:
        product = store.product(pending)
        action = journey.stage_action(customer, product)
        reply = ("Great. Here's exactly what will happen — please confirm with your "
                 "OTP to go ahead. Nothing moves until you do.")
        return {"reply": llm.rephrase(reply, customer["language"]),
                "proposal": action, "pending": None}

    # 2) Balance question.
    if _has(text, BALANCE):
        bal = journey.rupees(customer["savings_balance"])
        return {"reply": llm.rephrase(f"Your savings balance is {bal}.", customer["language"]),
                "proposal": None, "pending": None}

    # 3) A specific product the customer asked about.
    for words, code in ((FD_WORDS, "FD"), (SIP_WORDS, "SIP"), (INS_WORDS, "TERM")):
        if _has(text, words):
            product = store.product(code)
            if product and rules.is_eligible(customer, product):
                return _explain_and_offer(customer, product)
            return {"reply": llm.rephrase(
                f"You're not eligible for {product['name'] if product else 'that'} right now, "
                "but I can suggest something that fits you. Want to see?",
                customer["language"]), "proposal": None, "pending": None}

    # 4) Open exploration → next best action from the rules engine.
    if _has(text, EXPLORE):
        product = rules.next_best_action(customer, store.products)
        if product:
            return _explain_and_offer(customer, product)

    # 5) Greeting / fallback.
    name = customer["name"].split()[0]
    hint = "You can ask me what to do with idle money, or about an FD, SIP or insurance."
    return {"reply": llm.rephrase(f"Namaste {name}! {hint}", customer["language"]),
            "proposal": None, "pending": None}


def confirm(action: dict | None, otp: str) -> dict:
    """Execute a staged action (passed back by the client) once the OTP matches."""
    if not action:
        return {"ok": False, "message": "There's nothing waiting to be confirmed."}
    return journey.execute(action, otp)
