import sqlite3

def get_conn():
    return sqlite3.connect("lab.db", timeout=30)

def reset():
    conn = get_conn()
    conn.executescript("""
        DROP TABLE IF EXISTS accounts;
        DROP TABLE IF EXISTS processed_keys;
        DROP TABLE IF EXISTS dead_letters;
        CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL);
        CREATE TABLE processed_keys (key TEXT PRIMARY KEY);
        CREATE TABLE dead_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            task_id TEXT,
            args TEXT,
            error TEXT,
            at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO accounts (id, balance) VALUES (1, 1000);
    """)
    conn.commit()
    conn.close()