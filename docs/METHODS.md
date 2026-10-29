# Methods — observed demand and archived benchmarks

The current empirical question is whether Tesla's German registration changes
come from the BEV market, Tesla's share, or separately identified drivers.
Registrations measure registrations/deliveries, not purchase decisions or
manufacturer sell-out. Explained variation, prediction and causation are
different claims.

## Current Stage 1

The normative definition is the immutable
[Task 04 protocol](REGIME_STATE_SPACE_PROTOCOL.md), version
`task-04-regimes/1.0.0`. Its [freeze record](../data/task04_regimes/freeze.json)
predates the first real fit. The already-known development data mean this is
not an outcome-blind preregistration.

The 69 observed months run from January 2021 through September 2026.
`Tesla = official BEV market × Tesla BEV share`. Annual share is the ratio of
annual sums, not the mean monthly share. Symmetric market/share changes add
exactly; this is accounting, not causal attribution. Administrative counts do
not receive invented sampling confidence intervals.

The joint Gaussian system models log BEV and Tesla/Rest and VW/Rest log ratios.
Rest includes all other BEV; VW means the brand, not the group.
M0 has a fixed trend and calendar; M1 a local level/slope; M2 adds documented
subsidy regimes. Calendar means one annual Fourier pair, quarter-end and
training-centred national weekdays net of national holidays. Twelve month
dummies plus quarter-end would be collinear.

The primary level SD is 0.03; slope SD remains 0.01. All predeclared level,
portal-date and logit sensitivities remain visible. The small prior synthetic
recovery comparison had imprecise policy recovery at every candidate SD;
it does not validate the state variance. Priors, seeds, covariance estimation,
conditional joint draws and MC limits are specified in the protocol.

Rolling Origin uses at least 48 months, 21 one-month and 19 three-month targets
per model. Future outcomes are excluded; future policy is included only when
known by the origin. The logit branch forecasts the Pkw denominator using the
previous year's matching month. Results are current-vintage retrospective
backtests, not reconstructed publication-lag-correct real-time forecasts.
ADF/KPSS, marginal one-step innovations, Ljung–Box/Holm, ACF, annual variation
and large forecast errors are diagnostics, not automatic tuning instructions.
Both stationarity of target levels and remaining innovations must be examined.

See [results and reproduction](../results/task04/README.md),
[all model results](../results/task04/stage1/report.md) and
[limits](LIMITATIONS.md). The original statistical contracts and empirical
protocols remain normative at their existing paths.

## Conditional next questions — not already executed

Relative prices require comparable tax, battery, variant, segment, incentives,
validity dates and availability. A cheap city car is not automatically a Model Y
substitute. Exact prices cover only 23 of 80 researched annual top-10 model-years;
that does not create a monthly price index. Same-year sales weights would leak
future information into predictions: freeze baskets/weights using prior knowledge.
Never interpolate undocumented historical prices or missing brand counts.

Separate market growth from brand choice. Negative Tesla/China share correlation
is mechanically affected by compositional constraints; contemporary rival sales
are joint outcomes, not an exogenous competition regressor. First KBA listing
is not a documented market launch. Buyer-type transition, diffusion, early
adopters and brand image are hypotheses, not measured latent-state labels.

Fuel and finance need lawful source-specific admission, compatible time masks,
real-price definitions and fixed lags. Diesel is not petrol; purchase price per
WLTP range is not operating cost. Relative price × operating cost interactions
need main effects and prior scaling; do not fill a short series with all possible
cross-products. Start with fixed relationships, compare a parsimonious dynamic
model, then consider varying coefficients only with identifiable information.
A Kalman smoother uses future observations. Process variance zero is a serious
constant-coefficient comparison, not a defect to tune away.

HypoForge remains suitable for audited fixed lag/difference features, not forced
Hill transformations of car prices. VARX/VECM require their own sufficient data,
integration/cointegration diagnostics and question. Existing
[literature/portal research](EV_DEMAND_LITERATURE_AND_PORTALS.md) documents a
AutoScout24 AGPI method break in March 2025: measurement changes can mimic
changing price sensitivity.

## Earlier research, preserved rather than substituted for real data

[Task 02](../results/task02/report.md) is a synthetic identifiability experiment.
Its null false positives, interval coverage and sign errors remain limitations;
it does not establish a universal failure of always-on media or a validated
continuous MDE. Its ten original files and hashes remain unchanged.

[Task 01G](TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md) and
[Task 01I.3](SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md) remain frozen.
Private studies and source permits are not automatically public.
[Statistical Contracts v0.2.0](STATISTICAL_CONTRACTS.md) describe the separate
semi-synthetic benchmark. They are not the target interface of the observed
Task 04 study.
