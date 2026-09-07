# NEXUS Data Model

This document outlines the core deterministic structures underlying the Data Evolution Engine.

## DatasetSnapshot
Represents the structural and statistical state of a dataset at a point in time.
- **snapshot_id**: Unique ID.
- **schema_def**: List of `ColumnSchema` detailing types, nullability, and cardinality.
- **statistics**: Numeric properties such as mean, variance, min, max, and null_rates.

## DataConstitution
The formal contract defining what the dataset *should* look like.
- **expected_schema**: The contracted schema.
- **baseline_statistics**: Expected baselines.

## EvolutionEvent
Represents a calculated delta between two snapshots. This structured evidence serves as ground-truth for future AI investigators.
- **change_type**: (e.g. `COLUMN_ADDED`, `TYPE_CHANGE`, `STATISTICAL_DRIFT`)
- **severity**: `INFO` to `CRITICAL`.
- **evidence**: A strictly structured dictionary explaining exactly what changed (e.g., `{"previous_mean": 42.1, "current_mean": 187.4}`).
