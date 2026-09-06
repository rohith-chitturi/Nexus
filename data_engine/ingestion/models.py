from datetime import datetime

from pydantic import BaseModel, Field


class MatchEvent(BaseModel):
    """
    Synthetic multiplayer gaming telemetry event.
    """
    event_id: str = Field(description="Unique identifier for the event")
    timestamp: datetime = Field(description="Time the event occurred")
    match_id: str = Field(description="Identifier for the match")
    player_id: int = Field(description="Identifier for the player")
    event_type: str = Field(description="Type of the event (e.g., match_completed)")
    latency_ms: int = Field(description="Player latency in milliseconds")
    region: str = Field(description="Server region (e.g., NA, EU, ASIA)")
    game_version: str = Field(description="Version of the game client")
