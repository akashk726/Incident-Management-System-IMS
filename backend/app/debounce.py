import time

# Cache stores last signal time
cache = {}

def should_create_work_item(component):
    now = time.time()

    # If same component within 10 sec → ignore
    if component in cache:
        if now - cache[component] < 10:
            return False

    cache[component] = now
    return True