"""
forecasting.py
Projects future savings growth month by month.
"""

import pandas as pd


def generate_forecast(
    monthly_income: float,
    total_spending: float,
    current_savings: float,
    savings_goal: float,
    months: int = 12,
) -> tuple[pd.DataFrame, float, float | None]:
    """
    Returns:
        forecast_df      – DataFrame with Month and Projected Savings columns.
        monthly_savings  – Net amount saved per month (income − spending).
        estimated_months – How many months to reach savings_goal, or None.
    """
    monthly_savings = monthly_income - total_spending

    rows = []
    balance = current_savings

    for i in range(1, months + 1):
        balance = max(0.0, balance + monthly_savings)
        rows.append({"Month": f"Month {i}", "Projected Savings": round(balance, 2)})

    forecast_df = pd.DataFrame(rows)

    if monthly_savings > 0 and savings_goal > current_savings:
        remaining = savings_goal - current_savings
        estimated_months = remaining / monthly_savings
    elif savings_goal <= current_savings:
        estimated_months = 0.0
    else:
        estimated_months = None  # can't reach goal with negative savings

    return forecast_df, monthly_savings, estimated_months