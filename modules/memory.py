"""
memory.py
Thin wrapper that re-exports chat-history helpers from database.py.
All persistence happens in the shared SQLite database.
"""

from modules.database import (
    save_chat_message,
    get_chat_history,
    clear_chat_history,
    create_tables as _create_tables,
)


def create_chat_table():
    """Ensure the chat_history table exists (called on startup)."""
    _create_tables()