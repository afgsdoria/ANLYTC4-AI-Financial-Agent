import sqlite3

DB_NAME = "data/financialAIAgent.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


# =========================
# CREATE TABLES
# =========================

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        user_type TEXT,
        monthly_income REAL,
        savings_goal REAL,
        current_savings REAL
    )
    """)

    # =========================
    # EXPENSES TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    """)

    # =========================
    # GOALS TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal_name TEXT,
        target_amount REAL,
        deadline TEXT,
        is_active INTEGER DEFAULT 0
    )
    """)

    # =========================
    # MIGRATION:
    # ADD is_active COLUMN
    # IF MISSING
    # =========================

    cursor.execute("""
    PRAGMA table_info(goals)
    """)

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "is_active" not in columns:

        cursor.execute("""
        ALTER TABLE goals
        ADD COLUMN is_active
        INTEGER DEFAULT 0
        """)

    conn.commit()
    conn.close()

    conn = connect_db()
    cursor = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        user_type TEXT,
        monthly_income REAL,
        savings_goal REAL,
        current_savings REAL
    )
    """)

    # =========================
    # EXPENSES TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    """)

    # =========================
    # GOALS TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal_name TEXT,
        target_amount REAL,
        deadline TEXT,
        is_active INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# =========================
# USER FUNCTIONS
# =========================

def save_user(
    username,
    user_type,
    monthly_income,
    savings_goal,
    current_savings
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users (
        username,
        user_type,
        monthly_income,
        savings_goal,
        current_savings
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        user_type,
        monthly_income,
        savings_goal,
        current_savings
    ))

    conn.commit()
    conn.close()


def get_user(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_type,
        monthly_income,
        savings_goal,
        current_savings
    FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    conn.close()

    return user


# =========================
# GOAL FUNCTIONS
# =========================

def save_goal(
    username,
    goal_name,
    target_amount,
    deadline
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO goals (
        username,
        goal_name,
        target_amount,
        deadline,
        is_active
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        goal_name,
        target_amount,
        deadline,
        0
    ))

    conn.commit()
    conn.close()


def get_goals(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        goal_name,
        target_amount,
        deadline,
        is_active
    FROM goals
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    goals = cursor.fetchall()

    conn.close()

    return goals


def get_active_goal(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        goal_name,
        target_amount,
        deadline
    FROM goals
    WHERE username = ?
    AND is_active = 1
    LIMIT 1
    """, (username,))

    goal = cursor.fetchone()

    conn.close()

    return goal


def update_goal(
    goal_id,
    goal_name,
    target_amount,
    deadline
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE goals
    SET
        goal_name = ?,
        target_amount = ?,
        deadline = ?
    WHERE id = ?
    """, (
        goal_name,
        target_amount,
        deadline,
        goal_id
    ))

    conn.commit()
    conn.close()


def delete_goal(goal_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM goals
    WHERE id = ?
    """, (goal_id,))

    conn.commit()
    conn.close()


def set_active_goal(
    username,
    goal_id
):

    conn = connect_db()
    cursor = conn.cursor()

    # Remove previous active goal

    cursor.execute("""
    UPDATE goals
    SET is_active = 0
    WHERE username = ?
    """, (username,))

    # Set new active goal

    cursor.execute("""
    UPDATE goals
    SET is_active = 1
    WHERE id = ?
    """, (goal_id,))

    conn.commit()
    conn.close()


# =========================
# EXPENSE FUNCTIONS
# =========================

def add_expense(
    username,
    category,
    amount,
    date
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (
        username,
        category,
        amount,
        date
    )
    VALUES (?, ?, ?, ?)
    """, (
        username,
        category,
        amount,
        date
    ))

    conn.commit()
    conn.close()


def get_expenses(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        category,
        amount,
        date
    FROM expenses
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    expenses = cursor.fetchall()

    conn.close()

    return expenses


def get_total_spending(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE username = ?
    """, (username,))

    total = cursor.fetchone()[0]

    conn.close()

    return total if total else 0