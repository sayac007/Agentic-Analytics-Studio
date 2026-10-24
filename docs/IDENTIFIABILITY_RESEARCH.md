# Synthetic identifiability research — new task-02 stage

Question: when does an MMM recover a known media effect, and when does it fail?
This new protocol does not rewrite Task01a/01G/01I.3, their contracts or results.
The 1000-seed grid and null controls were committed before new simulations in
`benchmarks/task02/PROTOCOL.md` / `protocol.json`. Expected near-5% legacy rejection
and improved flighting detection are hypotheses, not results to force.

```sh
# Python 3.12, pinned requirements-attention.lock installed
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m research_benchmark.run --output NEW_DIRECTORY
python -m research_benchmark.verify NEW_DIRECTORY
# --smoke uses 20 seeds and is explicitly not scientific power evidence.
```

Each of 18 cells (legacy effect/null plus 12 new effect cells and four null controls)
uses both fixed calendar specifications. Truth/evaluation CSVs preserve SNR,
coefficient/interval, sign, coverage, failures and new flags for every seed.
`summary.csv` reports recovery quantiles, rates, Monte Carlo SE and Wilson intervals.
`mde.csv` reports **tested-grid thresholds only**, separately for two-sided rejection
and positive detection; no continuous/validated MDE. Null size and wrong signs must
be read alongside nominal power. `legacy_flags.csv` re-evaluates original seed42
without overwriting its historical artifacts. `power.png` is the one requested plot.

HypoForge transforms use finite-kernel zero-padding between independent seed series;
unit tests compare with separate seed calls. FWL/QR batch OLS/media HAC is checked
against full NumPy least squares and existing HAC. It executes in a fresh process
containing only estimator-safe y/h arrays and the estimator, with the existing
file-access guard. No generator/B/truth files or source imports are available there.
Only the parent evaluator reads ground truth. No new statistical dependencies.

All runtime/code/protocol/output hashes stay in the data manifest; no extra QA
inventory. Synthetic identifiability research CI produces a full verified artifact
with 30-day retention. Actual findings and CI results are reported in the PR.
No observed data, UI, causal claim, transform search or automatic merge.
