def generate_recommendations(
    monthly_income,
    total_spending,
    savings_goal
):

    recommendations = []

    remaining = monthly_income - total_spending

    # Weekly budget
    weekly_budget = remaining / 4

    recommendations.append(
        f"💡 Suggested weekly budget: "
        f"₱{weekly_budget:.2f}"
    )

    # Savings advice
    suggested_savings = monthly_income * 0.2

    recommendations.append(
        f"💰 Recommended monthly savings: "
        f"₱{suggested_savings:.2f}"
    )

    # Goal pacing
    if savings_goal > 0:

        months = (
            savings_goal / suggested_savings
        )

        recommendations.append(
            f"🎯 Estimated goal timeline: "
            f"{months:.1f} months"
        )

    return recommendations