import pandas as pd


def generate_forecast(
    monthly_income,
    total_spending,
    current_savings,
    savings_goal
):

    monthly_savings = monthly_income - total_spending

    months = []
    projected_savings = []

    savings = current_savings

    for month in range(1, 13):

        savings += monthly_savings

        months.append(f"Month {month}")

        projected_savings.append(savings)

    forecast_df = pd.DataFrame({
        "Month": months,
        "Projected Savings": projected_savings
    })

    # Goal estimation
    if monthly_savings > 0:

        remaining_goal = savings_goal - current_savings

        estimated_months = remaining_goal / monthly_savings

    else:
        estimated_months = None

    return (
        forecast_df,
        monthly_savings,
        estimated_months
    )