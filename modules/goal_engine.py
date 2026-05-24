"""
goal_engine.py
Converts natural-language goal statements into structured goal dicts.
"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Maps common item keywords to sensible default amounts (₱)
_AMOUNT_HINTS = {
    "laptop":        50_000,
    "phone":         25_000,
    "smartphone":    25_000,
    "iphone":        60_000,
    "concert":        5_000,
    "ticket":         3_000,
    "vacation":      30_000,
    "travel":        30_000,
    "trip":          20_000,
    "car":          700_000,
    "motorcycle":   100_000,
    "emergency fund": 50_000,
    "emergency":     50_000,
    "tuition":       30_000,
    "school":        15_000,
    "rent":          15_000,
    "wedding":      200_000,
    "gadget":        20_000,
    "airpods":       15_000,
    "tablet":        25_000,
}

_MONTH_NAMES = (
    "january|february|march|april|may|june|"
    "july|august|september|october|november|december"
)


def _extract_amount(text: str) -> float:
    """Pull the first peso amount from the text, else 0."""
    # Handles: ₱50,000 / 50000 / 50,000 / P50000
    match = re.search(r"[₱P]?\s?([\d,]+(?:\.\d+)?)\b", text)
    if match:
        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


def _infer_amount_from_keyword(text_lower: str) -> float:
    for keyword, amount in _AMOUNT_HINTS.items():
        if keyword in text_lower:
            return float(amount)
    return 0.0


def _extract_goal_name(text_lower: str) -> str:
    patterns = [
        r"(?:save for|saving for|to buy|for a|for an|for my|for the)\s+(.+?)(?:\s+(?:in|by|within|before|worth|costing|amounting)|$)",
        r"(?:want to|plan to|trying to)\s+(?:save|buy|purchase|get)\s+(.+?)(?:\s+(?:in|by|within|before)|$)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text_lower)
        if m:
            name = m.group(1).strip().title()
            # Trim trailing noise words
            name = re.sub(
                r"\s*(worth|costing|amounting|that costs?|priced at).*$",
                "",
                name,
                flags=re.IGNORECASE,
            ).strip()
            if name:
                return name
    return "Savings Goal"


def _extract_deadline(text_lower: str, today: datetime) -> str | None:
    """Return deadline string or None if not found."""

    # Pattern: "in X months"
    m = re.search(r"in\s+(\d+)\s+month", text_lower)
    if m:
        return (today + relativedelta(months=int(m.group(1)))).strftime("%Y-%m-%d")

    # Pattern: "within X months"
    m = re.search(r"within\s+(\d+)\s+month", text_lower)
    if m:
        return (today + relativedelta(months=int(m.group(1)))).strftime("%Y-%m-%d")

    # Pattern: "in X years" / "within X years"
    m = re.search(r"(?:in|within)\s+(\d+)\s+year", text_lower)
    if m:
        return (today + relativedelta(years=int(m.group(1)))).strftime("%Y-%m-%d")

    # Pattern: "by January 2027" / "before Dec 2026"
    m = re.search(
        rf"(?:by|before|until)\s+({_MONTH_NAMES})\s+(\d{{4}})",
        text_lower,
    )
    if m:
        try:
            d = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %Y")
            return d.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Pattern: ISO date "2026-12-31"
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text_lower)
    if m:
        return m.group(1)

    return None


def extract_goal_from_text(text: str, monthly_income: float = 0.0) -> dict:
    """
    Parse a natural-language goal statement into a structured dict.

    Returns:
        {
            "goal_name":     str,
            "target_amount": float,
            "deadline":      str,   # YYYY-MM-DD
        }
    """
    today = datetime.today()
    text_lower = text.lower()

    # --- Amount ---
    target_amount = _extract_amount(text)
    if target_amount == 0.0:
        target_amount = _infer_amount_from_keyword(text_lower)

    # --- Goal name ---
    goal_name = _extract_goal_name(text_lower)

    # --- Deadline ---
    deadline = _extract_deadline(text_lower, today)

    # If no deadline given, estimate from monthly income (20% savings rate)
    if deadline is None:
        if monthly_income > 0 and target_amount > 0:
            monthly_savings = monthly_income * 0.20
            estimated_months = max(1, round(target_amount / monthly_savings))
            deadline = (
                today + relativedelta(months=estimated_months)
            ).strftime("%Y-%m-%d")
        else:
            # Default: 6 months
            deadline = (today + relativedelta(months=6)).strftime("%Y-%m-%d")

    return {
        "goal_name":     goal_name,
        "target_amount": target_amount,
        "deadline":      deadline,
    }