"""
alerts.py
Detects risky spending patterns and returns alert messages.
"""
from collections import defaultdict

_THRESHOLDS = {
    "Food":          0.30,
    "Entertainment": 0.15,
    "Shopping":      0.20,
    "Transportation": 0.20,
    "Bills":         0.35,
}


def generate_spending_alerts(
    monthly_income: float,
    total_spending: float,
    expenses: list[tuple],
) -> list[str]:
    alerts = []
    if monthly_income <= 0:
        return alerts
    spending_ratio = total_spending / monthly_income
    if total_spending > monthly_income:
        over = total_spending - monthly_income
        alerts.append(f"🚨 You are spending ₱{over:,.2f} MORE than your income this period!")
    elif spending_ratio > 0.90:
        alerts.append(f"⚠️ Spending is at {spending_ratio*100:.0f}% of income — very little room to save.")
    elif spending_ratio > 0.80:
        alerts.append(f"⚠️ Spending exceeds 80% of income ({spending_ratio*100:.0f}%). Consider cutting discretionary expenses.")
    category_totals: dict[str, float] = defaultdict(float)
    for category, amount, _ in (expenses or []):
        category_totals[category] += amount
    for category, threshold in _THRESHOLDS.items():
        cat_total = category_totals.get(category, 0.0)
        if cat_total > monthly_income * threshold:
            pct = cat_total / monthly_income * 100
            alerts.append(f"⚠️ {category} spending is {pct:.0f}% of income (₱{cat_total:,.2f}). Recommended: ≤{threshold*100:.0f}%.")
    if total_spending >= monthly_income and monthly_income > 0:
        alerts.append("💡 You have no money left to save this month. Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.")
    return alerts