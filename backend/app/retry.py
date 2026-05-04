import asyncio
from collections import deque

# queue of failed ops
retry_queue = deque()

# push failed operation
def enqueue_retry(func, *args):
    retry_queue.append((func, args))

# background retry worker
async def retry_worker():
    while True:
        if retry_queue:
            func, args = retry_queue.popleft()
            try:
                func(*args)
                print("♻️ Retry success")
            except Exception as e:
                print("❌ Retry failed, re-queue:", e)
                retry_queue.append((func, args))
        await asyncio.sleep(2)