# Architecture Decision Records (ADRs)

## ADR-001: Python 3.13 Target
**Status**: Accepted
**Context**: The platform needs to leverage modern Python features for typing, performance, and compatibility.
**Decision**: We will target Python 3.13. Local development may use Python >=3.11 with Docker providing strict 3.13 parity where necessary.

## ADR-002: PostgreSQL as Control-Plane Metadata Store
**Status**: Accepted
**Context**: We need transactional safety, relational integrity for lineage, and semantic capabilities.
**Decision**: Use PostgreSQL (with pgvector) as the primary state backend for the control plane.

## ADR-003: DuckDB for Analytical/Replay Workloads
**Status**: Accepted
**Context**: Replaying data transformations over historical Parquet datasets requires a fast, embedded OLAP engine.
**Decision**: Use DuckDB to handle all analytical profiling and counterfactual replays.

## ADR-004: LangGraph for Agent Orchestration
**Status**: Accepted
**Context**: The investigative and remediation processes involve multiple specialized agents with complex routing and state.
**Decision**: Use LangGraph over single monolithic prompts to build resilient, multi-agent workflows.
