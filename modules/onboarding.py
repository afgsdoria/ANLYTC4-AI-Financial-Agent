"""
onboarding.py
Getting Started guide content for new and returning users
"""


def get_getting_started_content() -> str:
    return """
# 🚀 Getting Started with Your AI Finance Coach

Welcome to your **Financial AI Agent**! This guide will help you get the most out of every feature.

## 📊 **Dashboard** — Your Financial Snapshot
Your dashboard is the heartbeat of the app. Here you'll see key metrics, a financial health score,
AI-generated spending breakdowns, and risk flags — all generated autonomously by the reasoning engine.

## 💸 **Expense Tracker** — Know Where Your Money Goes
Log every expense to understand your spending patterns. Note: future dates are not allowed.

## 🔮 **Savings Forecast** — Project Your Future
See where you'll be financially in the coming months with an AI-generated forecast.

## 💬 **AI Chat** — Ask Questions Anytime
Chat with your personal AI finance coach. Ask about banks, investments, loans, or any financial topic!

## 📄 **Report** — Download Your Financial Summary
Generate a comprehensive PDF report on your chosen schedule: daily, weekly, monthly, or a custom date.

## ⚙️ **Settings** — Manage Profile, Goals & Schedule
Update your profile, manage multiple active goals, and configure your report schedule here.
"""


if __name__ == "__main__":
    print(get_getting_started_content())