# Research task-02 identifiability protocol v1.0.0

New scientific stage, separate from the historical Task 01a/01G/01I.3 and the
unrelated Task 02A–C UI work. Commit this protocol before implementation or new fits.
No frozen protocol, old artifact or established v0.2 result schema is modified.
Only the existing 72-month synthetic development baseline is used. No employer,
observed-source, private empirical or newly acquired data. No causal ROI claims.

## Fixed design

Normative constants: protocol.json. Seeds 0..999, SeedSequence(seed).spawn(2),
PCG64 media/noise streams exactly as Task 01a. Baseline and 60/12 split unchanged.
First 72 media normal draws generate 100*exp(.3*N(0,1)); the noise stream generates
72 independent N(0,1). Spend and noise do not use fitted outcomes or holdout targets.

Always-on independent exactly retains legacy spend. Calendar alignment multiplies
spend by exp(.6*sin(2*pi*t/12)+.6*quarter_end); no outcome-based alignment. Flighting
selects exactly 24/60 training and 5/12 holdout on-months without replacement,
using media-stream draws after the initial 72 normals. Independent selection uniform;
aligned selection weights exp(.75*sin(2*pi*t/12)+1.5*quarter_end), normalized within
each split. Spend is zero off-month and positive spend divided by .4 on-months.
The known calendar is specified prospectively; no holdout outcomes enter generation.

Adstock/Hill use the existing audited pinned HypoForge APIs: alpha .5, finite L=3,
normalize=False, n=1.5. New-grid k is the median TRAINING adstock among current-spend
on-months, recalculated per seed before outcome generation. This train-only scale
must not use holdout values. Legacy anchor retains fixed k=100 and 8% effect;
seed42 must reproduce Task01a numerical results, not a modified favourable design.
A separately labelled legacy 0% null uses the same fixed-k design to assess size.

beta=effect_fraction*mean(B_train)/mean(h_train); sigma=.05*mean(B_train).
y=B+beta*h+sigma*noise. No clipping. Effect fractions 3/8/15% for each of four new
design/confounding combinations plus their four 0% null controls. Null controls are
necessary to distinguish real detection from a poorly calibrated test. No new
scenarios, noise levels, search or result-driven tuning after inspection.

## Estimation, truth and uncertainty

Two fixed original calendar specifications with/without quarter-end, intercept,
trend and annual Fourier1; only h is the media regressor. No B, beta or sigma input
to estimation. Implement batch OLS by Frisch–Waugh–Lovell QR residualization against
calendar controls; prove numerical parity with numpy.linalg.lstsq and the full
existing HAC implementation. Scalar media HAC uses residualized h times full-fit
residuals, Bartlett three lags, correction n/(n-p), normal 95% intervals. Rank/
nonfinite/zero-variance failures retain scenario/seed/model and reason. No dropping
failed fits silently; denominators and failure rates are reported.

Truth and evaluation record SNR=sd(beta*h_train,ddof=1)/sigma. Also record training
spend minimum, realized on fraction, beta, sigma and k. Per-seed estimates/evaluation
are in a research-stage CSV (not falsely labelled old contract-compatible results).
Known reference/truth remain outside the narrow fit function. Synthetic Stage-A
legacy flags are computed as a separate new-stage evaluation; historical files stay
byte-identical. Data/protocol/code hashes live only in the run's data manifest.

## Fixed summaries and flags

For each cell/model: n scheduled/estimated/failed, median beta_hat/beta and quartiles
(undefined/null for zero beta), nominal two-sided rejection rate ("power" under
nonzero beta), positive detection lower>0, wrong-sign rejection upper<0, interval
coverage of actual seed beta, and Monte Carlo SE sqrt(p*(1-p)/n). Binomial Wilson
95% intervals accompany rates; these describe simulation error, not robustness to
misspecification. Show all results, including opposite signs, bad coverage or false
positives. User-supplied near-5% legacy power and higher flighting power are hypotheses
to test, not acceptance targets to manufacture. Baseline misspecification can make
them false. No reruns/tuning to obtain expected results or significance.

Flags (new stage only, descriptive and not proof of causal identification):
- sign_uncertain: lower<=0<=upper.
- not_identified: sign_uncertain OR full interval width > abs(beta_hat).
- extrapolated_counterfactual: contribution is against zero spend and minimum
  training spend > .01*mean(training spend). The .01 is a declared numerical support
  heuristic, not a scientific detection threshold. Flighting with observed zero
  spend need not extrapolate to zero; always-on can, even if the response plot itself
  stays inside support.

MDE is limited to the tested effect grid. Report smallest tested effect with
nominal rejection>=.8 (or >15%/not reached); never interpolate/claim continuous MDE.
Also report positive-detection-based grid threshold and empirical null rejection.
Mark all thresholds exploratory/design-conditional, not validated MDE, especially
when null size, sign or coverage is poor. Wilson intervals show uncertainty at the
80% boundary. Failed fits count as nondetections in power denominators; coverage
among estimable fits reports its denominator explicitly.

## Outputs and scope

Deterministic per-seed truth/evaluation CSV, cell summaries CSV, grid-threshold CSV,
one PNG power-vs-effect figure with Monte Carlo intervals, results-first report and
a data manifest with protocol/input/implementation versions/hashes. No extra hash
inventories or per-run QA document collection. A small CI smoke plus synthetic-only
result export; full 1000-seed scientific run executed and reported separately.
Single-thread BLAS; pinned current requirements-attention.lock. No empirical sources,
UI changes, transform search, Bayesian/geo/VAR model or automatic merge.
