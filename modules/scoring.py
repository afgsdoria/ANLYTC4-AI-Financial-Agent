"""
scoring.py
Calculates a financial health score (0–100) and a descriptive level.
"""


def calculate_financial_health_score(
    monthly_income: float,
    total_spending: float,
    current_savings: float,
) -> tuple[int, str]:
    """
    Score breakdown (starts at 50 base):
        Spending ratio    – up to ±30 pts
        Savings cushion   – up to ±20 pts
    Returns (score: int, level: str)
    """
    score = 50

    if monthly_income <= 0:
        return 0, "Poor"

    spending_ratio = total_spending / monthly_income
    savings_ratio  = current_savings / monthly_income

    # --- Spending penalty / bonus ---
    if spending_ratio == 0:
        score += 30          # no spending recorded yet – neutral benefit
    elif spending_ratio <= 0.50:
        score += 30          # excellent — spending ≤ 50 %
    elif spending_ratio <= 0.70:
        score += 15          # good — spending 51–70 %
    elif spending_ratio <= 0.90:
        score += 0           # fair — spending 71–90 %
    else:
        score -= 20          # poor — spending > 90 %

    # --- Savings cushion bonus ---
    if savings_ratio >= 1.0:
        score += 20          # savings ≥ 1 month income
    elif savings_ratio >= 0.5:
        score += 10
    elif savings_ratio >= 0.1:
        score += 5
    else:
        score -= 10

    score = max(0, min(100, score))

    if score >= 80:
        level = "Excellent 🌟"
    elif score >= 60:
        level = "Good 👍"
    elif score >= 40:
        level = "Fair ⚠️"
    else:
        level = "Poor 🔴"

    return score, level