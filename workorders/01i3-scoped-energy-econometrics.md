# Codex Workorder — Task 01I.3: Scoped Private Energy Econometrics

Repository: https://github.com/sayac007/Agentic-Analytics-Studio
Date: 2026-10-24

## Objective

Conduct the first **private, retrospective, exploratory** econometric analysis of German Tesla registrations and energy prices, using **only the source-specific private admissions already documented in merged PR #18**. Do not execute the broader Task 01J, and do not change the frozen Task 01G protocol.

## 0. Preconditions and branch

1. Pull current `main` and verify PR #18 merge commit `2f644e4ba85731aef023a82b4378043f52c1f00b` is included.
2. Read `AGENTS.md`, `docs/ENERGY_RIGHTS_ADMISSION.md`, `docs/REAL_ENERGY_DATA_IMPORT.md`, `data/fuel_oil/rights_admission.json`, relevant KBA source/admission contracts and the existing Task 01G protocol.
3. Create `research/task-01i3-scoped-energy-study` from current `main`. Draft PR only, no self-merge.
4. Confirm the actual private raw/normalized energy files and hash-bound permits are available in the execution workspace. **Do not infer workspace paths or manufacture missing files.** Verify hashes, series identities, units and private permits before reading numeric outcomes.
5. The public repository must not contain real raw/derived energy observations, private numerical study results, local private paths or identifying metadata.

## 1. Source scope and hard gates

- **Admitted:** ECB monthly EUR/USD `EXR.M.USD.EUR.SP00.A`, USD per EUR, 96/96 months for 2018–2025; European Commission Germany diesel, with taxes, qualified private monthly calendar-overlap approximation in EUR/litre, 83/96 months.
- **Not admitted:** EIA Brent `RBRTE`, because Refinitiv/LSEG rights remain unresolved. No Brent variable, transformation, ratio or proxy in this study.
- **Not available:** 2026 KBA registration observations. Limit the outcome analysis to 2018-01 through 2025-12; 2026 energy-price observations may only appear in a separate, clearly non-outcome descriptive appendix if privately permitted.
- **Diesel missing months:** 2018-04, 2018-12, 2019-01, 2019-04, 2019-12, 2020-01, 2020-04, 2020-12, 2021-01, 2021-04, 2021-12, 2022-01, 2022-04. Preserve all 13 as missing. No interpolation, forward-fill, or fabricated zero.
- Do not treat a qualified private admission as public redistribution approval or historical point-in-time availability.
- Validate that KBA Tesla observations are approved for the intended retrospective analysis; historical as-of restrictions remain unchanged.

## 2. Pre-register a narrow exploratory protocol before inspecting cross-series relationships

Commit `docs/SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md` **first**, in its own commit, before any real-data join, plot, correlation or model fit. Hash and freeze it for the task. Include:

- Research question: whether German diesel prices and EUR/USD show descriptive and conditional predictive associations with monthly Tesla registrations, not a causal oil-shock or advertising effect.
- Explicit outcome units and transformations; positive-count-safe log1p option; deterministic seasonality and trend controls; careful interpretation of levels and differences.
- Fixed sample 2018–2025, exact common-month eligibility, separate complete-case diesel sample and full EUR/USD sample.
- Predefined ACF/PACF and fixed-specification ADF/KPSS diagnostics with null hypotheses and warnings; no automatic test-based cherry-picking.
- A small **predeclared** lag grid (e.g. 0–3 months primary, 4–6 months sensitivity) with explicit direction `x[t-k] -> y[t]`. If lagged diesel values are missing, mark the corresponding observation unusable; report the resulting sample size for every lag.
- Prefer a parsimonious baseline with deterministic month indicators and trend; add **one** energy predictor at a time. Avoid overparameterization, lag-search optimization, and automatic dummies chosen after observing results.
- A clear distinction between cross-correlation, conditional association, incremental prediction and causal inference. Diesel and FX are not instruments and must not be labelled exogenous shocks without identification evidence.
- Predefined HAC covariance approach and multiplicity treatment; do not call conditional intervals causal confidence intervals.
- A limited retrospective 2025 holdout only if data alignment permits, explicitly **not** a historical real-time backtest: present-day data vintages and source revisions invalidate as-of claims.
- 2022 episode: descriptive window only, not an identified Ukraine/oil causal treatment. Explicitly note missing diesel January and April 2022.
- Confounders (subsidies, Tesla prices, launches, supply constraints, macro conditions, Google attention) remain unmodelled unless separately admitted and preregistered; do not add them post hoc.
- No 2026 Tesla/BEV outcome comparisons and no changes to Task 01J or Task 01G.

## 3. Execution, only after the protocol commit and gates pass

Create a small private CLI using existing libraries and data interfaces. Read admitted private sources and verified retrospective KBA only. Validate one-to-one month joins, duplicate periods, units, source hashes and missingness before computation.

Produce **private** outputs:
- Sample inventory and provenance/hash manifest.
- Plots of source series, transformed series, ACF/PACF, and predeclared lag associations.
- ADF/KPSS diagnostics with sample sizes and caveats.
- A concise comparison table: baseline versus one-predictor models, coefficients, uncertainty, effective n and holdout metrics where legitimate.
- A plain-language report including null/negative results, limitations and why no causal effect is identified.

Do not alter model specifications to improve significance or results. Do not copy real numbers into GitHub PR descriptions, CI logs or public artifacts. In public documents report only implementation status, pass/fail, file counts, hashes where safe and methodological limitations.

## 4. Tests and reproducibility

Add offline synthetic fixtures covering admission refusal, Brent rejection, source-hash mismatch, correct lag direction, month alignment, diesel missingness propagation (including 2022-01 and 2022-04), stationarity test edge cases, HAC shape, deterministic output and public-output leakage. Do not run real data in CI.

Run the full existing test suite, Ruff, existing contracts/audits and CI. Clearly separate synthetic software tests from actual private empirical results. If a prerequisite fails, stop and report precisely which gate failed; do not silently weaken it.

## 5. Deliverables and finish

- Draft PR with protocol, CLI, offline tests and a **public status-only** report.
- Private output directory with full empirical diagnostics and hash-bound manifest; provide an authorised export mechanism if available, but do not pretend a workspace path is a ChatGPT download link.
- Final summary: exact source permits checked, sample coverage, missingness, tests/CI status, and whether a private study actually ran. Do not publish numerical estimates.

**Acceptance:** A transparent, reproducible, preregistered, privately executed exploratory analysis using only ECB EUR/USD and qualified EC diesel, or a precise documented refusal if a gate is unmet. No Brent, no 2026 registration analysis, no public real values, no automatic merge.
