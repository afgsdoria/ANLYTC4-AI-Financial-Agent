"""
ai_engine.py — All OpenAI GPT calls with agentic reasoning
Reasoning engine: multi-step planning, decision rules, autonomous analysis
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not found in .env file.")
        _client = OpenAI(api_key=key)
    return _client


def _today():
    return datetime.today().strftime("%Y-%m-%d")


def _chat(system: str, user: str, temperature=0.7, max_tokens=1500) -> str:
    try:
        r = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 1. AGENTIC FULL ANALYSIS  (reasoning engine + decision rules + planning)
#    Returns JSON with keys: health_summary, spending_habits, risk_flags,
#    step_plan, chart_insights, forecast_narrative
# ══════════════════════════════════════════════════════════════════════════════

def run_full_agent_analysis(
    username, user_type, age, income, current_savings,
    savings_goal, total_spending, expenses,
    active_goal=None, file_context=None
) -> dict:
    """
    Autonomous multi-step reasoning:
      Step 1 — Assess financial health
      Step 2 — Identify spending patterns & risks
      Step 3 — Build a concrete step-by-step plan
      Step 4 — Generate chart narrative & forecast commentary
    Returns a structured dict for the dashboard.
    """
    exp_lines = "\n".join(
        f"  • {cat}: ₱{amt:,.2f} on {dt}"
        for cat, amt, dt in (expenses or [])[:30]
    ) or "  No expenses recorded yet."

    goal_block = "No active goal."
    if active_goal:
        goal_block = (
            f"Goal: {active_goal['goal_name']} | "
            f"Target: ₱{active_goal['target_amount']:,.2f} | "
            f"Deadline: {active_goal['deadline']}"
        )

    file_block = ""
    if file_context:
        file_block = f"\nUPLOADED TRACKER CONTEXT:\n{file_context[:1500]}"

    remaining = income - total_spending
    sav_rate  = (remaining / income * 100) if income > 0 else 0

    system = (
        "You are an autonomous AI financial planning agent for Filipinos. "
        "You reason step-by-step, apply financial decision rules, and produce "
        "a concrete multi-step action plan. Always respond in valid JSON only."
    )

    user_prompt = f"""
TODAY: {_today()}
USER: {username} | Type: {user_type} | Age: {age}
Monthly Income:  ₱{income:,.2f}
Total Spending:  ₱{total_spending:,.2f}
Remaining:       ₱{remaining:,.2f} ({sav_rate:.1f}% savings rate)
Current Savings: ₱{current_savings:,.2f}
Savings Goal:    ₱{savings_goal:,.2f}
ACTIVE GOAL: {goal_block}
EXPENSES:
{exp_lines}
{file_block}

AGENT REASONING STEPS:
Step 1 — Health Assessment: Evaluate income vs spending vs savings ratio.
Step 2 — Spending Pattern Analysis: Identify top categories, risks, anomalies.
Step 3 — Goal Planning: Build a numbered, week-by-week or month-by-month action plan to reach the active goal.
Step 4 — Chart Narrative: Describe what the spending chart and forecast chart reveal.

Return ONLY this JSON (no markdown fences):
{{
  "health_summary": "2-3 sentence financial health assessment",
  "spending_habits": "2-3 sentences on spending patterns and top categories",
  "risk_flags": ["risk1", "risk2"],
  "step_plan": [
    {{"step": 1, "action": "...", "timeline": "...", "amount": "..."}},
    {{"step": 2, "action": "...", "timeline": "...", "amount": "..."}},
    {{"step": 3, "action": "...", "timeline": "...", "amount": "..."}},
    {{"step": 4, "action": "...", "timeline": "...", "amount": "..."}},
    {{"step": 5, "action": "...", "timeline": "...", "amount": "..."}}
  ],
  "chart_insights": "What the spending breakdown chart reveals",
  "forecast_narrative": "What the 12-month savings forecast means for the user",
  "recommended_monthly_savings": 0,
  "months_to_goal": 0,
  "weekly_budget": 0
}}
"""
    raw = _chat(system, user_prompt, temperature=0.4, max_tokens=2000)

    # Strip markdown fences if model adds them
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except Exception:
        # Fallback so the app never crashes
        return {
            "health_summary": raw[:300],
            "spending_habits": "Unable to parse spending analysis.",
            "risk_flags": [],
            "step_plan": [],
            "chart_insights": "Chart data loaded from your expenses.",
            "forecast_narrative": "Forecast based on current savings rate.",
            "recommended_monthly_savings": max(0, remaining),
            "months_to_goal": 0,
            "weekly_budget": max(0, remaining / 4.33),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2. FINANCIAL ADVICE (for PDF report)
# ══════════════════════════════════════════════════════════════════════════════

def generate_financial_advice(
    username, user_type, income, savings_goal,
    current_savings, total_spending, expenses, active_goal=None
) -> str:
    exp_lines = "\n".join(
        f"  • {c}: ₱{a:,.2f} ({d})" for c, a, d in (expenses or [])
    ) or "  No expenses."
    goal_block = "No active goal."
    if active_goal:
        goal_block = (
            f"{active_goal['goal_name']} — "
            f"₱{active_goal['target_amount']:,.2f} by {active_goal['deadline']}"
        )
    system = "You are a practical financial coach for Filipinos. Be specific and concise."
    prompt = f"""
TODAY: {_today()}
USER: {username} ({user_type})
Income: ₱{income:,.2f} | Spending: ₱{total_spending:,.2f} | Savings: ₱{current_savings:,.2f}
Goal: {goal_block}
Expenses:
{exp_lines}

Write a 200-word financial summary covering:
1. Current financial standing
2. Three specific improvement tips
3. Goal progress commentary
Use ₱ for peso amounts.
"""
    return _chat(system, prompt)


# ══════════════════════════════════════════════════════════════════════════════
# 3. UPLOADED FILE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def analyze_uploaded_financial_file(file_content: str) -> str:
    system = "You are a financial data analyst for Filipinos."
    prompt = f"""
TODAY: {_today()}
Analyze this uploaded financial tracker:

{file_content[:3000]}

Provide:
1. Key spending patterns (2-3 observations)
2. Top 2 areas to cut back
3. One savings strategy from the data
Under 200 words. Use ₱.
"""
    return _chat(system, prompt)


# ══════════════════════════════════════════════════════════════════════════════
# 4. FORECAST ADVICE
# ══════════════════════════════════════════════════════════════════════════════

def generate_forecast_advice(monthly_savings: float, estimated_months) -> str:
    timeline = f"~{estimated_months:.1f} months" if estimated_months is not None \
               else "Goal unreachable at current rate (negative savings)"
    system = "You are a financial forecast assistant for Filipinos."
    prompt = f"""
TODAY: {_today()}
Monthly Net Savings: ₱{monthly_savings:,.2f}
Goal Timeline: {timeline}

Give 3 points:
1. Whether savings rate is on track
2. How to shorten the timeline
3. Motivating closing remark
Under 150 words. Use ₱.
"""
    return _chat(system, prompt)


# ══════════════════════════════════════════════════════════════════════════════
# 5. FINANCE-ONLY CHATBOT WITH MEMORY & PERSONALIZATION
# ══════════════════════════════════════════════════════════════════════════════

def financial_chatbot_with_memory(
    username: str,
    user_message: str,
    chat_history: list,
    current_context: str = "",
    ai_analysis: dict = None,
) -> str:
    analysis_block = ""
    if ai_analysis:
        plan_text = "\n".join(
            f"  Step {s['step']}: {s['action']} ({s.get('timeline','')}, {s.get('amount','')})"
            for s in ai_analysis.get("step_plan", [])
        )
        analysis_block = f"""
LATEST AI ANALYSIS:
Health: {ai_analysis.get('health_summary','')}
Spending: {ai_analysis.get('spending_habits','')}
Risks: {', '.join(ai_analysis.get('risk_flags', []))}
Action Plan:
{plan_text}
"""

    system = f"""
You are Financial AI Agent — a personalized financial coach for Filipinos.
TODAY: {_today()}

SCOPE RULES:
- Answer ANY question that could help the user make better financial decisions or reach their goal.
  This includes: budgeting, savings, expenses, goals, debt, investments, banking products,
  salary negotiation, side hustles, comparison of financial products (e.g. "Is Maya better than
  GCash?", "Is MariBank a good savings bank?"), insurance, credit cards, stock market basics,
  crypto risks, loans, and general money mindset questions.
- If the user asks something completely unrelated to money or financial well-being
  (e.g. cooking recipes, sports scores, coding questions), politely redirect:
  "I'm your finance coach — I can best help with money-related questions.
   Is there a financial topic I can help you with?"
- Always personalize answers using the user's actual data below when relevant.
- Be concise (≤250 words), warm, and practical.
- Use ₱ for Philippine Peso amounts.
- Reference the user's specific income, spending, or goal when it adds value.

USER FINANCIAL PROFILE:
{current_context}
{analysis_block}
"""
    try:
        client = _get_client()
        messages = [{"role": "system", "content": system}]
        for role, msg in chat_history[-20:]:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": user_message})
        r = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages,
            temperature=0.65, max_tokens=600
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Chatbot error: {e}"