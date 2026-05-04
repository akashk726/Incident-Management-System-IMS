from datetime import datetime
import json
from app.repository import IncidentRepository
from app.debounce import should_create_work_item
from app.utils import calculate_mttr

class IncidentService:

    def __init__(self):
        self.repo = IncidentRepository()

    def process_signal(self, signal):
        component = signal["component_id"]
        severity = signal["severity"]
        timestamp = signal["timestamp"]
        now = datetime.utcnow().isoformat()

        # Merge if exists
        if self.repo.merge_signal(component):
            print("Merged into existing incident")
            return

        # Debounce
        if not should_create_work_item(component):
            print("Debounce blocked")
            return

        # Create new incident
        self.repo.create_incident(component, severity, timestamp, now)
        print("New incident created")

    def get_incidents(self):
        rows = self.repo.get_all()

        return [
            {
                "id": r[0],
                "component_id": r[1],
                "severity": r[2],
                "status": r[3],
                "start_time": r[4],
                "signal_count": r[5],
                "rca": json.loads(r[6]) if r[6] else None,
                "mttr": r[7]
            }
            for r in rows
        ]

    def close_incident(self, id, rca):
        start = datetime.fromisoformat(rca.start)
        end = datetime.fromisoformat(rca.end)

        mttr = calculate_mttr(start, end)

        updated = self.repo.close_incident(id, json.dumps(rca.dict()), mttr)

        if updated == 0:
            return {"error": "not found or already closed"}

        return {"message": "closed", "mttr": mttr}