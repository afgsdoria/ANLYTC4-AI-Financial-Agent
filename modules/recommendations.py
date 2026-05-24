"""
recommendations.py
Produces context-aware financial recommendations.
"""

from collections import defaultdict


def generate_recommendations(
    monthly_income: float,
    total_spending: float,
    savings_goal: float,
    current_savings: float = 0.0,
    expenses: list[tuple] | None = None,
    active_goal: dict | None = None,
) -> list[str]:
    """
    Returns a list of recommendation strings tailored to the user's data.
    """
    recs = []

    if monthly_income <= 0:
        recs.append("💡 Enter your monthly income to unlock personalised recommendations.")
        return recs

    net = monthly_income - total_spending
    spending_ratio = total_spending / monthly_income

    # --- Weekly budget ---
    if net > 0:
        weekly = net / 4.33
        recs.append(
            f"📅 Suggested weekly budget from remaining balance: ₱{weekly:,.2f}"
        )
    else:
        recs.append(
            "🛑 You have no remaining balance. Aim to cut at least "
            f"₱{abs(net):,.2f} in spending this month."
        )

    # --- 50/30/20 rule ---
    needs   = monthly_income * 0.50
    wants   = monthly_income * 0.30
    savings = monthly_income * 0.20
    recs.append(
        f"🔢 50/30/20 guide — Needs: ₱{needs:,.2f} | "
        f"Wants: ₱{wants:,.2f} | Savings: ₱{savings:,.2f}"
    )

    # --- Category-specific advice ---
    if expenses:
        cat_totals: dict[str, float] = defaultdict(float)
        for cat, amt, _ in expenses:
            cat_totals[cat] += amt

        if cat_totals.get("Food", 0) > monthly_income * 0.25:
            recs.append(
                "🍱 Try meal prepping or cooking at home to reduce food expenses — "
                "you can save ₱500–₱1,500/month easily."
            )
        if cat_totals.get("Entertainment", 0) > monthly_income * 0.10:
            recs.append(
                "🎮 Look for free or low-cost entertainment alternatives "
                "(free parks, community events, library books)."
            )
        if cat_totals.get("Transportation", 0) > monthly_income * 0.15:
            recs.append(
                "🚌 Consider carpooling, bike commuting, or optimising routes "
                "to trim transportation costs."
            )

    # --- Goal progress ---
    if active_goal and monthly_income > 0:
        target = active_goal.get("target_amount", 0)
        remaining_goal = max(0, target - current_savings)
        if net > 0 and remaining_goal > 0:
            months_to_goal = remaining_goal / net
            recs.append(
                f"🎯 At your current rate you'll reach "
                f"'{active_goal['goal_name']}' in ~{months_to_goal:.1f} months. "
                f"Save an extra ₱{net*0.1:,.2f}/month to get there faster!"
            )
    elif savings_goal > 0 and current_savings < savings_goal:
        gap = savings_goal - current_savings
        if net > 0:
            months_needed = gap / net
            recs.append(
                f"🎯 You need ₱{gap:,.2f} more to hit your savings goal. "
                f"Estimated: {months_needed:.1f} months at current pace."
            )

    # --- Emergency fund nudge ---
    emergency_fund = monthly_income * 3
    if current_savings < emergency_fund:
        recs.append(
            f"🛡️ Build a 3-month emergency fund (₱{emergency_fund:,.2f}) "
            "before focusing on other goals."
        )

    return recs