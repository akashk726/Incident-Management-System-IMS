from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio, time
from datetime import datetime
from collections import defaultdict, deque

from app.db import save_incident, update_incident, load_incidents

# retry worker (ADDED)
from app.retry import retry_worker

app = FastAPI()

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ CONFIG ------------------
WORKER_COUNT = 2
QUEUE_MAXSIZE = 1000
RATE_LIMIT_PER_SEC = 200

# ------------------ STORAGE ------------------
incidents = []
incident_id_counter = 1

queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
component_locks = defaultdict(asyncio.Lock)
req_times = deque()

# ------------------ MODELS ------------------
class Signal(BaseModel):
    component_id: str
    timestamp: str

class RCA(BaseModel):
    start: str
    end: str
    rootCause: str
    fix: str
    prevention: str

# ------------------ RATE LIMIT ------------------
def check_rate_limit():
    now = time.time()
    while req_times and now - req_times[0] > 1:
        req_times.popleft()

    if len(req_times) >= RATE_LIMIT_PER_SEC:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    req_times.append(now)

# ------------------ WORKER ------------------
async def worker():
    print("🧵 Worker started...")

    while True:
        signal = await queue.get()
        print("⚙️ Processing:", signal)
        await process_signal(signal)
        queue.task_done()

# ------------------ PRIORITY ------------------
def assign_priority():
    open_incidents = [i for i in incidents if i["status"] == "OPEN"]

    sorted_incidents = sorted(
        open_incidents,
        key=lambda x: x["signal_count"],
        reverse=True
    )

    levels = ["P0", "P1", "P2", "P3"]

    for idx, inc in enumerate(sorted_incidents):
        inc["severity"] = levels[min(idx, 3)]
        update_incident(inc)

# ------------------ PROCESS SIGNAL ------------------
async def process_signal(signal):
    global incident_id_counter

    component = signal["component_id"]

    async with component_locks[component]:

        open_incident = None
        for inc in incidents:
            if inc["component_id"] == component and inc["status"] == "OPEN":
                open_incident = inc
                break

        if open_incident:
            print("🔁 Updating:", component)
            open_incident["signal_count"] += 1
            update_incident(open_incident)

        else:
            print("🆕 Creating NEW:", component)

            new_incident = {
                "id": incident_id_counter,
                "component_id": component,
                "severity": "P3",
                "status": "OPEN",
                "signal_count": 1,
                "start_time": datetime.now().isoformat(),
                "rca": None,
                "mttr": None
            }

            incidents.append(new_incident)
            incident_id_counter += 1

            save_incident(new_incident)

        assign_priority()

# ------------------ STARTUP ------------------
@app.on_event("startup")
async def startup():
    global incidents, incident_id_counter

    print("🚀 Loading DB...")

    db_data = load_incidents()
    if db_data:
        incidents.extend(db_data)
        incident_id_counter = max(i["id"] for i in incidents) + 1

    print("🚀 Starting workers...")

    for _ in range(WORKER_COUNT):
        asyncio.create_task(worker())

    # START RETRY WORKER
    asyncio.create_task(retry_worker())

# ------------------ APIs ------------------
@app.get("/")
def root():
    return {"message": "API running"}

@app.post("/ingest")
async def ingest(signal: Signal):
    print("📥 Received:", signal.dict())

    check_rate_limit()

    try:
        await asyncio.wait_for(queue.put(signal.dict()), timeout=1)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="Queue full")

    return {"message": "queued"}

@app.get("/incidents")
def get_incidents():
    return incidents

# HEALTH ENDPOINT (ADDED)
@app.get("/health")
def health():
    return {
        "status": "ok",
        "queue_size": queue.qsize(),
        "total_incidents": len(incidents)
    }

# ------------------ CLOSE ------------------
@app.post("/close/{id}")
def close_incident(id: int, rca: RCA):
    for inc in incidents:
        if inc["id"] == id:

            try:
                start = datetime.fromisoformat(rca.start)
                end = datetime.fromisoformat(rca.end)
            except:
                return {"error": "Invalid datetime"}

            mttr = int((end - start).total_seconds())

            inc["status"] = "CLOSED"
            inc["rca"] = rca.dict()
            inc["mttr"] = mttr

            update_incident(inc)
            assign_priority()

            return {"message": "incident closed", "mttr": mttr}

    return {"error": "not found"}
