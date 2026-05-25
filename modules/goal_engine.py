"""
goal_engine.py
Converts natural-language goal statements into structured dicts.
AI is primary parser; regex is the fallback.
Handles: no amount, no deadline, vague goals.
"""

import re
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ── Keyword → sensible default Philippine price (₱) ──────────────────────────
_AMOUNT_HINTS = {
    "laptop":          50_000,
    "macbook":         90_000,
    "macbook pro":    120_000,
    "phone":           25_000,
    "smartphone":      25_000,
    "iphone":          65_000,
    "samsung":         40_000,
    "android":         20_000,
    "concert":          5_000,
    "ticket":           3_000,
    "vacation":        30_000,
    "travel":          30_000,
    "trip":            20_000,
    "japan":           60_000,
    "korea":           50_000,
    "europe":         100_000,
    "car":            700_000,
    "motorcycle":     100_000,
    "motor":          100_000,
    "emergency fund":  50_000,
    "emergency":       50_000,
    "tuition":         30_000,
    "school":          15_000,
    "rent":            15_000,
    "wedding":        200_000,
    "gadget":          20_000,
    "airpods":         15_000,
    "tablet":          25_000,
    "ipad":            40_000,
    "camera":          30_000,
    "investment":      50_000,
    "business":       100_000,
    "capital":        100_000,
    "house":        1_000_000,
    "condo":          500_000,
    "savings":         20_000,
    "fund":            20_000,
}

_MONTH_MAP = {
    "jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06",
    "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12",
    "january":"01","february":"02","march":"03","april":"04",
    "june":"06","july":"07","august":"08",
    "september":"09","october":"10","november":"11","december":"12",
}
_MONTH_PAT = (
    r"january|february|march|april|may|june|july|august|"
    r"september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
)


# ── Regex helpers ─────────────────────────────────────────────────────────────

def _regex_amount(text: str) -> float:
    """₱50,000 / P50000 / 50000 / 50,000"""
    # Try explicit peso prefix first
    m = re.search(r"[₱Pp]\s?([\d,]+(?:\.\d+)?)", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    # Bare number with comma thousands separator (≥ 3 digits)
    m = re.search(r"\b([\d]{1,3}(?:,[\d]{3})+(?:\.\d+)?)\b", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    # Plain number ≥ 4 digits
    m = re.search(r"\b(\d{4,}(?:\.\d+)?)\b", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0


def _keyword_amount(text_lower: str) -> float:
    # Longer keywords first to avoid partial matches
    for kw in sorted(_AMOUNT_HINTS.keys(), key=len, reverse=True):
        if kw in text_lower:
            return float(_AMOUNT_HINTS[kw])
    return 0.0


def _regex_goal_name(text_lower: str) -> str:
    patterns = [
        r"(?:save for|saving for|to buy|for a|for an|for my|for the|"
        r"purchase a|purchase an|get a|get an|buy a|buy an)\s+"
        r"(.+?)(?:\s+(?:in|by|within|before|worth|costing|that costs?)|$)",
        r"(?:want to|plan to|trying to|planning to|hoping to)\s+"
        r"(?:save|buy|purchase|get|have|build)\s+"
        r"(.+?)(?:\s+(?:in|by|within|before)|$)",
        r"(?:save|build|create)\s+(?:up\s+)?(?:an?\s+)?(.+?)\s+"
        r"(?:fund|savings|goal)",
    ]
    for p in patterns:
        m = re.search(p, text_lower)
        if m:
            name = m.group(1).strip().title()
            name = re.sub(
                r"\s*(worth|costing|amounting|totaling|that costs?|"
                r"priced at|of\s+[₱p\d]).*$",
                "", name, flags=re.IGNORECASE,
            ).strip()
            if name and len(name) > 1 and not name.replace(",","").replace(".","").isdigit():
                return name
    return "Savings Goal"


def _regex_deadline(text_lower: str, today: datetime) -> str | None:
    # "in/within X months"
    m = re.search(r"(?:in|within)\s+(\d+)\s+month", text_lower)
    if m:
        return (today + relativedelta(months=int(m.group(1)))).strftime("%Y-%m-%d")
    # "in/within X weeks"
    m = re.search(r"(?:in|within)\s+(\d+)\s+week", text_lower)
    if m:
        return (today + relativedelta(weeks=int(m.group(1)))).strftime("%Y-%m-%d")
    # "in/within X years"
    m = re.search(r"(?:in|within)\s+(\d+)\s+year", text_lower)
    if m:
        return (today + relativedelta(years=int(m.group(1)))).strftime("%Y-%m-%d")
    # "next year" / "next month"
    if "next year"  in text_lower:
        return (today + relativedelta(years=1)).strftime("%Y-%m-%d")
    if "next month" in text_lower:
        return (today + relativedelta(months=1)).strftime("%Y-%m-%d")
    # "by/before/until January 2027"
    m = re.search(rf"(?:by|before|until|on|end of)\s+({_MONTH_PAT})\s+(\d{{4}})", text_lower)
    if m:
        mon = _MONTH_MAP.get(m.group(1).lower()[:3], "01")
        return f"{m.group(2)}-{mon}-01"
    # "by December" (no year)
    m = re.search(rf"(?:by|before|until|end of)\s+({_MONTH_PAT})\b", text_lower)
    if m:
        mon_num = int(_MONTH_MAP.get(m.group(1).lower()[:3], "01"))
        yr = today.year + (1 if mon_num <= today.month else 0)
        return f"{yr}-{mon_num:02d}-01"
    # ISO date
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text_lower)
    if m:
        return m.group(1)
    # "end of 2027"
    m = re.search(r"end of\s+(\d{4})", text_lower)
    if m:
        return f"{m.group(1)}-12-31"
    return None


def _estimate_deadline(target_amount: float, monthly_income: float, today: datetime) -> str:
    """Estimate deadline using 20% savings rate. Minimum 1 month."""
    if monthly_income > 0 and target_amount > 0:
        months = max(1, round(target_amount / (monthly_income * 0.20)))
    else:
        months = 6
    return (today + relativedelta(months=months)).strftime("%Y-%m-%d")


# ── AI parser (primary) ───────────────────────────────────────────────────────

def _ai_parse(text: str, monthly_income: float, today: datetime) -> dict | None:
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return None
        client = OpenAI(api_key=key)
        today_str = today.strftime("%Y-%m-%d")

        prompt = f"""Today: {today_str}
Monthly income: ₱{monthly_income:,.2f}

Parse this Filipino user's financial goal:
"{text}"

Rules:
1. goal_name: short, descriptive (e.g. "Laptop Fund", "Travel to Japan", "Emergency Fund")
2. target_amount: peso amount as a number.
   - If explicitly stated, use it.
   - If NOT stated, infer from the item type using Philippine market prices.
     Common defaults: laptop=50000, phone=25000, iphone=65000, travel/vacation=30000,
     emergency fund=50000, car=700000, wedding=200000, business capital=100000,
     concert ticket=5000, gadget=20000, general savings=20000.
3. deadline: YYYY-MM-DD string.
   - If a timeframe is given ("6 months", "by December 2026"), compute from today.
   - If NO deadline is given, estimate: ceil(target_amount / (monthly_income * 0.20)) months from today.
   - Minimum: 1 month from today. Never return a past date.

Return ONLY valid JSON, no markdown fences:
{{"goal_name": "...", "target_amount": 0, "deadline": "YYYY-MM-DD"}}"""

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial goal parser for Filipinos. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=120,
        )
        raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        data = json.loads(raw)

        goal_name     = str(data.get("goal_name", "") or "").strip() or "Savings Goal"
        target_amount = float(data.get("target_amount", 0) or 0)
        deadline      = str(data.get("deadline", "") or "").strip()

        # Validate deadline
        if deadline:
            try:
                dl_dt = datetime.strptime(deadline, "%Y-%m-%d")
                if dl_dt <= today:          # never return a past date
                    deadline = ""
            except ValueError:
                deadline = ""

        if not deadline:
            deadline = _estimate_deadline(target_amount or 20_000, monthly_income, today)

        return {"goal_name": goal_name, "target_amount": target_amount, "deadline": deadline}

    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def extract_goal_from_text(text: str, monthly_income: float = 0.0) -> dict:
    """
    Parse a natural-language goal into:
        {"goal_name": str, "target_amount": float, "deadline": str}
    AI is tried first; regex is the fallback.
    Neither amount nor deadline is required from the user.
    """
    today = datetime.today()

    # ── 1. AI parser ─────────────────────────────────────────────────────────
    ai = _ai_parse(text, monthly_income, today)
    if ai:
        # Fill any zero amount using keyword hints as a safety net
        if ai["target_amount"] == 0:
            ai["target_amount"] = _keyword_amount(text.lower()) or _regex_amount(text) or 20_000
        return ai

    # ── 2. Regex fallback ─────────────────────────────────────────────────────
    t_lower = text.lower()
    amount  = _regex_amount(text) or _keyword_amount(t_lower) or 20_000
    name    = _regex_goal_name(t_lower)
    dl      = _regex_deadline(t_lower, today) or _estimate_deadline(amount, monthly_income, today)

    return {"goal_name": name, "target_amount": amount, "deadline": dl}