import requests
import time

URL = "http://127.0.0.1:8000/ingest"

for i in range(20):
    data = {
        "component_id": f"COMP_{i%5}",
        "timestamp": "2026-04-03T10:00:00"
    }
    r = requests.post(URL, json=data)
    print(i, r.status_code)
    time.sleep(0.1)