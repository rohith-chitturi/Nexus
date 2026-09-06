import os
import tempfile
from datetime import datetime

from data_engine.contracts.constitution import DataConstitution
from data_engine.ingestion.consumer import KafkaTelemetryConsumer
from data_engine.ingestion.models import MatchEvent
from data_engine.profiling.duckdb_client import DuckDBClient
from data_engine.profiling.profiler import DatasetProfiler


def test_profiler_and_constitution():
    """
    Verify that the profiler extracts schemas and numeric statistics accurately.
    """
    events = [
        MatchEvent(event_id="e1", timestamp=datetime.utcnow(), match_id="m1", player_id=1, event_type="started", latency_ms=10, region="NA", game_version="1.0"),
        MatchEvent(event_id="e2", timestamp=datetime.utcnow(), match_id="m2", player_id=2, event_type="completed", latency_ms=20, region="NA", game_version="1.0"),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        consumer = KafkaTelemetryConsumer(lake_path=tmp_dir)
        consumer.write_to_parquet(events)

        duck = DuckDBClient()
        duck.register_parquet_view("match_events", os.path.join(tmp_dir, "**", "*.parquet"))

        profiler = DatasetProfiler(duck)
        snapshot = profiler.profile_view("match_events_dataset", "match_events")

        # Verify Schema extraction
        schema_dict = {col.column: col.data_type for col in snapshot.schema_def}
        assert "latency_ms" in schema_dict
        assert "BIGINT" in schema_dict["latency_ms"].upper()

        # Verify Statistics
        latency_stats = snapshot.statistics.get("latency_ms")
        assert latency_stats is not None
        assert latency_stats.min == 10
        assert latency_stats.max == 20
        assert latency_stats.mean == 15.0
        assert latency_stats.null_rate == 0.0

        # Create dummy constitution to verify imports and serialization
        constitution = DataConstitution(
            dataset_id="match_events_dataset",
            version="1.0",
            expected_schema=snapshot.schema_def,
            baseline_statistics=snapshot.statistics,
            quality_constraints={}
        )
        assert constitution.version == "1.0"
        
        duck.close()
