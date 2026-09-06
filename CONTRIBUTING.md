# Contributing to NEXUS

NEXUS is built as a serious, professional-grade platform. We enforce strong engineering standards.

## Engineering Principles
1. **Correctness over speed**: Do not merge without tests.
2. **Deterministic execution**: Use statistical/deterministic methods first; use LLMs for semantic interpretation and synthesis.
3. **Reproducibility**: Counterfactual replays must be isolated and reproducible.

## Git Workflow
We strictly adhere to a GitHub-centric workflow:
1. Create a GitHub Issue for every meaningful feature.
2. Branch from `main` using `feature/<issue-name>`.
3. Keep commits short, meaningful, and logically scoped (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).
4. Create a Pull Request and require code review before merging.
5. Do not push directly to `main`.

## Local Development
- Target Python 3.13 (Docker execution preferred for strict parity).
- Use `uv` for dependency management.
- Ensure all tests pass (`pytest`) and code is formatted (`ruff`).
