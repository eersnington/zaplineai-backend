import asyncio
import sqlite3
from prisma import Prisma

db = Prisma()

conn = sqlite3.connect('user_metrics.db')
c = conn.cursor()

# Create the user_metrics table if it doesn't exist
with conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS user_metrics (
                     user_id TEXT,
                     calls INTEGER,
                     automated_calls INTEGER,
                     transferred_calls INTEGER,
                     abandoned_calls INTEGER,
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )''')
    

