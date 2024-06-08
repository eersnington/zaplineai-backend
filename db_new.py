import sqlite3
from random import choices, randint
from datetime import datetime, timedelta

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

# Define the user ID for which calls should be added
user_id = 'kp_1071d97754b44202a1cc766e2cc6a512'

# Define the ratios for automated, transferred, and abandoned calls
ratios = [80, 18, 2]

# Define the start and end dates for the calls
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

c.execute('''SELECT strftime('%Y-%m-%d %H:%M:%S', timestamp), call_type, call_intent FROM user_metrics WHERE user_id=? ORDER BY timestamp DESC LIMIT 7''', (user_id,))
recent_calls = c.fetchall()

print(recent_calls)

# Add 250 calls
for _ in range(342):
    call_type = choices(['automated', 'transferred', 'abandoned'], ratios)[0]
    if call_type == 'automated':
        call_intent = choices(['Order Status', 'Returns', 'Product Info', 'Refund'], [25, 25, 25, 25])[0]
    elif call_type == 'transferred':
        call_intent = choices(['Sales', 'Transfer'], [50, 50])[0]
    else:
        call_intent = 'Neither'
    timestamp = start_date + timedelta(days=randint(0, 7))
    c.execute('''INSERT INTO user_metrics (user_id, calls, automated_calls, transferred_calls, abandoned_calls, call_type, call_intent, timestamp)
                      VALUES (?, 1, ?, ?, ?, ?, ?, ?)''',
                   (user_id,
                    call_type == 'automated',
                    call_type == 'transferred',
                    call_type == 'abandoned',
                    call_type,
                    call_intent,
                    timestamp))

# Commit the changes and close the connection
conn.commit()
conn.close()
