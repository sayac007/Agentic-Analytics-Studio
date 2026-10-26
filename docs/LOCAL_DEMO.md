# Task 02A–02C / 03A — local synthetic analytics workspace

## Small architecture

FastAPI serves a static HTML/CSS/JavaScript page and a typed local API in one process.
No frontend build, cloud account, model key or new statistics engine. The adapter calls
`studio.pipeline.run`, validates its artifact bundle, and presents computed output.
The existing engine already pins HypoForge adstock/Hill and isolates estimator input
from generator reference/truth. The adapter reads synthetic truth only after fitting.
No existing contract, engine implementation, frozen protocol or empirical input changes.

Only `Synthetic MMM Demo`, seed 42, is available. Two separate projects use this
same asset, with `with-quarter` and `without-quarter` defaults. They are not two
different datasets. The allowed configuration selects
the predeclared with/without-quarter-end model. The unchanged pipeline computes both
on the same synthetic data; 02A displays the selected one. Changing this selection
changes estimates, not the underlying data. No freeform seed/model/path/upload input.

## Install and start

Python 3.12 and Git are prerequisites. From repository root, Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-demo.lock
.venv/bin/python -m demo
```

Open `http://127.0.0.1:8000`. Choose a model and click **Run analysis**. The page shows
status/errors, training/holdout sizes, formula, coefficient/HAC interval table,
count-equivalent contributions, a plot and a computed interpretation. Ground truth
is a separately labelled evaluator comparison, never an estimator regressor.

Windows equivalent (not yet tested on Windows):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-demo.lock
.venv\Scripts\python -m demo
```

The last command is the single start command after installation; UI and API share
one port. Bind is loopback-only. No multiuser/deployment/authentication claim.
SQLite and the complete original validated synthetic bundles persist in
`.aas-workspace/` in the launch directory, excluded from Git. Set `AAS_WORKSPACE_DIR`
on the server to use another dedicated directory outside the checkout (or explicitly
Git-ignored); no HTTP request accepts a path.
Only one application process/worker may open that directory at a time.
No file browsing or private empirical-data routes.

Choose a project, write a note, run an analysis, then stop and restart the server.
The selected project can be bookmarked in the URL; its latest result opens after
artifact/hash revalidation. Use **Wo haben wir aufgehört?** to retrieve actual
context and current warnings. No previous Tesla study or conversation is imported.
Stored statements, unexecuted decision/development-work-order proposals, explicit
human approvals and verified tool outputs have separate labels. A proposal approval
only records your decision; it executes no tool and changes no data, method or code.
There is no LLM, so unsupported text is saved as a note with an honest acknowledgement.

The view shows the last 40 messages and 20 runs/executions/decisions; older records
remain in SQLite. Historical run metadata means **validated at creation**. Opening
a result, report, comparison or resume response checks the original bundle again.
An interrupted operation is labelled interrupted on restart, never retried or treated
as successful. Corrupt or incompatible workspaces fail rather than resetting history.

The directory is owner-private on tested Linux; it is not encrypted. Do not paste
credentials or proprietary data into this synthetic prototype. Back up the SQLite
file **and** `runs/` together while the server is stopped. Runs grow without eviction;
failed/interrupted fits can leave unreferenced partial directories, retained for
inspection and never shown as successes. Cleanup/retention must be done offline;
automatic deletion, migrations and production backup are outside this increment.
Windows commands above remain untested; Windows filesystem/lock behavior is not
certified. [Architecture and official integration review](PERSISTENT_WORKSPACE.md).

## Checks and limits

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -p test_demo.py -v
```

Tests use a real local HTTP server and freshly generated synthetic data. Existing
full-suite CI installs the demo lock alongside the research lock and includes these
tests. Actual local/remote check evidence belongs in the PR, never assumed from YAML.

This is Stage A, fixed oracle transformations, conditional three-lag Newey-West HAC,
60 training/12 holdout months, intentionally incomplete baseline. One seed does not
validate interval coverage, power, MDE, real ROI or causal marketing effects.
Scientific warnings and poor recovery are preserved, not tuned away.

02B adds a two-model comparison, identical 21-point response grid with separately
labelled truth, full time-series decomposition and residual plot. Export returns the
existing engine-generated synthetic Markdown report, never empirical output.
02C implements a deterministic exact-phrase router (case/whitespace/final punctuation
normalization). No LLM/API key. The analytics examples and resume action use real tools:

| Request | Tool |
|---|---|
| Zeige den Beispieldatensatz. | describe_dataset |
| Starte die MMM-Analyse. | run_demo_analysis |
| Vergleiche die beiden Modellläufe. | compare_runs |
| Erkläre die Warnungen und die Modellgrenzen. | summarize_diagnostics |
| Wo haben wir aufgehört? | resume_workspace |

`Welche Datensätze gibt es?` also maps to `list_datasets`. The first tool previews
12 actually generated rows without fitting; the second executes a fresh fixed
analysis using the project's declared default model (with-quarter in the first,
without-quarter in the second). Compare/diagnostics require an existing selected run and
report missing results instead of inventing an answer. Each response identifies the
tool, execution status and actual structured output. Arbitrary commands and extra
arguments are rejected. No application-defined shell/eval/network tools exist; the
unchanged core engine itself uses its established isolated estimator subprocess.

Project API: `GET /api/projects`, `GET /api/projects/{project}/workspace`,
`POST /api/projects/{project}/messages` (conversation ID plus text and optional run ID),
and project-scoped `/runs`, `/runs/{id}`, `/comparison`, `/report`, `/decisions`,
`/decisions/{id}/approve`. Project identity and record ownership are checked server-side.
The legacy Task 02 API remains restricted to the first project:
`GET /api/datasets`, `POST /api/runs` (dataset/model literals only),
`GET /api/runs/{id}`, `/comparison`, `/report`, `POST /api/agent` (message/run_id),
`GET /api/tools`. Strict request models reject unknown fields. `demo.agent.call_tool`
is the allowlisted typed-argument adapter seam for a future transport; it is **not**
a working MCP connection or server. MCP remains deferred beyond Task 03A. No MCP server is present. Future enterprise,
Microsoft, PPTX, deployment and empirical integrations remain outside this MVP.

Optional automated browser check (Playwright 1.56.0, existing system Chromium):

```sh
.venv/bin/python -m pip install -r requirements-demo-browser.lock
.venv/bin/python scripts/demo_browser_smoke.py
```

Start the app in a second terminal first for that legacy smoke. Set `DEMO_CHROMIUM` if Chromium is installed
elsewhere. This optional check clicks the form twice, verifies changed coefficients,
the SVG series and a narrow viewport. Linux Chromium was actually exercised; this is
an automated browser check, not a claim of manual nontechnical user acceptance.

The self-contained persistent-workspace browser smoke starts its own temporary
server on a free port, with no existing user history, and actually restarts it:

```sh
.venv/bin/python scripts/workspace_browser_smoke.py
```

It checks notes rendered as text, explicit proposal approval, real fits, all four
analytics tools, exports, project separation, resume and original results after
restart. The ordinary full unittest CI also includes real HTTP restart, integrity,
failure and project-isolation checks without needing Chromium.


## Live demo checklist

1. Start the server; open the loopback address. Verify SYNTHETIC / NOT EMPIRICAL.
2. Run the with-quarter model. Check completed/validated status, coefficient table,
   separate ground truth and the 2023 holdout separator.
3. Compare models. Observe identical data/grid, different estimates, unchanged null
   detection-limit flag and retained poor recovery; do not present a causal ROI.
4. Export the synthetic Markdown report; its numbers match the displayed estimates.
5. Click each of the four assistant examples. Inspect the named tool/output; a
   compare request without a selected result asks for analysis instead of inventing.
6. Enter an unsupported command and verify rejection; stop the server with Ctrl+C.

Linux fresh-install API tests and actual Chromium browser automation were executed.
Windows commands are illustrative equivalents, not tested platform certification.
An optional human nontechnical walkthrough remains useful. No interval-coverage,
empirical-use, production-security or MCP integration claim is made.
