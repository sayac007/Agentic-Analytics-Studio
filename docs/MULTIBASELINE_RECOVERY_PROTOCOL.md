# Multi-baseline recovery protocol — design v1.0, no runs performed

Task 01B is data acquisition, not Statistical Stage B (transform search).
This protocol precedes any recovery on the observed KBA references. It does not
change the fixed synthetic Task 01a run or its poor results. Statistical Contracts
v0.2.0 statistical rules remain normative; v0.2.1 adds the provenance/admission patch. A reviewed Stage-C execution specification is still needed.

## Admission, windows and selection

Only `admitted` references may enter later runs. Task 01B.1 admits all four candidates under the **retrospective immutable-reference**
regime; historical Point-in-time use remains blocked. Missing publication days are
retained at their actual precision rather than fabricated. See PUBLICATION_PRECISION.md. See [data evidence](KBA_MULTIBASELINE.md).
Freeze source catalog, raw hashes, normalized hashes, code/dependency versions and
any resolved publication evidence before generation. Never convert a failed gate
into a synthetic label or extend an observed reference with simulated counts.

The primary proposed paired window is **2021-01–2025-12**: training 2021-01–2024-12
(48), untouched final holdout 2025-01–2025-12 (12). This is the earliest available
60-month common window with an explicit BEV column. The original availability plan
was revised solely for this constraint, before any observed-baseline recovery; its
2018–2023 brand-selection criteria are unchanged. Full 2018–2025 histories for the
three brands may support a separately reported length-sensitivity experiment; its
results cannot be pooled with the 60-month primary experiment.

C=Toyota minimizes sample CV over complete 2018–2023 brand totals with mean >=1000;
D=VW maximizes mean among remaining eligible brands. Tesla and aggregate/model rows
are excluded. Ties use lexical names. Freeze the complete eligible ranking, not just
winners. Never replace Toyota because VW later looks quieter or a model recovers
better. Selection uses descriptions, never MMM results. A calm series is not
necessarily less confounded, better identified or causally easier.

These are monthly German passenger-car registrations. All three brand references
cover **all powertrains**; only the total-market reference is BEV-only. Shared market
shocks and overlapping Tesla/BEV counts mean these are paired fixed-case studies,
not four independent randomly sampled populations.

## Paired generation and fixed estimator

For replication r, use `SeedSequence(20261022).spawn(R)` and for each replication
spawn two PCG64 streams (media, noise); archive the full stream identifiers and NumPy
version. Reuse the **same standard normal vectors** across baselines, model variants,
effect cells and experiments A/B. Root seed 20261022 is fixed by this protocol; R and stream mapping must be frozen in
the reviewed execution manifest; do not reuse Task 01a's one run as a calibration
sample, pick favorable seeds or stop on a favorable detection.

Keep the approved finite causal adstock alpha=.5, L=3, normalize=False, Hill k=100,
n=1.5, zero prehistory and full train-to-holdout history. Fit the same original-unit
OLS (`numpy.linalg.lstsq`) with intercept, linear month index, annual Fourier order 1
and media, with two predeclared variants including/omitting quarter-end. No reference
regressor, target lag, baseline fit, data-dependent break or arbitrary proxy is
allowed. No transform search is part of this design; later Stage-B results require a
separate training-only search and uncertainty protocol.

Noise is `epsilon_i[t] = s * mean(B_i_train) * z_noise[t]` for both A and B, using the
same z_noise across baselines and experiments. Thus standardized noise is paired;
absolute noise differs with baseline scale, deliberately exposing different absolute
signal-to-noise ratios in B. Do not change the noise convention between experiments.
Candidate later grid: effect fractions 0,.03,.08,.15; noise fractions .02,.05,.10.
These are experimental cells, **not** calibrated detection thresholds.

Media: `x_i[t]=100*exp(.3*z_media[t]+lambda*qz[t]+lambda*bz_i[t])`, with train-only
mean/sample-SD standardization, applied unchanged in holdout; reject zero SD or
nonfinite values. Predeclare three scenario families: independent (`lambda=0`),
quarter-end only (`lambda=.3`, baseline term disabled), and quarter-end plus baseline
peaks (`lambda=.3` for both). In the latter, shared shocks z are paired but actual
spend differs across baselines because bz differs. Record the induced correlations;
do not call these exogenous media. Quarter-end-only requires a reviewed generator
protocol extension: v0.2.0 executable contracts currently allow independent or joint
quarter-end-and-baseline-peak confounding only. Do not silently reinterpret an enum.

Construct the common 21-point raw-spend grid from the intersection of **training**
support across all baselines in the paired cell, before fitting; serialize the same
points into truth/results. Empty or constant intersection is a recorded failed cell,
not a reason to select a different reference or inspect holdout. Use the approved
steady full-kernel constant-spend response convention. The actual x can differ under
joint confounding even with common random numbers.

## Experiment A: equal relative effect

For each reference i and each cell:

`beta_i = f * mean(B_i_train) / mean(H(adstock(x_i_train)))`.

The mean injected **training** contribution is f times that reference's training
mean. No holdout calibration or matching of realized noisy effects. Truth keeps beta,
noiseless monthly contributions, shared-grid curve and reference/generator hashes.
This compares recovery under equal relative injected effects, not real marketing ROI.

## Experiment B: equal absolute effect

Use Tesla as a fixed, already selected scale anchor, not whichever reference later
recovers well. For each paired cell set

`beta_absolute = f * mean(B_Tesla_train) / mean(H(adstock(x_Tesla_train)))`

and use that **same beta** for all baselines. It follows that all true response curves
on the same spend grid are identical count-equivalent curves. Under independent or
quarter-end-only media the actual injected paths are also identical; under joint
confounding actual exposure and contributions differ, even though the absolute
response function is identical. Do not simultaneously claim equal realized totals
under different exposure paths. Noise still scales by each reference mean as above.
Record both absolute/relative effect and noise scales. A sensitivity experiment with
common absolute noise would be a separately declared experiment, not a hidden default.

**Contract proposal, not implementation:** generator v0.2.0 fixes calibration to
`training_reference_mean_only`; it cannot express a cross-baseline absolute-beta
anchor without ambiguity. Before executing B, review an explicit absolute-calibration
contract, anchor artifact/hash, beta units, privacy boundary and evaluator bindings.
No incompatible schema change, engine change or workaround is introduced in Task 01B.
The single-run comparison schema also requires identical data hashes, so cross-baseline
summaries need a separate reviewed Stage-C aggregate contract; do not pass them off as
current two-model comparison artifacts.

## Outcomes, replication failures and interpretation

For each attempt preserve coefficient/intervals, holdout contributions and sum,
response curve, test predictions/RMSE and rank/condition diagnostics. Primary recovery
metrics are signed contribution error, absolute contribution error and shared-grid
curve RMSE in count-equivalent units. Also report contribution error divided by
training-reference mean × holdout length and curve RMSE divided by training-reference
mean; these remain defined under f=0. Record beta error for oracle Stage A, but do not
substitute it for curve recovery in future misspecified models.

Report fixed-transform interval coverage of planted beta and holdout contribution;
pointwise curve coverage is distinguished from simultaneous coverage (not provided).
Positive detection means beta interval lower bound >0; two-sided rejection means
zero excluded. Under f=0 report two-sided false-positive rate. HAC uses the approved
three lags/Bartlett/N/(N-p)/normal critical value, conditional on fixed transformations;
it does not remove omitted-baseline bias or guarantee nominal coverage.

Use all intended attempts for operational detection/coverage rates, counting failed
fits as failures. Separately show success-conditional coverage/detection, n attempted,
n successful and failures by reason, including input gates, rank, conditioning,
numerical failure and empty support. Recovery error summaries use successful fits
with an explicit denominator. Common random numbers require paired differences and
paired uncertainty; baselines/runs are not independent observations. Bootstrap whole
replication IDs together if that aggregate uncertainty method is approved. For each
single rate use predeclared Wilson Monte Carlo intervals; disclose multiple grid cells.

Open scientific decisions before execution: R and Monte Carlo precision, recovery
accuracy tolerance and recovery-rate definition, acceptable false-positive/coverage
criteria, power target, aggregate multiplicity policy, paired-difference interval
method, exact absolute-calibration/aggregate schemas and the proposed additional
confounding family. Nothing in the current data descriptions supplies these choices.
No Monte Carlo runs, empirical power, calibrated MDE or actual 95% coverage are claimed.
`effect_below_detection_limit` stays null and status `not_calibrated` until a separately
reviewed calibration satisfies the normative statistical detection-limit policy.

## File boundary

`immutable KBA reference → private generator → semi-synthetic outcome/media CSV →
isolated estimator → evaluator`.

Only generator/evaluator read reference, release ledger and truth. A future admitted
series becomes a separately hashed two-column `period,observed_registrations` CSV
with observed column lineage and one fully evidenced release record per month.
Estimator inputs remain exactly `period,synthetic_media,semi_synthetic_outcome` plus
approved calendar configuration. Never give the estimator a source path, true beta,
noise scale, reference value, reference-derived regressor or baseline-peak feature.
