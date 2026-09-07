# NEXUS Architecture

This document describes the intended architecture of the NEXUS platform.

## High-Level Components

### 1. Control Plane (Planned)
- **FastAPI API**: Central orchestration layer
- **PostgreSQL**: Metadata storage, constitution state, approval state
- **Next.js Console**: Engineering UI

### 2. Data Engine (Planned)
- **Ingestion**: Kafka-based telemetry ingest
- **Profiling**: Deterministic extraction of schemas and stats
- **Replay**: DuckDB-based historical counterfactual testing
- **DuckDB Analytical Layer**: Provides lightweight `read_parquet` capabilities without moving data, extracting structural and statistical profiles.
- **Data Evolution Engine**: Compares `DatasetSnapshots` deterministically based on a `DriftPolicy`, emitting structured `EvolutionEvents` to the `EvolutionRegistry`.

### 3. Agent System (Planned)
Built on LangGraph to coordinate specialized agents:
- **Observer Agent**: Monitors incoming profiles
- **Schema/Quality/Semantic Agents**: Specialized drift detectors
- **Agentic Investigator (Phase 3+)**: LLM agents consume `EvolutionEvents` and lineage data to generate hypotheses. transforms/fixes
- **Validator Agent**: Static and dynamic checks of proposals

### 4. Lineage Graph (Planned)
- Maps producers -> datasets -> transformations -> downstream consumers.

*Currently, only the repository foundation (Phase 0) is implemented. The components above will be built incrementally.*
