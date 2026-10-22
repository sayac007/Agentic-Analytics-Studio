# Task 00 audit — 2026-10-22

This is an audit and contract proposal, not an MMM implementation. Local checks below
are observed evidence. External source contents, remote CI and unavailable reference
projects remain explicitly **NOT VERIFIED**. Task 01 needs human approval.

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

Public repository identities were discovered through
<https://github.com/sayac007?tab=repositories>, retrieved with HTTP 200, then cloned
read-only using the existing HTTPS Git access. They are temporary audit checkouts,
not dependencies or additions to environment repository membership.

| Repository | Local inspection path | Commit / declared version | License and evidence | Reuse decision |
|---|---|---|---|---|
| [WKR](https://github.com/sayac007/-wkr-automotive-forecasting-lab) | `/tmp/task00-references/-wkr-automotive-forecasting-lab` | `071056370247ac58bfd29a67b47482bd3143617c` / 0.1.0 | No root LICENSE found; pyproject has no license declaration; 5 local tests passed | Patterns only; do not copy code or data without rights review |
| [HypoForge Python](https://github.com/sayac007/HypoForge-Python) | `/tmp/task00-references/HypoForge-Python` | `c47f636d24a39a820574a13133d6af693134a180` / 0.4.0 | Apache-2.0 in LICENSE and pyproject; 22 local tests passed plus numerical probes | Prefer exact-commit dependency for Task 01, with explicit adapter validation |
| [HypoForge R](https://github.com/sayac007/HypoForge-R) | `/tmp/task00-references/HypoForge-R` | `1ba1546239e18c28518caed6fb52e3595951be0a` / 0.2.0 | Apache license text; DESCRIPTION says Apache License (>= 2); runtime tests NOT VERIFIED | Source API compatible in concept; runtime parity pending |
| Kinderwelt | Not mounted; no identity found on the inspected profile pages | NOT VERIFIED | License, APIs and tests NOT VERIFIED | Apply the principle already documented in this repository; no claim of an upstream audit |

Kinderwelt snapshot/URL was requested. Temporary paths are evidence locations in this
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
| KBA, Tesla, Google Trends help, GitHub API HTTPS probes | Proxy CONNECT denied, HTTP 403; source contents not retrieved |
| `gh auth status` | Could not verify injected GH_TOKEN; do not infer Git write/API authorization from Git read success |
| Remote CI | CI: awaiting maintainer verification; no remote test-run claim |

## Open requirements

- Enable required research domains in environment settings and repeat source retrieval.
  A network-only configuration draft was saved; it preserves the package-manager
  preset and adds `www.kba.de`, `www.tesla.com`, `support.google.com`,
  `trends.google.com`, `api.github.com`, `adstransparency.google.com`,
  `www.facebook.com`, `www.dwd.de`, and `www.bafa.de`. Review/save and publish are
  separate from this draft save; no runtime activation is claimed.
- Supply Kinderwelt's exact repository URL or a permitted snapshot.
- Verify KBA release/vintage, Tesla brand row, coverage and exact reuse terms before
  committing any observed data. Source catalog remains a blocked research ledger.
- Approve Task 00 contracts and Python-first choice before Task 01. Passing contract
  checks do not approve implementation or establish benchmark recovery performance.
