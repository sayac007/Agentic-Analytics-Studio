# Contract tests

From repository root with Python 3.12 and `jsonschema==4.26.0`:
`python3 -m unittest discover -s tests -v`.

The original safety/provenance assertions are migrated to v0.2.0's separate
estimator/reference CSVs. All month/path/hash/Git-SHA patterns live in shared offline
schema definitions and retain positive/negative traversal, whitespace, nonfinite,
header, split, count and lineage tests. Generator-only count tests are not discarded.

Statistical-contract checks reject reference/truth fields at estimator boundaries,
prove manifest validation reads only estimator data, check a full private file graph,
benchmark admission, break evidence, intervals/contributions, common grids, artifact
binding, recovery/detection arithmetic and the prohibition on uncalibrated MDE flags.
Temporary file graphs and coefficients are hand-authored shape tests, not generated
DGP outputs or fitted models. `purpose=contract_fixture` prevents benchmark use.

CI executes the same suite and both committed interface examples. Actual remote
status belongs to its exact Actions run; no model recovery/coverage claim follows.
