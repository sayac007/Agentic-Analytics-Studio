# Contract checks

Run `python3 -m unittest discover -s tests -v` from repository root with
`jsonschema==4.26.0`. The suite validates four JSON Schemas, a synthetic manifest/CSV,
and rejection of invalid provenance, target substitution, truth leakage into the
manifest, missing/invalid values, dates, checksum mismatch and temporal overlap.
These are contract tests, not MMM estimation, recovery or external-source tests.
