# Agentic Analytics Studio

An auditable, incremental marketing-mix modelling research project. **Task 01a now
runs a fully synthetic Stage-A benchmark**, with an intentionally difficult baseline,
known media transformations and honest recovery diagnostics. It is not evidence of
real Tesla advertising effectiveness.

## Run the synthetic pipeline

Python 3.12 and Git are required. From repository root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-kba.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m studio run --output artifacts/task01a-run1
.venv/bin/python -m studio verify artifacts/task01a-run1
```

Choose a new output directory for each run. Both include/omit-quarter-end models use
the same 72-month synthetic dataset, 60/12 split, fixed oracle transforms and common
spend grid. No parameters are searched and no fit is tuned to improve recovery.

Read [Run instructions and limitations](docs/RUN_SYNTHETIC_MMM.md),
[Statistical Contracts v0.2.0](docs/STATISTICAL_CONTRACTS.md),
[Readiness](docs/TASK_01_READINESS.md), and the generated
[Example report](examples/task-01a/report.md).

## Validate

```sh
.venv/bin/python contracts/validate.py
.venv/bin/python contracts/validate.py contracts/examples/generator.json --kind generator
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -v
```

CI runs these checks plus an end-to-end smoke test. The estimator runs in a fresh
process/directory without private reference/truth files; those are available only to
generation/evaluation. All output hashes and implementation/runtime identities are
saved. The example has poor recovery, which remains visible rather than corrected.

## Scope

No observed-baseline MMM execution, transform search, scenario grid, Bayesian model, geo-test, UI
or MCP server is included. No empirical power, validated MDE, actual 95% coverage or
real causal marketing ROI is claimed. WKR, HypoForge and Kinderwelt remain independent;
HypoForge is consumed only as a dependency pinned to its audited Git commit.

See [Source audit](docs/SOURCE_CATALOG.md) and [Contracts](contracts/README.md).

Task 01B adds [verified KBA multi-baseline acquisition](docs/KBA_MULTIBASELINE.md)
and a [future paired recovery protocol](docs/MULTIBASELINE_RECOVERY_PROTOCOL.md).
Tesla/Toyota/VW each have 96 verified consecutive months; the explicit BEV total has
60. All remain blocked from benchmark admission pending exact publication evidence
or a reviewed date-precision contract extension. Run `python -m kba audit` offline.
