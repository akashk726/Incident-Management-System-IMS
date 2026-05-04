from app.db import conn, cursor

class IncidentRepository:
    def merge_signal(self, component):
        cursor.execute("""
            UPDATE incidents
            SET signal_count = signal_count + 1
            WHERE component_id=? AND status='OPEN'
        """, (component,))
        return cursor.rowcount > 0

    def create_incident(self, component, severity, timestamp, created_at):
        cursor.execute("""
            INSERT INTO incidents
            (component_id, severity, status, start_time, signal_count, created_at)
            VALUES (?, ?, 'OPEN', ?, 1, ?)
        """, (component, severity, timestamp, created_at))

    def get_all(self):
        cursor.execute("""
            SELECT id, component_id, severity, status, start_time, signal_count, rca, mttr
            FROM incidents ORDER BY id DESC
        """)
        return cursor.fetchall()

    def close_incident(self, id, rca_json, mttr):
        cursor.execute("""
            UPDATE incidents
            SET status='CLOSED', rca=?, mttr=?
            WHERE id=? AND status='OPEN'
        """, (rca_json, mttr, id))
        return cursor.rowcount