"""Product eligibility + suitability engine.

This is the *source of truth* for what a customer may be offered. The agent
never invents products or decides suitability on its own — it reads the answer
from here. In a real bank this maps onto the existing, compliant product-rules
engine; the point of keeping it separate is exactly that separation.
"""

from __future__ import annotations


def is_eligible(customer: dict, product: dict) -> bool:
    e = product.get("eligibility", {})
    if "min_savings_balance" in e and customer["savings_balance"] < e["min_savings_balance"]:
        return False
    if "min_monthly_surplus" in e and customer["avg_monthly_surplus"] < e["min_monthly_surplus"]:
        return False
    if "min_age" in e and customer["age"] < e["min_age"]:
        return False
    if "max_age" in e and customer["age"] > e["max_age"]:
        return False
    if e.get("requires_no_existing_term") and customer.get("has_term_insurance"):
        return False
    return True


def eligible_products(customer: dict, products: dict) -> list[dict]:
    return [p for p in products.values() if is_eligible(customer, p)]


def _opportunity_score(customer: dict, product: dict) -> float:
    """Rough ranking of how much value this product unlocks for this customer.

    Deposits score on idle lump-sum, investments on annual surplus, insurance
    on the protection gap. Deterministic and explainable on purpose.
    """
    cat = product["category"]
    if cat == "deposit":
        return float(customer["savings_balance"])
    if cat == "investment":
        return float(customer["avg_monthly_surplus"]) * 12
    if cat == "insurance":
        return 30000.0  # a fixed "importance" weight for having any cover at all
    return 0.0


# tie-break order so the pick is stable and sensible
_CATEGORY_ORDER = {"deposit": 0, "investment": 1, "insurance": 2}


def next_best_action(customer: dict, products: dict) -> dict | None:
    eligible = eligible_products(customer, products)
    if not eligible:
        return None
    eligible.sort(
        key=lambda p: (-_opportunity_score(customer, p), _CATEGORY_ORDER.get(p["category"], 9))
    )
    return eligible[0]
