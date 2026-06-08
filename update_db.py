# update_db.py

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE users
ADD COLUMN password TEXT
""")

conn.commit()
conn.close()

print("Password column added.")