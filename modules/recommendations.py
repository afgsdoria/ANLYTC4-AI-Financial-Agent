"""
recommendations.py
Produces context-aware financial recommendations.
"""
from collections import defaultdict


def _get_emergency_fund_goal(active_goals: list[dict] | None) -> dict | None:
    if not active_goals:
        return None

    for goal in active_goals:
        goal_name = str(goal.get("goal_name", "")).strip().lower()
        if "emergency" in goal_name:
            return goal

    return None


def _get_emergency_fund_recommendation(active_goals: list[dict] | None, current_savings: float, monthly_income: float) -> str | None:
    recommended_target = monthly_income * 3
    if recommended_target <= 0:
        return None

    if current_savings >= recommended_target:
        return None

    emergency_goal = _get_emergency_fund_goal(active_goals)
    if emergency_goal:
        target_amount = float(emergency_goal.get("target_amount", 0) or 0)
        if target_amount < recommended_target:
            return (
                f"🛡️ Increase your Emergency Fund target to ₱{recommended_target:,.2f} based on your current income. "
                f"Your current target is ₱{target_amount:,.2f}."
            )
        return None

    return (
        f"🛡️ Consider setting an Emergency Fund goal of ₱{recommended_target:,.2f} based on your current income. "
        f"You currently have ₱{current_savings:,.2f} saved."
    )


def generate_recommendations(
    monthly_income: float,
    total_spending: float,
    savings_goal: float,
    current_savings: float = 0.0,
    expenses: list[tuple] | None = None,
    active_goal: dict | None = None,
    active_goals: list[dict] | None = None,
) -> list[str]:
    recs = []
    if monthly_income <= 0:
        recs.append("💡 Enter your monthly income to unlock personalised recommendations.")
        return recs
    net = monthly_income - total_spending
    spending_ratio = total_spending / monthly_income
    if net > 0:
        weekly = net / 4.33
        recs.append(f"📅 Suggested weekly budget from remaining balance: ₱{weekly:,.2f}")
    else:
        recs.append(f"🛑 You have no remaining balance. Aim to cut at least ₱{abs(net):,.2f} in spending this month.")
    label_lookup = {
        "Food": "Needs",
        "Groceries": "Needs",
        "Bills": "Needs",
        "Telecommunication Bills": "Needs",
        "Transportation": "Needs",
        "Health": "Needs",
        "School": "Needs",
        "Insurance": "Needs",
        "Government Contribution": "Needs",
        "HMO": "Needs",
        "Savings": "Savings",
        "Investment": "Savings",
        "Entertainment": "Wants",
        "Shopping": "Wants",
        "Other": "Wants",
    }
    section_totals: dict[str, float] = {"Needs": 0.0, "Wants": 0.0, "Savings": 0.0}
    if expenses:
        for category, amount, _ in expenses:
            section = label_lookup.get(category, "Wants")
            section_totals[section] += amount
        portions = []
        for section in ["Needs", "Wants", "Savings"]:
            portion = section_totals[section] / monthly_income
            portions.append(f"{section}: {portion*100:.0f}% (₱{section_totals[section]:,.2f})")
        recs.append(
            "🔢 Personalized spending breakdown — " + ", ".join(portions)
        )
    else:
        recs.append(
            "🔢 Personalised budget suggestion: focus your spending on needs first, then wants, and grow savings based on your income and goals."
        )
    if expenses:
        cat_totals: dict[str, float] = defaultdict(float)
        for cat, amt, _ in expenses:
            cat_totals[cat] += amt
        if cat_totals.get("Food", 0) > monthly_income * 0.25:
            recs.append("🍱 Try meal prepping or cooking at home to reduce food expenses — you can save ₱500–₱1,500/month easily.")
        if cat_totals.get("Entertainment", 0) > monthly_income * 0.10:
            recs.append("🎮 Look for free or low-cost entertainment alternatives (free parks, community events, library books).")
        if cat_totals.get("Transportation", 0) > monthly_income * 0.15:
            recs.append("🚌 Consider carpooling, bike commuting, or optimising routes to trim transportation costs.")
    if active_goal and monthly_income > 0:
        target = active_goal.get("target_amount", 0)
        remaining_goal = max(0, target - current_savings)
        if net > 0 and remaining_goal > 0:
            months_to_goal = remaining_goal / net
            recs.append(
                f"🎯 At your current rate you'll reach '{active_goal['goal_name']}' in ~{months_to_goal:.1f} months. "
                f"Save an extra ₱{net*0.1:,.2f}/month to get there faster!"
            )
    elif savings_goal > 0 and current_savings < savings_goal:
        gap = savings_goal - current_savings
        if net > 0:
            months_needed = gap / net
            recs.append(f"🎯 You need ₱{gap:,.2f} more to hit your savings goal. Estimated: {months_needed:.1f} months at current pace.")

    emergency_recommendation = _get_emergency_fund_recommendation(active_goals, current_savings, monthly_income)
    if emergency_recommendation:
        recs.append(emergency_recommendation)
    return recs