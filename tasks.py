import os
import sqlite3
import time

from celery import Task

from celery_app import app
from db import get_conn


@app.task(acks_late=True)
def add(x, y):
    return x + y


@app.task(acks_late=True)          # <- decorator của charge nằm ở đây
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
        conn.close()

    print(f"[PID {pid}] ĐÃ TRỪ TIỀN, đang gửi biên lai...")
    time.sleep(15)
    print(f"[PID {pid}] XONG")
    return "charged"


class TransientError(Exception):
    """Lỗi tạm thời (kiểu 503, timeout): đáng retry."""


class PermanentError(Exception):
    """Lỗi vĩnh viễn (kiểu 400): retry vô ích."""


class AlertOnFailure(Task):
    """Chạy khi task thất bại hẳn (hết retry hoặc lỗi không được retry)."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"[DEAD] {self.name} id={task_id} args={args} lỗi={exc!r}")
        conn = get_conn()
        try:
            conn.execute(
                "INSERT INTO dead_letters (task_name, task_id, args, error) "
                "VALUES (?, ?, ?, ?)",
                (self.name, task_id, str(args), repr(exc)),
            )
            conn.commit()
        finally:
            conn.close()


@app.task(
    bind=True,
    base=AlertOnFailure,
    autoretry_for=(TransientError,),   # chỉ retry loại lỗi này
    retry_backoff=True,                # chờ tăng dần
    retry_backoff_max=60,              # trần thời gian chờ (giây)
    retry_jitter=True,                # tắt trước, sau đó bật lên để so sánh
    max_retries=4,
)
def call_api(self, mode):
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] call_api mode={mode} lần thử (retries)={self.request.retries}")

    if mode == "ok_after_2":
        if self.request.retries < 2:
            raise TransientError("503 giả lập")
        return "ok"
    if mode == "always_503":
        raise TransientError("503 giả lập")
    if mode == "bad_request":
        raise PermanentError("400 giả lập")
    return "mode không hợp lệ"