# Empirical Studio — first private Azure live test

Authorised by the user's 2026-10-28 instruction: archive the synthetic-development
direction, use the collected real observations, and prepare an Azure live test.
The user explicitly accepts incomplete explanatory power and wants unexplained
peaks investigated, rather than invented media or tuned significance.

This is a separate private exploratory extension. Task 01G/01I.3 protocols,
their original private results and the permanently preserved Task-02 benchmark
remain unchanged. The stopped README/null-calibration drafts are archived locally,
not published. No new synthetic observations enter the empirical product.

## Fixed first model comparison, before new outcome joins or fits

- Use the already acquired 2018-01–2025-12 KBA Tesla all-powertrain registrations,
  Destatis national CPI, ECB consumption-credit AAR/NDER, ECB EUR/USD and qualified
  German diesel-overlap approximation. Source identities, units, original snapshot
  hashes, attribution and all 13 diesel gaps remain binding. This user instruction
  authorises their private exploratory modeling here; it does not rewrite the older
  QA-only source manifest, clear Brent or approve public redistribution.
- Target `dlog1p_registrations[t] = log1p(y[t]) - log1p(y[t-1])` on the original
  monthly calendar. No compression, imputation, rounding or clipping.
- Four fixed specifications: month-of-year baseline (intercept + 11 indicators);
  baseline + lag-1 target change; that dynamic model + lag-1 monthly CPI log change,
  consumption-credit change in percentage points and EUR/USD log change; finally
  the same macro model + lag-1 diesel log change. No search over lags or variables.
- Credit is a rate, not APRC or an index; do not log it. Every differenced/lagged
  input requires its actual calendar-adjacent source months. Complete-case masks
  are explicit. Compare each augmented model with its dynamic/calendar comparator
  on identical rows; do not compare unequal samples as an incremental contribution.
- Conditional OLS with NumPy least squares and the already tested three-calendar-
  lag Bartlett Newey-West implementation, correction `n/(n-p)`. Full rank, finite
  output and >=20 residual degrees of freedom required, else `not_estimable`.
  Show all coefficients/conditional 95% intervals, rank and sample sizes; no
  significance-based model selection or causal attribution. No new hypothesis-test
  family or claimed empirical interval coverage.
- Report in-sample R² for target changes, adjusted R² and residual error, without
  a minimum fit target. Separately train through 2024-12 and score all eligible
  2025 months, with no model selection from that window. Compare on paired rows.
  This is retrospective, conditional **one-month-ahead** prediction: observed
  prior-month registrations anchor each count prediction. It is not a fixed-origin
  12-month or historical real-time forecast; vintage/availability is unverified.
- Count prediction is `expm1(log1p(y[t-1]) + predicted_change[t])`, without clipping
  or data-selected corrections. Show RMSE/MAE and negative predictions. R² on the
  change scale can be negative out of sample. Preserve poor or contradictory results.
- Rank eight largest absolute **training** residuals of the fixed macro model
  as research leads; show 2025 errors separately. Link documented ledger events
  from each month and the previous three calendar months. Date precision/status
  and source links remain visible. These are post-hoc hypotheses, not causes or
  new regressors. Do not turn unknown launch/promotion coverage into zero.

## Product and delivery

Make observed series, coverage, fixed models, paired comparisons and unexplained
peaks the main Studio view. Keep the old synthetic UI explicitly in an archive.
Private observed values/results stay outside Git, images and public CI artifacts.
Any external interpretation requires a separate explicit preview/consent; existing
synthetic-only consent is not permission to transmit empirical data.

Use the existing Azure VM/HTTPS/Key Vault setup. Do not request API keys in chat.
The environment has no authenticated Azure connector; any required Cloud Shell
step is supplied as a concrete command for the account owner. Report the actual
live URL/check separately from local tests and CI. No automatic merge.
