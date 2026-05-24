import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "financialAIAgent.db"
)


def connect_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CREATE TABLES
# =========================

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        username        TEXT UNIQUE NOT NULL,
        user_type       TEXT DEFAULT 'Student',
        monthly_income  REAL DEFAULT 0,
        savings_goal    REAL DEFAULT 0,
        current_savings REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        category TEXT NOT NULL,
        amount   REAL NOT NULL,
        date     TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS goals (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL,
        goal_name     TEXT NOT NULL,
        target_amount REAL DEFAULT 0,
        deadline      TEXT,
        is_active     INTEGER DEFAULT 0,
        created_at    TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS chat_history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT NOT NULL,
        role       TEXT NOT NULL,
        message    TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # Migration: add created_at to existing goals if missing
    # Note: ALTER TABLE cannot use non-constant defaults (e.g. datetime('now')),
    # so we use NULL as the default for existing rows.
    cursor.execute("PRAGMA table_info(goals)")
    cols = [row[1] for row in cursor.fetchall()]
    if "created_at" not in cols:
        cursor.execute(
            "ALTER TABLE goals ADD COLUMN created_at TEXT DEFAULT NULL"
        )

    conn.commit()
    conn.close()


# =========================
# USER FUNCTIONS
# =========================

def save_user(username, user_type, monthly_income, savings_goal, current_savings):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, user_type, monthly_income, savings_goal, current_savings)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            user_type       = excluded.user_type,
            monthly_income  = excluded.monthly_income,
            savings_goal    = excluded.savings_goal,
            current_savings = excluded.current_savings
    """, (username, user_type, monthly_income, savings_goal, current_savings))
    conn.commit()
    conn.close()


def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_type, monthly_income, savings_goal, current_savings
        FROM users WHERE username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    return tuple(row) if row else None


# =========================
# EXPENSE FUNCTIONS
# =========================

def add_expense(username, category, amount, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (username, category, amount, date)
        VALUES (?, ?, ?, ?)
    """, (username, category, float(amount), date))
    conn.commit()
    conn.close()


def get_expenses(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, amount, date
        FROM expenses WHERE username = ?
        ORDER BY id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def delete_expense(expense_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_expenses_with_id(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, amount, date
        FROM expenses WHERE username = ?
        ORDER BY date DESC, id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def get_total_spending(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE username = ?",
        (username,)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return float(total)


def get_spending_by_category(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COALESCE(SUM(amount), 0) as total
        FROM expenses WHERE username = ?
        GROUP BY category ORDER BY total DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows]


# =========================
# GOAL FUNCTIONS
# =========================

def save_goal(username, goal_name, target_amount, deadline):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO goals (username, goal_name, target_amount, deadline, is_active)
        VALUES (?, ?, ?, ?, 0)
    """, (username, goal_name, float(target_amount), deadline))
    conn.commit()
    conn.close()


def get_goals(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, goal_name, target_amount, deadline, is_active
        FROM goals WHERE username = ?
        ORDER BY id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def get_active_goal(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, goal_name, target_amount, deadline
        FROM goals WHERE username = ? AND is_active = 1
        LIMIT 1
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "goal_name": row[1],
            "target_amount": row[2],
            "deadline": row[3]
        }
    return None


def set_active_goal(username, goal_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET is_active = 0 WHERE username = ?", (username,)
    )
    cursor.execute(
        "UPDATE goals SET is_active = 1 WHERE id = ? AND username = ?",
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
    """, (goal_name, float(target_amount), deadline, goal_id))
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


def get_chat_history(username, limit=20):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message FROM chat_history
        WHERE username = ?
        ORDER BY id DESC LIMIT ?
    """, (username, limit))
    rows = cursor.fetchall()
    conn.close()
    return [(r[0], r[1]) for r in reversed(rows)]


def clear_chat_history(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chat_history WHERE username = ?", (username,)
    )
    conn.commit()
    conn.close()