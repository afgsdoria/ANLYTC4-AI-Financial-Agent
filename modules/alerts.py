def generate_spending_alerts(
    monthly_income,
    total_spending,
    expenses
):

    alerts = []

    # Overspending alert
    if total_spending > monthly_income:

        alerts.append(
            "⚠ Spending exceeds monthly income."
        )

    # High spending ratio
    spending_ratio = (
        total_spending / monthly_income
        if monthly_income > 0 else 1
    )

    if spending_ratio > 0.8:

        alerts.append(
            "⚠ You are spending more than 80% "
            "of your income."
        )

    # Food overspending
    food_total = 0

    for expense in expenses:

        category, amount, date = expense

        if category == "Food":
            food_total += amount

    if food_total > monthly_income * 0.3:

        alerts.append(
            "⚠ Food spending is unusually high."
        )

    return alerts