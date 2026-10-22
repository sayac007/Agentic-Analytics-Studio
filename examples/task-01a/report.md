# Synthetic Stage-A recovery benchmark

All reference, media and outcomes are synthetic. Not observed Tesla data or real causal marketing ROI.

One seed, 60 training months and 12 holdout months. Fixed oracle transforms; deliberately incomplete baseline.
Conditional HAC intervals do not establish actual 95% coverage, empirical power or a validated MDE.

Planted media coefficient: 307.856266596; noise SD: 139.875000000.

| Run | beta | conditional 95% interval | Holdout RMSE | holdout contribution | beta error | curve RMSE | interval contains truth (one run) |
|---|---:|---|---:|---:|---:|---:|---|
| with-quarter | -418.880454772 | [-1984.707707846, 1146.946798303] | 327.594500281 | -3757.133746794 | -726.736721367 | 565.248406486 | True |
| without-quarter | -460.563321034 | [-2173.522423988, 1252.395781920] | 350.282041967 | -4131.006773601 | -768.419587629 | 597.668914545 | True |

Contributions and response errors use count-equivalent units; spend is synthetic currency per month.
Relative response change: 0.090504094; declared sensitivity flags: [].
The comparison limit is a predeclared engineering sensitivity rule, not a scientific detection threshold.
`detection_limit_status=not_calibrated`; `effect_below_detection_limit=null`.

## Artifact identity

- `private/reference.csv`: `53b6c185afa1009047bc9c7cc934c51caf63866c03c3b16dd3a02ffb80732181`
- `private/generator.json`: `25fb178fc3930f8a75f625ec87b71209832517917f89e9c1e6620d3819cc742f`
- `safe/data.csv`: `1700c002d5712cad3ea18c857ad707331541a1d2d992831466187b60a0d04fe0`
- `private/truth.json`: `ac3f5f578725bdc2ed9658e47e5f96600723b7258ae2cd1ab1280452af046961`
- `safe/with-quarter.manifest.json`: `1f1a70be4981f4e9b9acde9e1d3a1544256e55ca5a0d73dd66404a80160c5896`
- `safe/with-quarter.result.json`: `dd049a407f9517b300d820ce639eb8777e12975d2a2a43d59e6f4057ac367d44`
- `safe/without-quarter.manifest.json`: `2f22e367f2e4393bcdef23beb11aea4b2050760f5996908897a2f28f2ccb6951`
- `safe/without-quarter.result.json`: `be9b10aab2fae4090a3e2a2a186a4fd7db3efd8bdb7eb4140ad38c9ee9049a3f`
- `comparison.json`: `27f4fc7ffd3f8c1c904c062976a88f6bf226b2a79a66e16efacf0159ce117334`

Every artifact, including prediction CSVs and access records, is hashed in inventory.json.
Reference/truth are evaluator-only. The estimator processes ran in separate workspaces without those files.
Known transforms do not remove bias from omitted baseline disturbances. No recovery tuning was performed.
