# Task 03A — persistent local synthetic workspace

Implement the bounded scope and acceptance checks in
[the reviewed architecture decision](../../RESEARCH_WORKFLOW.md).
Use SQLite and the unchanged Task 02 synthetic engine; persist two separate project
conversations, proposed/human-approved decisions, real tool logs and validated bundles.
Prove restart, project separation, failure handling and the existing browser workflow.
No general LLM, live data acquisition, reconciliation engine, Codex execution, new
statistical method or external publication. One draft PR; no automatic merge.

Acceptance executed on Linux:

- [x] Two explicitly synthetic projects, separate conversations/results/default models.
- [x] Typed statements, stored proposals and separate explicit human approvals.
- [x] Real tool executions, durable original bundles, revalidation before use.
- [x] Actual process restart and interrupted-process handling without automatic retry.
- [x] Project/legacy-route isolation, failure/corruption refusal and atomic rollback.
- [x] Existing analytics and real browser workflow preserved; 348 full-suite tests pass.
- [x] Scope and official Codex/LLM-interface documentation assessed before code.
- [x] Draft PR #26 created; observed remote CI results recorded in the PR.

General conversational AI, empirical project import and development execution remain
explicitly deferred. See the architecture decision for commands, limitations and
the next bounded product step.
