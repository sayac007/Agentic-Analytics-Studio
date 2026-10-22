# Agentic Analytics Studio

An incremental, auditable MMM and agent-orchestration research project. **This repository starts as a task-oriented project scaffold, not a functioning MMM engine.**

## First milestone
A semi-synthetic Tesla Germany benchmark: observed monthly registration data retained unchanged; a separately labeled generated outcome injects a known media effect through adstock + Hill. Fit a simple `lm`-style baseline, run twice, compare diagnostics, expose one minimal MCP tool, and write a Markdown report. The benchmark must not claim real Tesla marketing effectiveness.

## Getting started with Codex
1. Give Codex access to this repository.
2. Ask it to read `AGENTS.md` and complete **only** `workorders/00-audit-and-contracts.md` in one PR.
3. Review and merge after checking evidence. Then assign `workorders/01-walking-skeleton.md`.
4. Keep five workstreams visible in `docs/ROADMAP.md`, but deliver one coherent increment at a time.

## References
- WKR Automotive Forecasting Lab — engineering patterns; access must be verified.
- HypoForge R and Python — reusable analytical transforms; inspect actual exported API before use.
- Kinderwelt — incremental delivery, regression testing and honest QA evidence.

## Status

Task 00.5 proposes statistical file contracts v0.2.0: private reference/truth are
separate from estimator inputs, with explicit uncertainty, contribution, response
and recovery outputs. No MMM engine, generated benchmark, MCP server or real Tesla
marketing effect is claimed. See [Statistical contracts](docs/STATISTICAL_CONTRACTS.md),
[Readiness](docs/TASK_01_READINESS.md), [Source evidence](docs/SOURCE_CATALOG.md)
and [Validation](contracts/README.md).

From repository root, Python 3.12 and `jsonschema==4.26.0`:

```sh
python3 contracts/validate.py
python3 contracts/validate.py contracts/examples/generator.json --kind generator
python3 -m unittest discover -s tests -v
```

The six-row examples test contracts, not model recovery. GitHub Actions runs the same
checks on push and pull request. Task 01 needs human authorization; only synthetic
Stage A has a proposed complete development path, while real-data admission and
Stage B/C scientific choices remain explicit.
