# Task 00 decisions — proposed for review

> Task 00.5 supersedes the v0.1.0 statistical proposal below. The normative design is
> [STATISTICAL_CONTRACTS.md](STATISTICAL_CONTRACTS.md): observed reference/truth are
> generator/evaluator-only; fixed calendar controls explain the baseline. Contracts
> v0.2.0 add Stage-A uncertainty, contributions, common-grid curves and recovery
> evaluation. Python remains selected; no R-parity gate. Historical source/API/license
> observations remain valid; no new model or upstream implementation is introduced.

## Python reference and orchestration

Python remains selected for OLS, file orchestration, cloud integration and later MCP.
HypoForge Python's actual APIs were exercised during the audit. The user's subsequent
review removed R parity from scope; missing R does not block this Python workflow.
No R installation or parity implementation is part of Task 00. Statistical/data
contract blockers, not language parity, gate Task 01. See the readiness assessment.

## Reuse verified HypoForge, avoid an unnecessary Hill copy

Prefer `hypoforge` 0.4.0 at exact Git commit
`c47f636d24a39a820574a13133d6af693134a180`, under Apache-2.0 with required notices.
The application does not yet declare/install this dependency. Call exported
`evaluate(FeatureSpec(...), df)` for Hill and import geometric adstock from
`hypoforge.media`. Require finite nonnegative inputs, positive finite k/n and explicit
lag/normalization settings at the boundary. This wrapper is an interface adaptation,
not a second reference implementation. No local Hill fallback is needed now.

If packaging/access later prevents reuse, a **temporary** local adapter may only be
added in Task 01 with attribution, documented removal condition and parity tests
against this exact commit: H(0)=0, H(k)=0.5, asymptote, fractional n, k/n bounds,
negative/NA/infinite inputs, zero and impulse exposure, alpha=0 and near 1, l_max=0,
available-history edges, both normalization modes, and future-perturbation causality.
Use ordinary finite test ranges and explicit tolerances (initial proposal atol=1e-12,
rtol=1e-10). Stress-test overflow separately; do not claim arbitrary-scale stability.
R source-level formula similarity is not a substitute for executing those probes.

WKR supplies file contracts, parity and validation patterns only. No license grant
was found, and its source-attribution caveats prevent reusing its datasets as verified
Tesla inputs. No WKR or HypoForge source modifications are needed.

## Superseded conditional-baseline proposal (not Task 01 specification)

Proposed Task 01 DGP:

`a[t] = sum(alpha**lag * media[t-lag], lag=0..min(t,l_max))`

`h[t] = a[t]**n / (k**n + a[t]**n)`

`y_semi[t] = b0 + b_ref * observed_reference[t] + b_media * h[t] + epsilon[t]`

Use predeclared seeded media/noise generation, record generator ID/version, RNG,
seed and noise scale in evaluator-only truth, and save generated artifacts/checksums.
Do not clamp/round the continuous semi-synthetic outcome: that changes the DGP.
The original reference remains untouched. Regression uses the reference as a
baseline covariate; this is a conditional recovery benchmark, not an ex ante forecast
of unknown future registrations. Holdout is temporal nevertheless.

Manifest supplies fixed predeclared alpha/k/n and transform order, with
`normalize=False`; truth supplies generator coefficients/noise and actual DGP
parameters. The first benchmark deliberately uses oracle transform settings: report
that limitation and do not claim blind transform recovery. The estimator never
receives the truth path or coefficients. The evaluator alone opens truth after fitting.
A schema cannot enforce process isolation: separate command arguments/access and an
integration test in Task 01 must prove the estimator did not read truth. Effect
recovery concerns injected coefficients only, not real Tesla ROI.

## Historical v0.1.0 temporal policy (v0.2.0 admission rules supersede)

CSV is a complete, unique, ascending monthly DE series; no interpolation,
forward-fill, implicit zero, random split or row deletion. Reject missing/nonfinite
reference, media and target values. Early adstock uses zero prehistory; carry the
finite causal train history into test without resetting state or reading future rows.
The validator checks contiguous adjacent train/holdout intervals. Fit model parameters,
scalers and any later hyperparameter selection on training data only. Keep the final
holdout untouched; introducing rolling selection requires a separately specified inner
split. Six fixture rows test the contract only, not statistical adequacy; choose an
adequate real window and identifiability diagnostics before fitting in Task 01.

## Existing point-output contracts (insufficient for revised Task 01)

Save coefficients, train/test n, MAE and RMSE in target units, design rank and condition
number; omit MAPE because a benchmark target can be zero or negative. Proposed
`weak_identification`: condition number >= 1e8 for the declared, unscaled design;
`rank_deficient`: rank < 3. Report feature scaling because condition number depends
on units. A failed fit must exit nonzero and must not write a success result. No MDE
claim from a single coefficient. Threshold calibration and recovery tolerance remain
review questions, not measured performance.

Initial comparison is limited to distinct runs with identical data hashes, target and
holdout. Verify actual files/hashes and metadata; do not trust a claimed compatibility
boolean alone. Recompute right-minus-left deltas. Different data windows are rejected
by this initial contract rather than compared as if metrics had identical support.
Changing transforms or training specification is permitted with explicit manifests.
A future recovery-evaluation artifact can compare estimated and planted coefficients;
its tolerance/uncertainty contract requires Task 01 review. No fake fitted result or
run comparison is committed as evidence.

## Kinderwelt-style increments

Use the principle defined in this repository's AGENTS.md: runnable contract checks,
one reviewed increment, deterministic fixtures and rejection tests, explicit failures,
no empty green CI, then an approved end-to-end slice. Kinderwelt at
`d65ed9fd122b00f72ccd917916c3fa0a177f7c8e` provides concrete references:
`tests/run.sh` isolates state, preserves exit status and checks a clean shipping copy;
`tests/android/test_verification.py` rejects hash/content/payload drift; and
`docs/test-report.md` separates executed checks from device/release limitations.
Sixteen packaging tests passed locally; historical Godot/render totals were not
reproduced. Reuse these QA patterns without importing app code or licensed assets.

Deferred: MMM engine, downloads/scrapers, MCP server, dashboard, PPTX, automated
publication, unrestricted execution tools, VAR/SVAR and external reference changes.
Task 00's remaining campaign/Trends access limits and per-source reuse restrictions remain visible;
passing schemas do not resolve them or authorize Task 01.
