import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    COLUMN_ADDED = "COLUMN_ADDED"
    COLUMN_REMOVED = "COLUMN_REMOVED"
    TYPE_CHANGE = "TYPE_CHANGE"
    NULLABILITY_CHANGE = "NULLABILITY_CHANGE"
    STATISTICAL_DRIFT = "STATISTICAL_DRIFT"
    CARDINALITY_CHANGE = "CARDINALITY_CHANGE"
    NULL_RATE_CHANGE = "NULL_RATE_CHANGE"
    
    # Placeholders for future agentic reasoning
    SEMANTIC_DRIFT = "SEMANTIC_DRIFT"
    UNIT_DRIFT = "UNIT_DRIFT"
    ENUM_EVOLUTION = "ENUM_EVOLUTION"

class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EvolutionEvent(BaseModel):
    """
    Represents a detected change between two DatasetSnapshots.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str
    from_snapshot_id: str
    to_snapshot_id: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    change_type: ChangeType
    severity: Severity
    affected_columns: List[str]
    
    # Structured evidence to ground future AI investigation
    evidence: Dict[str, Any]
    
    confidence: float = Field(default=1.0, description="1.0 for deterministic engines")
    status: str = Field(default="OPEN")
