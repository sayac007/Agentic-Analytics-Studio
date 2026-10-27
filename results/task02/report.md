# Research task-02: when does the synthetic media effect recover?

1000 seeds per cell; full preregistered grid, no tuning.

Only synthetic data. Rejection is not reliable recovery if null size, sign or coverage fails.

| Cell | Model | SNR median | β̂/β median [Q1,Q3] | Rejection ± MCSE | Positive detection | Wrong-sign rejection | Coverage ± MCSE | Failed |
|---|---|---:|---|---|---:|---:|---|---:|
| legacy-always_on-independent-0 | with-quarter | 0.000 | undefined (null) | 0.166 ± 0.012 | 0.014 | 0.152 | 0.834 ± 0.012 | 0 |
| legacy-always_on-independent-0 | without-quarter | 0.000 | undefined (null) | 0.113 ± 0.010 | 0.021 | 0.092 | 0.887 ± 0.010 | 0 |
| legacy-always_on-independent-0.08 | with-quarter | 0.138 | 0.080 [-1.228, 1.471] | 0.095 ± 0.009 | 0.044 | 0.051 | 0.834 ± 0.012 | 0 |
| legacy-always_on-independent-0.08 | without-quarter | 0.138 | 0.490 [-0.900, 1.902] | 0.094 ± 0.009 | 0.070 | 0.024 | 0.887 ± 0.010 | 0 |
| grid-always_on-independent-0 | with-quarter | 0.000 | undefined (null) | 0.149 ± 0.011 | 0.014 | 0.135 | 0.851 ± 0.011 | 0 |
| grid-always_on-independent-0 | without-quarter | 0.000 | undefined (null) | 0.118 ± 0.010 | 0.026 | 0.092 | 0.882 ± 0.010 | 0 |
| grid-always_on-independent-0.03 | with-quarter | 0.088 | -0.231 [-2.385, 2.016] | 0.113 ± 0.010 | 0.039 | 0.074 | 0.851 ± 0.011 | 0 |
| grid-always_on-independent-0.03 | without-quarter | 0.088 | 0.324 [-1.923, 2.649] | 0.097 ± 0.009 | 0.054 | 0.043 | 0.882 ± 0.010 | 0 |
| grid-always_on-independent-0.08 | with-quarter | 0.235 | 0.538 [-0.269, 1.381] | 0.141 ± 0.011 | 0.111 | 0.030 | 0.851 ± 0.011 | 0 |
| grid-always_on-independent-0.08 | without-quarter | 0.235 | 0.747 [-0.096, 1.618] | 0.156 ± 0.011 | 0.141 | 0.015 | 0.882 ± 0.010 | 0 |
| grid-always_on-independent-0.15 | with-quarter | 0.441 | 0.754 [0.323, 1.203] | 0.323 ± 0.015 | 0.319 | 0.004 | 0.851 ± 0.011 | 0 |
| grid-always_on-independent-0.15 | without-quarter | 0.441 | 0.865 [0.415, 1.330] | 0.353 ± 0.015 | 0.349 | 0.004 | 0.882 ± 0.010 | 0 |
| grid-always_on-calendar_aligned-0 | with-quarter | 0.000 | undefined (null) | 0.136 ± 0.011 | 0.029 | 0.107 | 0.864 ± 0.011 | 0 |
| grid-always_on-calendar_aligned-0 | without-quarter | 0.000 | undefined (null) | 0.532 ± 0.016 | 0.532 | 0.000 | 0.468 ± 0.016 | 0 |
| grid-always_on-calendar_aligned-0.03 | with-quarter | 0.186 | 0.099 [-2.332, 2.332] | 0.119 ± 0.010 | 0.053 | 0.066 | 0.864 ± 0.011 | 0 |
| grid-always_on-calendar_aligned-0.03 | without-quarter | 0.186 | 6.690 [4.942, 8.659] | 0.669 ± 0.015 | 0.669 | 0.000 | 0.468 ± 0.016 | 0 |
| grid-always_on-calendar_aligned-0.08 | with-quarter | 0.495 | 0.662 [-0.250, 1.499] | 0.153 ± 0.011 | 0.125 | 0.028 | 0.864 ± 0.011 | 0 |
| grid-always_on-calendar_aligned-0.08 | without-quarter | 0.495 | 3.134 [2.478, 3.872] | 0.857 ± 0.011 | 0.857 | 0.000 | 0.468 ± 0.016 | 0 |
| grid-always_on-calendar_aligned-0.15 | with-quarter | 0.928 | 0.820 [0.334, 1.266] | 0.312 ± 0.015 | 0.309 | 0.003 | 0.864 ± 0.011 | 0 |
| grid-always_on-calendar_aligned-0.15 | without-quarter | 0.928 | 2.138 [1.788, 2.532] | 0.968 ± 0.006 | 0.968 | 0.000 | 0.468 ± 0.016 | 0 |
| grid-flighting-independent-0 | with-quarter | 0.000 | undefined (null) | 0.124 ± 0.010 | 0.052 | 0.072 | 0.876 ± 0.010 | 0 |
| grid-flighting-independent-0 | without-quarter | 0.000 | undefined (null) | 0.095 ± 0.009 | 0.041 | 0.054 | 0.905 ± 0.009 | 0 |
| grid-flighting-independent-0.03 | with-quarter | 0.466 | 0.939 [0.479, 1.371] | 0.455 ± 0.016 | 0.452 | 0.003 | 0.876 ± 0.010 | 0 |
| grid-flighting-independent-0.03 | without-quarter | 0.466 | 0.949 [0.457, 1.431] | 0.405 ± 0.016 | 0.404 | 0.001 | 0.905 ± 0.009 | 0 |
| grid-flighting-independent-0.08 | with-quarter | 1.242 | 0.977 [0.805, 1.139] | 0.993 ± 0.003 | 0.993 | 0.000 | 0.876 ± 0.010 | 0 |
| grid-flighting-independent-0.08 | without-quarter | 1.242 | 0.981 [0.797, 1.162] | 0.986 ± 0.004 | 0.986 | 0.000 | 0.905 ± 0.009 | 0 |
| grid-flighting-independent-0.15 | with-quarter | 2.329 | 0.988 [0.896, 1.074] | 1.000 ± 0.000 | 1.000 | 0.000 | 0.876 ± 0.010 | 0 |
| grid-flighting-independent-0.15 | without-quarter | 2.329 | 0.990 [0.891, 1.086] | 1.000 ± 0.000 | 1.000 | 0.000 | 0.905 ± 0.009 | 0 |
| grid-flighting-calendar_aligned-0 | with-quarter | 0.000 | undefined (null) | 0.133 ± 0.011 | 0.065 | 0.068 | 0.867 ± 0.011 | 0 |
| grid-flighting-calendar_aligned-0 | without-quarter | 0.000 | undefined (null) | 0.480 ± 0.016 | 0.479 | 0.001 | 0.520 ± 0.016 | 0 |
| grid-flighting-calendar_aligned-0.03 | with-quarter | 0.517 | 1.023 [0.425, 1.554] | 0.364 ± 0.015 | 0.362 | 0.002 | 0.867 ± 0.011 | 0 |
| grid-flighting-calendar_aligned-0.03 | without-quarter | 0.517 | 2.354 [1.783, 2.833] | 0.855 ± 0.011 | 0.855 | 0.000 | 0.520 ± 0.016 | 0 |
| grid-flighting-calendar_aligned-0.08 | with-quarter | 1.378 | 1.009 [0.784, 1.208] | 0.931 ± 0.008 | 0.931 | 0.000 | 0.867 ± 0.011 | 0 |
| grid-flighting-calendar_aligned-0.08 | without-quarter | 1.378 | 1.508 [1.294, 1.687] | 1.000 ± 0.000 | 1.000 | 0.000 | 0.520 ± 0.016 | 0 |
| grid-flighting-calendar_aligned-0.15 | with-quarter | 2.583 | 1.005 [0.885, 1.111] | 1.000 ± 0.000 | 1.000 | 0.000 | 0.867 ± 0.011 | 0 |
| grid-flighting-calendar_aligned-0.15 | without-quarter | 2.583 | 1.271 [1.157, 1.367] | 1.000 ± 0.000 | 1.000 | 0.000 | 0.520 ± 0.016 | 0 |

## Grid thresholds (not validated MDE)

| Design | Confounding | Model | Null rejection | Two-sided ≥80% grid threshold | Positive ≥80% grid threshold |
|---|---|---|---:|---|---|
| always_on | independent | with-quarter | 0.149 | >15% / not reached | >15% / not reached |
| always_on | independent | without-quarter | 0.118 | >15% / not reached | >15% / not reached |
| always_on | calendar_aligned | with-quarter | 0.136 | >15% / not reached | >15% / not reached |
| always_on | calendar_aligned | without-quarter | 0.532 | 8% | 8% |
| flighting | independent | with-quarter | 0.124 | 8% | 8% |
| flighting | independent | without-quarter | 0.095 | 8% | 8% |
| flighting | calendar_aligned | with-quarter | 0.133 | 8% | 8% |
| flighting | calendar_aligned | without-quarter | 0.480 | 3% | 3% |

## Interpretation limits

The old small condition number/stability flags do not establish identification. New flags are interval/support heuristics, not causal tests.
Always-on baseline misspecification, narrow transformed spend, confounding and finite-sample HAC calibration can drive bias, wrong signs and false positives.
No curve fitting, lag search, scenario retuning or significance selection. No empirical data or real marketing ROI.
Wilson bounds and denominators are in summary.csv; seed-level truth/evaluations include SNR and every failure. Continuous MDE and general coverage claims are not established.

## Reproduction and artifact identity

`python -m research_benchmark.run --output NEW_DIRECTORY` with pinned requirements-attention.lock and single-thread BLAS.
The existing synthetic baseline, frozen new protocol, implementation versions and output hashes are bound in manifest.json only.
