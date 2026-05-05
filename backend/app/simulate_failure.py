import requests
import time
from datetime import datetime

URL = "http://127.0.0.1:8000/ingest"

def send_signal(component):
    payload = {
        "component_id": component,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        res = requests.post(URL, json=payload)
        print(component, res.status_code)
    except Exception as e:
        print("Error:", e)

def simulate_failure():
    print("🔥 Starting Failure Simulation...\n")

    # Step 1: RDBMS Failure (High frequency)
    print("⚠️ RDBMS Failure...")
    for _ in range(10):
        send_signal("RDBMS_01")
        time.sleep(0.1)

    # Step 2: API Impact
    print("\n⚠️ API Failure due to DB...")
    for _ in range(6):
        send_signal("API_01")
        time.sleep(0.2)

    # Step 3: Cache Degradation
    print("\n⚠️ Cache Instability...")
    for _ in range(4):
        send_signal("CACHE_01")
        time.sleep(0.3)

    # Step 4: MCP Failure
    print("\n⚠️ MCP Failure...")
    for _ in range(5):
        send_signal("MCP_01")
        time.sleep(0.2)

    print("\n✅ Simulation Complete")

if __name__ == "__main__":
    simulate_failure()