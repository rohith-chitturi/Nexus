import random
import uuid
from datetime import datetime, timedelta
from typing import List

from data_engine.ingestion.models import MatchEvent


class TelemetryGenerator:
    """
    Generates deterministic synthetic telemetry for testing and simulation.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng = random.Random(seed)
        
        self.regions = ["NA", "EU", "ASIA", "OCE"]
        self.event_types = [
            "match_started",
            "player_killed",
            "item_purchased",
            "match_completed"
        ]
        self.game_versions = ["4.17", "4.17.1", "4.18"]
        self.base_time = datetime(2026, 9, 6, 12, 0, 0)
        self.event_counter = 0

    def generate_events(self, count: int) -> List[MatchEvent]:
        events = []
        for _ in range(count):
            self.event_counter += 1
            
            # Deterministic uuid generation using rng
            event_uuid_str = str(uuid.UUID(int=self._rng.getrandbits(128), version=4))
            
            match_id = f"M{self._rng.randint(1000, 9999)}"
            player_id = self._rng.randint(1, 100000)
            
            # Progress time slightly
            time_delta = self.event_counter * self._rng.uniform(0.1, 5.0)
            event_time = self.base_time + timedelta(seconds=time_delta)
            
            event = MatchEvent(
                event_id=event_uuid_str,
                timestamp=event_time,
                match_id=match_id,
                player_id=player_id,
                event_type=self._rng.choice(self.event_types),
                latency_ms=self._rng.randint(15, 250),
                region=self._rng.choice(self.regions),
                game_version=self._rng.choice(self.game_versions)
            )
            events.append(event)
            
        return events
