# Architecture decisions (initial)

## Five workstreams, one integrated vertical slice
1. Data Hub: ingest, provenance, quality checks.
2. MMM Engine: adstock, Hill, linear model, recovery checks.
3. Stability Engine: version comparison, uncertainty, detection limits.
4. MCP / Agent: narrowly scoped tools with explicit schemas.
5. Reporting: reproducible Markdown first; UI/PPTX later.

## Data path
`raw observed KBA registrations` -> immutable baseline -> `synthetic media generator` -> `semi-synthetic outcome generator` -> `model manifest` -> `fit` -> `diagnostics` -> `version comparison` -> `MCP tool` -> `Markdown report`.

Keep the observed KBA target and injected synthetic target in distinct fields and artifacts. Never overwrite or present injected outcomes as observed sales. A reproducible generator must save the seed and true adstock/Hill coefficients.

## Runtime boundaries
- Python may orchestrate pipelines, manifests and MCP.
- R may run MMM estimation through a CLI consuming a manifest + CSV and emitting JSON. Confirm tool availability before selecting R-only implementation.
- HypoForge R/Python dependencies must be inspected and pinned before production use.
- Persist machine-readable diagnostics and evidence; do not depend on free-form LLM interpretation for numbers.

## Deferred
Full dashboard, PPTX, email/Power Automate, Nielsen/Circana licensed feeds, autonomous meetings/Dots, NVIDIA GPU use case, VAR/SVAR implementation. Document design seams without stubs or claims of functionality.
