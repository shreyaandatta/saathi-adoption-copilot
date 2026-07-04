"""Illustrations, staged actions and the consent gate.

Every number a customer sees is computed here by deterministic formulas — the
language model is never the source of a figure. Anything that moves money is
returned as a *staged* action and can only be executed after an explicit OTP
confirmation (the consent gate).
"""

from __future__ import annotations

import uuid

DEMO_OTP = "1234"  # fixed for the demo; a real build would send a one-time code


def rupees(n: float) -> str:
    return "₹" + f"{round(n):,}"


# ---- illustrations (clearly marked as illustrative, never guarantees) -----

def fd_maturity(principal: float, rate: float, years: int) -> float:
    return principal * (1 + rate) ** years


def sip_future_value(monthly: float, annual_return: float, years: int) -> float:
    i = annual_return / 12
    n = years * 12
    return monthly * (((1 + i) ** n - 1) / i) * (1 + i)


def term_premium(cover: float, per_lakh: float) -> float:
    return (cover / 100000) * per_lakh


def build_illustration(customer: dict, product: dict) -> dict:
    """Return {amount, summary, illustration} for a product + this customer."""
    cat = product["category"]
    if cat == "deposit":
        principal = float(customer["savings_balance"])
        years = product["default_tenure_years"]
        maturity = fd_maturity(principal, product["annual_rate"], years)
        return {
            "amount": principal,
            "summary": f"Fixed Deposit of {rupees(principal)} for {years} years",
            "illustration": (
                f"At about {product['annual_rate']*100:.1f}% a year, {rupees(principal)} "
                f"could grow to roughly {rupees(maturity)} in {years} years. "
                "Illustrative only, not a guarantee."
            ),
        }
    if cat == "investment":
        monthly = max(product["min_amount"], round(customer["avg_monthly_surplus"] * 0.15 / 100) * 100)
        years = product["default_tenure_years"]
        fv = sip_future_value(monthly, product["assumed_return"], years)
        invested = monthly * years * 12
        return {
            "amount": monthly,
            "summary": f"SIP of {rupees(monthly)} every month for {years} years",
            "illustration": (
                f"Putting in {rupees(monthly)} a month, you would invest {rupees(invested)} over "
                f"{years} years. At an assumed {product['assumed_return']*100:.0f}% return that could "
                f"be around {rupees(fv)}. Markets vary — this is illustrative, not a promise."
            ),
        }
    if cat == "insurance":
        cover = float(product["default_cover"])
        premium = term_premium(cover, product["monthly_premium_per_lakh"])
        return {
            "amount": premium,
            "summary": f"Term cover of {rupees(cover)}",
            "illustration": (
                f"About {rupees(premium)} a month gives your family {rupees(cover)} of cover. "
                "Final premium depends on the insurer's underwriting."
            ),
        }
    return {"amount": 0, "summary": product["name"], "illustration": ""}


def stage_action(customer: dict, product: dict) -> dict:
    """Create an action that is ready to run but blocked on consent."""
    ill = build_illustration(customer, product)
    return {
        "id": "ACT-" + uuid.uuid4().hex[:8].upper(),
        "product_code": product["code"],
        "product_name": product["name"],
        "amount": ill["amount"],
        "summary": ill["summary"],
        "needs_consent": True,
        "otp_hint": DEMO_OTP,
    }


def execute(action: dict, otp: str) -> dict:
    """Run a staged action once the OTP matches. Returns a booking result."""
    if otp.strip() != DEMO_OTP:
        return {"ok": False, "message": "That OTP didn't match. Please try again."}
    ref = "SB" + uuid.uuid4().hex[:10].upper()
    return {
        "ok": True,
        "reference": ref,
        "message": f"Done. Your {action['product_name']} is set up (ref {ref}).",
    }
