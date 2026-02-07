import sqlite3

def connect_db():
    return sqlite3.connect("database.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            interests TEXT
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
