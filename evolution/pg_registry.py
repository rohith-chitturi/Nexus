import json
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor

from evolution.models import ChangeType, EvolutionEvent, Severity
from evolution.registry import EvolutionRegistry


class PostgreSQLEvolutionRegistry(EvolutionRegistry):
    """
    Production registry backed by PostgreSQL.
    """
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._init_db()

    def _init_db(self):
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS evolution_events (
                        event_id VARCHAR PRIMARY KEY,
                        dataset_id VARCHAR NOT NULL,
                        from_snapshot_id VARCHAR NOT NULL,
                        to_snapshot_id VARCHAR NOT NULL,
                        detected_at TIMESTAMP NOT NULL,
                        change_type VARCHAR NOT NULL,
                        severity VARCHAR NOT NULL,
                        affected_columns JSONB NOT NULL,
                        evidence JSONB NOT NULL,
                        confidence FLOAT NOT NULL,
                        status VARCHAR NOT NULL
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_evo_dataset ON evolution_events(dataset_id)")

    def record(self, event: EvolutionEvent) -> None:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO evolution_events (
                        event_id, dataset_id, from_snapshot_id, to_snapshot_id,
                        detected_at, change_type, severity, affected_columns,
                        evidence, confidence, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        confidence = EXCLUDED.confidence
                """, (
                    event.event_id,
                    event.dataset_id,
                    event.from_snapshot_id,
                    event.to_snapshot_id,
                    event.detected_at,
                    event.change_type.value,
                    event.severity.value,
                    json.dumps(event.affected_columns),
                    json.dumps(event.evidence),
                    event.confidence,
                    event.status
                ))

    def _row_to_event(self, row: dict) -> EvolutionEvent:
        return EvolutionEvent(
            event_id=row['event_id'],
            dataset_id=row['dataset_id'],
            from_snapshot_id=row['from_snapshot_id'],
            to_snapshot_id=row['to_snapshot_id'],
            detected_at=row['detected_at'],
            change_type=ChangeType(row['change_type']),
            severity=Severity(row['severity']),
            affected_columns=row['affected_columns'],
            evidence=row['evidence'],
            confidence=row['confidence'],
            status=row['status']
        )

    def get(self, event_id: str) -> EvolutionEvent | None:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM evolution_events WHERE event_id = %s", (event_id,))
                row = cur.fetchone()
                return self._row_to_event(row) if row else None

    def list_for_dataset(self, dataset_id: str) -> List[EvolutionEvent]:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM evolution_events WHERE dataset_id = %s ORDER BY detected_at ASC",
                    (dataset_id,)
                )
                return [self._row_to_event(row) for row in cur.fetchall()]

    def list_between_versions(self, dataset_id: str, from_version: str, to_version: str) -> List[EvolutionEvent]:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM evolution_events 
                    WHERE dataset_id = %s AND from_snapshot_id = %s AND to_snapshot_id = %s
                    ORDER BY detected_at ASC
                    """,
                    (dataset_id, from_version, to_version)
                )
                return [self._row_to_event(row) for row in cur.fetchall()]
