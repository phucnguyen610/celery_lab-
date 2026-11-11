import os
import sqlite3
import time

from celery_app import app
from db import get_conn


@app.task(acks_late=True)
def add(x, y):
    return x + y

def charge(account_id, amount, idempotency_key):
    pid = os.getpid()
    print(f"[PID {pid}] BẮT ĐẦU charge key={idempotency_key}")

    conn = get_conn()
    try:
        try:
            conn.execute(
                "INSERT INTO processed_keys (key) VALUES (?)",
                (idempotency_key,),
            )
        except sqlite3.IntegrityError:
            print(f"[PID {pid}] key={idempotency_key} đã xử lý, BỎ QUA")
            return "skipped"

        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, account_id),
        )
        conn.commit()          # MỘT commit duy nhất: key + trừ tiền cùng thành công
    finally:
        conn.close()           # nhánh nào cũng đóng kết nối

    print(f"[PID {pid}] ĐÃ TRỪ TIỀN, đang gửi biên lai...")
    time.sleep(15)
    print(f"[PID {pid}] XONG")
    return "charged"