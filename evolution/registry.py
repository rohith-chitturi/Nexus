import copy
from typing import List, Protocol

from evolution.models import EvolutionEvent


class EvolutionRegistry(Protocol):
    """
    Interface for tracking detected EvolutionEvents.
    """
    def record(self, event: EvolutionEvent) -> None:
        ...

    def get(self, event_id: str) -> EvolutionEvent | None:
        ...

    def list_for_dataset(self, dataset_id: str) -> List[EvolutionEvent]:
        ...

    def list_between_versions(self, dataset_id: str, from_version: str, to_version: str) -> List[EvolutionEvent]:
        ...


class InMemoryEvolutionRegistry(EvolutionRegistry):
    """
    Lightweight in-memory registry for testing and development.
    """
    def __init__(self):
        self._events: dict[str, EvolutionEvent] = {}

    def record(self, event: EvolutionEvent) -> None:
        self._events[event.event_id] = copy.deepcopy(event)

    def get(self, event_id: str) -> EvolutionEvent | None:
        return copy.deepcopy(self._events.get(event_id))

    def list_for_dataset(self, dataset_id: str) -> List[EvolutionEvent]:
        res = [e for e in self._events.values() if e.dataset_id == dataset_id]
        # Sort by detected_at ascending
        return sorted(res, key=lambda x: x.detected_at)

    def list_between_versions(self, dataset_id: str, from_version: str, to_version: str) -> List[EvolutionEvent]:
        res = [
            e for e in self._events.values() 
            if e.dataset_id == dataset_id and e.from_snapshot_id == from_version and e.to_snapshot_id == to_version
        ]
        return sorted(res, key=lambda x: x.detected_at)
