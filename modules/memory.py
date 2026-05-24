from modules.database import connect_db


# =========================
# CREATE CHAT TABLE
# =========================

def create_chat_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# SAVE MESSAGE
# =========================

def save_chat_message(
    username,
    role,
    message
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chat_history
    (
        username,
        role,
        message
    )
    VALUES (?, ?, ?)
    """, (
        username,
        role,
        message
    ))

    conn.commit()
    conn.close()


# =========================
# LOAD CHAT HISTORY
# =========================

def get_chat_history(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM chat_history
    WHERE username = ?
    ORDER BY id ASC
    """, (username,))

    history = cursor.fetchall()

    conn.close()

    return history