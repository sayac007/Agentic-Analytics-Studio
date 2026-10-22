# Task 00 audit — 2026-10-22

This is an audit and contract proposal, not an MMM implementation. Local checks below
are observed evidence. Unretrieved source contents, remote CI and unexecuted runtime checks
remain explicitly **NOT VERIFIED**. Task 01 needs human approval.

## Repository and architecture

Audited base: `sayac007/Agentic-Analytics-Studio` at
`8d7a06c80e85d8ea127dda95856250581c9c966e`. Read `AGENTS.md`, `README.md`,
`docs/ARCHITECTURE.md`, `docs/DATA_POLICY.md`, and Task 00 before editing.
There were no pre-existing local changes. The base has documentation placeholders,
no estimator, dependency manifest, dataset, server, or executable CI workflow.

The five workstreams can meet at versioned files: Data Hub supplies immutable
reference data and per-column provenance; the generator produces separate exposure,
outcome and evaluator-only truth; the estimator consumes only its manifest and CSV;
the evaluator/comparator consumes results and truth; reporting and a future read-only
MCP tool consume validated saved comparisons. No free-form LLM output becomes a
statistic. Contracts now specify this boundary; none of those services is implemented.

## Reference inspection and exact revisions

WKR/HypoForge repository identities were discovered through
<https://github.com/sayac007?tab=repositories>, retrieved with HTTP 200; Kinderwelt
was subsequently found with `gh repo list sayac007 --limit 100 --json name,url`.
All four were cloned read-only using the existing HTTPS Git access. They are temporary audit checkouts,
not dependencies or additions to environment repository membership.

| Repository | Local inspection path | Commit / declared version | License and evidence | Reuse decision |
|---|---|---|---|---|
| [WKR](https://github.com/sayac007/-wkr-automotive-forecasting-lab) | `/tmp/task00-references/-wkr-automotive-forecasting-lab` | `071056370247ac58bfd29a67b47482bd3143617c` / 0.1.0 | No root LICENSE found; pyproject has no license declaration; 5 local tests passed | Patterns only; do not copy code or data without rights review |
| [HypoForge Python](https://github.com/sayac007/HypoForge-Python) | `/tmp/task00-references/HypoForge-Python` | `c47f636d24a39a820574a13133d6af693134a180` / 0.4.0 | Apache-2.0 in LICENSE and pyproject; 22 local tests passed plus numerical probes | Prefer exact-commit dependency for Task 01, with explicit adapter validation |
| [HypoForge R](https://github.com/sayac007/HypoForge-R) | `/tmp/task00-references/HypoForge-R` | `1ba1546239e18c28518caed6fb52e3595951be0a` / 0.2.0 | Apache license text; DESCRIPTION says Apache License (>= 2); runtime tests NOT VERIFIED | Source API compatible in concept; runtime parity pending |
| [Kinderwelt](https://github.com/sayac007/Kinderwelt) | `/tmp/task00-references/Kinderwelt` | `d65ed9fd122b00f72ccd917916c3fa0a177f7c8e` / 0.6.0 | Root MIT license for foundation software; separate asset licenses; 16 packaging-verification tests passed locally | Reuse QA/evidence patterns, no app/assets copied |

Kinderwelt identity was initially requested, then resolved through the working GitHub CLI.
The similarly named private variant was not inspected. Temporary paths are evidence locations in this
instance, not durable installation instructions. Reproduce with clones at the exact
commits above, not their moving default branches. No upstream files were changed.

## Actual transform APIs

Python `src/hypoforge/__init__.py` exports `FeatureSpec` and
`evaluate(spec: FeatureSpec, df: pandas.DataFrame) -> pandas.Series`.
`FeatureSpec(name, op, inputs, params=(), kind='numeric', lookback=0, complexity=1)`
is a frozen dataclass; `inputs` and `params` are tuples. There is **no top-level
standalone `hill()` export**. Verified invocation:

```python
from hypoforge import FeatureSpec, evaluate
from hypoforge.media import geometric_adstock
spec = FeatureSpec('h', 'hill', ('x',), (('k', 4.0), ('n', 2.0)))
# evaluate(spec, DataFrame({'x': [0., 4., 8.]})) -> [0., .5, .8]
# geometric_adstock([1, 0, 0], alpha=.5, l_max=2, normalize=False)
# -> [1., .5, .25]
```

The module-level public function is
`geometric_adstock(x, alpha=0.5, l_max=8, *, normalize=True)`.
It returns a Series, includes lag zero through `l_max`, normalizes using available
history by default, and silently treats NA exposure as zero. Our contract rejects
missing exposure before calling it and explicitly selects `normalize=False`.
The Hill branch uses `x**n / (k**n + x**n)`, requires positive k/n and maps negative
x to NA. Validate finite, nonnegative exposure first; no automatic overflow safety
is claimed. `generate_candidates()` can derive thresholds/k from the supplied data:
do not run it on the entire train-plus-test dataset.

R `NAMESPACE` exports `hf_spec(name, op, inputs, params=list())`,
`hf_evaluate(spec, data)` and
`hf_geometric_adstock(x, alpha=.5, l_max=8L, normalize=TRUE)`.
Hill lives in `hf_evaluate(hf_spec('h','hill','x',list(k=4,n=2)), data)`;
there is no exported `hf_hill`. Source inspection shows the same Hill formula and
finite geometric kernel, but different parameter validation: the R Hill branch does
not explicitly enforce positive k/n. No cross-language numerical equivalence is
claimed. `tests/testthat/test-core.R` has identity/lag, rolling split and tournament
checks; it does not establish Hill/adstock parity.

WKR useful design seams: `calendar_pipeline.validate(rows, start, end)`,
`compare(rows, legacy_path, output_dir)`, and the file-based pipeline entry points;
`docs/calendar_parity.md` and `docs/decisions/0002-r-reference-python-engineering.md`
separate R reference behavior from Python engineering. WKR `metrics(actual,
predicted)` is sales/EUR oriented, not a drop-in registration metric contract.
Its calendar demand windows are modelling assumptions, not simply public-holiday
flags. Its data-source document explicitly leaves extraction vintages, VDA attribution
and DWD aggregation unresolved. Do not relabel those files as verified Tesla data.

Kinderwelt inspected files: `README.md`, `tests/run.sh`,
`tests/android/test_verification.py`, `docs/test-report.md`, `docs/test-evidence.json`
and root `LICENSE`. The runner uses `set -euo pipefail`, isolated temporary state,
checks process exit codes **and** error text, imports a fresh shipping-files-only copy,
and exercises boot and regression tests. The packaging tests reject modified/missing/
duplicate data, permission drift, development files and invalid ELF alignment. The
report separates desktop renders from device tests and historical evidence from
unverified remote CI. These are useful patterns for immutable data hashes, clean
runs, negative fixtures and scoped statistical claims here. Historical upstream
counts in that report were read, not reproduced. Only the 16-test packaging subset
was executed locally; no Godot/Android build or render validation is claimed.

## Executed checks

Current runtime: Python 3.12.14; R/Rscript absent. `jsonschema` 4.26.0 was available.
An isolated `/tmp/task00-venv` with system-site packages was used for reference tests;
pytest 9.1.1, numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0,
scipy 1.17.0, statsmodels 0.15.0 and matplotlib 3.10.8 were observed.
Initial reference test prerequisite check failed because pytest was absent; it was
installed in that temporary environment. An initial HTTP probe using `requests`
failed because requests was absent; research probes then used stdlib urllib.

| Command / check | Observed outcome |
|---|---|
| `git ls-remote origin HEAD` | Read access works; HEAD matched audited base at time of check |
| `PYTHONPATH=/tmp/task00-references/HypoForge-Python/src /tmp/task00-venv/bin/python -m pytest -q /tmp/task00-references/HypoForge-Python/tests` | 22 passed |
| `PYTHONPATH=/tmp/task00-references/-wkr-automotive-forecasting-lab/src /tmp/task00-venv/bin/python -m pytest -q /tmp/task00-references/-wkr-automotive-forecasting-lab/tests` | 5 passed; not live API/source reconciliation tests |
| HypoForge numerical probes shown above, using `numpy.testing.assert_allclose` | Both passed |
| `python3 -m unittest discover -s tests -v` | 13 contract tests passed, including negative cases |
| `python3 contracts/validate.py` | Valid manifest and CSV, 6 hand-authored fixture rows |
| R tests and R/Python parity | NOT RUN: no R runtime |
| Initial primary-source/API HTTPS probes | Proxy CONNECT denied, HTTP 403; these failures were later superseded for the successful destinations below |
| Subsequent KBA archive/workbook/license, Tesla DE and Trends help/export-documentation requests | HTTP 200; source contents read, retrieval hashes in `docs/source-evidence.json` |
| KBA FZ 10 January 2025 workbook | Verified `TESLA ZUSAMMEN`, 1,277 registrations and equality to sum of four model rows; this is one month, not a complete series |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/android -p test_verification.py -v` from Kinderwelt checkout | 16 passed; full Godot/Android suites not run |
| Tesla legal/incentives and Meta Ad Library requests | HTTP 403; remaining access limitation |
| Google Trends DE/Tesla explore query | HTTP 429; actual CSV export NOT VERIFIED |
| Google Ads Transparency Center | HTTP 200 application shell only; no advertiser/campaign evidence |
| `gh auth status`, then actual PR/API operations | Status check initially reported failure; subsequent repository listing and PR creation/read succeeded. Actual operations establish those capabilities |
| `git push -u origin audit/task-00-contracts` | Succeeded; branch on origin, targeting main via Draft PR #1 |
| Remote CI | CI: awaiting maintainer verification; no remote test-run claim |

## Remaining review questions and limitations

- Review the proposed contracts, Python-first choice, oracle transform settings,
  condition-number flag and recovery tolerances before approving Task 01.
- KBA workbook and license were verified for January 2025. A full multi-year series
  still needs release-by-release retrieval, vintage tracking and admission checks.
- Tesla's current financing terms are verified as a retrieved snapshot, not historical
  price cuts or a paid advertising campaign. No real campaign spend/ROI is claimed.
- Trends CSV access is rate-limited; campaign-library evidence and Tesla legal pages
  remain incomplete. See the source catalog for precise observed outcomes and rights.
- R runtime and Python/R parity remain unrun. Kinderwelt's full Godot/Android tests
  were not needed for the QA-pattern audit and were not run here.
- A network-only configuration draft was saved with `www.kba.de`, `www.tesla.com`,
  `support.google.com`, `trends.google.com`, `api.github.com`,
  `adstransparency.google.com`, `www.facebook.com`, `www.dwd.de`, and `www.bafa.de`;
  package-manager presets were preserved. Later requests demonstrate current access
  only for their successful destinations; they do not prove every domain works.
  Review/save the changes in environment settings and publish to persist the intended
  configuration version. A draft save alone is not publication.
- [Draft PR #1](https://github.com/sayac007/Agentic-Analytics-Studio/pull/1) targets
  `main` from `audit/task-00-contracts`. It is not merged. Remote CI remains unverified.


## Technical hardening of PR #1

The original 13 tests above describe the first audit snapshot. The hardening pass
retains them and adds 17 focused boundary tests (30 total). The original schemas
were syntactically valid but their end anchors admitted trailing newlines; month
patterns also admitted Unicode digits/year zero, and path patterns allowed dot and
empty components. The CSV reader silently skipped blank records, Python number
parsing admitted noncontract notation, and float rounding could admit a large
fractional registration count. Manifest NaN/Infinity and output-symlink containment
also needed explicit validation. Those cases now have rejection tests.

Executed in a freshly created `/tmp/task00-contract-ci-venv`, Python 3.12.14, with
`python3 -m pip install jsonschema==4.26.0`:

- `python3 contracts/validate.py`: valid manifest/CSV, six rows.
- `python3 -m unittest discover -s tests -v`: **30 tests passed**.
- `git diff --check`: passed.

All 16 existing regex fields in the four schemas are exercised. No scenario,
generator or recovery schemas were added. Reference-project tests were not rerun
in this pass and no upstream files were changed. Statistical readiness is explicitly
separate: see [Task 01 blockers](TASK_01_READINESS.md). Python remains selected;
R parity is not a gate. The proposed workflow runs on both push and pull request;
its remote result must be verified on the actual pushed commit and is reported in
the PR, independently of these local results. PR #1 remains Draft until maintainer
approval; no merge or Task 01 implementation is authorized by successful tests.
