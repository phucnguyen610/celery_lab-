import sqlite3

def get_conn():
    return sqlite3.connect("lab.db", timeout=30)

def reset():
    conn = get_conn()
    conn.executescript("""
        DROP TABLE IF EXISTS accounts;
        CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL);
        INSERT INTO accounts (id, balance) VALUES (1, 1000);
    """)
    conn.commit()
    conn.close()