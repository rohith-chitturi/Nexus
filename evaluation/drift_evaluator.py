import os
import tempfile

import pyarrow as pa
import pyarrow.parquet as pq

from data_engine.ingestion.generator import TelemetryGenerator
from data_engine.ingestion.scenarios import (
    inject_column_addition,
    inject_column_removal,
    inject_nullability_drift,
    inject_statistical_drift,
    inject_type_drift_player_id,
)
from data_engine.profiling.duckdb_client import DuckDBClient
from data_engine.profiling.profiler import DatasetProfiler
from evolution.engine import EvolutionEngine
from evolution.models import ChangeType
from evolution.policy import DriftPolicy


class DriftEvaluator:
    def __init__(self):
        self.generator = TelemetryGenerator(seed=101)
        self.baseline_events = self.generator.generate_events(500)
        self.engine = EvolutionEngine(DriftPolicy.default_policy())
        
    def _run_pipeline(self, data_dicts, lake_path: str, view_name: str) -> None:
        """Helper to write raw dicts to parquet and profile them."""
        os.makedirs(lake_path, exist_ok=True)
        # Use pyarrow to write directly to handle schema drifts seamlessly
        table = pa.Table.from_pylist(data_dicts)
        pq.write_to_dataset(table, root_path=lake_path)
        
    def evaluate_scenario(self, name: str, expected_type: ChangeType, mutator_func) -> dict:
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            # V1: Baseline
            baseline_dicts = [e.model_dump() for e in self.baseline_events]
            self._run_pipeline(baseline_dicts, tmp1, "v1")
            
            # V2: Mutated
            mutated_dicts = mutator_func(self.baseline_events)
            self._run_pipeline(mutated_dicts, tmp2, "v2")
            
            # Profile both
            duck = DuckDBClient()
            duck.register_parquet_view("v1_view", os.path.join(tmp1, "*.parquet"))
            duck.register_parquet_view("v2_view", os.path.join(tmp2, "*.parquet"))
            
            profiler = DatasetProfiler(duck)
            snap_a = profiler.profile_view("dataset", "v1_view")
            snap_b = profiler.profile_view("dataset", "v2_view")
            
            duck.close()
            
            # Compare
            events = self.engine.compare(snap_a, snap_b)
            detected_types = {e.change_type for e in events}
            
            detected = expected_type in detected_types
            
            return {
                "scenario": name,
                "expected": True,
                "detected": detected,
                "correct": detected,
                "all_detected_types": [e.value for e in detected_types]
            }

    def run_all(self):
        scenarios = [
            ("type_drift", ChangeType.TYPE_CHANGE, inject_type_drift_player_id),
            ("column_addition", ChangeType.COLUMN_ADDED, inject_column_addition),
            ("column_removal", ChangeType.COLUMN_REMOVED, inject_column_removal),
            ("nullability_drift", ChangeType.NULLABILITY_CHANGE, inject_nullability_drift),
            ("statistical_drift", ChangeType.STATISTICAL_DRIFT, inject_statistical_drift)
        ]
        
        results = []
        for name, expected_type, func in scenarios:
            res = self.evaluate_scenario(name, expected_type, func)
            results.append(res)
            
        return results
