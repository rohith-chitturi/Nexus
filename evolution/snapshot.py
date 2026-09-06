from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    column: str
    data_type: str
    nullable: bool
    cardinality: Optional[int] = None

class ColumnStatistics(BaseModel):
    null_rate: float
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    variance: Optional[float] = None

class DatasetSnapshot(BaseModel):
    """
    Represents the deterministic state and statistics of a dataset at a point in time.
    """
    dataset_id: str = Field(description="Identifier for the dataset")
    snapshot_id: str = Field(description="Unique identifier for this snapshot")
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    schema_def: List[ColumnSchema] = Field(description="Schema definition of the dataset")
    statistics: Dict[str, ColumnStatistics] = Field(description="Column-level statistics")
