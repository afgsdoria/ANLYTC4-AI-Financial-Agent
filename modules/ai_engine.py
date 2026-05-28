"""
ai_engine.py — All OpenAI GPT calls with agentic reasoning
Reasoning engine: multi-step planning, decision rules, autonomous analysis

NEW: Web-search tool enabled for chatbot and goal parser so the agent can
     look up real-time prices (concert tickets, gadgets, travel, etc.)
     before answering affordability questions or extracting goal amounts.
"""

import os
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        # Try environment variable first (Codespaces secrets)
        key = os.getenv("OPENAI_API_KEY")
        
        # If environment variable doesn't have a valid key, load from .env
        if not key or not key.strip().startswith("sk-"):
            load_dotenv(override=True)
            key = os.getenv("OPENAI_API_KEY")
        
        if not key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in Codespaces secrets or .env file.")
        
        # Clean up whitespace
        key = key.strip()
        
        # Validate API key format (should start with 'sk-' or 'sk-proj-')
        if not key.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY has invalid format. It should start with 'sk-' or 'sk-proj-'")
        
        _client = OpenAI(api_key=key)
    return _client


def _today():
    return datetime.today().strftime("%Y-%m-%d")


def _chat(system: str, user: str, temperature=0.7, max_tokens=1500) -> str:
    """Plain chat call — no tools."""
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
        # Sanitize error message to hide API key and sensitive details
        error_str = str(e)
        if "invalid_api_key" in error_str.lower() or "401" in error_str:
            return "⚠️ AI Error: Authentication failed. Please check your API key configuration."
        elif "rate_limit" in error_str.lower() or "429" in error_str:
            return "⚠️ AI Error: Service is temporarily busy. Please try again in a moment."
        elif "model" in error_str.lower() and "not" in error_str.lower():
            return "⚠️ AI Error: Model not available. Please try again later."
        else:
            # Generic error for anything else (hides API key and internal details)
            return "⚠️ AI Error: Service unavailable. Please try again."


def _ai_error_text() -> str:
    return "The AI service is currently unavailable. Please check your OpenAI API key and try again."


def _is_ai_error(raw: str) -> bool:
    return isinstance(raw, str) and raw.strip().startswith("⚠️ AI Error:")


# ── Web-search tool definition (OpenAI function calling) ─────────────────────

_WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for real-time information such as current prices, "
            "event ticket costs, product prices, exchange rates, and other "
            "up-to-date data that the model may not have in its training data. "
            "Use this whenever the user asks about the price of something specific "
            "(concert tickets, gadgets, travel fares, etc.) or when you need a "
            "current market price to answer an affordability question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A concise, specific search query. "
                        "Examples: 'Saranggola concert Patron B ticket price Philippines 2025', "
                        "'iPhone 16 price Philippines peso 2025', "
                        "'Manila to Tokyo airfare economy 2025'."
                    ),
                }
            },
            "required": ["query"],
        },
    },
}


def _perform_web_search(query: str) -> str:
    """
    Execute a web search via the Responses API (search_preview) and return
    a plain-text summary of the results.

    Falls back gracefully if the search model is unavailable, keeping the
    chatbot functional even in restricted environments.
    """
    try:
        client = _get_client()

        # Use the Responses API with web_search_preview tool
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview"}],
            input=query,
        )

        # Extract text from the response output
        for block in response.output:
            if hasattr(block, "type") and block.type == "message":
                for content in block.content:
                    if hasattr(content, "type") and content.type == "output_text":
                        return content.text.strip()

        return "No search results found."

    except Exception as e:
        # Graceful fallback — let the LLM note it couldn't search
        return f"[Search unavailable: {e}]"


def _chat_with_search(
    system: str,
    messages: list,
    temperature: float = 0.65,
    max_tokens: int = 1000,
) -> str:
    """
    Agentic chat call that:
      1. Sends the conversation to GPT-4o-mini with a web_search function tool.
      2. If the model decides to call web_search, executes the search and
         feeds the result back.
      3. Returns the final text reply.

    Supports up to 3 search rounds to handle multi-hop queries.
    """
    try:
        client = _get_client()
        msgs = list(messages)

        for _ in range(3):  # max 3 search rounds
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=msgs,
                tools=[_WEB_SEARCH_TOOL],
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            msg = choice.message

            # No tool call → final answer
            if not msg.tool_calls:
                return (msg.content or "").strip()

            # Process all tool calls in this round
            msgs.append(msg)  # add assistant message with tool_calls
            for tc in msg.tool_calls:
                if tc.function.name == "web_search":
                    try:
                        args = json.loads(tc.function.arguments)
                        query = args.get("query", "")
                    except Exception:
                        query = tc.function.arguments

                    search_result = _perform_web_search(query)

                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": search_result,
                    })

        # Safety: one final call without tools to force a text answer
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    except Exception as e:
        # Sanitize error message to hide API key and sensitive details
        error_str = str(e)
        if "invalid_api_key" in error_str.lower() or "401" in error_str:
            return "⚠️ AI Error: Authentication failed. Please check your API key configuration."
        elif "rate_limit" in error_str.lower() or "429" in error_str:
            return "⚠️ AI Error: Service is temporarily busy. Please try again in a moment."
        elif "model" in error_str.lower() and "not" in error_str.lower():
            return "⚠️ AI Error: Model not available. Please try again later."
        else:
            # Generic error for anything else (hides API key and internal details)
            return "⚠️ AI Error: Service unavailable. Please try again."


# ══════════════════════════════════════════════════════════════════════════════
# 1. AGENTIC FULL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def run_full_agent_analysis(
    username, user_type, age, income, current_savings,
    savings_goal, total_spending, expenses,
    active_goals=None, file_context=None
) -> dict:
    exp_lines = "\n".join(
        f"  • {cat}: ₱{amt:,.2f} on {dt}"
        for cat, amt, dt in (expenses or [])[:30]
    ) or "  No expenses recorded yet."

    goal_block = "No active goals."
    if active_goals:
        # Format all active goals
        goal_lines = []
        for goal in active_goals:
            goal_lines.append(
                f"• {goal['goal_name']}: ₱{goal['target_amount']:,.2f} by {goal['deadline']}"
            )
        goal_block = "Active Goals:\n" + "\n".join(goal_lines)

    file_block = ""
    if file_context:
        file_block = f"\nUPLOADED TRACKER CONTEXT:\n{file_context[:1500]}"

    remaining = income - total_spending
    sav_rate  = (remaining / income * 100) if income > 0 else 0

    system = (
        "You are an autonomous AI financial planning agent for Filipinos. "
        "You reason step-by-step, apply financial decision rules, and produce "
        "a concrete multi-step action plan. You also generate structured chart data "
        "for AI-driven visualization. Always respond in valid JSON only — no markdown fences."
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
Step 3 — Goal Planning: Build a numbered, week-by-week or month-by-month action plan.
Step 4 — Chart Narrative: Describe what the spending chart and forecast chart reveal.
Step 5 — Chart Data Generation: Produce structured category/amount pairs from the expenses
          for AI-generated visualization. If no expenses, generate realistic estimated
          budget allocations based on the user's income, user type, and Philippine cost of living.

Return ONLY this JSON (no markdown fences, no extra text):
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
  "chart_insights": "What the spending breakdown chart reveals (1-2 sentences)",
  "forecast_narrative": "What the 12-month savings forecast means for the user (1-2 sentences)",
  "recommended_monthly_savings": 0,
  "months_to_goal": 0,
  "weekly_budget": 0,
  "chart_data": {{
    "categories": ["Food", "Transportation", "Bills", "Entertainment", "Savings", "Other"],
    "amounts": [0, 0, 0, 0, 0, 0],
    "insight": "One sentence insight on the most notable category"
  }}
}}
"""
    raw = _chat(system, user_prompt, temperature=0.4, max_tokens=2200)

    if _is_ai_error(raw):
        fallback_chart = {}
        if expenses:
            from collections import defaultdict
            cat_totals = defaultdict(float)
            for c, a, _ in expenses:
                cat_totals[c] += a
            fallback_chart = {
                "categories": list(cat_totals.keys()),
                "amounts": list(cat_totals.values()),
                "insight": "Chart from expense data.",
            }
        return {
            "health_summary": _ai_error_text(),
            "spending_habits": "AI analysis unavailable right now.",
            "risk_flags": [],
            "step_plan": [],
            "chart_insights": "Chart data loaded from your expenses.",
            "forecast_narrative": "Forecast based on current savings rate.",
            "recommended_monthly_savings": max(0, remaining),
            "months_to_goal": 0,
            "weekly_budget": max(0, remaining / 4.33),
            "chart_data": fallback_chart,
        }

    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
        cd = result.get("chart_data", {})
        cats = cd.get("categories", [])
        amts = cd.get("amounts", [])
        if not cats or not amts or len(cats) != len(amts):
            if expenses:
                from collections import defaultdict
                cat_totals = defaultdict(float)
                for c, a, _ in expenses:
                    cat_totals[c] += a
                result["chart_data"] = {
                    "categories": list(cat_totals.keys()),
                    "amounts": list(cat_totals.values()),
                    "insight": "Chart built from your logged expense data.",
                }
            else:
                result["chart_data"] = {}
        return result
    except Exception:
        fallback_chart = {}
        if expenses:
            from collections import defaultdict
            cat_totals = defaultdict(float)
            for c, a, _ in expenses:
                cat_totals[c] += a
            fallback_chart = {
                "categories": list(cat_totals.keys()),
                "amounts": list(cat_totals.values()),
                "insight": "Chart from expense data.",
            }
        return {
            "health_summary": _ai_error_text(),
            "spending_habits": "Unable to parse spending analysis.",
            "risk_flags": [],
            "step_plan": [],
            "chart_insights": "Chart data loaded from your expenses.",
            "forecast_narrative": "Forecast based on current savings rate.",
            "recommended_monthly_savings": max(0, remaining),
            "months_to_goal": 0,
            "weekly_budget": max(0, remaining / 4.33),
            "chart_data": fallback_chart,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2. AI CHART DATA GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_ai_charts(expenses: list, income: float, user_type: str) -> dict:
    if not expenses:
        return {}

    from collections import defaultdict
    cat_totals = defaultdict(float)
    for c, a, _ in expenses:
        cat_totals[c] += a

    system = (
        "You are a financial data analyst. Given expense data, "
        "return structured JSON for chart visualization. No markdown fences."
    )
    lines = "\n".join(f"  {c}: ₱{a:,.2f}" for c, a in cat_totals.items())
    prompt = f"""
User Type: {user_type}
Monthly Income: ₱{income:,.2f}
Expense totals:
{lines}

Return ONLY this JSON:
{{
  "categories": [...],
  "amounts": [...],
  "insight": "One insight sentence about spending distribution"
}}
"""
    raw = _chat(system, prompt, temperature=0.2, max_tokens=400)
    if _is_ai_error(raw):
        return {
            "categories": list(cat_totals.keys()),
            "amounts": list(cat_totals.values()),
            "insight": _ai_error_text(),
        }

    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        data = json.loads(raw)
        if len(data.get("categories", [])) == len(data.get("amounts", [])):
            return data
    except Exception:
        pass

    return {
        "categories": list(cat_totals.keys()),
        "amounts": list(cat_totals.values()),
        "insight": "Chart built from your logged expense data.",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3. FINANCIAL ADVICE (for PDF report)
# ══════════════════════════════════════════════════════════════════════════════

def _local_financial_summary(
    username, user_type, income, savings_goal,
    current_savings, total_spending, expenses, active_goal=None
) -> str:
    remaining = income - total_spending
    savings_rate = (remaining / income * 100) if income else 0.0
    lines = [
        f"Personal financial snapshot for {username}.",
        f"Monthly income is ₱{income:,.2f}, total spending is ₱{total_spending:,.2f}, and current savings are ₱{current_savings:,.2f}.",
        f"This leaves ₱{remaining:,.2f} available each month, which is a {savings_rate:.0f}% savings rate.",
    ]
    if savings_goal and savings_goal > 0:
        lines.append(
            f"Your savings goal is ₱{savings_goal:,.2f}. Keep tracking progress and aim to save consistently toward that target."
        )
    if active_goal:
        lines.append(
            f"Active goal: {active_goal['goal_name']} for ₱{float(active_goal.get('target_amount') or 0):,.2f} due by {active_goal['deadline']}."
        )
    lines.append("Key next steps: review your top spending categories, reduce non-essential expenses, and allocate any surplus toward savings.")
    if expenses:
        categories = sorted({c for c, _, _ in expenses})
        lines.append(f"Recorded expense categories: {', '.join(categories)}.")
    return "\n\n".join(lines)


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
    raw = _chat(system, prompt)
    if _is_ai_error(raw):
        return _local_financial_summary(
            username, user_type, income, savings_goal,
            current_savings, total_spending, expenses, active_goal
        )
    return raw


# ══════════════════════════════════════════════════════════════════════════════
# 4. UPLOADED FILE ANALYSIS
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
    raw = _chat(system, prompt)
    if _is_ai_error(raw):
        return _ai_error_text()
    return raw


# ══════════════════════════════════════════════════════════════════════════════
# 5. FORECAST ADVICE
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
    raw = _chat(system, prompt)
    if _is_ai_error(raw):
        return _ai_error_text()
    return raw


# ══════════════════════════════════════════════════════════════════════════════
# 6. FINANCE CHATBOT — WITH MEMORY, WEB SEARCH, AND REAL-TIME PRICING
# ══════════════════════════════════════════════════════════════════════════════

def financial_chatbot_with_memory(
    username: str,
    user_message: str,
    chat_history: list,
    current_context: str = "",
    ai_analysis: dict = None,
) -> str:
    """
    Personalized finance chatbot with:
    - Full conversation memory
    - Web search tool for real-time prices (concerts, gadgets, travel, etc.)
    - Affordability analysis using the user's actual financial profile
    - Philippine-specific financial guidance
    """
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

    system_content = f"""
You are Financial AI Agent — a personalized financial coach for Filipinos.
TODAY: {_today()}

═══════════════════════════════════════════════════
WEB SEARCH CAPABILITY & WHEN TO USE IT
═══════════════════════════════════════════════════
You have access to a web_search function tool. Use it proactively whenever:

1. The user asks about the price/cost of ANYTHING specific:
   - Concert tickets (e.g. "Saranggola concert Patron B price")
   - Gadgets or electronics (e.g. "iPhone 16 price Philippines")
   - Appliances, furniture, clothing brands
   - Travel fares (flights, hotels, tours)
   - Food/restaurant prices
   - Event tickets (sports, shows, theme parks)
   - Real estate, vehicles

2. Affordability questions ("can I afford...", "is _____ within my budget?")
   → ALWAYS search for the current price first, THEN compute affordability.

3. Current exchange rates, fuel prices, or any market data

SEARCH STRATEGY:
- Be specific: include the exact product/event name + "price Philippines" + current year
- For concerts: search "[artist] concert [city/venue] ticket price [tier] [year]"
- For gadgets: search "[product model] price Philippines peso [year]"
- If first search is vague, do a follow-up search with more detail
- After getting the price, ALWAYS compute: can the user afford it right now?
  And how long would it take them to save for it?

AFFORDABILITY FORMULA (use the user's real data below):
  • Immediate: Can they pay from current savings + remaining monthly balance?
  • Short-term: Months needed = (price - available funds) / monthly net savings
  • Show both the "comfortable" (no sacrifice) and "stretch" (sacrifice) timelines

═══════════════════════════════════════════════════
SCOPE & BEHAVIOR
═══════════════════════════════════════════════════
- Answer ANY question that helps the user make better financial decisions.
  Covers: budgeting, savings, debt, Philippine banks (GCash, Maya, MariBank,
  BPI, BDO, Metrobank, UnionBank, etc.), UITF, mutual funds, PSE stocks,
  crypto risks, insurance, credit cards, BNPL, side hustles, salary negotiation,
  SSS, Pag-IBIG, PhilHealth, inflation, cost of living, financial literacy.
- For non-finance questions, politely redirect:
  "I'm your finance coach — I can best help with money-related questions."
- Always personalize using the user's actual financial data.
- Be concise (≤350 words), warm, practical, and encouraging.
- Use ₱ for Philippine Peso amounts.
- Show step-by-step calculations when doing affordability analysis.
- Cite where you found the price when you use web search.

USER FINANCIAL PROFILE:
{current_context}
{analysis_block}
"""

    try:
        client = _get_client()
        messages = [{"role": "system", "content": system_content}]

        # Build conversation history
        for role, msg in chat_history[-20:]:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": user_message})

        return _chat_with_search(
            system=system_content,
            messages=messages,
            temperature=0.65,
            max_tokens=900,
        )

    except ValueError as ve:
        # API key configuration error
        return f"⚠️ Configuration error: {str(ve)}"
    except Exception as e:
        # Other errors (network, rate limit, etc.)
        error_str = str(e)
        if "invalid_api_key" in error_str.lower() or "401" in error_str:
            return "⚠️ Chatbot error: Authentication failed. Please check your API key in Codespaces secrets or .env file."
        else:
            return f"⚠️ Chatbot error: {error_str}"


# ══════════════════════════════════════════════════════════════════════════════
# 7. REAL-TIME PRICE LOOKUP (standalone — for goal engine)
# ══════════════════════════════════════════════════════════════════════════════

def lookup_price_for_goal(goal_text: str, monthly_income: float) -> dict:
    """
    Uses web search to find the real-time market price for a goal item.
    Returns {"found": bool, "price": float, "source_note": str, "search_query": str}

    Called by goal_engine.py before falling back to keyword defaults.
    """
    # Build a smart search query from the goal text
    query_prompt = f"""
Extract the specific item/product/event from this goal description and create
the best Google search query to find its current price in the Philippines:

Goal: "{goal_text}"

Rules:
- Be specific (include brand, tier, model, event name if mentioned)
- Always append "price Philippines peso 2025" or the relevant year
- For concerts: include artist name + venue/city + ticket tier
- For travel: include destination + "airfare" or "tour package"
- Return ONLY the search query string, nothing else.
"""
    search_query = _chat(
        "You are a search query generator. Return only the search query, no explanation.",
        query_prompt,
        temperature=0.1,
        max_tokens=60,
    ).strip().strip('"')

    # Check if we got an error message instead of a valid search query
    if search_query.startswith("⚠️ AI Error:") or not search_query or len(search_query) < 5:
        return {"found": False, "price": 0.0, "source_note": "AI service unavailable", "search_query": ""}

    # Perform the web search
    search_result = _perform_web_search(search_query)

    if "[Search unavailable" in search_result or "No search results" in search_result or search_result.startswith("⚠️ AI Error:"):
        return {"found": False, "price": 0.0, "source_note": "Search unavailable", "search_query": search_query}

    # Ask the AI to extract the price from search results
    extract_prompt = f"""
Goal: "{goal_text}"
Monthly income for context: ₱{monthly_income:,.2f}

Search results:
{search_result[:2000]}

Extract the most relevant price for the goal item in Philippine Pesos.

Rules:
1. Return the price as a plain number (no ₱ symbol, no commas).
2. If multiple price tiers exist, use the one that matches the goal description.
   If no tier is specified, use the mid-range price.
3. If converting from USD, use approximate rate: 1 USD = 58 PHP.
4. If no price found at all, return 0.
5. Also return a short one-sentence source note explaining what price you found.

Return ONLY valid JSON:
{{"price": 0, "source_note": "e.g. Patron B ticket found at ₱X,XXX on TicketNet"}}
"""
    raw = _chat(
        "You are a price extraction assistant. Return only valid JSON.",
        extract_prompt,
        temperature=0.0,
        max_tokens=120,
    ).strip().replace("```json", "").replace("```", "").strip()

    # Check if we got an error message instead of valid JSON
    if raw.startswith("⚠️ AI Error:"):
        return {"found": False, "price": 0.0, "source_note": "Price extraction failed", "search_query": search_query}

    try:
        data = json.loads(raw)
        price = float(data.get("price", 0) or 0)
        source_note = str(data.get("source_note", "") or "")
        if price > 0:
            return {
                "found": True,
                "price": price,
                "source_note": source_note,
                "search_query": search_query,
            }
    except Exception:
        pass

    return {"found": False, "price": 0.0, "source_note": "", "search_query": search_query}