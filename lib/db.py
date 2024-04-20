import asyncio
import sqlite3
from prisma import Prisma

db = Prisma()

conn = sqlite3.connect('user_metrics.db')
c = conn.cursor()

with conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS user_metrics (
                     user_id TEXT,
                     calls INTEGER,
                     automated_calls INTEGER,
                     transferred_calls INTEGER,
                     abandoned_calls INTEGER,
                     call_type TEXT DEFAULT "automated",
                     call_intent TEXT DEFAULT "Order Status",
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )''')


def track_metrics(user_id: str, call_type: str, call_intent: str) -> None:
    """
    Tracks the metrics of a user's call.

    Args:
        user_id (str): The user's ID.
        call_type (str): The type of call to be tracked.
        call_intent (str): The intent of the call.

    Returns:
        None. The function performs an insert operation and does not return anything.
    """
    sql = '''INSERT INTO user_metrics (user_id, calls, automated_calls, transferred_calls, abandoned_calls, call_type, call_intent)
                VALUES (?, ?, ?, ?, ?, ?, ?)'''

    if call_type == "automated":
        data = (user_id, 1, 1, 0, 0, "automated", call_intent)
        c.execute(sql, data)
    elif call_type == "transferred":
        data = (user_id, 1, 0, 1, 0, "transferred", call_intent)
        c.execute(sql, data)
    elif call_type == "abandoned":
        data(user_id, 1, 0, 0, 1, "abandoned", "Neither")
        c.execute(sql, data)

    conn.commit()
