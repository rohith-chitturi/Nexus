# NEXUS — Data Evolution & Intelligence Engine

## Problem Statement
Data platforms evolve over time, but tracking exactly *how* and *why* they evolve remains a complex challenge. Uncoordinated schema changes, subtle statistical shifts, and undetected semantic drift can severely compromise downstream ML models, analytics, and business intelligence.

## Motivation
NEXUS aims to solve the problem of opaque data evolution. It goes beyond simple anomaly detection by employing an agentic system that can:
1. Reconstruct historical data platform evolution
2. Distinguish legitimate changes from harmful drift
3. Investigate root causes using a lineage graph
4. Generate and validate remediation strategies through historical replay
5. Support a human-in-the-loop approval workflow

## Architecture Overview
NEXUS is designed as a modular, agent-driven platform.
*(See `ARCHITECTURE.md` for full details)*

## Core Technologies
- **Python 3.13** (Core runtime)
- **PostgreSQL / pgvector** (Metadata and semantic control plane)
- **DuckDB / Parquet** (Analytical engine and replay workload)
- **FastAPI** (Backend APIs)
- **Next.js** (Engineering Console)
- **LangGraph** (Agent Orchestration)

## Current Implementation Status
NEXUS is currently in its initial phase. 

**Implemented**
- Phase 0: Repository Foundation (Docker, CI, Linting, Structure)

**Planned**
- Phase 1: Synthetic Telemetry & Analytical Layer
- Phase 2: Dataset Profiler & Data Constitution
- Phase 3: Evolution Registry
- *(and further agentic/investigative phases)*

## Running Locally (Phase 0)
1. Ensure Docker, Python >=3.11 (3.13 target), and `uv` are installed.
2. Start infrastructure: `docker compose up -d`
3. Install dependencies: `uv pip install -e .[dev]`
4. Run tests: `pytest`
5. Run linting: `ruff check .`
