# Contract and numerical tests

Install `requirements-kba.lock` in Python 3.12, then run from repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests -v
```

The original 49 contract tests retain their traversal/hash/provenance/CSV/split and
statistical-boundary coverage. `test_synthetic_mmm.py` adds actual generation,
numerical OLS/HAC checks, HypoForge values, history, failure handling, process
isolation, hash-bound end-to-end verification and full-bundle deterministic repetition.
The analytical HAC example is documented in `docs/RUN_SYNTHETIC_MMM.md`.

Legacy file graphs are labeled `contract_fixture` and never claimed as model outputs.
The new pipeline tests use the actual `development_benchmark` protocol, without any
assertion that beta recovery must be good. No real-data or Monte Carlo experiment is
run. CI adds a separate Stage-A smoke generation/verification after the unittest suite.
Actual remote CI results belong to the exact Actions run linked in the PR.

Task 01B adds offline KBA table-layout, provenance/hash, month/brand/BEV, revision,
coverage/admission, selection, reconciliation and deterministic-extraction tests.
XLSX fixtures are explicitly transformed table-only snapshots with separate original
and fixture hashes; they cannot be fetched as original data or admitted as benchmarks.
The full normalized-data audit is separate from raw re-extraction. CI never downloads
live KBA data. See `docs/KBA_MULTIBASELINE.md` for full-cache reproduction.
