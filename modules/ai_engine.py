from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

# =========================
# ENVIRONMENT
# =========================

load_dotenv()

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)

# =========================
# FINANCIAL ADVICE AI
# =========================

def generate_financial_advice(
    username,
    user_type,
    income,
    savings_goal,
    current_savings,
    total_spending,
    expenses,
    active_goal=None
):

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    expense_text = ""

    if expenses:

        for expense in expenses:

            category, amount, date = (
                expense
            )

            expense_text += (
                f"- {category}: "
                f"₱{amount:,.2f} "
                f"({date})\n"
            )

    else:

        expense_text = (
            "No expenses recorded."
        )

    # =========================
    # ACTIVE GOAL
    # =========================

    goal_text = (
        "No active financial goal."
    )

    if active_goal:

        (
            goal_id,
            goal_name,
            target_amount,
            deadline
        ) = active_goal

        goal_text = f"""
        Goal Name: {goal_name}
        Target Amount:
        ₱{target_amount:,.2f}

        Deadline:
        {deadline}
        """

    prompt = f"""
You are Financial AI Agent.

TODAY'S DATE:
{today}

IMPORTANT RULES:
- Only use CURRENT financial data
- Never assume old goals
- Never reference past years
unless user explicitly says so
- Speak based on PRESENT finances
- Use latest expenses only
- Be practical and realistic
- Use Filipino-friendly examples

USER PROFILE

Username:
{username}

User Type:
{user_type}

Monthly Income:
₱{income:,.2f}

Current Savings:
₱{current_savings:,.2f}

Savings Goal:
₱{savings_goal:,.2f}

Total Spending:
₱{total_spending:,.2f}

ACTIVE GOAL
{goal_text}

CURRENT EXPENSES
{expense_text}

TASKS:
1. Analyze spending behavior
2. Suggest savings improvements
3. Recommend practical budgeting
4. Mention risks if overspending
5. Help achieve active goal
6. Give short actionable advice

Keep response:
- concise
- practical
- future-focused
- present-date aware
"""

    response = (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful "
                        "financial coach "
                        "for Filipinos."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )
    )

    return (
        response
        .choices[0]
        .message.content
    )


# =========================
# FILE ANALYSIS AI
# =========================

def analyze_uploaded_financial_file(
    file_content
):

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    prompt = f"""
Today's Date:
{today}

Analyze this uploaded
financial tracker.

FILE CONTENT:
{file_content}

IMPORTANT:
- Focus on current habits
- Avoid outdated assumptions
- Give present-day advice
- Detect spending patterns
- Suggest savings opportunities
- Be practical for Filipinos
"""

    response = (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are a financial "
                    "analysis AI."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )
    )

    return (
        response
        .choices[0]
        .message.content
    )


# =========================
# FORECAST ADVICE
# =========================

def generate_forecast_advice(
    monthly_savings,
    estimated_months
):

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    prompt = f"""
Today's Date:
{today}

Monthly Savings:
₱{monthly_savings:,.2f}

Estimated Goal Completion:
{estimated_months}

Explain forecast using
present-day financial context.

Give:
- realistic expectations
- saving strategies
- practical budgeting advice
"""

    response = (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are a financial "
                    "forecast assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )
    )

    return (
        response
        .choices[0]
        .message.content
    )


# =========================
# CHATBOT WITH MEMORY
# =========================

def financial_chatbot_with_memory(
    username,
    user_message,
    chat_history,
    current_context=""
):

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    messages = [
        {
            "role": "system",
            "content": f"""
You are Financial AI Agent.

TODAY:
{today}

RULES:
- Use CURRENT financial data
- Avoid old dates
- Never mention outdated goals
- Stay present-focused
- Give practical advice
- Use Filipino context

CURRENT FINANCIAL CONTEXT:
{current_context}
"""
        }
    ]

    # =========================
    # MEMORY
    # =========================

    for role, message in (
        chat_history
    ):

        messages.append({
            "role": role,
            "content": message
        })

    # =========================
    # USER MESSAGE
    # =========================

    messages.append({
        "role": "user",
        "content": user_message
    })

    response = (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
    )

    return (
        response
        .choices[0]
        .message.content
    )