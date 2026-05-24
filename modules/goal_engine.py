import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


def extract_goal_from_text(
    text,
    monthly_income=0
):

    text_lower = text.lower()

    # =========================
    # DEFAULT VALUES
    # =========================

    goal_name = "General Savings Goal"
    target_amount = 0
    deadline = "No deadline set"

    today = datetime.today()

    # =========================
    # EXTRACT MONEY
    # =========================

    amount_match = re.search(
        r'₱?\s?([\d,]+)',
        text
    )

    if amount_match:

        target_amount = float(
            amount_match.group(1)
            .replace(",", "")
        )

    # =========================
    # EXTRACT GOAL NAME
    # =========================

    goal_patterns = [

        r'for\s(.+?)(?:\sby|\swithin|\sin|\sbefore|$)',

        r'to buy\s(.+?)(?:\sby|\swithin|\sin|\sbefore|$)',

        r'to save for\s(.+?)(?:\sby|\swithin|\sin|\sbefore|$)'
    ]

    for pattern in goal_patterns:

        match = re.search(
            pattern,
            text_lower
        )

        if match:

            goal_name = (
                match.group(1)
                .strip()
                .title()
            )

            break

    # =========================
    # MONTHS
    # Example:
    # within 8 months
    # in 6 months
    # =========================

    months_match = re.search(
        r'(\d+)\smonth',
        text_lower
    )

    if months_match:

        months = int(
            months_match.group(1)
        )

        future_date = (
            today +
            relativedelta(
                months=months
            )
        )

        deadline = future_date.strftime(
            "%Y-%m-%d"
        )

    # =========================
    # YEARS
    # Example:
    # within 2 years
    # in 1 year
    # =========================

    years_match = re.search(
        r'(\d+)\syear',
        text_lower
    )

    if years_match:

        years = int(
            years_match.group(1)
        )

        future_date = (
            today +
            relativedelta(
                years=years
            )
        )

        deadline = future_date.strftime(
            "%Y-%m-%d"
        )

    # =========================
    # SPECIFIC DATE
    # Example:
    # before Dec 2026
    # by January 2027
    # before 2027-12-31
    # =========================

    month_names = (
        "january|february|march|april|"
        "may|june|july|august|"
        "september|october|november|"
        "december"
    )

    specific_match = re.search(
        rf"(?:before|by|in)\s("
        rf"(?:{month_names})"
        rf"\s+\d{{4}}"
        rf")",
        text_lower
    )

    if specific_match:

        date_text = specific_match.group(1)

        parsed_date = datetime.strptime(
            date_text,
            "%B %Y"
        )

        deadline = parsed_date.strftime(
            "%Y-%m-%d"
        )

    # =========================
    # ESTIMATE DATE
    # If user gives target amount
    # but no deadline
    # =========================

    if (
        deadline == "No deadline set"
        and monthly_income > 0
        and target_amount > 0
    ):

        estimated_monthly_savings = (
            monthly_income * 0.20
        )

        estimated_months = max(
            1,
            round(
                target_amount /
                estimated_monthly_savings
            )
        )

        estimated_date = (
            today +
            relativedelta(
                months=estimated_months
            )
        )

        deadline = (
            estimated_date.strftime(
                "%Y-%m-%d"
            )
        )

    # =========================
    # RETURN
    # =========================

    return {
        "goal_name": goal_name,
        "target_amount": target_amount,
        "deadline": deadline
    }