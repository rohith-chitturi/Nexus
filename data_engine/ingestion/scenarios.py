from typing import List

from data_engine.ingestion.models import MatchEvent


def inject_type_drift_player_id(events: List[MatchEvent]) -> List[dict]:
    """
    Simulates TYPE_CHANGE by converting player_id from integer to string.
    Returns dicts because it violates the baseline Pydantic model.
    """
    drifted = []
    for e in events:
        d = e.model_dump()
        d['player_id'] = f"STR_{d['player_id']}"
        drifted.append(d)
    return drifted

def inject_column_addition(events: List[MatchEvent]) -> List[dict]:
    """
    Simulates COLUMN_ADDED by injecting a 'device_type' column.
    """
    drifted = []
    for e in events:
        d = e.model_dump()
        d['device_type'] = "PC"
        drifted.append(d)
    return drifted

def inject_column_removal(events: List[MatchEvent]) -> List[dict]:
    """
    Simulates COLUMN_REMOVED by removing the 'region' column.
    """
    drifted = []
    for e in events:
        d = e.model_dump()
        if 'region' in d:
            del d['region']
        drifted.append(d)
    return drifted

def inject_nullability_drift(events: List[MatchEvent]) -> List[dict]:
    """
    Simulates NULLABILITY_CHANGE and NULL_RATE_CHANGE by making 'region' null for 50% of events.
    """
    drifted = []
    for i, e in enumerate(events):
        d = e.model_dump()
        if i % 2 == 0:
            d['region'] = None
        drifted.append(d)
    return drifted

def inject_statistical_drift(events: List[MatchEvent]) -> List[dict]:
    """
    Simulates STATISTICAL_DRIFT by doubling latency_ms.
    """
    drifted = []
    for e in events:
        d = e.model_dump()
        d['latency_ms'] = d['latency_ms'] * 2
        drifted.append(d)
    return drifted
