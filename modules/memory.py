"""
memory.py
Thin wrapper that re-exports chat-history helpers from database.py.
"""
from modules.database import (
    save_chat_message,
    get_chat_history,
    clear_chat_history,
    create_tables as _create_tables,
)


def create_chat_table():
    _create_tables()