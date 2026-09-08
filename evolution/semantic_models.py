from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SemanticContract(BaseModel):
    """
    Defines the semantic meaning, expected behavior, and business context
    of a specific column to ground future AI investigation.
    """
    column: str = Field(description="Name of the column")
    meaning: str = Field(description="Human-readable description of what the data represents")
    unit: Optional[str] = Field(default=None, description="The unit of measurement (e.g., milliseconds, USD)")
    data_type: str = Field(description="Expected logical data type")
    domain: str = Field(description="Business domain this data belongs to (e.g., gameplay telemetry, billing)")
    
    expected_range: Optional[List[float]] = Field(default=None, description="Expected [min, max] range for numeric types")
    allowed_values: Optional[List[Any]] = Field(default=None, description="Explicitly allowed enum or categorical values")
    invariants: Optional[List[str]] = Field(default=None, description="Business rules (e.g., 'must_be_non_negative')")
    description: Optional[str] = Field(default=None, description="Additional context or caveats about the field")
