import time

# Track request timestamps
calls = {}

def allow_request(ip, limit=5, window=1):
    now = time.time()

    history = calls.get(ip, [])
    history = [t for t in history if now - t < window]

    # Too many requests → block
    if len(history) >= limit:
        return False

    history.append(now)
    calls[ip] = history
    return True