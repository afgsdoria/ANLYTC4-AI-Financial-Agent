"""
app.py — Financial AI Agent
Redesigned user journey:
  Landing → Onboarding wizard → Auto-dashboard with AI analysis
  Returning users → Sidebar expense/goal logging → AI re-analysis
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

from modules.database import (
    create_tables,
    save_user, get_user, set_onboarding_done,
    set_file_context, update_report_schedule,
    add_expense, get_expenses, get_expenses_with_id,
    get_total_spending, delete_expense,
    save_goal, get_goals, get_active_goal, get_active_goals,
    set_active_goal, toggle_goal_active, update_goal, delete_goal,
    save_chat_message, get_chat_history, clear_chat_history,
    save_ai_analysis, get_latest_ai_analysis,
)
from modules.ai_engine import (
    run_full_agent_analysis,
    generate_financial_advice,
    analyze_uploaded_financial_file,
    generate_forecast_advice,
    financial_chatbot_with_memory,
)
from modules.file_processor   import process_uploaded_file
from modules.forecasting       import generate_forecast
from modules.scoring           import calculate_financial_health_score
from modules.goal_engine       import extract_goal_from_text
from modules.alerts            import generate_spending_alerts
from modules.recommendations   import generate_recommendations
from modules.reports           import generate_financial_report

create_tables()

st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  DARK MODE CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body{color-scheme:dark}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
section.main,.main .block-container{
  background:#0D1117 !important;color:#E2E8F0 !important;
  font-family:'Inter',sans-serif;
}
[data-testid="stHeader"]{background:#0D1117 !important}
h1,h2,h3,h4,h5,h6{color:#F0F4FF !important}
p,li,span,label{color:#CBD5E0}

/* sidebar */
[data-testid="stSidebar"]{background:#080D18 !important;border-right:1px solid #1E2A3A !important}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,[data-testid="stSidebar"] span{color:#94A3B8 !important}
[data-testid="stSidebar"] hr{border-color:#1E2A3A !important}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stDateInput input{
  background:#131B2E !important;border:1px solid #2D3B55 !important;
  color:#E2E8F0 !important;border-radius:8px !important}
[data-testid="stSidebar"] .stSelectbox>div>div,
[data-testid="stSidebar"] [data-baseweb="select"]>div{
  background:#131B2E !important;border:1px solid #2D3B55 !important;
  color:#E2E8F0 !important;border-radius:8px !important}
[data-testid="stSidebar"] .stButton>button{
  background:linear-gradient(135deg,#3B82F6,#2563EB) !important;
  color:#fff !important;border:none !important;border-radius:8px !important;
  font-weight:600 !important;width:100%}
[data-testid="stSidebar"] .stProgress>div>div{background:#3B82F6 !important}
[data-testid="stSidebar"] .stProgress>div{background:#1E2A3A !important;border-radius:4px}

/* main inputs */
input,textarea,[data-baseweb="input"] input,.stTextInput input,
.stNumberInput input,.stTextArea textarea,.stDateInput input{
  background:#131B2E !important;border:1px solid #2D3B55 !important;
  color:#E2E8F0 !important;border-radius:8px !important}
input::placeholder,textarea::placeholder{color:#4A5568 !important}
[data-baseweb="select"]>div,.stSelectbox>div>div{
  background:#131B2E !important;border:1px solid #2D3B55 !important;color:#E2E8F0 !important}
[data-baseweb="popover"] ul,[data-baseweb="menu"]{
  background:#131B2E !important;border:1px solid #2D3B55 !important}
[data-baseweb="option"]{color:#E2E8F0 !important}
[data-baseweb="menu"] li:hover{background:#1E2A3A !important}

/* tabs */
.stTabs [data-baseweb="tab-list"]{background:#131B2E;border-radius:12px;padding:5px;gap:3px}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:#64748B !important;
  border-radius:8px !important;border:none !important;font-weight:500 !important;padding:8px 14px !important}
.stTabs [aria-selected="true"]{background:#1E2A3A !important;color:#60A5FA !important;font-weight:700 !important}
.stTabs [data-baseweb="tab-highlight"]{display:none !important}

/* metrics */
[data-testid="metric-container"]{background:#131B2E !important;border:1px solid #1E2A3A !important;
  border-radius:12px !important;padding:16px 20px !important;box-shadow:0 2px 10px rgba(0,0,0,.35) !important}
[data-testid="metric-container"] label,[data-testid="stMetricLabel"]{
  color:#64748B !important;font-size:.76rem !important;font-weight:600 !important;
  text-transform:uppercase;letter-spacing:.06em}
[data-testid="stMetricValue"]{color:#F0F4FF !important;font-weight:800 !important}
[data-testid="stMetricDelta"]{color:#60A5FA !important}

/* buttons */
.stButton>button{background:transparent !important;border:1.5px solid #3B82F6 !important;
  color:#60A5FA !important;border-radius:8px !important;font-weight:600 !important;
  transition:all .15s ease}
.stButton>button:hover{background:#3B82F6 !important;color:#fff !important}

/* alerts */
[data-testid="stAlert"]{border-radius:10px !important;border-left-width:4px !important;
  background:#131B2E !important}

/* chat */
[data-testid="stChatMessage"]{background:#131B2E !important;
  border:1px solid #1E2A3A !important;border-radius:12px !important}
[data-testid="stChatInput"]>div{background:#131B2E !important;
  border:1px solid #2D3B55 !important;border-radius:12px !important}
[data-testid="stChatInput"] textarea{background:transparent !important;color:#E2E8F0 !important}

/* forms */
[data-testid="stForm"]{background:#0F1623 !important;border:1px solid #1E2A3A !important;
  border-radius:12px !important;padding:16px !important}

/* expander */
[data-testid="stExpander"]{background:#131B2E !important;border:1px solid #1E2A3A !important;border-radius:10px !important}
[data-testid="stExpander"] summary{color:#94A3B8 !important}

/* uploader */
[data-testid="stFileUploader"]{background:#131B2E !important;
  border:1px dashed #2D3B55 !important;border-radius:10px !important}

hr{border-color:#1E2A3A !important}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#0D1117}
::-webkit-scrollbar-thumb{background:#2D3B55;border-radius:3px}

/* custom cards */
.profile-card{background:#131B2E;border:1px solid #1E2A3A;border-radius:14px;
  padding:20px 24px;margin-top:1rem;box-shadow:0 4px 16px rgba(0,0,0,.4)}
.profile-card h4{color:#F0F4FF;margin:0 0 14px;font-size:1rem;font-weight:700}
.profile-row{display:flex;justify-content:space-between;align-items:center;
  padding:9px 0;border-bottom:1px solid #1E2A3A}
.profile-row:last-child{border-bottom:none}
.profile-label{color:#64748B;font-size:.85rem;font-weight:500}
.profile-value{color:#E2E8F0;font-size:.9rem;font-weight:600}

.score-badge{display:inline-flex;align-items:center;
  background:linear-gradient(135deg,#1E3A8A,#3B82F6);
  color:#fff;border-radius:50px;padding:6px 22px;
  font-size:1.4rem;font-weight:800;box-shadow:0 4px 14px rgba(59,130,246,.4)}

.shdr{font-size:1rem;font-weight:700;color:#93C5FD;
  padding-left:10px;border-left:3px solid #3B82F6;margin:18px 0 10px}

/* plan step */
.plan-step{background:#0F1623;border:1px solid #1E2A3A;border-radius:10px;
  padding:14px 18px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start}
.plan-num{background:linear-gradient(135deg,#1E3A8A,#3B82F6);color:#fff;
  border-radius:50%;width:32px;height:32px;display:flex;align-items:center;
  justify-content:center;font-weight:800;font-size:.9rem;flex-shrink:0}
.plan-body{}
.plan-action{color:#E2E8F0;font-weight:600;font-size:.9rem}
.plan-meta{color:#64748B;font-size:.78rem;margin-top:3px}

/* risk badge */
.risk-badge{display:inline-block;background:#1C0808;border:1px solid #EF4444;
  color:#FCA5A5;border-radius:6px;padding:4px 10px;font-size:.78rem;
  font-weight:600;margin:3px 4px 3px 0}

/* wizard */
.wizard-card{background:linear-gradient(135deg,#0C1A2E,#0F2040);
  border:1px solid #1E3A5C;border-radius:20px;padding:40px 48px;
  max-width:820px;margin:0 auto;box-shadow:0 12px 40px rgba(0,0,0,.6)}
.wizard-card h1{color:#60A5FA;font-size:2rem;font-weight:800;margin:0 0 6px}
.wizard-card .sub{color:#64748B;font-size:1rem;margin:0 0 32px}
.step-pill{display:inline-flex;align-items:center;gap:6px;
  background:#131B2E;border:1px solid #2D3B55;border-radius:50px;
  padding:4px 14px;font-size:.78rem;color:#64748B;margin-bottom:24px}
.step-pill .active-dot{width:8px;height:8px;border-radius:50%;background:#3B82F6;display:inline-block}

/* landing feature card */
.feat-card{background:#0F1623;border:1px solid #1E2A3A;border-radius:14px;
  padding:20px;text-align:center}
.feat-icon{font-size:2rem;margin-bottom:10px}
.feat-title{color:#60A5FA;font-weight:700;font-size:.95rem;margin-bottom:6px}
.feat-desc{color:#64748B;font-size:.82rem;line-height:1.5}

/* success toast */
.toast-success{background:#052e16;border:1px solid #22C55E;border-radius:10px;
  padding:12px 18px;color:#86EFAC;font-weight:600;margin:8px 0}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def pesos(v): return f"₱{float(v):,.2f}"
def shdr(t):  st.markdown(f'<div class="shdr">{t}</div>', unsafe_allow_html=True)
def pcfg():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0D1117",
        font=dict(color="#94A3B8", family="Inter"),
        xaxis=dict(gridcolor="#1E2A3A", linecolor="#1E2A3A"),
        yaxis=dict(gridcolor="#1E2A3A", linecolor="#1E2A3A"),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS = dict(
    app_stage="landing",        # landing | onboard_profile | onboard_goal | dashboard
    username="",
    user_type="Student",
    age=18,
    monthly_income=0.0,
    savings_goal=0.0,
    current_savings=0.0,
    report_schedule="monthly",
    report_date=None,
    file_context=None,
    chat_messages=[],
    ai_analysis=None,           # latest dict from run_full_agent_analysis
    sidebar_exp_success=None,
    sidebar_goal_success=None,
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _load_user_into_session(udata: dict, username: str):
    st.session_state.username        = username
    st.session_state.user_type       = udata.get("user_type", "Student")
    st.session_state.age             = udata.get("age", 18) or 18
    st.session_state.monthly_income  = udata.get("monthly_income", 0.0)
    st.session_state.savings_goal    = udata.get("savings_goal", 0.0)
    st.session_state.current_savings = udata.get("current_savings", 0.0)
    st.session_state.report_schedule = udata.get("report_schedule", "monthly")
    st.session_state.file_context    = udata.get("file_context")
    fc = udata.get("file_context")
    st.session_state.file_context    = fc


def _trigger_ai_analysis():
    """Run the full agentic analysis and cache it in DB + session."""
    uname    = st.session_state.username
    expenses = get_expenses(uname)
    spending = get_total_spending(uname)
    goal     = get_active_goal(uname)
    result   = run_full_agent_analysis(
        username        = uname,
        user_type       = st.session_state.user_type,
        age             = st.session_state.age,
        income          = st.session_state.monthly_income,
        current_savings = st.session_state.current_savings,
        savings_goal    = st.session_state.savings_goal,
        total_spending  = spending,
        expenses        = expenses,
        active_goal     = goal,
        file_context    = st.session_state.file_context,
    )
    plan_text = json.dumps(result.get("step_plan", []))
    save_ai_analysis(uname, result.get("health_summary",""), plan_text)
    st.session_state.ai_analysis = result


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE: LANDING
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.app_stage == "landing":

    st.markdown("""
    <div style="text-align:center;padding:40px 20px 20px">
      <div style="font-size:3.5rem;margin-bottom:12px">💰</div>
      <h1 style="font-size:2.6rem;font-weight:800;color:#60A5FA;margin:0">Financial AI Agent</h1>
      <p style="color:#64748B;font-size:1.1rem;margin:10px 0 40px">
        Your autonomous AI financial coach — budgets, goals, forecasts & insights, all in one place.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    feats = [
        ("🤖", "Agentic Analysis",    "Multi-step AI reasoning that builds a personalized plan to reach your goal."),
        ("📊", "Live Dashboard",       "Health score, spending breakdown, and forecast — updated every time you log."),
        ("🎯", "Smart Goal Planner",   "Describe a goal in plain language. AI extracts the amount and deadline."),
        ("💬", "Finance-Only Chatbot", "Personalized AI coach that knows your income, spending, and goals."),
        ("📄", "Auto PDF Reports",     "Schedule daily, weekly, or monthly reports delivered as a downloadable PDF."),
        ("📁", "File Upload Analysis", "Upload your bank statement or expense tracker for AI-powered insights."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(feats):
        with cols[i % 3]:
            st.markdown(
                f'<div class="feat-card">'
                f'<div class="feat-icon">{icon}</div>'
                f'<div class="feat-title">{title}</div>'
                f'<div class="feat-desc">{desc}</div>'
                f'</div><br>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#64748B;font-size:.9rem;margin-bottom:6px">'
        'Enter a username to continue</p>',
        unsafe_allow_html=True,
    )

    lc, mc, rc = st.columns([2, 2, 2])
    with mc:
        uinput = st.text_input("Username", placeholder="e.g. juan_dela_cruz",
                               label_visibility="collapsed")
        b1, b2 = st.columns(2)
        go_new = b1.button("🚀 Create Account", use_container_width=True)
        go_log = b2.button("🔐 Login",          use_container_width=True)

    if go_new or go_log:
        name = uinput.strip()
        if not name:
            st.warning("Please enter a username.")
        else:
            existing = get_user(name)
            if existing and existing.get("onboarding_done"):
                # Returning user → go straight to dashboard
                _load_user_into_session(existing, name)
                cached = get_latest_ai_analysis(name)
                if cached[0]:
                    try:
                        plan = json.loads(cached[1]) if cached[1] else []
                        st.session_state.ai_analysis = {
                            "health_summary": cached[0],
                            "step_plan": plan,
                            "spending_habits": "",
                            "risk_flags": [],
                            "chart_insights": "",
                            "forecast_narrative": "",
                        }
                    except Exception:
                        pass
                st.session_state.app_stage = "dashboard"
                st.rerun()
            else:
                # New user OR incomplete onboarding → wizard
                st.session_state.username  = name
                st.session_state.app_stage = "onboard_profile"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE: ONBOARDING — PROFILE + GOAL (two-step wizard)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.app_stage in ("onboard_profile", "onboard_goal"):

    stage = st.session_state.app_stage
    step_label = "Step 1 of 2 — Your Profile" if stage == "onboard_profile" else "Step 2 of 2 — Your Goal"

    st.markdown(
        f'<div style="text-align:center;padding:30px 10px 0">'
        f'<span class="step-pill"><span class="active-dot"></span> &nbsp;{step_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Wizard card container ──────────────────────────────
    lpad, main_col, rpad = st.columns([1, 4, 1])
    with main_col:

        # ── STEP 1: Profile ───────────────────────────────
        if stage == "onboard_profile":
            st.markdown(
                '<div class="wizard-card">'
                '<h1>👋 Welcome!</h1>'
                '<p class="sub">Let\'s set up your financial profile. '
                'This takes about 60 seconds.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

            # ── Report preference is OUTSIDE the form so custom date
            #    picker appears reactively when "custom date" is chosen ──────
            st.markdown("#### 📅 Report Preference")
            report_schedule = st.selectbox(
                "How often would you like your financial report?",
                ["daily", "weekly", "monthly", "custom date"],
                key="ob_sched",
            )
            report_date = None
            if st.session_state.get("ob_sched") == "custom date":
                report_date = str(st.date_input(
                    "Pick your report date",
                    value=date.today(),
                    key="ob_rdate",
                ))
                st.caption("You'll be able to generate a report on this date from the Report tab.")

            st.markdown("#### 📂 Previous Financial Tracker (Optional · max 200 MB)")
            st.caption("Upload a CSV, Excel, PDF, or Word file from your old tracker. "
                       "The AI will use it as extra context for your analysis.")
            uploaded = st.file_uploader(
                "Upload file", type=["csv","xlsx","xls","txt","pdf","docx"],
                key="ob_upload",
                label_visibility="collapsed",
            )

            with st.form("onboard_profile_form"):
                st.markdown("#### 👤 About You")
                user_type = st.selectbox(
                    "What best describes you?",
                    ["Student", "Working Individual", "Business Owner",
                     "Part-time Worker", "Freelancer"],
                )
                age = st.number_input("Your age", min_value=13, max_value=100, value=22, step=1)

                st.markdown("#### 💵 Your Finances")
                monthly_income = st.number_input(
                    "Monthly Income / Allowance (₱)",
                    min_value=0.0, value=0.0, step=500.0, format="%.2f",
                    help="Your take-home pay or monthly allowance",
                )
                current_savings = st.number_input(
                    "Current Savings (₱)",
                    min_value=0.0, value=0.0, step=500.0, format="%.2f",
                    help="How much you have saved right now",
                )
                savings_goal = st.number_input(
                    "Overall Savings Target (₱)",
                    min_value=0.0, value=0.0, step=1000.0, format="%.2f",
                    help="Total amount you want to save (can be updated anytime)",
                )

                submitted = st.form_submit_button("Continue →", use_container_width=True)

            if submitted:
                if monthly_income <= 0:
                    st.error("Please enter your monthly income to continue.")
                else:
                    file_ctx = None
                    if uploaded:
                        if uploaded.size > 200 * 1024 * 1024:
                            st.error("File exceeds 200 MB limit. Please upload a smaller file.")
                            st.stop()
                        with st.spinner("Reading your uploaded tracker…"):
                            raw_text = process_uploaded_file(uploaded)
                            file_ctx = raw_text[:5000]

                    save_user(
                        username        = st.session_state.username,
                        user_type       = user_type,
                        monthly_income  = monthly_income,
                        savings_goal    = savings_goal,
                        current_savings = current_savings,
                        age             = int(age),
                        report_schedule = report_schedule,
                        report_date     = report_date,
                        file_context    = file_ctx,
                        onboarding_done = 0,
                    )
                    st.session_state.user_type       = user_type
                    st.session_state.age             = int(age)
                    st.session_state.monthly_income  = monthly_income
                    st.session_state.current_savings = current_savings
                    st.session_state.savings_goal    = savings_goal
                    st.session_state.report_schedule = report_schedule
                    st.session_state.report_date     = report_date
                    st.session_state.file_context    = file_ctx
                    st.session_state.app_stage       = "onboard_goal"
                    st.rerun()

        # ── STEP 2: Goal ──────────────────────────────────
        elif stage == "onboard_goal":
            st.markdown(
                '<div class="wizard-card">'
                '<h1>🎯 What\'s Your Goal?</h1>'
                '<p class="sub">Describe your financial goal in plain language. '
                'The AI will extract the amount and deadline automatically.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="background:#0C1A2E;border:1px solid #1E3A5C;border-radius:10px;'
                'padding:14px 18px;margin-bottom:16px">'
                '<p style="color:#60A5FA;font-weight:700;margin:0 0 4px">💡 Examples</p>'
                '<p style="color:#64748B;font-size:.85rem;margin:0">'
                '"I want to save ₱50,000 for a laptop in 6 months"<br>'
                '"I want an emergency fund of ₱30,000 by December 2026"<br>'
                '"Save ₱200,000 for a travel fund within 2 years"'
                '</p></div>',
                unsafe_allow_html=True,
            )

            with st.form("onboard_goal_form"):
                goal_text = st.text_area(
                    "Describe your goal",
                    placeholder="I want to save ₱50,000 for a laptop in 6 months",
                    height=100, label_visibility="collapsed",
                )
                col_back, col_next = st.columns(2)
                go_back = col_back.form_submit_button("← Back")
                go_next = col_next.form_submit_button("🚀 Build My Dashboard", use_container_width=True)

            if go_back:
                st.session_state.app_stage = "onboard_profile"
                st.rerun()

            if go_next:
                if goal_text.strip():
                    parsed = extract_goal_from_text(goal_text, st.session_state.monthly_income)
                    save_goal(
                        st.session_state.username,
                        parsed["goal_name"],
                        parsed["target_amount"],
                        parsed["deadline"],
                    )
                    # Activate the new goal
                    goals = get_goals(st.session_state.username)
                    if goals:
                        toggle_goal_active(st.session_state.username, goals[0][0], True)

                # Mark onboarding complete & run AI
                set_onboarding_done(st.session_state.username)
                with st.spinner("🤖 AI is analyzing your finances… this takes ~15 seconds"):
                    _trigger_ai_analysis()

                st.session_state.app_stage = "dashboard"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE: DASHBOARD  (main app for all logged-in users)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.app_stage == "dashboard":

    uname    = st.session_state.username
    income   = st.session_state.monthly_income
    savings  = st.session_state.current_savings
    goal_amt = st.session_state.savings_goal
    spending = get_total_spending(uname)
    remaining = income - spending
    active_goals = get_active_goals(uname)           # list of dicts
    active_goal  = active_goals[0] if active_goals else None  # first one for compat

    # Load cached AI analysis if session is empty (e.g. after page refresh)
    if st.session_state.ai_analysis is None:
        cached = get_latest_ai_analysis(uname)
        if cached[0]:
            try:
                plan = json.loads(cached[1]) if cached[1] else []
            except Exception:
                plan = []
            st.session_state.ai_analysis = {
                "health_summary": cached[0],
                "step_plan": plan,
                "spending_habits": "",
                "risk_flags": [],
                "chart_insights": "",
                "forecast_narrative": "",
            }

    ai = st.session_state.ai_analysis or {}

    # ── SIDEBAR (returning users: expense logger + goal adder) ──
    with st.sidebar:
        st.markdown(f"## 💰 Hi, {uname}!")
        st.markdown(
            f"<small style='color:#4A5568'>{st.session_state.user_type} · "
            f"Age {st.session_state.age}</small>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Active Goal(s) Progress ──────────────────────
        active_goals_sb = get_active_goals(uname_sb)
        if active_goals_sb:
            st.markdown(f"### 🎯 Active Goal{'s' if len(active_goals_sb)>1 else ''}")
            for ag in active_goals_sb:
                prog = min(1.0, savings / ag["target_amount"]
                           if ag["target_amount"] > 0 else 0)
                st.markdown(
                    f"<span style='color:#E2E8F0;font-weight:600'>{ag['goal_name']}</span>",
                    unsafe_allow_html=True,
                )
                st.progress(prog)
                st.markdown(
                    f"<small style='color:#60A5FA'>{pesos(savings)} / "
                    f"{pesos(ag['target_amount'])} ({prog*100:.0f}%)"
                    f" · 🗓 {ag['deadline']}</small>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")

        # ── Expense Logger ───────────────────────────────
        st.markdown("### ➕ Log Expense")
        exp_cat = st.selectbox(
            "Category",
            ["Food","Transportation","School","Shopping",
             "Entertainment","Bills","Savings","Health","Other"],
            key="sb_cat",
        )
        exp_amt  = st.number_input("Amount (₱)", min_value=0.01, step=10.0,
                                    format="%.2f", key="sb_amt")
        exp_date = st.date_input("Date", value=date.today(), key="sb_date")

        if st.button("➕ Add Expense", use_container_width=True):
            if exp_amt > 0:
                add_expense(uname, exp_cat, exp_amt, str(exp_date))
                st.session_state.sidebar_exp_success = (
                    f"✅ {pesos(exp_amt)} ({exp_cat}) logged on {exp_date}!"
                )
                # Re-run AI analysis after new expense
                with st.spinner("Updating AI analysis…"):
                    _trigger_ai_analysis()
                st.rerun()
            else:
                st.warning("Amount must be > 0.")

        if st.session_state.sidebar_exp_success:
            st.success(st.session_state.sidebar_exp_success)
            st.session_state.sidebar_exp_success = None

        st.markdown("---")

        # ── Goal Adder ───────────────────────────────────
        st.markdown("### 🎯 Add Goal")
        new_goal_txt = st.text_area(
            "Describe your goal", height=80,
            placeholder="Save ₱20,000 for a phone in 4 months",
            key="sb_goal_txt",
        )
        if st.button("✨ Save Goal", use_container_width=True):
            if new_goal_txt.strip():
                parsed = extract_goal_from_text(new_goal_txt, income)
                save_goal(uname, parsed["goal_name"],
                          parsed["target_amount"], parsed["deadline"])
                # Auto-activate the newly added goal
                goals = get_goals(uname)
                if goals:
                    toggle_goal_active(uname, goals[0][0], True)
                st.session_state.sidebar_goal_success = (
                    f"✅ Goal saved & activated: **{parsed['goal_name']}** — "
                    f"{pesos(parsed['target_amount'])} by {parsed['deadline']}"
                )
                with st.spinner("Updating AI analysis…"):
                    _trigger_ai_analysis()
                st.rerun()
            else:
                st.warning("Describe your goal first.")

        if st.session_state.sidebar_goal_success:
            st.success(st.session_state.sidebar_goal_success)
            st.session_state.sidebar_goal_success = None

        st.markdown("---")
        if st.button("🔄 Re-run AI Analysis", use_container_width=True):
            with st.spinner("Running AI analysis…"):
                _trigger_ai_analysis()
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── MAIN TABS ────────────────────────────────────────────────────────────
    (t_dash, t_plan, t_expenses, t_forecast,
     t_chat, t_report, t_settings) = st.tabs([
        "📊 Dashboard", "🗺️ Action Plan", "💸 Expenses",
        "🔮 Forecast",  "💬 AI Chat",     "📄 Report",
        "⚙️ Settings",
    ])

    # ════════════════════════════════════════════════════
    # TAB 1 — DASHBOARD
    # ════════════════════════════════════════════════════
    with t_dash:
        st.markdown("## 📊 Dashboard")
        st.caption(f"Auto-updated by AI · Last analysis includes all logged data.")

        # ── KPIs ────────────────────────────────────────
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Monthly Income",  pesos(income))
        k2.metric("Total Spending",  pesos(spending),
                  f"{spending/income*100:.0f}% of income" if income else None)
        k3.metric("Remaining",       pesos(remaining))
        k4.metric("Current Savings", pesos(savings),
                  f"{savings/goal_amt*100:.0f}% of goal" if goal_amt else None)

        st.markdown("---")

        # ── Health Score ─────────────────────────────────
        score, level = calculate_financial_health_score(income, spending, savings)
        score_col = "#22C55E" if score>=80 else "#F59E0B" if score>=60 else "#EF4444"
        c_sc, c_ga = st.columns([1,2])

        with c_sc:
            st.markdown("#### 💡 Financial Health Score")
            st.markdown(
                f'<div style="margin:14px 0">'
                f'<span class="score-badge">{score}/100</span></div>'
                f'<p style="font-size:1.05rem;font-weight:700;color:{score_col};margin:4px 0">{level}</p>',
                unsafe_allow_html=True,
            )
            # AI health summary
            if ai.get("health_summary"):
                st.info(ai["health_summary"])

        with c_ga:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                number={"suffix":"/100","font":{"color":"#E2E8F0","size":26}},
                domain={"x":[0,1],"y":[0,1]},
                gauge={
                    "axis":{"range":[0,100],"tickcolor":"#2D3B55","tickfont":{"color":"#64748B"}},
                    "bar":{"color":score_col,"thickness":0.28},
                    "bgcolor":"#131B2E","bordercolor":"#1E2A3A",
                    "steps":[
                        {"range":[0,40],"color":"#1C0808"},
                        {"range":[40,60],"color":"#1C1507"},
                        {"range":[60,80],"color":"#052E16"},
                        {"range":[80,100],"color":"#0C1A2E"},
                    ],
                },
            ))
            fig_g.update_layout(
                height=220, margin=dict(t=20,b=10,l=20,r=20),
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8"),
            )
            st.plotly_chart(fig_g, use_container_width=True)

        st.markdown("---")

        # ── AI Spending Habits + Risk Flags ─────────────
        expenses = get_expenses(uname)
        sh_col, rf_col = st.columns(2)

        with sh_col:
            shdr("🔍 AI Spending Analysis")
            if ai.get("spending_habits"):
                st.info(ai["spending_habits"])
            else:
                alerts = generate_spending_alerts(income, spending, expenses)
                for a in (alerts or ["✅ No spending issues detected."]):
                    st.warning(a) if "⚠" in a or "🚨" in a else st.success(a)

        with rf_col:
            shdr("🚩 Risk Flags")
            flags = ai.get("risk_flags") or []
            if flags:
                badges = "".join(f'<span class="risk-badge">{f}</span>' for f in flags)
                st.markdown(badges, unsafe_allow_html=True)
            else:
                recs = generate_recommendations(income, spending, goal_amt,
                                                savings, expenses, active_goal)
                for r in recs[:3]:
                    st.info(r)

        st.markdown("---")

        # ── Charts (AI-narrated) ─────────────────────────
        shdr("📈 Spending Breakdown")
        if expenses:
            df_e = pd.DataFrame(expenses, columns=["Category","Amount","Date"])
            ch1, ch2 = st.columns(2)
            with ch1:
                fig_pie = px.pie(
                    df_e, names="Category", values="Amount", hole=0.42,
                    color_discrete_sequence=[
                        "#3B82F6","#8B5CF6","#10B981","#F59E0B",
                        "#EF4444","#06B6D4","#EC4899","#84CC16","#F97316"
                    ],
                )
                fig_pie.update_traces(textfont=dict(color="#E2E8F0"), pull=[0.03]*20)
                fig_pie.update_layout(height=300, margin=dict(t=20,b=10,l=10,r=10),
                                       paper_bgcolor="rgba(0,0,0,0)",
                                       legend=dict(font=dict(color="#94A3B8")))
                st.plotly_chart(fig_pie, use_container_width=True)
            with ch2:
                df_cat = df_e.groupby("Category",as_index=False)["Amount"].sum()
                df_cat = df_cat.sort_values("Amount", ascending=True)
                fig_bar = px.bar(df_cat, x="Amount", y="Category", orientation="h",
                                  color="Amount",
                                  color_continuous_scale=["#1E3A5C","#3B82F6","#60A5FA"])
                fig_bar.update_layout(height=300,margin=dict(t=20,b=10,l=10,r=10),
                                       coloraxis_showscale=False,**pcfg())
                st.plotly_chart(fig_bar, use_container_width=True)
            # AI chart narrative
            if ai.get("chart_insights"):
                st.caption(f"🤖 {ai['chart_insights']}")
        else:
            st.info("Log expenses using the sidebar — charts will appear here.")

    # ════════════════════════════════════════════════════
    # TAB 2 — ACTION PLAN
    # ════════════════════════════════════════════════════
    with t_plan:
        st.markdown("## 🗺️ Your AI Action Plan")
        st.caption("A step-by-step roadmap generated by the AI reasoning engine to reach your goal.")

        # Goal progress banners — all active goals
        all_active = get_active_goals(uname)
        for ag in all_active:
            ag_prog = min(1.0, savings / ag["target_amount"] if ag["target_amount"] > 0 else 0)
            st.markdown(
                f'<div style="background:#0C1A2E;border:1px solid #1E3A5C;'
                f'border-radius:12px;padding:14px 18px;margin-bottom:10px">'
                f'<p style="color:#60A5FA;font-weight:700;margin:0 0 6px">'
                f'🎯 {ag["goal_name"]}</p>'
                f'<p style="color:#94A3B8;font-size:.82rem;margin:0 0 8px">'
                f'{pesos(savings)} saved of {pesos(ag["target_amount"])} '
                f'· Deadline: {ag["deadline"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.progress(ag_prog, text=f"{ag_prog*100:.0f}% of {ag['goal_name']} reached")

        st.markdown("---")

        steps = ai.get("step_plan") or []
        if steps:
            shdr("📋 Step-by-Step Plan")
            for s in steps:
                amount_badge = ""
                if s.get("amount") and str(s["amount"]).strip():
                    amount_badge = (
                        f'<span style="color:#60A5FA;font-weight:700">'
                        f'{s["amount"]}</span> · '
                    )
                st.markdown(
                    f'<div class="plan-step">'
                    f'  <div class="plan-num">{s["step"]}</div>'
                    f'  <div class="plan-body">'
                    f'    <div class="plan-action">{s["action"]}</div>'
                    f'    <div class="plan-meta">{amount_badge}'
                    f'    ⏱ {s.get("timeline","")}</div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Run the AI analysis (sidebar → 🔄 Re-run AI Analysis) to generate your action plan.")

        st.markdown("---")
        shdr("💡 Smart Recommendations")
        expenses = get_expenses(uname)
        recs = generate_recommendations(income, spending, goal_amt,
                                         savings, expenses, active_goal)
        for r in recs:
            st.info(r)

        if ai.get("forecast_narrative"):
            st.markdown("---")
            shdr("🔮 AI Forecast Commentary")
            st.info(ai["forecast_narrative"])

    # ════════════════════════════════════════════════════
    # TAB 3 — EXPENSES
    # ════════════════════════════════════════════════════
    with t_expenses:
        st.markdown("## 💸 Expense Tracker")

        exps_id = get_expenses_with_id(uname)
        if exps_id:
            df_all = pd.DataFrame(exps_id, columns=["ID","Category","Amount","Date"])
            total  = df_all["Amount"].sum()

            e1,e2 = st.columns(2)
            e1.metric("Total Transactions", len(df_all))
            e2.metric("Total Spent", pesos(total))
            st.markdown("---")

            cat_filter = st.multiselect(
                "Filter by category",
                options=sorted(df_all["Category"].unique()), default=[],
            )
            df_show = df_all if not cat_filter else df_all[df_all["Category"].isin(cat_filter)]

            h1,h2,h3,h4 = st.columns([2,3,2,1])
            for col, lbl in zip([h1,h2,h3,h4],["DATE","CATEGORY","AMOUNT",""]):
                col.markdown(
                    f"<span style='color:#60A5FA;font-size:.8rem;font-weight:700'>{lbl}</span>",
                    unsafe_allow_html=True,
                )
            st.markdown("<hr style='margin:4px 0 6px;border-color:#1E2A3A'>",
                        unsafe_allow_html=True)

            for _, row in df_show.iterrows():
                c1,c2,c3,c4 = st.columns([2,3,2,1])
                c1.markdown(f"<span style='color:#4A5568;font-size:.87rem'>{row['Date']}</span>",
                             unsafe_allow_html=True)
                c2.markdown(f"<span style='color:#CBD5E0;font-weight:600'>{row['Category']}</span>",
                             unsafe_allow_html=True)
                c3.markdown(f"<span style='color:#60A5FA;font-weight:700'>{pesos(row['Amount'])}</span>",
                             unsafe_allow_html=True)
                if c4.button("🗑️", key=f"del_{row['ID']}", help="Delete"):
                    delete_expense(int(row["ID"]))
                    with st.spinner("Updating AI analysis…"):
                        _trigger_ai_analysis()
                    st.rerun()

            st.markdown("---")
            shdr("📅 Daily Spending Trend")
            df_t = df_all.copy()
            df_t["Date"] = pd.to_datetime(df_t["Date"], errors="coerce")
            df_t = df_t.dropna(subset=["Date"])
            if not df_t.empty:
                df_daily = df_t.groupby("Date")["Amount"].sum().reset_index()
                fig_t = px.area(df_daily, x="Date", y="Amount",
                                 color_discrete_sequence=["#3B82F6"])
                fig_t.update_traces(fill="tozeroy", fillcolor="rgba(59,130,246,0.1)")
                fig_t.update_layout(height=260,margin=dict(t=20,b=20,l=20,r=20),**pcfg())
                st.plotly_chart(fig_t, use_container_width=True)
        else:
            st.info("No expenses yet. Use the sidebar to log your first expense!")

    # ════════════════════════════════════════════════════
    # TAB 4 — FORECAST
    # ════════════════════════════════════════════════════
    with t_forecast:
        st.markdown("## 🔮 Savings Forecast")

        spending_now = get_total_spending(uname)
        fdf, monthly_sav, est_mo = generate_forecast(
            income, spending_now, savings, goal_amt
        )

        f1,f2,f3 = st.columns(3)
        f1.metric("Monthly Net Savings", pesos(monthly_sav))
        f2.metric("Months to Goal",
                  f"{est_mo:.1f}" if est_mo is not None else "N/A")
        f3.metric("Goal Amount", pesos(goal_amt))

        fig_fc = px.line(fdf, x="Month", y="Projected Savings",
                          markers=True, color_discrete_sequence=["#3B82F6"])
        fig_fc.update_traces(line=dict(width=2.5),
                              marker=dict(size=7, color="#60A5FA"))
        if goal_amt > 0:
            fig_fc.add_hline(
                y=goal_amt, line_dash="dash", line_color="#EF4444", line_width=1.5,
                annotation_text=f"🎯 Goal: {pesos(goal_amt)}",
                annotation_font_color="#EF4444",
            )
        fig_fc.update_layout(height=340,margin=dict(t=30,b=20,l=20,r=20),**pcfg())
        st.plotly_chart(fig_fc, use_container_width=True)

        if ai.get("forecast_narrative"):
            st.info(f"🤖 {ai['forecast_narrative']}")

        if st.button("🤖 Get Fresh AI Forecast Advice"):
            with st.spinner("Generating forecast advice…"):
                adv = generate_forecast_advice(monthly_sav, est_mo)
            shdr("AI Forecast Analysis")
            st.info(adv)

    # ════════════════════════════════════════════════════
    # TAB 5 — AI CHAT
    # ════════════════════════════════════════════════════
    with t_chat:
        st.markdown("## 💬 AI Financial Coach")
        st.caption(
            "I'm your personalized finance coach. I only answer finance-related questions "
            "and I know your income, spending, goals, and plan."
        )

        if not st.session_state.chat_messages:
            db_h = get_chat_history(uname)
            st.session_state.chat_messages = [{"role":r,"content":m} for r,m in db_h]

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask about your finances…")
        if prompt:
            st.session_state.chat_messages.append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            context = (
                f"User: {uname} | Type: {st.session_state.user_type} | Age: {st.session_state.age}\n"
                f"Monthly Income: {pesos(income)}\n"
                f"Current Savings: {pesos(savings)}\n"
                f"Total Spending: {pesos(get_total_spending(uname))}\n"
                f"Savings Goal: {pesos(goal_amt)}\n"
                f"Active Goal: {active_goal['goal_name'] if active_goal else 'None'}"
            )
            history = get_chat_history(uname)
            with st.spinner("Thinking…"):
                reply = financial_chatbot_with_memory(
                    uname, prompt, history, context, ai
                )
            save_chat_message(uname,"user",prompt)
            save_chat_message(uname,"assistant",reply)
            st.session_state.chat_messages.append({"role":"assistant","content":reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

        if st.button("🗑️ Clear Chat"):
            clear_chat_history(uname)
            st.session_state.chat_messages = []
            st.rerun()

    # ════════════════════════════════════════════════════
    # TAB 6 — REPORT
    # ════════════════════════════════════════════════════
    with t_report:
        st.markdown("## 📄 Financial Report")
        st.caption("Auto-generates a PDF with your full AI analysis, plan, score, and recommendations.")

        # Report schedule info
        sched = st.session_state.report_schedule
        st.info(
            f"📅 Your report is scheduled: **{sched.capitalize()}**"
            + (f" on {st.session_state.get('report_date','')}"
               if sched == "custom date" else "")
            + " — you can change this in ⚙️ Settings."
        )

        if st.button("🖨️ Generate PDF Report Now"):
            spending_r = get_total_spending(uname)
            expenses_r = get_expenses(uname)
            active_r   = get_active_goal(uname)
            score_r, level_r = calculate_financial_health_score(income, spending_r, savings)
            alerts_r = generate_spending_alerts(income, spending_r, expenses_r)
            recs_r   = generate_recommendations(income, spending_r, goal_amt,
                                                 savings, expenses_r, active_r)
            with st.spinner("Generating AI analysis for report…"):
                advice_r = generate_financial_advice(
                    uname, st.session_state.user_type, income, goal_amt,
                    savings, spending_r, expenses_r, active_r,
                )
            with st.spinner("Building PDF…"):
                pdf_path = generate_financial_report(
                    username=uname, advice=advice_r,
                    score=score_r, level=level_r,
                    recommendations=recs_r, alerts=alerts_r,
                    monthly_income=income, total_spending=spending_r,
                    current_savings=savings, savings_goal=goal_amt,
                    goal_name=active_r["goal_name"]     if active_r else None,
                    target_amount=active_r["target_amount"] if active_r else None,
                    deadline=active_r["deadline"]       if active_r else None,
                )
            with open(pdf_path,"rb") as f:
                st.download_button(
                    "⬇️ Download PDF Report", data=f,
                    file_name=f"{uname}_financial_report.pdf",
                    mime="application/pdf", use_container_width=True,
                )
            st.success("✅ Report ready! Click above to download.")

    # ════════════════════════════════════════════════════
    # TAB 7 — SETTINGS
    # ════════════════════════════════════════════════════
    with t_settings:
        st.markdown("## ⚙️ Settings")

        # ── Profile update ───────────────────────────────
        shdr("👤 Update Profile")
        with st.form("settings_profile"):
            opts = ["Student","Working Individual","Business Owner",
                    "Part-time Worker","Freelancer"]
            u_type = st.selectbox("User Type", opts,
                                   index=opts.index(st.session_state.user_type)
                                   if st.session_state.user_type in opts else 0)
            u_age  = st.number_input("Age", min_value=13, max_value=100,
                                      value=int(st.session_state.age), step=1)
            u_inc  = st.number_input("Monthly Income (₱)", min_value=0.0,
                                      value=float(income), step=500.0, format="%.2f")
            u_sav  = st.number_input("Current Savings (₱)", min_value=0.0,
                                      value=float(savings), step=500.0, format="%.2f")
            u_goal = st.number_input("Savings Target (₱)", min_value=0.0,
                                      value=float(goal_amt), step=1000.0, format="%.2f")
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                save_user(uname, u_type, u_inc, u_goal, u_sav, int(u_age),
                          st.session_state.report_schedule,
                          st.session_state.get("report_date"),
                          st.session_state.file_context, 1)
                st.session_state.user_type       = u_type
                st.session_state.age             = int(u_age)
                st.session_state.monthly_income  = u_inc
                st.session_state.current_savings = u_sav
                st.session_state.savings_goal    = u_goal
                with st.spinner("Re-running AI analysis with updated data…"):
                    _trigger_ai_analysis()
                st.success("✅ Profile updated and AI analysis refreshed!")
                st.rerun()

        st.markdown("---")

        # ── Report schedule — outside form so custom date picker is reactive ─
        shdr("📅 Report Schedule")
        sched_opts = ["daily","weekly","monthly","custom date"]
        cur_idx = sched_opts.index(st.session_state.report_schedule) \
                  if st.session_state.report_schedule in sched_opts else 2
        sched = st.selectbox("How often do you want a report?", sched_opts,
                              index=cur_idx, key="set_sched")
        rdate = None
        if sched == "custom date":
            rdate = str(st.date_input("Pick date", value=date.today(), key="set_rdate"))
            st.caption("Report will be available on this date in the Report tab.")
        if st.button("💾 Save Schedule", key="save_sched"):
            update_report_schedule(uname, sched, rdate)
            st.session_state.report_schedule = sched
            st.session_state.report_date     = rdate
            st.success(f"✅ Report schedule set to: **{sched}**"
                       + (f" on {rdate}" if rdate else ""))

        st.markdown("---")

        # ── Goals manager ─────────────────────────────────────────────────────
        shdr("🎯 Manage Goals")
        st.caption("You can have **multiple active goals** at the same time. Toggle each on or off independently.")
        all_goals = get_goals(uname)
        if all_goals:
            for gid, gname, gtarget, gdeadline, gactive in all_goals:
                gp = min(1.0, savings / gtarget if gtarget > 0 else 0)
                gc1, gc2, gc3, gc4 = st.columns([4, 2, 1, 1])
                with gc1:
                    status_icon = "🟢 Active" if gactive else "⚫ Inactive"
                    st.markdown(f"**{gname}** &nbsp; {status_icon}")
                    st.caption(f"{pesos(gtarget)} · Deadline: {gdeadline}")
                    st.progress(gp, text=f"{gp*100:.0f}% saved")
                with gc2:
                    btn_label = "⏸ Deactivate" if gactive else "▶ Activate"
                    if st.button(btn_label, key=f"tog_{gid}", use_container_width=True):
                        toggle_goal_active(uname, gid, not bool(gactive))
                        st.rerun()
                with gc3:
                    if st.button("✏️", key=f"eg_{gid}", help="Edit"):
                        st.session_state[f"em_{gid}"] = True
                with gc4:
                    if st.button("🗑️", key=f"dg_{gid}", help="Delete"):
                        delete_goal(gid)
                        st.rerun()
                if st.session_state.get(f"em_{gid}"):
                    with st.form(f"ef_{gid}"):
                        n = st.text_input("Goal Name", value=gname)
                        a = st.number_input("Target Amount (₱)", value=float(gtarget), step=500.0)
                        d = st.text_input("Deadline (YYYY-MM-DD)", value=str(gdeadline))
                        cs_, cc_ = st.columns(2)
                        if cs_.form_submit_button("💾 Save"):
                            update_goal(gid, n, a, d)
                            st.session_state[f"em_{gid}"] = False
                            st.rerun()
                        if cc_.form_submit_button("✖ Cancel"):
                            st.session_state[f"em_{gid}"] = False
                            st.rerun()
                st.markdown("---")
        else:
            st.info("No goals yet. Add one from the sidebar.")

        # ── Profile card ─────────────────────────────────
        st.markdown("---")
        shdr("📋 Current Profile Summary")
        rows = [
            ("👤 Username",        uname),
            ("🏷️ User Type",       st.session_state.user_type),
            ("🎂 Age",             str(st.session_state.age)),
            ("💵 Monthly Income",  pesos(income)),
            ("🎯 Savings Target",  pesos(goal_amt)),
            ("🏦 Current Savings", pesos(savings)),
            ("📅 Report Schedule", st.session_state.report_schedule.capitalize()),
        ]
        rows_html = "".join(
            f'<div class="profile-row">'
            f'<span class="profile-label">{lb}</span>'
            f'<span class="profile-value">{vl}</span>'
            f'</div>'
            for lb,vl in rows
        )
        st.markdown(
            f'<div class="profile-card"><h4>Profile</h4>{rows_html}</div>',
            unsafe_allow_html=True,
        )