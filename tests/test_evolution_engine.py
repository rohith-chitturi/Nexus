from datetime import datetime

from evolution.engine import EvolutionEngine
from evolution.models import ChangeType, Severity
from evolution.policy import DriftPolicy
from evolution.snapshot import ColumnSchema, ColumnStatistics, DatasetSnapshot


def build_snapshot(schema_def, stats) -> DatasetSnapshot:
    return DatasetSnapshot(
        dataset_id="test_ds",
        snapshot_id="test",
        captured_at=datetime.utcnow(),
        schema_def=schema_def,
        statistics=stats
    )

def test_identical_snapshots():
    engine = EvolutionEngine()
    schema = [ColumnSchema(column="id", data_type="INT", nullable=False)]
    stats = {"id": ColumnStatistics(null_rate=0.0, mean=10.0)}
    
    snap_a = build_snapshot(schema, stats)
    events = engine.compare(snap_a, snap_a)
    assert len(events) == 0

def test_column_added_and_removed():
    engine = EvolutionEngine()
    
    schema_a = [ColumnSchema(column="id", data_type="INT", nullable=False)]
    schema_b = [ColumnSchema(column="new_id", data_type="INT", nullable=False)]
    
    snap_a = build_snapshot(schema_a, {})
    snap_b = build_snapshot(schema_b, {})
    
    events = engine.compare(snap_a, snap_b)
    assert len(events) == 2
    types = {e.change_type for e in events}
    assert ChangeType.COLUMN_REMOVED in types
    assert ChangeType.COLUMN_ADDED in types

def test_type_change():
    engine = EvolutionEngine()
    schema_a = [ColumnSchema(column="player_id", data_type="BIGINT", nullable=False)]
    schema_b = [ColumnSchema(column="player_id", data_type="VARCHAR", nullable=False)]
    
    events = engine.compare(build_snapshot(schema_a, {}), build_snapshot(schema_b, {}))
    assert len(events) == 1
    assert events[0].change_type == ChangeType.TYPE_CHANGE
    assert events[0].affected_columns == ["player_id"]
    assert events[0].evidence["previous_type"] == "BIGINT"
    assert events[0].evidence["current_type"] == "VARCHAR"

def test_statistical_drift():
    engine = EvolutionEngine()
    schema = [ColumnSchema(column="latency", data_type="INT", nullable=False)]
    
    stats_a = {"latency": ColumnStatistics(null_rate=0.0, mean=50.0)}
    stats_b = {"latency": ColumnStatistics(null_rate=0.0, mean=100.0)} # 100% change
    
    events = engine.compare(build_snapshot(schema, stats_a), build_snapshot(schema, stats_b))
    assert len(events) == 1
    assert events[0].change_type == ChangeType.STATISTICAL_DRIFT
    assert events[0].severity == Severity.MEDIUM
    assert events[0].evidence["relative_change"] == 1.0

def test_small_statistical_movement_ignored():
    policy = DriftPolicy(relative_mean_change_threshold=0.20)
    engine = EvolutionEngine(policy)
    
    schema = [ColumnSchema(column="latency", data_type="INT", nullable=False)]
    stats_a = {"latency": ColumnStatistics(null_rate=0.0, mean=50.0)}
    stats_b = {"latency": ColumnStatistics(null_rate=0.0, mean=55.0)} # 10% change < 20%
    
    events = engine.compare(build_snapshot(schema, stats_a), build_snapshot(schema, stats_b))
    assert len(events) == 0
