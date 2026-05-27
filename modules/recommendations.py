def generate_recommendations(
    monthly_income,
    total_spending,
    savings_goal,
    current_savings=0,
    expenses=None,
    active_goal=None,
):
    recommendations = []

    monthly_income   = float(monthly_income  or 0)
    total_spending   = float(total_spending  or 0)
    savings_goal     = float(savings_goal    or 0)
    current_savings  = float(current_savings or 0)

    if monthly_income <= 0:
        recommendations.append(
            "💡 Set your monthly income in your profile to receive personalised recommendations."
        )
        return recommendations

    remaining = monthly_income - total_spending

    # =========================
    # WEEKLY BUDGET
    # =========================
    if remaining > 0:
        weekly_budget = remaining / 4
        recommendations.append(
            f"💡 Suggested weekly budget: ₱{weekly_budget:,.2f}"
        )
    else:
        recommendations.append(
            "⚠️ Your spending exceeds your income. Try to cut non-essential expenses immediately."
        )

    # =========================
    # SAVINGS ADVICE
    # =========================
    suggested_savings = monthly_income * 0.20
    recommendations.append(
        f"💰 Recommended monthly savings (20% rule): ₱{suggested_savings:,.2f}"
    )

    # =========================
    # GOAL PACING
    # =========================
    if savings_goal > 0 and suggested_savings > 0:
        months_to_goal = savings_goal / suggested_savings
        recommendations.append(
            f"🎯 At ₱{suggested_savings:,.2f}/month, "
            f"you'll reach your ₱{savings_goal:,.2f} goal in "
            f"~{months_to_goal:.1f} months."
        )

    # =========================
    # ACTIVE GOAL PACING
    # =========================
    if active_goal:
        try:
            target   = float(active_goal.get("target_amount") or 0)
            deadline = str(active_goal.get("deadline") or "")
            name     = active_goal.get("goal_name", "your goal")
            remaining_goal = max(0, target - current_savings)

            if target > 0 and remaining > 0:
                months_needed = remaining_goal / remaining
                recommendations.append(
                    f"🏁 For '{name}': you need ₱{remaining_goal:,.2f} more. "
                    f"Saving ₱{remaining:,.2f}/month gets you there in "
                    f"~{months_needed:.1f} months."
                )
        except Exception:
            pass

    # =========================
    # EMERGENCY FUND
    # Only show if current savings
    # are below 3 months of income
    # =========================
    emergency_fund_target = monthly_income * 3

    if current_savings < emergency_fund_target:
        shortfall = emergency_fund_target - current_savings
        recommendations.append(
            f"🛡️ Emergency Fund: You need ₱{emergency_fund_target:,.2f} "
            f"(3× your monthly income of ₱{monthly_income:,.2f}). "
            f"You currently have ₱{current_savings:,.2f} saved — "
            f"₱{shortfall:,.2f} short. "
            f"Try saving ₱{shortfall/12:,.2f}/month to build it in a year."
        )
    # If current_savings >= emergency_fund_target, skip — goal already met

    # =========================
    # HIGH SPENDING WARNING
    # =========================
    spending_ratio = total_spending / monthly_income if monthly_income > 0 else 0

    if spending_ratio > 0.9:
        recommendations.append(
            "🚨 Critical: You are spending over 90% of your income. "
            "Review your expenses and cut non-essentials urgently."
        )
    elif spending_ratio > 0.7:
        recommendations.append(
            "⚠️ You are spending over 70% of your income. "
            "Consider reducing discretionary spending."
        )

    # =========================
    # CATEGORY-SPECIFIC TIPS
    # =========================
    if expenses:
        food_total     = sum(float(e[1]) for e in expenses if e[0] == "Food")
        shopping_total = sum(float(e[1]) for e in expenses if e[0] == "Shopping")

        if food_total > monthly_income * 0.30:
            recommendations.append(
                f"🍽️ Food spending (₱{food_total:,.2f}) exceeds 30% of your income. "
                f"Consider meal prepping or cooking at home more often."
            )

        if shopping_total > monthly_income * 0.20:
            recommendations.append(
                f"🛍️ Shopping (₱{shopping_total:,.2f}) is over 20% of your income. "
                f"Try a 24-hour rule before non-essential purchases."
            )

    return recommendations