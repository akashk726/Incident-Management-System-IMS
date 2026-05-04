import sqlite3
import os
import json

# 🔥 retry helper (ADDED)
from app.retry import enqueue_retry

# ------------------ DB PATH ------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "incidents.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ------------------ CREATE TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY,
    component_id TEXT,
    severity TEXT,
    status TEXT,
    signal_count INTEGER,
    start_time TEXT,
    rca TEXT,
    mttr INTEGER
)
""")
conn.commit()

# ------------------ SAVE ------------------
def save_incident(incident):
    try:
        cursor.execute("""
        INSERT INTO incidents 
        (id, component_id, severity, status, signal_count, start_time, rca, mttr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(incident["id"]),
            str(incident["component_id"]),
            str(incident["severity"]),
            str(incident["status"]),
            int(incident["signal_count"]),
            str(incident["start_time"]),
            json.dumps(incident["rca"]) if incident["rca"] else None,
            incident["mttr"]
        ))
        conn.commit()
    except Exception as e:
        print("❌ DB save failed:", e)
        enqueue_retry(save_incident, incident)  # 🔁 retry later

# ------------------ UPDATE ------------------
def update_incident(incident):
    try:
        cursor.execute("""
        UPDATE incidents
        SET severity=?, status=?, signal_count=?, rca=?, mttr=?
        WHERE id=?
        """, (
            str(incident["severity"]),
            str(incident["status"]),
            int(incident["signal_count"]),
            json.dumps(incident["rca"]) if incident["rca"] else None,
            incident["mttr"],
            incident["id"]
        ))
        conn.commit()
    except Exception as e:
        print("❌ DB update failed:", e)
        enqueue_retry(update_incident, incident)  # 🔁 retry later

# ------------------ LOAD ------------------
def load_incidents():
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()

    data = []
    for row in rows:
        try:
            rca_data = json.loads(row[6]) if row[6] else None
        except:
            rca_data = None

        data.append({
            "id": row[0],
            "component_id": row[1],
            "severity": row[2],
            "status": row[3],
            "signal_count": int(row[4]),
            "start_time": row[5],
            "rca": rca_data,
            "mttr": row[7]
        })

    print("📦 Loaded from DB:", data)
    return data