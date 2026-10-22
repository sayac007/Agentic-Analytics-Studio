`contracts.yml` uses Python 3.12 and the full immutable dependency lock (including the
audited HypoForge Git commit). It validates the original contract fixtures, runs all
contract/numerical/isolation tests, then generates and verifies a small single-seed
Stage-A bundle. BLAS/OpenMP use one thread. This is not a power/coverage/MDE experiment
or a real Tesla pipeline. Check actual run status separately from local results.
