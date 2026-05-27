"""
scoring.py
Calculates a financial health score (0–100) and a descriptive level.
"""


def calculate_financial_health_score(
    monthly_income: float,
    total_spending: float,
    current_savings: float,
) -> tuple[int, str]:
    score = 50
    if monthly_income <= 0:
        return 0, "Poor"
    spending_ratio = total_spending / monthly_income
    savings_ratio  = current_savings / monthly_income
    if spending_ratio == 0:
        score += 30
    elif spending_ratio <= 0.50:
        score += 30
    elif spending_ratio <= 0.70:
        score += 15
    elif spending_ratio <= 0.90:
        score += 0
    else:
        score -= 20
    if savings_ratio >= 1.0:
        score += 20
    elif savings_ratio >= 0.5:
        score += 10
    elif savings_ratio >= 0.1:
        score += 5
    else:
        score -= 10
    score = max(0, min(100, score))
    if score >= 80:
        level = "Excellent"
    elif score >= 60:
        level = "Good"
    elif score >= 40:
        level = "Fair"
    else:
        level = "Poor"
    return score, level