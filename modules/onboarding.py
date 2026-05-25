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
A PDF report is generated automatically whenever you update your data, so your latest financial snapshot is always available.

## ⚙️ **Settings** — Manage Profile & Goals
Update your profile and manage multiple active goals in one place.
"""


if __name__ == "__main__":
    print(get_getting_started_content())