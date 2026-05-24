import streamlit as st
import pandas as pd
import plotly.express as px

from modules.database import (
    create_tables,
    save_user,
    get_user,
    save_goal,
    get_goals,
    update_goal,
    delete_goal,
    set_active_goal,
    get_active_goal,
    add_expense,
    get_expenses,
    get_total_spending
)

from modules.ai_engine import (
    generate_financial_advice,
    analyze_uploaded_financial_file,
    generate_forecast_advice,
    financial_chatbot_with_memory
)

from modules.file_processor import (
    process_uploaded_file
)

from modules.forecasting import (
    generate_forecast
)

from modules.scoring import (
    calculate_financial_health_score
)

from modules.memory import (
    create_chat_table,
    save_chat_message,
    get_chat_history
)

from modules.goal_engine import (
    extract_goal_from_text
)

from modules.alerts import (
    generate_spending_alerts
)

from modules.recommendations import (
    generate_recommendations
)

from modules.reports import (
    generate_financial_report
)

# =========================
# DATABASE
# =========================

create_tables()
create_chat_table()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Financial AI Agent")
st.subheader(
    "AI Financial Planning Agent for Filipinos"
)

st.divider()

# =========================
# LOGIN
# =========================

st.header("👤 User Login")

username = st.text_input(
    "Enter Username"
)

loaded_user = None

if username:
    loaded_user = get_user(username)

# Default values
user_type = "Student"
monthly_income = 0.0
savings_goal = 0.0
current_savings = 0.0

# Load existing user
if loaded_user:

    user_type = loaded_user[0]
    monthly_income = loaded_user[1]
    savings_goal = loaded_user[2]
    current_savings = loaded_user[3]

    st.success(
        "✅ Existing profile loaded!"
    )

# =========================
# USER PROFILE
# =========================

st.header("📝 User Profile")

user_type = st.selectbox(
    "User Type",
    [
        "Student",
        "Working Individual"
    ],
    index=0 if user_type == "Student" else 1
)

monthly_income = st.number_input(
    "Monthly Income / Allowance",
    min_value=0.0,
    value=float(monthly_income)
)

savings_goal = st.number_input(
    "Savings Goal",
    min_value=0.0,
    value=float(savings_goal)
)

current_savings = st.number_input(
    "Current Savings",
    min_value=0.0,
    value=float(current_savings)
)

if st.button("Save Profile"):

    save_user(
        username,
        user_type,
        monthly_income,
        savings_goal,
        current_savings
    )

    st.success("✅ Profile saved!")

st.divider()

# =========================
# SMART GOAL PLANNER
# =========================

st.subheader("🎯 Goal Planner")

goal_input = st.text_area(
    "Add a financial goal"
)

if st.button("Add Goal"):

    goal_data = extract_goal_from_text(
        goal_input,
        monthly_income
    )

    save_goal(
        username,
        goal_data["goal_name"],
        goal_data["target_amount"],
        goal_data["deadline"]
    )

    st.success("Goal added!")

# =========================
# OPTIONAL FILE UPLOAD
# =========================

st.header(
    "📂 Optional Financial Tracker Upload"
)

uploaded_file = st.file_uploader(
    "Upload previous expense tracker",
    type=[
        "csv",
        "xlsx",
        "txt",
        "pdf",
        "docx"
    ]
)

if uploaded_file is not None:

    st.success("Tracker uploaded!")

    file_content = process_uploaded_file(
        uploaded_file
    )

    if st.button(
        "Analyze Uploaded Tracker"
    ):

        with st.spinner(
            "Analyzing financial tracker..."
        ):

            analysis = (
                analyze_uploaded_financial_file(
                    file_content
                )
            )

        st.write(analysis)

st.divider()

# =========================
# LOAD ACTIVE GOAL
# =========================

saved_goal = None

if username:

    saved_goal = get_active_goal(
        username
    )

# =========================
# SIDEBAR
# =========================

st.sidebar.header(
    "💸 Expense Logger"
)

expense_category = (
    st.sidebar.selectbox(
        "Category",
        [
            "Food",
            "Transportation",
            "School",
            "Shopping",
            "Entertainment",
            "Bills",
            "Savings",
            "Other"
        ]
    )
)

expense_amount = (
    st.sidebar.number_input(
        "Expense Amount",
        min_value=0.0
    )
)

expense_date = (
    st.sidebar.date_input(
        "Expense Date"
    )
)

if st.sidebar.button(
    "Add Expense"
):

    add_expense(
        username,
        expense_category,
        expense_amount,
        str(expense_date)
    )

    st.sidebar.success(
        "Expense added!"
    )

st.sidebar.divider()

st.sidebar.header(
    "🎯 Goal Tracker"
)

if saved_goal:

    st.sidebar.success(
        f"""
Goal:
{saved_goal["goal_name"]}

Target:
₱{saved_goal["target_amount"]:,.2f}

Deadline:
{saved_goal["deadline"]}
"""
    )

else:

    st.sidebar.info(
        "No active goal."
    )

# =========================
# LOAD EXPENSES
# =========================

expenses = []

if username:
    expenses = get_expenses(
        username
    )

total_spending = (
    get_total_spending(
        username
    )
)

# =========================
# DASHBOARD
# =========================

st.header("📊 Dashboard")

remaining_balance = (
    monthly_income
    - total_spending
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "Income",
    f"₱{monthly_income:,.2f}"
)

col2.metric(
    "Goal",
    f"₱{savings_goal:,.2f}"
)

col3.metric(
    "Spending",
    f"₱{total_spending:,.2f}"
)

col4.metric(
    "Balance",
    f"₱{remaining_balance:,.2f}"
)

st.divider()

# =========================
# FINANCIAL HEALTH
# =========================

score, level = (
    calculate_financial_health_score(
        monthly_income,
        total_spending,
        current_savings
    )
)

st.header(
    "💡 Financial Health Score"
)

st.metric(
    "Health Score",
    f"{score}/100"
)

st.success(level)

st.divider()

# =========================
# ALERTS
# =========================

st.header(
    "🚨 Spending Alerts"
)

alerts = (
    generate_spending_alerts(
        monthly_income,
        total_spending,
        expenses
    )
)

if alerts:

    for alert in alerts:
        st.warning(alert)

else:
    st.success(
        "No financial risks detected."
    )

st.divider()

# =========================
# RECOMMENDATIONS
# =========================

st.header(
    "💡 Recommendations"
)

recommendations = (
    generate_recommendations(
        monthly_income,
        total_spending,
        savings_goal
    )
)

for recommendation in (
    recommendations
):
    st.info(recommendation)

st.divider()

# =========================
# VISUALIZATION
# =========================

st.header(
    "📈 Spending Visualization"
)

if expenses:

    df = pd.DataFrame(
        expenses,
        columns=[
            "Category",
            "Amount",
            "Date"
        ]
    )

    chart = px.pie(
        df,
        names="Category",
        values="Amount"
    )

    st.plotly_chart(
        chart,
        width="stretch"
    )

st.divider()

# =========================
# FORECAST
# =========================

st.header(
    "🔮 Financial Forecast"
)

(
    forecast_df,
    monthly_savings,
    estimated_months
) = generate_forecast(
    monthly_income,
    total_spending,
    current_savings,
    savings_goal
)

forecast_chart = px.line(
    forecast_df,
    x="Month",
    y="Projected Savings",
    markers=True
)

st.plotly_chart(
    forecast_chart,
    width="stretch"
)

if st.button(
    "Generate Forecast Advice"
):

    st.write(
        generate_forecast_advice(
            monthly_savings,
            estimated_months
        )
    )

st.divider()

# =========================
# AI FINANCIAL ASSISTANT
# =========================

st.header(
    "💬 AI Financial Assistant"
)

if "messages" not in (
    st.session_state
):
    st.session_state.messages = []

for message in (
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

prompt = st.chat_input(
    "Ask anything about finances..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    history = get_chat_history(
        username
    )

    active_goal = get_active_goal(
        username
    )

    context = f"""
    Income:
    ₱{monthly_income}

    Savings:
    ₱{current_savings}

    Total Spending:
    ₱{total_spending}

    Savings Goal:
    ₱{savings_goal}

    Active Goal:
    {active_goal}
    """

    response = (
        financial_chatbot_with_memory(
            username,
            prompt,
            history,
            context
        )
    )

    save_chat_message(
        username,
        "user",
        prompt
    )

    save_chat_message(
        username,
        "assistant",
        response
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    st.rerun()

st.divider()

# =========================
# REPORT DOWNLOAD
# =========================

st.header(
    "📄 Download Financial Report"
)

if st.button(
    "Generate Financial Report"
):

    advice = (
        generate_financial_advice(
            username,
            user_type,
            monthly_income,
            savings_goal,
            current_savings,
            total_spending,
            expenses
        )
    )

    pdf_file = (
        generate_financial_report(
            username,
            advice,
            score,
            level,
            recommendations,
            alerts
        )
    )

    with open(
        pdf_file,
        "rb"
    ) as file:

        st.download_button(
            label=(
                "Download PDF Report"
            ),
            data=file,
            file_name=pdf_file,
            mime="application/pdf"
        )
