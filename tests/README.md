# Contract checks

Run `python3 -m unittest discover -s tests -v` from repository root with
`jsonschema==4.26.0`. The suite validates four JSON Schemas, a synthetic manifest/CSV,
and rejection of invalid provenance, target substitution, truth leakage into the
manifest, missing/invalid values, dates, checksum mismatch and temporal overlap.
These are contract tests, not MMM estimation, recovery or external-source tests.

`test_validation_edges.py` covers all existing schema regex fields, ASCII month/path/hash
boundaries, traversal/encoded paths and symlinks; additional CSV number/blank/header/
split/provenance cases cover gaps in the original suite. Scientific notation, quoted
fields and CRLF have positive checks. The suite runs in GitHub Actions on push and
pull request; the PR records actual remote results separately from local results.
