# Task 01I.3 — public implementation status only

Scope: private retrospective exploratory Tesla/diesel/FX study, authorised by the
separate user workorder. This is not Task 01J or a change to Task 01G. No empirical
values, coefficients, p-values, RMSE, charts, effective-sample tables or identifying
private paths are included in this public report or PR.

## Frozen before execution

The [protocol](SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md) was committed alone in
`94d013ab1e2b623899641760d9524ac8f3ed59e9`, before a real join, plot, correlation or fit.
SHA-256: `429bca69a59d978bf2bb038a358dfd21bffd36ad1b21c66ca03214ed22ba7376`.
Runtime checks its original commit, exact current bytes and separate
[scope authorisation](../workorders/01i3-scoped-energy-econometrics.md) hash.
Methodological choices stay in that immutable document; this status page may change.

## Admission preflight

PR #18 merge `2f644e4ba85731aef023a82b4378043f52c1f00b` is included. Existing private
ECB and qualified EC permits and raw/native/monthly bindings were located and checked,
including human decision evidence, attribution, qualifications and unresolved scope
limits. KBA's unchanged Tesla all-powertrain source passed its retrospective audit;
this workorder authorises observed-outcome research, without changing historical
as-of/causal status. Brent is not admitted and no Brent data file is read. No 2026
outcome or energy appendix is included. No source status or permit was rewritten.

## Implemented methods

- One-to-one fixed calendar, original units, exact missingness, calendar differences
  and lag direction; no filling or compression of missing months.
- Source-separated samples, month indicators/trend, one energy predictor per model,
  fixed lag grid and single prespecified transformation robustness alternative.
- OLS with corrected three-**calendar**-month Newey–West covariance, conditional normal
  intervals and full prespecified Holm family. Calendar gaps are not consecutive rows.
- Longest-contiguous-segment ACF/PACF and fixed ADF/KPSS, explicit nulls/warnings and
  fixed calendar-baseline CUSUM caveat. No test-driven specification changes.
- Fixed lag-1 retrospective 2025 conditional pseudo-holdout; training-only fitting,
  paired baseline comparison, no real-time/as-of/causal claim or lag optimisation.
- All fits, missingness, warnings, null/negative outcomes and not-estimable cases
  retained privately. Confounding/qualified-source limitations stay explicit.

## Reproduction

Python 3.12, existing pinned `requirements-attention.lock`, no new dependency:

```sh
python -m unittest discover -s tests -p test_scoped_energy.py -v
python tests/fixtures/scoped_energy/generate.py --output /tmp/NEW-SYNTHETIC-input
python -m fuel_oil.scoped_study --fixture \
  --energy-dir /tmp/NEW-SYNTHETIC-input/energy \
  --permits-dir /tmp/NEW-SYNTHETIC-input/permits \
  --kba /tmp/NEW-SYNTHETIC-input/SYNTHETIC_kba.csv \
  --output /tmp/NEW-SYNTHETIC-results
```

An actual admitted-source run uses the existing private energy and permit directories:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m fuel_oil.scoped_study \
  --energy-dir /PRIVATE/verified-energy-input \
  --permits-dir /PRIVATE/source-admissions \
  --output /PRIVATE/NEW-scoped-study
```

Real mode accepts only the repository's audited KBA file. Private input/permit
hashes must match the merged matrix and source snapshot. Synthetic mode has its own
manifest/permits and rejects mixed real inputs. No raw energy download, real Trends
file, extra source or public-output option exists. Use a fresh output outside Git;
repository/symlink output and overwrite are refused. Gate errors stop before numeric
outcome parsing or completed output. Full commit history in CI supports the explicit
protocol-commit check; all study executions in CI use synthetic inputs only.

Private outputs are `results.json`, `samples.json`, `associations.csv`, `report.md`,
`provenance.json`, four PNGs and a final hash manifest. Provenance retains source/
permit/protocol/code/KBA hashes, exact units, credits, constraints and runtime versions,
without exposing input paths. The private report includes all predeclared estimates
and error comparisons, not a selected successful result. These files are not public
artifacts. Workspace paths are not ChatGPT downloads; use only an authorised private
workspace export facility if available. No export to a public destination is performed.

## Observed execution status

**A real admitted-source private study actually ran and completed**, after protocol
commit `94d013ab1e2b623899641760d9524ac8f3ed59e9` and implementation commit
`536491526672b13e9de5980d9867f22d9c13aef7`. Existing ECB and qualified EC source
permits plus KBA retrospective/source-rights checks passed before outcome parsing.
The only study scope was Task 01I.3. Neither Task 01J nor the frozen Task 01G was run
or altered. No real coefficients, diagnostics, associations, prediction errors or
numerical effective-sample outputs are reported here.

A second real execution reproduced **all ten** private output files byte-for-byte,
including the hash manifest. An explicit filesystem read guard refused unadmitted
Brent raw/normalized file names during that replay and passed. Output period bounds,
source set, exact diesel missingness and manifest checks passed. Current source
vintages, credits, qualified EC limitations, missingness and no-public/no-as-of
restrictions are retained in private provenance/report files. Source inputs,
source permits and KBA observations remain unchanged. All predeclared results,
including non-estimable/null/negative cases if present, are retained without tuning.

Private results are workspace-only. An authorised workspace terminal or private
export facility, if available, can access them; no ChatGPT download or public export
is claimed. Actual private paths and numerical findings are not committed.

## Executed software verification

Pinned Python 3.12 environment, existing dependencies:

- Full suite: **310 tests passed**, 50.221 s (294 prior + 16 scoped-study tests).
- Targeted scoped suite: **16 passed**, 9.898 s; all software-test data synthetic.
- Both contract examples, KBA audit, source-rights check, Ruff import/format,
  whitespace and protected-source/protocol checks passed.
- Synthetic-only end-to-end smoke completed. Numerical tests include a hand OLS
  example, corrected HAC agreement with statsmodels on contiguous months, manually
  checked gapped-calendar score pairs, lag/missingness and holdout-training isolation.
- Real execution/replay is separate private empirical work, not evidence from
  software fixtures or scientific/causal validation.

Remote CI conclusions/links are recorded in the Draft PR only after observed
completion at its exact head. CI never receives real private energy inputs/results.
