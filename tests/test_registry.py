from evolution.models import ChangeType, EvolutionEvent, Severity
from evolution.registry import InMemoryEvolutionRegistry


def create_dummy_event(dataset_id="test_ds", from_snap="v1", to_snap="v2"):
    return EvolutionEvent(
        dataset_id=dataset_id,
        from_snapshot_id=from_snap,
        to_snapshot_id=to_snap,
        change_type=ChangeType.TYPE_CHANGE,
        severity=Severity.HIGH,
        affected_columns=["player_id"],
        evidence={"previous_type": "integer", "current_type": "string"}
    )

def test_in_memory_registry():
    registry = InMemoryEvolutionRegistry()
    event = create_dummy_event()
    
    # Test record and get
    registry.record(event)
    retrieved = registry.get(event.event_id)
    assert retrieved is not None
    assert retrieved.event_id == event.event_id
    assert retrieved.evidence["current_type"] == "string"
    
    # Test list_for_dataset
    registry.record(create_dummy_event(dataset_id="other_ds"))
    ds_events = registry.list_for_dataset("test_ds")
    assert len(ds_events) == 1
    
    # Test list_between_versions
    registry.record(create_dummy_event(from_snap="v2", to_snap="v3"))
    version_events = registry.list_between_versions("test_ds", "v1", "v2")
    assert len(version_events) == 1
    assert version_events[0].from_snapshot_id == "v1"

# NOTE: PostgreSQL test would require a running instance. We can skip it here for fast unit tests,
# or mock it. For now, testing the interface through InMemory is sufficient for basic domain logic.
