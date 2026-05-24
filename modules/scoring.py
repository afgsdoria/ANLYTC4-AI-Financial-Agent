def calculate_financial_health_score(
    monthly_income,
    total_spending,
    current_savings
):

    score = 100

    spending_ratio = total_spending / monthly_income \
        if monthly_income > 0 else 1

    savings_ratio = current_savings / monthly_income \
        if monthly_income > 0 else 0

    # Spending penalty
    if spending_ratio > 0.9:
        score -= 40

    elif spending_ratio > 0.7:
        score -= 20

    # Savings bonus
    if savings_ratio > 0.5:
        score += 10

    elif savings_ratio < 0.1:
        score -= 10

    # Clamp score
    score = max(0, min(score, 100))

    # Health level
    if score >= 80:
        level = "Excellent"

    elif score >= 60:
        level = "Good"

    elif score >= 40:
        level = "Fair"

    else:
        level = "Poor"

    return score, level