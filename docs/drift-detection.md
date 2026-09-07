# Deterministic Drift Detection

NEXUS uses a rigorous deterministic engine to identify data evolution before engaging any LLMs.

## Drift Policy
The engine compares snapshots based on the `DriftPolicy`. It prevents minor statistical noise from triggering events while ensuring legitimate evolution is recorded.
- **relative_mean_change_threshold**: e.g., `0.10` (10%)
- **null_rate_delta_threshold**: e.g., `0.05` (+5% absolute)
- **cardinality_delta_threshold**: e.g., `100`

*These values are engineering baselines and can be overridden.*

## Severity Classification
Events are explicitly classified without an LLM:
- **CRITICAL**: Contract-breaking changes (e.g., column removed).
- **HIGH**: Type changes or massive null-rate spikes.
- **MEDIUM**: Detectable statistical drift violating policy.
- **LOW**: Minor cardinality changes.
- **INFO**: Non-breaking additions (e.g., column added).

## Evaluation
The `DriftEvaluator` executes the pipeline end-to-end to measure True Positives and False Positives. It injects known changes (e.g. `player_id: integer -> string`) into baseline telemetry and asserts the `EvolutionEngine` emits the exact corresponding `EvolutionEvent`.
