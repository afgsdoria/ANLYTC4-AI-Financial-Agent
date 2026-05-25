"""
database.py — All SQLite operations for Financial AI Agent
Extended: age, report_schedule, file_context, ai_analysis cache
"""

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


# ─────────────────────────────────────────────────────────
# CREATE / MIGRATE TABLES
# ─────────────────────────────────────────────────────────

def create_tables():
    conn = connect_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        username         TEXT UNIQUE NOT NULL,
        user_type        TEXT DEFAULT 'Student',
        age              INTEGER DEFAULT 0,
        birthday         TEXT DEFAULT NULL,
        monthly_income   REAL DEFAULT 0,
        savings_goal     REAL DEFAULT 0,
        current_savings  REAL DEFAULT 0,
        report_schedule  TEXT DEFAULT 'monthly',
        report_date      TEXT DEFAULT NULL,
        file_context     TEXT DEFAULT NULL,
        onboarding_done  INTEGER DEFAULT 0
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
        created_at    TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS chat_history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT NOT NULL,
        role       TEXT NOT NULL,
        message    TEXT NOT NULL,
        created_at TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS ai_analysis (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT NOT NULL,
        analysis   TEXT NOT NULL,
        plan       TEXT NOT NULL,
        created_at TEXT DEFAULT NULL
    );
    """)

    # ── Safe migrations ────────────────────────────────
    def _add_col(table, col, typedef):
        c.execute(f"PRAGMA table_info({table})")
        existing = [r[1] for r in c.fetchall()]
        if col not in existing:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")

    _add_col("users", "age",             "INTEGER DEFAULT 0")
    _add_col("users", "birthday",        "TEXT DEFAULT NULL")
    _add_col("users", "report_schedule", "TEXT DEFAULT 'monthly'")
    _add_col("users", "report_date",     "TEXT DEFAULT NULL")
    _add_col("users", "file_context",    "TEXT DEFAULT NULL")
    _add_col("users", "onboarding_done", "INTEGER DEFAULT 0")
    _add_col("goals", "created_at",      "TEXT DEFAULT NULL")

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────────────────

def save_user(username, user_type, monthly_income, savings_goal,
              current_savings, birthday=None, age=0, report_schedule="monthly",
              report_date=None, file_context=None, onboarding_done=0):
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users
            (username, user_type, age, birthday, monthly_income, savings_goal,
             current_savings, report_schedule, report_date,
             file_context, onboarding_done)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(username) DO UPDATE SET
            user_type        = excluded.user_type,
            age              = excluded.age,
            birthday         = excluded.birthday,
            monthly_income   = excluded.monthly_income,
            savings_goal     = excluded.savings_goal,
            current_savings  = excluded.current_savings,
            report_schedule  = excluded.report_schedule,
            report_date      = excluded.report_date,
            file_context     = COALESCE(excluded.file_context, file_context),
            onboarding_done  = excluded.onboarding_done
    """, (username, user_type, age, birthday, monthly_income, savings_goal,
          current_savings, report_schedule, report_date,
          file_context, onboarding_done))
    conn.commit()
    conn.close()


def get_user(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        SELECT user_type, monthly_income, savings_goal, current_savings,
               age, birthday, report_schedule, report_date, file_context, onboarding_done
        FROM users WHERE username = ?
    """, (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def set_file_context(username, text):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE users SET file_context = ? WHERE username = ?", (text, username))
    conn.commit()
    conn.close()


def set_onboarding_done(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE users SET onboarding_done = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def update_report_schedule(username, schedule, report_date=None):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET report_schedule=?, report_date=? WHERE username=?",
        (schedule, report_date, username)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# EXPENSES
# ─────────────────────────────────────────────────────────

def add_expense(username, category, amount, date):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (username,category,amount,date) VALUES (?,?,?,?)",
        (username, category, float(amount), date)
    )
    conn.commit()
    conn.close()


def get_expenses(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT category,amount,date FROM expenses WHERE username=? ORDER BY id DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def get_expenses_with_id(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT id,category,amount,date FROM expenses WHERE username=? ORDER BY date DESC,id DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def delete_expense(expense_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


def get_total_spending(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE username=?", (username,))
    val = c.fetchone()[0]
    conn.close()
    return float(val)


def get_spending_by_category(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        SELECT category, COALESCE(SUM(amount),0) as total
        FROM expenses WHERE username=?
        GROUP BY category ORDER BY total DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows]


# ─────────────────────────────────────────────────────────
# GOALS
# ─────────────────────────────────────────────────────────

def save_goal(username, goal_name, target_amount, deadline):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO goals (username,goal_name,target_amount,deadline,is_active) VALUES (?,?,?,?,0)",
        (username, goal_name, float(target_amount), deadline)
    )
    conn.commit()
    conn.close()


def get_goals(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT id,goal_name,target_amount,deadline,is_active FROM goals WHERE username=? ORDER BY id DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def get_active_goal(username):
    """Return the first active goal (legacy / sidebar widget)."""
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT id,goal_name,target_amount,deadline FROM goals WHERE username=? AND is_active=1 LIMIT 1",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "goal_name": row[1], "target_amount": row[2], "deadline": row[3]}
    return None


def get_active_goals(username):
    """Return ALL active goals as a list of dicts."""
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT id,goal_name,target_amount,deadline FROM goals WHERE username=? AND is_active=1 ORDER BY id ASC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "goal_name": r[1], "target_amount": r[2], "deadline": r[3]} for r in rows]


def set_active_goal(username, goal_id):
    """Deactivate all then activate one (used during onboarding)."""
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE goals SET is_active=0 WHERE username=?", (username,))
    c.execute("UPDATE goals SET is_active=1 WHERE id=? AND username=?", (goal_id, username))
    conn.commit()
    conn.close()


def toggle_goal_active(username: str, goal_id: int, make_active: bool):
    """Activate or deactivate a single goal without touching others (multi-goal support)."""
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE goals SET is_active = ? WHERE id = ? AND username = ?",
        (1 if make_active else 0, goal_id, username)
    )
    conn.commit()
    conn.close()


def update_goal(goal_id, goal_name, target_amount, deadline):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE goals SET goal_name=?,target_amount=?,deadline=? WHERE id=?",
        (goal_name, float(target_amount), deadline, goal_id)
    )
    conn.commit()
    conn.close()


def delete_goal(goal_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────

def save_chat_message(username, role, message):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (username,role,message) VALUES (?,?,?)",
        (username, role, message)
    )
    conn.commit()
    conn.close()


def get_chat_history(username, limit=30):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT role,message FROM chat_history WHERE username=? ORDER BY id DESC LIMIT ?",
        (username, limit)
    )
    rows = c.fetchall()
    conn.close()
    return [(r[0], r[1]) for r in reversed(rows)]


def clear_chat_history(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE username=?", (username,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# AI ANALYSIS CACHE
# ─────────────────────────────────────────────────────────

def save_ai_analysis(username, analysis, plan):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO ai_analysis (username,analysis,plan) VALUES (?,?,?)",
        (username, analysis, plan)
    )
    conn.commit()
    conn.close()


def get_latest_ai_analysis(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT analysis,plan FROM ai_analysis WHERE username=? ORDER BY id DESC LIMIT 1",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    return (row[0], row[1]) if row else (None, None)