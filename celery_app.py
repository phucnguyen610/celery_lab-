import os
from celery import Celery

VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "3600"))

app = Celery(
    "lab",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["tasks"],
)

app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_transport_options={"visibility_timeout": VISIBILITY_TIMEOUT},
)