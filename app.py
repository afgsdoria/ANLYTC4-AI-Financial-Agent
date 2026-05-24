"""
app.py
Financial AI Agent — Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

from modules.database import (
    create_tables,
    save_user, get_user,
    add_expense, get_expenses, get_expenses_with_id,
    get_total_spending, get_spending_by_category,
    delete_expense,
    save_goal, get_goals, get_active_goal,
    set_active_goal, update_goal, delete_goal,
    save_chat_message, get_chat_history, clear_chat_history,
)
from modules.ai_engine import (
    generate_financial_advice,
    analyze_uploaded_financial_file,
    generate_forecast_advice,
    financial_chatbot_with_memory,
)
from modules.file_processor import process_uploaded_file
from modules.forecasting import generate_forecast
from modules.scoring import calculate_financial_health_score
from modules.goal_engine import extract_goal_from_text
from modules.alerts import generate_spending_alerts
from modules.recommendations import generate_recommendations
from modules.reports import generate_financial_report
from modules.onboarding import get_getting_started_content

create_tables()

st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background-color: #0F172A;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F2744 0%, #1A3A5C 100%) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #CBD5E0 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: #1A1A1A;
    border: 1px solid #334155;
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: rgba(255,255,255,0.4) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1A1A1A !important;
    border: 1px solid #334155 !important;
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stNumberInput input {
    background: #1A1A1A !important;
    border: 1px solid #334155 !important;
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stDateInput input {
    background: #1A1A1A !important;
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
    transform: translateY(-1px);
}
[data-testid="stSidebar"] .stProgress > div > div {
    background-color: #3B82F6 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #1E293B;
    padding: 6px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #334155 !important;
    color: #60A5FA !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #1E293B;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.3);
    border: 1px solid #334155;
}
[data-testid="metric-container"] label {
    color: #94A3B8 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #E8EEF7 !important;
    font-weight: 700 !important;
}

/* ── Buttons (main area) ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: 1.5px solid #3B82F6 !important;
    color: #3B82F6 !important;
    background: transparent !important;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #3B82F6 !important;
    color: white !important;
}
.stButton > button[kind="primary"] {
    background: #3B82F6 !important;
    color: white !important;
}

/* ── Info / Warning / Success boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
}

/* ── Profile summary card ── */
.profile-card {
    background: #1E293B;
    border-radius: 14px;
    padding: 20px 24px;
    border: 1px solid #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    margin-top: 1rem;
}
.profile-card h4 {
    color: #E8EEF7;
    margin: 0 0 14px 0;
    font-size: 1rem;
    font-weight: 700;
}
.profile-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #334155;
}
.profile-row:last-child {
    border-bottom: none;
}
.profile-label {
    color: #94A3B8;
    font-size: 0.85rem;
    font-weight: 500;
}
.profile-value {
    color: #E8EEF7;
    font-size: 0.9rem;
    font-weight: 600;
}

/* ── Score badge ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #1E40AF, #3B82F6);
    color: white;
    border-radius: 50px;
    padding: 6px 20px;
    font-size: 1.4rem;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(59,130,246,0.35);
}

/* ── Section dividers ── */
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #E8EEF7;
    padding-left: 10px;
    border-left: 4px solid #3B82F6;
    margin: 18px 0 10px 0;
}

/* ── Expense table rows ── */
.exp-row {
    display: flex;
    align-items: center;
    background: #1E293B;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    border: 1px solid #334155;
    font-size: 0.88rem;
}
.exp-date  { color: #94A3B8; width: 110px; }
.exp-cat   { color: #E8EEF7; font-weight: 600; flex: 1; }
.exp-amt   { color: #60A5FA; font-weight: 700; width: 110px; text-align: right; }

/* ── Chat ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def pesos(v: float) -> str:
    return f"₱{v:,.2f}"


def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─── Session state defaults ────────────────────────────────────────────────────
for k, v in {
    "username": "", "user_type": "Student",
    "monthly_income": 0.0, "savings_goal": 0.0,
    "current_savings": 0.0, "logged_in": False,
    "chat_messages": [], "show_getting_started_modal": True,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 💰 Financial AI Agent")
    st.markdown("*Your personal finance coach*")
    st.markdown("---")

    # ── Login ────────────────────────────────────────────────
    st.markdown("### 👤 Login")
    username_input = st.text_input(
        "Username", value=st.session_state.username,
        placeholder="Enter your username",
        label_visibility="collapsed",
    )
    if st.button("🔐 Login / Load Profile", use_container_width=True):
        if username_input.strip():
            st.session_state.username = username_input.strip()
            existing = get_user(username_input.strip())
            if existing:
                (
                    st.session_state.user_type,
                    st.session_state.monthly_income,
                    st.session_state.savings_goal,
                    st.session_state.current_savings,
                ) = existing
                st.session_state.logged_in = True
                st.success("✅ Profile loaded!")
            else:
                st.session_state.logged_in = True
                st.info("👋 New user — fill in your profile!")
        else:
            st.warning("Enter a username to continue.")

    if not st.session_state.logged_in:
        st.markdown(
            "<small style='color:#94A3B8'>Enter a username and click Login to begin.</small>",
            unsafe_allow_html=True,
        )
        st.stop()

    st.markdown(
        f"<small style='color:#93C5FD'>Logged in as <b style='color:white'>"
        f"{st.session_state.username}</b></small>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Quick Expense Logger ─────────────────────────────────
    st.markdown("### ➕ Log Expense")
    exp_category = st.selectbox(
        "Category",
        ["Food", "Transportation", "School", "Shopping",
         "Entertainment", "Bills", "Savings", "Health", "Other"],
    )
    exp_amount = st.number_input("Amount (₱)", min_value=0.01, step=10.0, format="%.2f")
    exp_date   = st.date_input("Date", value=date.today())

    if st.button("➕ Add Expense", use_container_width=True):
        if exp_amount > 0:
            add_expense(st.session_state.username, exp_category, exp_amount, str(exp_date))
            st.success(f"✅ {pesos(exp_amount)} logged!")
            st.rerun()
        else:
            st.warning("Amount must be greater than 0.")

    st.markdown("---")

    # ── Active Goal widget ───────────────────────────────────
    uname_sb = st.session_state.username
    active_goal_sb = get_active_goal(uname_sb)
    if active_goal_sb:
        st.markdown("### 🎯 Active Goal")
        st.markdown(
            f"<span style='color:white;font-weight:600'>{active_goal_sb['goal_name']}</span>",
            unsafe_allow_html=True,
        )
        prog = min(1.0,
            st.session_state.current_savings / active_goal_sb["target_amount"]
            if active_goal_sb["target_amount"] > 0 else 0)
        st.progress(prog)
        st.markdown(
            f"<small style='color:#93C5FD'>"
            f"{pesos(st.session_state.current_savings)} / {pesos(active_goal_sb['target_amount'])} "
            f"({prog*100:.0f}%)</small>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<small style='color:#94A3B8'>🗓 Deadline: {active_goal_sb['deadline']}</small>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<small style='color:#94A3B8'>No active goal. Set one in the Goals tab.</small>",
            unsafe_allow_html=True,
        )



# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════════════════════
uname = st.session_state.username

# ── Getting Started Modal ──
if st.session_state.logged_in and st.session_state.show_getting_started_modal:
    st.warning("👋 **Welcome!** Check out the **🎓 Getting Started** tab to learn about all features.")
    col_modal_1, col_modal_2 = st.columns([3, 1])
    with col_modal_2:
        if st.button("✕ Dismiss", use_container_width=True):
            st.session_state.show_getting_started_modal = False
            st.rerun()
    st.markdown("---")

(tab_getting_started, tab_dashboard, tab_profile, tab_goals, tab_expenses,
 tab_forecast, tab_chat, tab_file, tab_report) = st.tabs([
    "🎓 Getting Started", "📊 Dashboard", "👤 Profile", "🎯 Goals", "💸 Expenses",
    "🔮 Forecast",  "💬 AI Chat", "📁 File Analysis", "📄 Report",
])


# ─── TAB 0 · GETTING STARTED ──────────────────────────────────────────────────
with tab_getting_started:
    st.markdown(get_getting_started_content())


# ─── TAB 1 · DASHBOARD ────────────────────────────────────────────────────────
with tab_dashboard:
    st.markdown("## 📊 Financial Dashboard")

    income    = st.session_state.monthly_income
    savings   = st.session_state.current_savings
    goal_amt  = st.session_state.savings_goal
    spending  = get_total_spending(uname)
    remaining = income - spending
    active_goal = get_active_goal(uname)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monthly Income",  pesos(income))
    c2.metric("Total Spending",  pesos(spending),
              f"{spending/income*100:.0f}% of income" if income > 0 else None)
    c3.metric("Remaining",       pesos(remaining))
    c4.metric("Current Savings", pesos(savings),
              f"{savings/goal_amt*100:.0f}% of goal" if goal_amt > 0 else None)

    st.markdown("---")

    # Health score
    score, level = calculate_financial_health_score(income, spending, savings)
    col_score, col_gauge = st.columns([1, 2])

    with col_score:
        st.markdown("#### 💡 Financial Health")
        st.markdown(
            f'<div style="margin:12px 0">'
            f'<span class="score-badge">{score}/100</span>'
            f'</div>'
            f'<p style="font-size:1.1rem;font-weight:600;color:#1E293B;margin:4px 0">'
            f'{level}</p>'
            f'<p style="font-size:0.8rem;color:#64748B">'
            f'Based on your spending ratio and savings cushion.</p>',
            unsafe_allow_html=True,
        )

    with col_gauge:
        color = "#22C55E" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"suffix": "/100", "font": {"color": "#1E293B", "size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#CBD5E0"},
                "bar":  {"color": color, "thickness": 0.28},
                "bgcolor": "#F1F5F9",
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0,  40], "color": "#FEE2E2"},
                    {"range": [40, 60], "color": "#FEF9C3"},
                    {"range": [60, 80], "color": "#DCFCE7"},
                    {"range": [80,100], "color": "#DBEAFE"},
                ],
            },
        ))
        fig_gauge.update_layout(
            height=220, paper_bgcolor="rgba(15,23,42,0.9)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=10, l=20, r=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # Alerts & Recommendations
    expenses = get_expenses(uname)
    alerts   = generate_spending_alerts(income, spending, expenses)
    recs     = generate_recommendations(income, spending, goal_amt, savings, expenses, active_goal)

    col_a, col_r = st.columns(2)
    with col_a:
        section("🚨 Spending Alerts")
        if alerts:
            for a in alerts:
                st.warning(a)
        else:
            st.success("✅ No issues detected — great job!")
    with col_r:
        section("💡 Recommendations")
        for r in recs:
            st.info(r)

    st.markdown("---")

    # Spending charts
    section("📈 Spending Breakdown")
    if expenses:
        df_exp = pd.DataFrame(expenses, columns=["Category", "Amount", "Date"])
        col_pie, col_bar = st.columns(2)
        with col_pie:
            fig_pie = px.pie(
                df_exp, names="Category", values="Amount", hole=0.42,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_pie.update_traces(textfont_size=12, pull=[0.03]*len(df_exp))
            fig_pie.update_layout(
                margin=dict(t=30, b=10, l=10, r=10), height=300,
                paper_bgcolor="rgba(15,23,42,0.9)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            df_cat = df_exp.groupby("Category", as_index=False)["Amount"].sum()
            df_cat = df_cat.sort_values("Amount", ascending=True)
            fig_bar = px.bar(
                df_cat, x="Amount", y="Category", orientation="h",
                color="Amount", color_continuous_scale=["#BFDBFE", "#1D4ED8"],
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=10, l=10, r=10), height=300,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(15,23,42,0.9)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="#334155"),
                xaxis=dict(gridcolor="#334155"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Log some expenses to see your spending breakdown.")


# ─── TAB 2 · PROFILE ──────────────────────────────────────────────────────────
with tab_profile:
    st.markdown("## 👤 User Profile")
    st.caption("Your profile is saved and automatically loaded on future logins.")

    with st.form("profile_form"):
        user_type_opts = ["Student", "Working Individual", "Freelancer", "Business Owner"]
        user_type = st.selectbox(
            "I am a…", user_type_opts,
            index=user_type_opts.index(st.session_state.user_type)
                  if st.session_state.user_type in user_type_opts else 0,
        )
        monthly_income = st.number_input(
            "Monthly Income / Allowance (₱)",
            min_value=0.0, value=float(st.session_state.monthly_income),
            step=500.0, format="%.2f",
        )
        savings_goal = st.number_input(
            "Overall Savings Target (₱)",
            min_value=0.0, value=float(st.session_state.savings_goal),
            step=1000.0, format="%.2f",
        )
        current_savings = st.number_input(
            "Current Savings (₱)",
            min_value=0.0, value=float(st.session_state.current_savings),
            step=500.0, format="%.2f",
        )
        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if submitted:
        save_user(uname, user_type, monthly_income, savings_goal, current_savings)
        st.session_state.user_type       = user_type
        st.session_state.monthly_income  = monthly_income
        st.session_state.savings_goal    = savings_goal
        st.session_state.current_savings = current_savings
        st.success("✅ Profile saved!")
        st.rerun()

    # ── Clean profile summary (no JSON / no code block) ──────
    if st.session_state.monthly_income > 0:
        st.markdown("---")
        rows = [
            ("👤 Username",        uname),
            ("🏷️ User Type",       st.session_state.user_type),
            ("💵 Monthly Income",  pesos(st.session_state.monthly_income)),
            ("🎯 Savings Target",  pesos(st.session_state.savings_goal)),
            ("🏦 Current Savings", pesos(st.session_state.current_savings)),
            ("📊 Remaining",       pesos(st.session_state.monthly_income
                                        - get_total_spending(uname))),
        ]
        rows_html = "".join(
            f'<div class="profile-row">'
            f'<span class="profile-label">{label}</span>'
            f'<span class="profile-value">{value}</span>'
            f'</div>'
            for label, value in rows
        )
        st.markdown(
            f'<div class="profile-card">'
            f'<h4>Your Current Profile</h4>'
            f'{rows_html}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─── TAB 3 · GOALS ────────────────────────────────────────────────────────────
with tab_goals:
    st.markdown("## 🎯 Goal Planner")
    st.caption(
        "Describe your goal in plain language — "
        "the AI will extract the amount and deadline automatically."
    )

    goal_text = st.text_area(
        "Describe your goal",
        placeholder="e.g. I want to save ₱50,000 for a laptop in 6 months",
        height=80,
    )
    if st.button("✨ Add Goal"):
        if goal_text.strip():
            parsed = extract_goal_from_text(goal_text, st.session_state.monthly_income)
            save_goal(uname, parsed["goal_name"], parsed["target_amount"], parsed["deadline"])
            st.success(
                f"✅ Goal added: **{parsed['goal_name']}** — "
                f"{pesos(parsed['target_amount'])} by {parsed['deadline']}"
            )
            st.rerun()
        else:
            st.warning("Please describe your goal first.")

    st.markdown("---")
    section("Your Goals")

    all_goals  = get_goals(uname)
    active_goal = get_active_goal(uname)

    if all_goals:
        for goal_id, goal_name, target_amount, deadline, is_active in all_goals:
            badge = "🟢 Active" if is_active else "⚪ Inactive"
            progress = min(1.0,
                st.session_state.current_savings / target_amount
                if target_amount > 0 else 0)

            with st.container():
                g1, g2, g3, g4 = st.columns([4, 2, 1, 1])
                with g1:
                    st.markdown(f"**{goal_name}** &nbsp; {badge}")
                    st.caption(f"{pesos(target_amount)} · Deadline: {deadline}")
                    st.progress(progress, text=f"{progress*100:.0f}% of goal saved")
                with g2:
                    if not is_active:
                        if st.button("⭐ Set Active", key=f"active_{goal_id}"):
                            set_active_goal(uname, goal_id)
                            st.rerun()
                with g3:
                    if st.button("✏️", key=f"edit_{goal_id}", help="Edit goal"):
                        st.session_state[f"edit_mode_{goal_id}"] = True
                with g4:
                    if st.button("🗑️", key=f"del_{goal_id}", help="Delete goal"):
                        delete_goal(goal_id)
                        st.rerun()

                if st.session_state.get(f"edit_mode_{goal_id}"):
                    with st.form(f"edit_form_{goal_id}"):
                        new_name   = st.text_input("Goal Name", value=goal_name)
                        new_amount = st.number_input("Target Amount (₱)", value=float(target_amount), step=500.0)
                        new_dl     = st.text_input("Deadline (YYYY-MM-DD)", value=str(deadline))
                        col_s, col_c = st.columns(2)
                        if col_s.form_submit_button("💾 Save"):
                            update_goal(goal_id, new_name, new_amount, new_dl)
                            st.session_state[f"edit_mode_{goal_id}"] = False
                            st.rerun()
                        if col_c.form_submit_button("✖ Cancel"):
                            st.session_state[f"edit_mode_{goal_id}"] = False
                            st.rerun()

                st.markdown("---")
    else:
        st.info("No goals yet. Describe one above and click **Add Goal**!")


# ─── TAB 4 · EXPENSES ─────────────────────────────────────────────────────────
with tab_expenses:
    st.markdown("## 💸 Expense Tracker")

    expenses_with_id = get_expenses_with_id(uname)
    if expenses_with_id:
        df_all = pd.DataFrame(expenses_with_id, columns=["ID", "Category", "Amount", "Date"])
        total  = df_all["Amount"].sum()

        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Total Transactions", len(df_all))
        col_s2.metric("Total Spent",        pesos(total))

        st.markdown("---")

        # Category filter
        cat_filter = st.multiselect(
            "Filter by category", options=sorted(df_all["Category"].unique()), default=[]
        )
        df_show = df_all if not cat_filter else df_all[df_all["Category"].isin(cat_filter)]

        # Table header
        hc1, hc2, hc3, hc4 = st.columns([2, 3, 2, 1])
        hc1.markdown("**Date**")
        hc2.markdown("**Category**")
        hc3.markdown("**Amount**")
        hc4.markdown("")
        st.markdown("<hr style='margin:4px 0 8px 0;border-color:#E2E8F0'>", unsafe_allow_html=True)

        for _, row in df_show.iterrows():
            c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
            c1.markdown(f"<span style='color:#64748B;font-size:0.88rem'>{row['Date']}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='font-weight:600;color:#334155'>{row['Category']}</span>",
                        unsafe_allow_html=True)
            c3.markdown(f"<span style='font-weight:700;color:#1D4ED8'>{pesos(row['Amount'])}</span>",
                        unsafe_allow_html=True)
            if c4.button("🗑️", key=f"delexp_{row['ID']}", help="Delete this expense"):
                delete_expense(int(row["ID"]))
                st.rerun()

        st.markdown("---")

        # Daily trend
        section("📅 Daily Spending Trend")
        df_trend = df_all.copy()
        df_trend["Date"] = pd.to_datetime(df_trend["Date"], errors="coerce")
        df_trend = df_trend.dropna(subset=["Date"])
        if not df_trend.empty:
            df_daily = df_trend.groupby("Date")["Amount"].sum().reset_index()
            fig_trend = px.area(
                df_daily, x="Date", y="Amount",
                color_discrete_sequence=["#3B82F6"],
            )
            fig_trend.update_traces(fill="tozeroy", fillcolor="rgba(59,130,246,0.12)")
            fig_trend.update_layout(
                height=260, margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(15,23,42,0.9)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="#334155", showline=False),
                yaxis=dict(gridcolor="#334155"),
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No expenses logged yet. Add one from the sidebar!")


# ─── TAB 5 · FORECAST ─────────────────────────────────────────────────────────
with tab_forecast:
    st.markdown("## 🔮 Savings Forecast")

    income   = st.session_state.monthly_income
    spending = get_total_spending(uname)
    savings  = st.session_state.current_savings
    goal_amt = st.session_state.savings_goal

    forecast_df, monthly_savings, est_months = generate_forecast(
        income, spending, savings, goal_amt
    )

    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Monthly Net Savings", pesos(monthly_savings))
    cf2.metric("Months to Goal",
               f"{est_months:.1f}" if est_months is not None else "N/A")
    cf3.metric("Goal Amount", pesos(goal_amt))

    fig_fc = px.line(
        forecast_df, x="Month", y="Projected Savings",
        markers=True, color_discrete_sequence=["#3B82F6"],
    )
    fig_fc.update_traces(
        line=dict(width=2.5),
        marker=dict(size=7, color="#1D4ED8"),
    )
    if goal_amt > 0:
        fig_fc.add_hline(
            y=goal_amt, line_dash="dash", line_color="#EF4444", line_width=1.5,
            annotation_text=f"🎯 Goal: {pesos(goal_amt)}",
            annotation_font_color="#EF4444",
        )
    fig_fc.update_layout(
        height=340, margin=dict(t=30, b=20, l=20, r=20),
        paper_bgcolor="rgba(15,23,42,0.9)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155"),
    )
    st.plotly_chart(fig_fc, use_container_width=True)

    if st.button("🤖 Get AI Forecast Advice"):
        with st.spinner("Generating forecast advice…"):
            advice = generate_forecast_advice(monthly_savings, est_months)
        section("AI Forecast Analysis")
        st.info(advice)


# ─── TAB 6 · AI CHAT ──────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("## 💬 AI Financial Assistant")
    st.caption("Chat with your AI coach. It remembers your recent conversation and knows your finances.")

    if not st.session_state.chat_messages:
        db_hist = get_chat_history(uname)
        st.session_state.chat_messages = [
            {"role": r, "content": m} for r, m in db_hist
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything about your finances…")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        spending_now = get_total_spending(uname)
        active_goal  = get_active_goal(uname)
        context = (
            f"Monthly Income: {pesos(st.session_state.monthly_income)}\n"
            f"Current Savings: {pesos(st.session_state.current_savings)}\n"
            f"Total Spending: {pesos(spending_now)}\n"
            f"Savings Goal: {pesos(st.session_state.savings_goal)}\n"
            f"Active Goal: {active_goal['goal_name'] if active_goal else 'None'}"
        )
        history = get_chat_history(uname)

        with st.spinner("Thinking…"):
            reply = financial_chatbot_with_memory(uname, prompt, history, context)

        save_chat_message(uname, "user", prompt)
        save_chat_message(uname, "assistant", reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("🗑️ Clear Chat History"):
        clear_chat_history(uname)
        st.session_state.chat_messages = []
        st.rerun()


# ─── TAB 7 · FILE ANALYSIS ────────────────────────────────────────────────────
with tab_file:
    st.markdown("## 📁 Upload Financial Tracker")
    st.caption("Upload a CSV, Excel, PDF, Word, or TXT file for AI analysis.")

    uploaded = st.file_uploader(
        "Choose a file", type=["csv", "xlsx", "xls", "txt", "pdf", "docx"]
    )
    if uploaded:
        st.success(f"✅ **{uploaded.name}** uploaded")
        if st.button("🔍 Analyze File"):
            with st.spinner("Analyzing your file…"):
                content  = process_uploaded_file(uploaded)
                analysis = analyze_uploaded_financial_file(content)
            section("🤖 AI Analysis")
            st.info(analysis)
            with st.expander("📄 Raw extracted text (first 2000 chars)"):
                st.text(content[:2000])


# ─── TAB 8 · REPORT ───────────────────────────────────────────────────────────
with tab_report:
    st.markdown("## 📄 Download Financial Report")
    st.caption("Generate a full PDF report with your financial summary, AI analysis, alerts, and recommendations.")

    if st.button("🖨️ Generate PDF Report"):
        income_r   = st.session_state.monthly_income
        savings_r  = st.session_state.current_savings
        goal_r     = st.session_state.savings_goal
        spending_r = get_total_spending(uname)
        expenses_r = get_expenses(uname)
        active_r   = get_active_goal(uname)

        score_r, level_r = calculate_financial_health_score(income_r, spending_r, savings_r)
        alerts_r = generate_spending_alerts(income_r, spending_r, expenses_r)
        recs_r   = generate_recommendations(income_r, spending_r, goal_r, savings_r, expenses_r, active_r)

        with st.spinner("Generating AI analysis…"):
            advice_r = generate_financial_advice(
                uname, st.session_state.user_type,
                income_r, goal_r, savings_r, spending_r, expenses_r, active_r,
            )

        with st.spinner("Building PDF…"):
            pdf_path = generate_financial_report(
                username        = uname,
                advice          = advice_r,
                score           = score_r,
                level           = level_r,
                recommendations = recs_r,
                alerts          = alerts_r,
                monthly_income  = income_r,
                total_spending  = spending_r,
                current_savings = savings_r,
                savings_goal    = goal_r,
                goal_name       = active_r["goal_name"]     if active_r else None,
                target_amount   = active_r["target_amount"] if active_r else None,
                deadline        = active_r["deadline"]      if active_r else None,
            )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label               = "⬇️ Download PDF Report",
                data                = f,
                file_name           = f"{uname}_financial_report.pdf",
                mime                = "application/pdf",
                use_container_width = True,
            )
        st.success("✅ Report ready!")