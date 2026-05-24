import streamlit as st
from modules.database import create_tables, save_user

create_tables()

st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Financial AI Agent")
st.subheader("AI Financial Planning Agent")

st.divider()

st.header("User Setup")

username = st.text_input("Enter Username")

monthly_income = st.number_input(
    "Monthly Allowance / Income",
    min_value=0.0
)

savings_goal = st.number_input(
    "Savings Goal",
    min_value=0.0
)

current_savings = st.number_input(
    "Current Savings",
    min_value=0.0
)

if st.button("Save Profile"):

    save_user(
        username,
        monthly_income,
        savings_goal,
        current_savings
    )

    st.success("Profile saved successfully!")