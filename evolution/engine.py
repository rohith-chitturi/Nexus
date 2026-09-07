from typing import Dict, List

from evolution.models import ChangeType, EvolutionEvent, Severity
from evolution.policy import DriftPolicy
from evolution.snapshot import DatasetSnapshot


class EvolutionEngine:
    """
    Deterministically compares two DatasetSnapshots and emits EvolutionEvents.
    """
    def __init__(self, policy: DriftPolicy = None):
        self.policy = policy or DriftPolicy.default_policy()

    def compare(self, snapshot_a: DatasetSnapshot, snapshot_b: DatasetSnapshot) -> List[EvolutionEvent]:
        events = []
        
        schema_a = {col.column: col for col in snapshot_a.schema_def}
        schema_b = {col.column: col for col in snapshot_b.schema_def}
        
        stats_a = snapshot_a.statistics
        stats_b = snapshot_b.statistics

        # 1. Detect Column Removals
        for col_name in schema_a:
            if col_name not in schema_b:
                events.append(self._build_event(
                    snapshot_a, snapshot_b,
                    ChangeType.COLUMN_REMOVED,
                    Severity.CRITICAL,
                    [col_name],
                    {"previous_type": schema_a[col_name].data_type}
                ))

        # 2. Detect Column Additions & Type/Nullability changes
        for col_name, col_b in schema_b.items():
            if col_name not in schema_a:
                events.append(self._build_event(
                    snapshot_a, snapshot_b,
                    ChangeType.COLUMN_ADDED,
                    Severity.INFO,
                    [col_name],
                    {"new_type": col_b.data_type}
                ))
            else:
                col_a = schema_a[col_name]
                
                # Type Change
                if col_a.data_type != col_b.data_type:
                    events.append(self._build_event(
                        snapshot_a, snapshot_b,
                        ChangeType.TYPE_CHANGE,
                        Severity.HIGH,
                        [col_name],
                        {"previous_type": col_a.data_type, "current_type": col_b.data_type}
                    ))
                
                # Nullability Change
                if not col_a.nullable and col_b.nullable:
                    events.append(self._build_event(
                        snapshot_a, snapshot_b,
                        ChangeType.NULLABILITY_CHANGE,
                        Severity.MEDIUM,
                        [col_name],
                        {"previous_nullable": col_a.nullable, "current_nullable": col_b.nullable}
                    ))

                # Cardinality Change
                if col_a.cardinality is not None and col_b.cardinality is not None:
                    delta = abs(col_b.cardinality - col_a.cardinality)
                    if delta > self.policy.cardinality_delta_threshold:
                        events.append(self._build_event(
                            snapshot_a, snapshot_b,
                            ChangeType.CARDINALITY_CHANGE,
                            Severity.LOW,
                            [col_name],
                            {"previous_cardinality": col_a.cardinality, "current_cardinality": col_b.cardinality, "delta": delta}
                        ))

        # 3. Detect Statistical & Null Rate Drift
        for col_name, stat_b in stats_b.items():
            if col_name in stats_a:
                stat_a = stats_a[col_name]
                
                # Null Rate Change
                null_delta = stat_b.null_rate - stat_a.null_rate
                if null_delta > self.policy.null_rate_delta_threshold:
                    events.append(self._build_event(
                        snapshot_a, snapshot_b,
                        ChangeType.NULL_RATE_CHANGE,
                        Severity.HIGH,
                        [col_name],
                        {"previous_null_rate": stat_a.null_rate, "current_null_rate": stat_b.null_rate, "delta": null_delta}
                    ))

                # Statistical Drift (Mean)
                if stat_a.mean is not None and stat_b.mean is not None and stat_a.mean != 0:
                    rel_change = abs(stat_b.mean - stat_a.mean) / abs(stat_a.mean)
                    if rel_change > self.policy.relative_mean_change_threshold:
                        events.append(self._build_event(
                            snapshot_a, snapshot_b,
                            ChangeType.STATISTICAL_DRIFT,
                            Severity.MEDIUM,
                            [col_name],
                            {"metric": "mean", "previous_mean": stat_a.mean, "current_mean": stat_b.mean, "relative_change": rel_change}
                        ))

        return events

    def _build_event(self, a: DatasetSnapshot, b: DatasetSnapshot, ctype: ChangeType, sev: Severity, cols: List[str], evidence: Dict) -> EvolutionEvent:
        return EvolutionEvent(
            dataset_id=a.dataset_id,
            from_snapshot_id=a.snapshot_id,
            to_snapshot_id=b.snapshot_id,
            change_type=ctype,
            severity=sev,
            affected_columns=cols,
            evidence=evidence
        )
