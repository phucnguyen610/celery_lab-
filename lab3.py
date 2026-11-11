import sys
import db
from tasks import call_api

db.reset()
mode = sys.argv[1]
r = call_api.delay(mode)
print("task id:", r.id)