from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from evolution.semantic_models import SemanticContract
from evolution.snapshot import ColumnSchema, ColumnStatistics


class QualityConstraints(BaseModel):
    max_null_rate: Optional[float] = None
    allowed_values: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class DataConstitution(BaseModel):
    """
    The formal contract and expected baseline for a dataset.
    """
    dataset_id: str
    version: str
    expected_schema: List[ColumnSchema]
    baseline_statistics: Dict[str, ColumnStatistics]
    quality_constraints: Dict[str, QualityConstraints]
    semantic_contracts: Dict[str, SemanticContract] = Field(default_factory=dict)
