import os
import tempfile
from datetime import datetime

from data_engine.ingestion.consumer import KafkaTelemetryConsumer
from data_engine.ingestion.models import MatchEvent
from data_engine.profiling.duckdb_client import DuckDBClient


def test_parquet_writing_and_duckdb_reading():
    """
    Verify that the consumer correctly writes Parquet files 
    and DuckDB can query them via hive partitioning.
    """
    # Create some dummy events
    events = [
        MatchEvent(
            event_id="e1",
            timestamp=datetime(2026, 9, 6, 12, 0, 0),
            match_id="m1",
            player_id=1,
            event_type="match_started",
            latency_ms=50,
            region="NA",
            game_version="1.0"
        ),
        MatchEvent(
            event_id="e2",
            timestamp=datetime(2026, 9, 7, 12, 0, 0), # different day for partitioning
            match_id="m2",
            player_id=2,
            event_type="match_completed",
            latency_ms=60,
            region="EU",
            game_version="1.0"
        )
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Write events to temp Parquet Lake
        consumer = KafkaTelemetryConsumer(lake_path=tmp_dir)
        consumer.write_to_parquet(events)
        
        # Verify directory structure (partitioning)
        partitions = os.listdir(tmp_dir)
        assert "event_date=2026-09-06" in partitions
        assert "event_date=2026-09-07" in partitions

        # 2. Query with DuckDB
        duck = DuckDBClient()
        # **/*.parquet grabs all part files in all partition dirs
        glob_path = os.path.join(tmp_dir, "**", "*.parquet")
        duck.register_parquet_view("match_events", glob_path)
        
        # Query total count
        res = duck.query("SELECT count(*) FROM match_events").fetchone()
        assert res[0] == 2
        
        # Query partition column extraction
        res_dates = duck.query("SELECT event_date FROM match_events ORDER BY event_date").fetchall()
        assert res_dates[0][0] == "2026-09-06"
        assert res_dates[1][0] == "2026-09-07"
        
        duck.close()
