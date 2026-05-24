import sqlite3

DB_NAME = "data/financialAIAgent.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        monthly_income REAL,
        savings_goal REAL,
        current_savings REAL
    )
    """)

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    """)

def save_user(username, monthly_income, savings_goal, current_savings):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users
    (username, monthly_income, savings_goal, current_savings)
    VALUES (?, ?, ?, ?)
    """, (
        username,
        monthly_income,
        savings_goal,
        current_savings
    ))    

    conn.commit()
    conn.close()