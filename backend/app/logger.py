import time

# Count signals processed
count = 0

def increment():
    global count
    count += 1

# Print metrics every 5 sec
def log_metrics():
    global count
    while True:
        print(f"[METRICS] signals/sec: {count}")
        count = 0
        time.sleep(5)