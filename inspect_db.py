# inspect_db.py

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()