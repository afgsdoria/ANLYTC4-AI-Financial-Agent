"""
onboarding.py
Getting Started guide content for new and returning users
"""


def get_getting_started_content() -> str:
    """Return formatted Getting Started guide for all 8 features"""
    return """
# 🚀 Getting Started with Your AI Finance Coach

Welcome to your **Financial AI Agent**! This guide will help you get the most out of every feature.

---

## 📊 **Dashboard** — Your Financial Snapshot
Your dashboard is the heartbeat of the app. Here you'll see:
- **Key Metrics**: Monthly income, total spending, remaining balance, and current savings
- **Financial Health Score**: A 0-100 rating based on your spending habits and savings cushion
- **Spending Breakdown**: Visual pie and bar charts showing where your money goes
- **Alerts & Recommendations**: AI-powered warnings about overspending and suggestions to improve

**Quick Tip**: Check the dashboard daily to stay aware of your financial status!

---

## 👤 **Profile** — Your Personal Details
Set up and manage your financial profile here:
- **User Type**: Choose from Student, Working Individual, Freelancer, or Business Owner
- **Monthly Income**: Your monthly earnings or allowance
- **Savings Goal**: Your total savings target (e.g., ₱100,000)
- **Current Savings**: How much you've saved so far

Your profile is automatically saved and loaded every time you log in.

**Quick Tip**: Update your income and savings if your financial situation changes!

---

## 🎯 **Goals** — Plan Your Future
Set specific, time-bound financial goals and track progress:
1. **Describe your goal** in plain language (e.g., "Save ₱50,000 for a laptop in 6 months")
2. **AI extracts the details** — amount and deadline
3. **Track progress** with visual progress bars
4. **Set one as active** to see it in the sidebar and get recommendations

**Quick Tip**: Goals give you direction and motivation. Set at least one!

---

## 💸 **Expense Tracker** — Know Where Your Money Goes
Log every expense to understand your spending patterns:
- **Quick Logging**: Use the sidebar form to add expenses instantly
- **Categories**: Food, Transportation, School, Shopping, Entertainment, Bills, Savings, Health, Other
- **View & Manage**: See all transactions with category filters and delete options
- **Daily Trends**: Visual area chart showing your spending over time

**Quick Tip**: The more expenses you log, the better the AI can help you!

---

## 🔮 **Savings Forecast** — Project Your Future
See where you'll be financially in the coming months:
- **Monthly Net Savings**: How much you save each month (income minus spending)
- **Months to Goal**: Estimated time to reach your savings target
- **Forecast Chart**: Visual projection of your savings growth
- **AI Forecast Advice**: Click "Get AI Forecast Advice" for personalized insights

**Quick Tip**: Use this to adjust your savings strategy if you won't hit your goal on time!

---

## 💬 **AI Chat** — Ask Questions Anytime
Chat with your personal AI finance coach:
- The AI knows your **complete financial situation** (income, spending, goals)
- Ask about budgeting strategies, expense categories, savings tips
- **Chat memory**: The AI remembers recent conversations
- **Save history**: Your conversation is saved and available next time you log in

**Quick Tip**: The more you chat, the better the AI understands your situation!

---

## 📁 **File Analysis** — Upload Financial Documents
Upload and analyze financial documents:
- **Supported formats**: CSV, Excel (xlsx/xls), PDF, Word (docx), TXT
- **AI Analysis**: The AI reads and analyzes your financial documents
- **Quick insights**: Get a summary of key findings from your upload
- **See raw text**: View the first 2000 characters of extracted text

**Quick Tip**: Great for analyzing bank statements, invoices, or financial reports!

---

## 📄 **Report** — Download Your Financial Summary
Generate a comprehensive PDF report with everything:
- Your financial snapshot (income, spending, savings, goals)
- Health score and trend analysis
- AI-generated advice tailored to your profile
- Spending alerts and personalized recommendations
- Ready to download and share

**Quick Tip**: Generate a report monthly to track your progress!

---

## 🎓 Pro Tips for Success

1. **Log expenses consistently** — The more data, the better the AI recommendations
2. **Set realistic goals** — Adjust if your spending doesn't match your target
3. **Chat with the AI** — Don't be shy! Ask questions about anything financial
4. **Review weekly** — Check your dashboard and spending trends weekly
5. **Update your profile** — Keep income and savings info current
6. **Use forecasts** — Let the AI guide your savings strategy

---

## 💡 Need Help?

- **Questions?** Ask the AI Chat assistant — it knows your finances!
- **Confused about a feature?** Come back to this Getting Started guide
- **Want to re-explore?** You can always click the **Getting Started** tab

---

**Ready to take control of your finances?** Start with the **Profile** tab to set up your details,
then head to **Expenses** to log your first transaction. Happy saving! 💰
"""


if __name__ == "__main__":
    # For testing: print the content
    print(get_getting_started_content())
