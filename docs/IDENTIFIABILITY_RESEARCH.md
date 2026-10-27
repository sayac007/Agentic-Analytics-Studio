# Synthetic identifiability research — new task-02 stage

Question: when does an MMM recover a known media effect, and when does it fail?
This new protocol does not rewrite Task01a/01G/01I.3, their contracts or results.
The 1000-seed grid and null controls were committed before new simulations in
`benchmarks/task02/PROTOCOL.md` / `protocol.json`. Expected near-5% legacy rejection
and improved flighting detection are hypotheses, not results to force.

```sh
# Python 3.12, pinned requirements-attention.lock installed
# Read and verify the committed original; no fitting or CI download:
python -m research_benchmark.verify results/task02
# Optional separate reproduction, never overwrite the preserved original:
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

## Permanent full results: original CI execution, not a reconstruction

The complete original is versioned in [results/task02](../results/task02/), without
Git LFS or any dependency on Actions artifact retention. Read the
[summary](../results/task02/summary.csv), [grid thresholds](../results/task02/mde.csv),
[original report](../results/task02/report.md) and [figure](../results/task02/power.png)
directly from Git. No simulation, estimator, frozen protocol or output value was
changed for this preservation task.

Inventory before preservation: main `f144c72140285533246f8ca0af6e347beeecb48e`
contained the frozen protocol, implementation and tests, but **no tracked Research
Task 02 result files**. The older portfolio branch at `6143c17` contains a seven-file
presentation subset with a different manifest/report; it is not on this main and
does not contain seed-level truth/evaluations. It cannot pass the full-run verifier.
Complete runs also existed as temporary local copies and expiring CI artifacts.

The latest successful full benchmark available at preservation was
[main run 40478719588](https://github.com/sayac007/Agentic-Analytics-Studio/actions/runs/40478719588).
The full-grid, verification and upload steps were each observed successful. Its
artifact was still available, so **no replacement full execution was necessary**.
Existing CI may execute new regression runs for the preservation PR; those do not
replace or rewrite this archived original.

| Identity | Original evidence |
|---|---|
| Generating source commit | `f144c72140285533246f8ca0af6e347beeecb48e` |
| Protocol | `research-task-02-identifiability`, version `1.0.0`, seeds 0–999 |
| Protocol SHA-256 | `71b84713c9c980db172e7bf5692bc85d9912021f85c5f23701d68df67a4a0723` |
| Original artifact ID | `12721762336` |
| Original artifact name | `synthetic-identifiability-f144c72140285533246f8ca0af6e347beeecb48e` |
| Artifact created | `2026-10-27T09:10:58Z` (10:10:58 Europe/Berlin) |
| Retrieval completed | `2026-10-27T09:25:20.924552Z` (10:25:20.924552 Europe/Berlin) |
| Downloaded artifact ZIP SHA-256 | `efeba524b64026ca784da2711e9adeb9c9b09d6acd1205cdfdbf6cf9f4b0ad70` |
| Original manifest SHA-256 | `3b14c47febcad8d776f3d6dbb56a3e93ce4c734f013613f26a300952be8a6807` |

The downloaded ZIP digest matched GitHub's artifact API digest before extraction.
All ten extracted files were copied **byte-for-byte**. The existing original
[manifest.json](../results/task02/manifest.json) retains all nine payload SHA-256s,
four implementation hashes, source commit and runtime unchanged. No ZIP or competing
hash inventory is committed. `.gitattributes` disables text/EOL conversion only for
this archive so that Windows checkouts also preserve the original CSV bytes.

The ten files total 11,138,975 bytes:

- `summary.csv`, `mde.csv`, `power.png`, `legacy_flags.csv`: requested key results.
- `truth.csv`, `evaluations.csv`: all 18,000 truth rows and 36,000 evaluations,
  enabling direct aggregation checks; both are entirely synthetic.
- `reference.csv`, `protocol.json`: original synthetic reference and frozen design.
- `report.md`, `manifest.json`: original interpretation and complete hash/version record.

Keeping the seed files, rather than only small presentation files, lets the
**unchanged existing verifier** check exact complete membership. There are 18 cells,
two calendar specifications, 1,000 seeds per cell, 36 summary rows, eight tested-grid
threshold rows and two legacy seed-42 rows. No failed fit was removed; all 36,000
archived evaluations have status `estimated`.

Comparison with earlier downloaded CI run
[40127583019](https://github.com/sayac007/Agentic-Analytics-Studio/actions/runs/40127583019):
all nine payloads, including the numeric CSVs and PNG, are byte-identical. Only the
original manifest's `code_commit` differs (`1f53bd303094db0bbcbf92ed1662ee6a49fde6a1`
in that earlier run). All other manifest fields are equal. Both remain separate
original executions; no results were reconstructed or combined.

Recorded generating runtime: Python **3.12.15**, NumPy **2.3.5**, pandas **2.2.3**,
SciPy **1.17.0**, statsmodels **0.14.6**, HypoForge **0.4.0** at
`c47f636d24a39a820574a13133d6af693134a180`. The manifest lists the other recorded
package versions. Additional dependencies are pinned by `requirements-attention.lock`
at the source commit. All four recorded implementation hashes were checked against
that Git commit and the unchanged current files.

## Verification without GitHub Actions

From a normal checkout with Python 3.12, install the existing pinned dependencies
if needed. No artifact URL, GitHub credential or access to private empirical data
is required:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-attention.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m research_benchmark.verify results/task02
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -p test_identifiability.py -k preserved -v
```

The first check printed:

```text
Verified synthetic experiment: 18000 truth rows, 36000 fits, 36 summaries
```

The two preservation tests bind the original manifest SHA, check every declared
cell/seed/model, match legacy rows, verify interval/sign/coverage arithmetic, and
recalculate all 36 summaries and eight grid thresholds **from stored evaluations**.
They never call the generator or estimator. Their recomputation checks the archived
data; it does not overwrite any result. Local verification used Python 3.12.14 with
the pinned dependencies, distinct from the original generating Python 3.12.15.

For a dependency-free byte check, Python's standard library is sufficient:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('results/task02')
raw = (root / 'manifest.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '3b14c47febcad8d776f3d6dbb56a3e93ce4c734f013613f26a300952be8a6807'
manifest = json.loads(raw)
for name, expected in manifest['files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
assert (root / 'protocol.json').read_bytes() == Path('benchmarks/task02/protocol.json').read_bytes()
print('Original manifest and all 9 payload SHA-256s match; protocol bytes match.')
PY
```

Full statistical/numerical checks remain in the existing test suite. Source and
artifact comparisons, byte checks, the full-run verifier and preservation tests
were actually executed; PR CI evidence is recorded in the PR after observation.

Observed locally on 2026-10-27: both preservation-only tests passed (0.953s), all
seven identifiability tests passed (5.292s), and the complete existing suite passed
**350 tests in 81.269s**. Both manifest/generator example checks and the standard-
library hash check passed. All ten staged Git blobs and a Git checkout with
`core.autocrlf=true` remained byte-identical to the original download;
`git diff --cached --check` passed with the archive's original CRLF recognized.

## Findings that must remain visible

Selected archived values (all other cells, Monte Carlo SEs and Wilson intervals
remain in the original CSV/report):

| Cell and model | Null rejection | Rejection at 8% | Positive detection at 8% | Wrong-sign rejection at 8% | Coverage at 8% |
|---|---:|---:|---:|---:|---:|
| Legacy, with quarter-end | 16.6% | 9.5% | 4.4% | 5.1% | 83.4% |
| Independent flighting, with quarter-end | 12.4% | 99.3% | 99.3% | 0.0% | 87.6% |
| Calendar-aligned always-on, without quarter-end | 53.2% | 85.7% | 85.7% | 0.0% | 46.8% |

Nominal alpha is 5%, while these null rejection rates are much larger. Nominal 95%
interval coverage is not achieved. In the positive-effect legacy cell, wrong-sign
rejection exceeds positive detection; the original seed-42 media estimates are
negative and all three declared heuristic flags are true in both models. At true
effect zero, the stored `wrong_sign_rejection` field denotes negative-tail false
rejection, not the direction of an existing effect.

High nominal rejection alone is therefore not reliable recovery or well-calibrated
power. For example, omitting quarter-end under calendar alignment gives a median
estimated/planted coefficient ratio of approximately 3.134 at 8%, alongside 53.2%
null rejection. The dataset intentionally has an imperfectly modelled baseline.

`mde.csv` contains only the smallest **tested** 3/8/15% effect reaching 80% nominal
rejection or positive detection, or an empty field when not reached. These are
exploratory design-conditional grid thresholds, **not validated continuous MDE**.
Monte Carlo intervals describe uncertainty for this fixed simulation design, not
robustness across real markets. No empirical Tesla data, actual marketing ROI,
general causal identification or general 95% coverage is established here.
