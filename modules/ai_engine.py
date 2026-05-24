"""
ai_engine.py
All OpenAI / GPT calls for the Financial AI Agent.
"""

import os
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Add it to your .env file."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def _today():
    return datetime.today().strftime("%Y-%m-%d")


def _chat(system: str, user: str, temperature: float = 0.7) -> str:
    """Helper: single-turn chat completion."""
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=temperature,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ============================================================
# 1. FINANCIAL ADVICE
# ============================================================

def generate_financial_advice(
    username,
    user_type,
    income,
    savings_goal,
    current_savings,
    total_spending,
    expenses,
    active_goal=None,
):
    expense_lines = "\n".join(
        f"  • {cat}: ₱{amt:,.2f} ({date})"
        for cat, amt, date in (expenses or [])
    ) or "  No expenses recorded."

    goal_section = "No active financial goal."
    if active_goal:
        goal_section = (
            f"Goal: {active_goal['goal_name']}\n"
            f"Target: ₱{active_goal['target_amount']:,.2f}\n"
            f"Deadline: {active_goal['deadline']}"
        )

    remaining = income - total_spending
    spending_pct = (total_spending / income * 100) if income > 0 else 0

    prompt = f"""
TODAY: {_today()}

USER: {username} ({user_type})
Monthly Income:   ₱{income:,.2f}
Total Spending:   ₱{total_spending:,.2f} ({spending_pct:.1f}% of income)
Remaining:        ₱{remaining:,.2f}
Current Savings:  ₱{current_savings:,.2f}
Savings Goal:     ₱{savings_goal:,.2f}

ACTIVE GOAL:
{goal_section}

RECENT EXPENSES:
{expense_lines}

INSTRUCTIONS:
1. Analyze the spending pattern in 2–3 sentences.
2. Give 3 specific, actionable tips to improve savings.
3. Comment on progress toward the active goal.
4. End with one encouraging sentence.
Use Philippine Peso (₱). Keep it friendly and concise (≤250 words).
"""
    system = (
        "You are a friendly, practical financial coach for Filipinos. "
        "Be specific, data-driven, and encouraging."
    )
    return _chat(system, prompt)


# ============================================================
# 2. UPLOADED FILE ANALYSIS
# ============================================================

def analyze_uploaded_financial_file(file_content: str) -> str:
    prompt = f"""
TODAY: {_today()}

Analyze the following financial tracker data uploaded by a Filipino user.

FILE CONTENT:
{file_content[:3000]}

Provide:
1. Key spending patterns you notice (2–3 observations).
2. Top 2 areas where the user can cut back.
3. One savings strategy tailored to the data.
Keep it under 200 words and use ₱ for currency.
"""
    system = "You are a financial analysis AI specializing in Filipino personal finance."
    return _chat(system, prompt)


# ============================================================
# 3. FORECAST ADVICE
# ============================================================

def generate_forecast_advice(monthly_savings: float, estimated_months) -> str:
    if estimated_months is None:
        timeline_text = "Goal cannot be reached with current spending (net savings is negative)."
    else:
        timeline_text = f"~{estimated_months:.1f} months"

    prompt = f"""
TODAY: {_today()}

Monthly Net Savings: ₱{monthly_savings:,.2f}
Estimated Goal Completion: {timeline_text}

Give a 3-point forecast summary:
1. Whether the current savings rate is on track.
2. What the user can do to shorten the timeline.
3. A motivating closing remark.
Keep it under 150 words. Use ₱ for amounts.
"""
    system = "You are a financial forecast assistant for Filipino users."
    return _chat(system, prompt)


# ============================================================
# 4. CHATBOT WITH MEMORY
# ============================================================

def financial_chatbot_with_memory(
    username: str,
    user_message: str,
    chat_history: list,
    current_context: str = "",
) -> str:
    system_prompt = f"""
You are Financial AI Agent — a helpful, friendly financial coach for Filipinos.
TODAY: {_today()}

CURRENT FINANCIAL SNAPSHOT:
{current_context}

RULES:
- Base advice on the financial snapshot above.
- Be concise (≤200 words per reply).
- Use ₱ for Philippine Peso amounts.
- If unsure about something, say so honestly.
- Never fabricate numbers not given to you.
"""
    try:
        client = _get_client()

        messages = [{"role": "system", "content": system_prompt}]

        # Inject memory (last N turns already filtered in get_chat_history)
        for role, message in chat_history:
            messages.append({"role": role, "content": message})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Chatbot error: {str(e)}"