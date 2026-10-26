# When does an MMM reliably recover a media effect?

A reproducible synthetic benchmark with known ground truth: 1,000 seeds per cell, 18 cells, two fixed models and 36,000 fits. No real campaign data, causal ROI or outcome-based tuning.

![Nominal rejection rates and Monte Carlo intervals](examples/research-task02/power.png)

## Detection thresholds by design — not validated MDE

| Spend design | Confounding | Calendar model | Smallest tested effect reaching 80% rejection | Null false positives |
|---|---|---|---|---:|
| always_on | independent | with-quarter | not reached (3/8/15%) | 14.9% |
| always_on | independent | without-quarter | not reached (3/8/15%) | 11.8% |
| always_on | calendar_aligned | with-quarter | not reached (3/8/15%) | 13.6% |
| always_on | calendar_aligned | without-quarter | 8% | 53.2% |
| flighting | independent | with-quarter | 8% | 12.4% |
| flighting | independent | without-quarter | 8% | 9.5% |
| flighting | calendar_aligned | with-quarter | 8% | 13.3% |
| flighting | calendar_aligned | without-quarter | 3% | 48.0% |

These are exploratory **tested-grid crossings, not validated MDEs**. The grid is 3%, 8%, 15%; no interpolation. Every design has inflated null rejection and/or undercoverage. An apparently low threshold under confounding can be a false-positive problem. Positive-detection thresholds and Monte Carlo Wilson bounds are retained in the CSVs.

## What the experiment shows

- **Always-on can miss the planted effect.** In the legacy 8% design, correct positive detection is 4.4%; nominal two-sided rejection is 9.5% (Monte Carlo SE 0.93 percentage points). Its null false-positive rate is 16.6%, so the anticipated near-5% two-sided operating characteristic is not reproduced.
- **Flighting improves recovery in this benchmark.** At 8%, independent flighting reaches 99.3% positive detection (MCSE 0.26 pp); median estimated/planted beta is 0.977. Yet interval coverage is only 87.6%, not 95%.
- **Significance is not identification.** Calendar-aligned media without the quarter-end control produces 53.2% / 48.0% null false positives (always-on / flighting). A small engineering condition number and agreement between two bad estimates do not establish recovery.
- **The original negative estimates now trigger warnings.** Both Task01a seed42 fits receive not_identified, sign_uncertain and extrapolated_counterfactual in the new-stage evaluation. Their original files remain unchanged. SNR for that original seed is 0.124840.

| Design at 8% mean effect | Median SNR | Positive detection | Null false positives | 95% interval coverage |
|---|---:|---:|---:|---:|
| Legacy always-on, fixed k=100 | 0.138 | 4.4% | 16.6% | 83.4% |
| Always-on, train-relative k | 0.235 | 11.1% | 14.9% | 85.1% |
| Flighting, independent | 1.242 | 99.3% | 12.4% | 87.6% |
| Flighting, calendar-aligned | 1.378 | 93.1% | 13.3% | 86.7% |

Primary table uses the with-quarter model. “Positive detection” means lower interval bound >0; null false positives use two-sided rejection. These are different quantities.

## Reproduce

Python 3.12, Git and the pinned runtime:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-attention.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m research_benchmark.run --output artifacts/research-task02
.venv/bin/python -m research_benchmark.verify artifacts/research-task02
```

Read the [full results report](examples/research-task02/report.md), [summary CSV](examples/research-task02/summary.csv), [grid thresholds](examples/research-task02/mde.csv) and [preregistered protocol](benchmarks/task02/PROTOCOL.md).
Successful **Synthetic identifiability research** Actions runs export complete seed-level truth/evaluations for 30 days. The committed presentation subset is derived from a verified full run; it is not the full 36,000-row data bundle.

## Limits

All findings are conditional on this synthetic baseline, spend/noise design, oracle transforms and finite-sample HAC intervals. They do not establish causal effects of real marketing, general power or reliable real-data inference.

## Appendix and earlier work

- [Scientific implementation and isolation](docs/IDENTIFIABILITY_RESEARCH.md)
- [Data sources and private acquisition limits](DATA_SOURCES.md)
- [Architecture](docs/ARCHITECTURE.md), [data policy](docs/DATA_POLICY.md), [statistical contracts](docs/STATISTICAL_CONTRACTS.md)
- [Earlier project milestones and commands](docs/PROJECT_HISTORY.md)
- [Local synthetic demo](docs/LOCAL_DEMO.md) is optional infrastructure; the scientific benchmark needs no UI, cloud account or model key.

One focused PR per package; no automatic merge. Real-data models, Bayesian extensions and additional integrations are outside these results.
