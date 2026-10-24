# Task 02A–02B — local synthetic analytics demo

## Small architecture

FastAPI serves a static HTML/CSS/JavaScript page and a typed local API in one process.
No frontend build, cloud account, model key or new statistics engine. The adapter calls
`studio.pipeline.run`, validates its artifact bundle, and presents computed output.
The existing engine already pins HypoForge adstock/Hill and isolates estimator input
from generator reference/truth. The adapter reads synthetic truth only after fitting.
No existing contract, engine implementation, frozen protocol or empirical input changes.

Only `Synthetic MMM Demo`, seed 42, is available. The allowed configuration selects
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
one port. Bind is loopback-only. No multiuser/deployment/authentication claim. Five
recent results are retained in process memory, lost on restart; temporary synthetic
engine bundles are deleted after reading. No file browsing or private data routes.

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
02C controlled language tools are not implemented in this intermediate commit. No MCP server is present. Future enterprise,
Microsoft, PPTX, deployment and empirical integrations remain outside this MVP.

Optional automated browser check (Playwright 1.56.0, existing system Chromium):

```sh
.venv/bin/python -m pip install -r requirements-demo-browser.lock
.venv/bin/python scripts/demo_browser_smoke.py
```

Start the app in a second terminal first. Set `DEMO_CHROMIUM` if Chromium is installed
elsewhere. This optional check clicks the form twice, verifies changed coefficients,
the SVG series and a narrow viewport. Linux Chromium was actually exercised; this is
an automated browser check, not a claim of manual nontechnical user acceptance.
