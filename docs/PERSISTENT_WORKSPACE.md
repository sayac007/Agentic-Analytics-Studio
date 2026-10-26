# Task 03A: persistent local workspace

## Independent assessment before implementation

Reviewed against main `77fb75b` on 2026-10-26. The product Task 02 MVP
(`demo/`) and the research Task 02 benchmark (`research_benchmark/`) are separate.
The former really uses FastAPI, static browser assets, five allowlisted tools,
two fixed model specifications and the existing validated synthetic pipeline.
`demo.app.RUNS` retains only five results; `demo.service.compute` deletes its
temporary artifact bundle. Context and results therefore disappear on restart.
The statistical engine needs no rewrite. The application needs a modest state
refactor, bounded to one focused PR; this is moderate integration work, not a new
statistics project.

Persistence is the next useful product increment. A general conversational agent
is a separate milestone: durable facts and tool lifecycle must exist before model
text can select actions. Calling this increment general AI would be misleading.
Two projects do not demonstrate arbitrary data support: both explicitly reuse the
same monthly, seed-42 synthetic asset, with different default model specifications.
The example Tesla discussion is a future use case, not imported project history.

Rejected alternatives: JSON transcript files lose relational/transactional safety;
PostgreSQL, embeddings/vector search and a multi-agent framework solve no current
need. Adding a paid LLM now introduces disclosure, cost, credential and tool-authority
decisions without fixing lost work. A synchronous single local process is adequate
for these short fixed fits; no queue, auto-retry or background scheduler is needed.

## Scope and acceptance

1. Open either of two named synthetic projects. Each has its own durable conversation,
   default model, explicit dataset/frequency/target/provenance and independent history.
2. Save messages, typed proposed/explicitly approved decisions, tool executions and
   original validated synthetic analysis bundles. No five-result eviction.
3. Restore conversation, selected historical results, comparisons and reports after
   a real process restart. Show project context from stored facts and verified tools.
4. Free text becomes a user note plus an honest deterministic acknowledgement.
   Existing fixed tool requests still execute real tools. A resume action reports
   actual state; no fictitious reasoning, conversation, result or general LLM reply.
5. Test cross-project rejection, interrupted/failed work, corruption, restart and
   actual browser use. Preserve all numerical contracts and estimator isolation.

## Decisions and boundaries

- **Storage:** standard-library SQLite, schema version 1, foreign keys and short
  transactions. One process/worker owns a workspace through an OS process lock.
  Startup refuses corruption/unsupported schemas and marks unfinished tool calls
  interrupted; it never retries or invents success. No transaction spans a fit.
- **Location:** server-only `AAS_WORKSPACE_DIR`, default `.aas-workspace/` in the
  launch directory, excluded from Git. Private owner directory, database and lock;
  reject symlink storage entries. No browser-supplied paths or empirical imports.
  SQLite plus its `runs/` directory constitute the workspace; not the database alone.
- **Identity:** fixed project IDs, one durable conversation per project in v1,
  opaque run/execution/decision IDs. All new routes and lookups are project-scoped.
  Legacy Task 02 endpoints remain restricted to the first project; knowing another
  project's run ID does not grant access. This is local separation, not multiuser auth.
- **Facts versus text:** messages retain role and kind (statement, acknowledgement,
  tool result or error). Project configuration, executions, runs and decisions are
  structured records, never facts inferred from transcript text. Approval requires
  a separate human UI/API action; tool handlers cannot approve decisions.
- **Context:** recent 40 messages and 20 runs/executions/decisions, with full records
  remaining in SQLite and older runs directly addressable by ID. No semantic search,
  transcript-derived memory or silent truncation presented as complete history.
- **Results:** retain the original immutable pipeline bundle, inventory hash, data
  identity, software and estimator configuration. Validate before a single atomic
  run/success commit, then verify bundle/hash again before use. A cached conversation
  cannot substitute for artifact verification. Hashes detect corruption, not a
  malicious local owner who can rewrite both database and files.
- **Permissions:** the existing registry remains the only analytics tool boundary;
  tools read the selected project or execute the fixed synthetic fit. Log lifecycle
  and sanitized failures, never raw subprocess/environment secrets. Unknown text
  executes nothing. No LLM credentials are requested, stored or read.
- **Compatibility/security:** preserve loopback, trusted-host and same-origin
  restrictions and escaped text rendering. One local owner, no network deployment,
  account system, arbitrary file explorer, cross-project tools or self-modification.
  Disk usage grows with runs; manual offline backup/retention is needed before
  substantial production use. No migration of old process-only history is possible.

## Official integration evidence and next steps

These official pages were actually retrieved on 2026-10-26 (HTTP 200), inspected
as documentation, and not executed as integrations:

- [Codex SDK](https://developers.openai.com/codex/sdk/), redirected to
  `https://learn.chatgpt.com/docs/codex-sdk`: documented TypeScript
  `@openai/codex-sdk` thread/run/resume interfaces and a Python SDK. Direct execution
  is technically available; no package/authentication/run was tested here.
- [Non-interactive Codex](https://developers.openai.com/codex/noninteractive/),
  redirected to `https://learn.chatgpt.com/docs/non-interactive-mode`: `codex exec`,
  structured output and sandbox/credential controls. A future development worker
  must have a separate checkout, credentials and explicit action approvals.
- [GitHub integration](https://developers.openai.com/codex/integrations/github/),
  redirected to `https://learn.chatgpt.com/docs/third-party/github`: PR comments such
  as `@codex review` require a connected/configured repository. A saved work order
  or a manually opened issue is a handoff, not proof that Codex ran. No such comment,
  issue handoff, development execution or deployment is triggered by this application.
- [Function calling](https://platform.openai.com/docs/guides/function-calling),
  redirected to `https://developers.openai.com/api/docs/guides/function-calling`:
  documented tool requests are executed by the host application. A future runtime
  provider needs explicit cost/data scope, strict schemas, bounded tool rounds,
  cancellation/timeouts and honest unavailable/error states. Structured tool output
  remains the authority for every number. No LLM integration is claimed in 03A.

The smallest development bridge is a stored, explicitly unexecuted development-work
order alongside decisions, manually handed to an external agent. It grants no source
edit permission. Next practical product step after acceptance: one real provider
using the persisted selected-project context and the same tool boundary, under an
explicit budget/data-use decision. Email ingestion, version reconciliation (including
small systematic revisions), new MMM specifications, storylines and presentation
rehearsal each need their own substantive slice; none requires a speculative framework
now. No 0.1% automatic acceptance rule is introduced.

## Implementation and validation evidence

Implementation, exact commands, observed results and remaining limits are recorded
below and in the PR after execution; the acceptance list above is a target, not a
claim that tests or integrations have already passed.
