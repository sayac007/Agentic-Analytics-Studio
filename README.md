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
Task 00 now proposes audited file contracts and a hand-authored synthetic fixture.
No MMM engine, observed Tesla dataset, MCP server or successful remote CI is claimed.
External source retrieval and Kinderwelt inspection remain blocked; see
[Audit](docs/AUDIT.md), [Source catalog](docs/SOURCE_CATALOG.md),
[Decisions](docs/DECISIONS.md), and [Contracts](contracts/README.md).

From repository root with Python >=3.11 and `jsonschema==4.26.0`:

```sh
python3 contracts/validate.py
python3 -m unittest discover -s tests -v
```

These validate contracts only. Task 01 requires human review and approval.
