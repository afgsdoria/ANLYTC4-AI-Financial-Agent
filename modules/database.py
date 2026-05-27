import sqlite3
import hashlib

DB_NAME = "data/financialAIAgent.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


# =========================
# PASSWORD HASHING
# =========================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against a stored hash."""
    return hash_password(password) == hashed


# =========================
# CREATE TABLES
# =========================

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        user_type TEXT,
        monthly_income REAL,
        savings_goal REAL,
        current_savings REAL,
        birthday TEXT,
        age INTEGER,
        report_schedule TEXT DEFAULT 'monthly',
        report_date TEXT,
        file_context TEXT,
        onboarding_done INTEGER DEFAULT 0
    )
    """)

    # EXPENSES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    """)

    # GOALS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal_name TEXT,
        target_amount REAL,
        deadline TEXT,
        is_active INTEGER DEFAULT 0,
        is_achieved INTEGER DEFAULT 0
    )
    """)

    # CHAT HISTORY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        message TEXT
    )
    """)

    # AI ANALYSIS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        health_summary TEXT,
        step_plan TEXT
    )
    """)

    # =========================
    # MIGRATIONS: safely add
    # missing columns if needed
    # =========================

    def _add_column_if_missing(cursor, table, column, col_type):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor.fetchall()]
        if column not in cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
            )

    _add_column_if_missing(cursor, "users", "password_hash",    "TEXT")
    _add_column_if_missing(cursor, "users", "birthday",         "TEXT")
    _add_column_if_missing(cursor, "users", "age",              "INTEGER")
    _add_column_if_missing(cursor, "users", "report_schedule",  "TEXT DEFAULT 'monthly'")
    _add_column_if_missing(cursor, "users", "report_date",      "TEXT")
    _add_column_if_missing(cursor, "users", "file_context",     "TEXT")
    _add_column_if_missing(cursor, "users", "onboarding_done",  "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "goals", "is_active",        "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "goals", "is_achieved",      "INTEGER DEFAULT 0")

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
    current_savings,
    birthday=None,
    age=None,
    report_schedule="monthly",
    report_date=None,
    file_context=None,
    onboarding_done=0,
    password_hash=None,
):
    conn = connect_db()
    cursor = conn.cursor()

    # If no new password_hash provided, keep the existing one
    if password_hash is None:
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        )
        row = cursor.fetchone()
        password_hash = row[0] if row else None

    cursor.execute("""
    INSERT OR REPLACE INTO users (
        username, password_hash, user_type, monthly_income, savings_goal,
        current_savings, birthday, age, report_schedule,
        report_date, file_context, onboarding_done
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username, password_hash, user_type, monthly_income, savings_goal,
        current_savings, birthday, age, report_schedule,
        report_date, file_context, onboarding_done,
    ))
    conn.commit()
    conn.close()


def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_type, monthly_income, savings_goal, current_savings,
           birthday, age, report_schedule, report_date, file_context,
           onboarding_done, password_hash
    FROM users WHERE username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    keys = [
        "user_type", "monthly_income", "savings_goal", "current_savings",
        "birthday", "age", "report_schedule", "report_date", "file_context",
        "onboarding_done", "password_hash",
    ]
    return dict(zip(keys, row))


def set_password(username: str, password: str):
    """Hash and store a new password for an existing user."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(password), username)
    )
    conn.commit()
    conn.close()


def set_onboarding_done(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET onboarding_done = 1 WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()


def set_file_context(username, file_context):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET file_context = ? WHERE username = ?",
        (file_context, username)
    )
    conn.commit()
    conn.close()


# =========================
# EXPENSE FUNCTIONS
# =========================

def add_expense(username, category, amount, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO expenses (username, category, amount, date)
    VALUES (?, ?, ?, ?)
    """, (username, category, amount, date))
    conn.commit()
    conn.close()


def get_expenses(username):
    """Returns list of (category, amount, date) — all rows for username."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT category, amount, date
    FROM expenses
    WHERE username = ?
    ORDER BY date DESC, id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_expenses_with_id(username):
    """Returns list of (id, category, amount, date) — all rows for username."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, category, amount, date
    FROM expenses
    WHERE username = ?
    ORDER BY date DESC, id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_total_spending(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM expenses
    WHERE username = ?
    """, (username,))
    total = cursor.fetchone()[0]
    conn.close()
    return float(total)


def delete_expense(expense_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


# =========================
# GOAL FUNCTIONS
# =========================

def save_goal(username, goal_name, target_amount, deadline):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO goals (username, goal_name, target_amount, deadline, is_active, is_achieved)
    VALUES (?, ?, ?, ?, 0, 0)
    """, (username, goal_name, target_amount, deadline))
    conn.commit()
    conn.close()


def get_goals(username):
    """Returns list of (id, goal_name, target_amount, deadline, is_active, is_achieved)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, goal_name, target_amount, deadline, is_active, is_achieved
    FROM goals
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_active_goal(username):
    """Returns the first active non-achieved goal as a dict, or None."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, goal_name, target_amount, deadline
    FROM goals
    WHERE username = ? AND is_active = 1 AND is_achieved = 0
    ORDER BY id ASC
    LIMIT 1
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "goal_name": row[1],
        "target_amount": row[2],
        "deadline": row[3],
    }


def get_active_goals(username):
    """Returns ALL active non-achieved goals as a list of dicts."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, goal_name, target_amount, deadline
    FROM goals
    WHERE username = ? AND is_active = 1 AND is_achieved = 0
    ORDER BY id ASC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "goal_name": r[1], "target_amount": r[2], "deadline": r[3]}
        for r in rows
    ]


def set_active_goal(username, goal_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET is_active = 0 WHERE username = ?", (username,)
    )
    cursor.execute(
        "UPDATE goals SET is_active = 1 WHERE id = ?", (goal_id,)
    )
    conn.commit()
    conn.close()


def toggle_goal_active(username, goal_id, active: bool):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET is_active = ? WHERE id = ? AND username = ?",
        (1 if active else 0, goal_id, username)
    )
    conn.commit()
    conn.close()


def mark_goal_achieved(username, goal_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET is_active = 0, is_achieved = 1 WHERE id = ? AND username = ?",
        (goal_id, username)
    )
    conn.commit()
    conn.close()


def update_goal(goal_id, goal_name, target_amount, deadline):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE goals
    SET goal_name = ?, target_amount = ?, deadline = ?
    WHERE id = ?
    """, (goal_name, target_amount, deadline, goal_id))
    conn.commit()
    conn.close()


def delete_goal(goal_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()


# =========================
# CHAT HISTORY FUNCTIONS
# =========================

def save_chat_message(username, role, message):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO chat_history (username, role, message)
    VALUES (?, ?, ?)
    """, (username, role, message))
    conn.commit()
    conn.close()


def get_chat_history(username):
    """Returns list of (role, message) tuples in chronological order."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT role, message
    FROM chat_history
    WHERE username = ?
    ORDER BY id ASC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_chat_history(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE username = ?", (username,))
    conn.commit()
    conn.close()


# =========================
# AI ANALYSIS FUNCTIONS
# =========================

def save_ai_analysis(username, health_summary, step_plan):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO ai_analysis (username, health_summary, step_plan)
    VALUES (?, ?, ?)
    """, (username, health_summary, step_plan))
    conn.commit()
    conn.close()


def get_latest_ai_analysis(username):
    """Returns (health_summary, step_plan) or (None, None)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT health_summary, step_plan
    FROM ai_analysis
    WHERE username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None