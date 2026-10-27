# Task 03B: bounded conversational analytics

## Independent assessment before implementation

Baseline reviewed on 2026-10-27: main `3b927a4`, merged Task 03A, durable original
Research Task 02 archive, existing FastAPI/static application, SQLite and six
allowlisted analytics tools. The archive passed its existing verifier before work.
No changes to research outputs, statistical protocols, estimator or contracts are
needed. A real provider conversation is now a useful product increment.

The proposal needs three qualifications. A synthetic project can contain private
notes; project membership and decision approval are not outbound consent. Model
text is an interpretation, not a verified measurement. Finally, request retries,
lost usage and restarts can incur real cost even without a displayed answer.
These require bounded selected context, explicit outbound permission, trustworthy
tool evidence and a durable conservative budget ledger, not a general framework.

Use one provider through the documented OpenAI Responses REST API and standard
library HTTPS. Keep the local deterministic mode. No SDK/framework/provider
abstraction or vector database is needed for this slice. The chat becomes the
primary UI; plots and reports remain evidence. No developer execution/MCP/Codex.

## Provider and cost decision

Official pages retrieved and inspected on 2026-10-27:

- https://developers.openai.com/api/reference/resources/responses/methods/create
- https://developers.openai.com/api/docs/guides/function-calling
- https://developers.openai.com/api/docs/guides/your-data
- https://developers.openai.com/api/docs/models/gpt-5.4-mini
- https://developers.openai.com/api/docs/quickstart

Choose documented snapshot `gpt-5.4-mini-2026-03-17`, Responses/function calling,
reasoning effort `none`. The model page's standard USD rate per million tokens is
input 0.75, cached input 0.075, output 4.50. This is a dated rate-card snapshot,
not a promise of future billing. The pricing homepage returned 403 in this
environment; no personal access to that page or billing help pages is claimed.
ChatGPT subscriptions do not supply this application's API key or API budget.

Server configuration: `AAS_OPENAI_ENABLED=1` plus `OPENAI_API_KEY`. Disabled by
default; no key, browser-side key, alternate endpoint or paid call is silently
required. This environment has no configured key: **LIVE API NOT VERIFIED**.
`store:false` disables Responses storage, not all provider retention; default
abuse-monitoring retention can be up to 30 days, with documented exceptions.

Initial fixed limits: three provider requests, two custom tool calls and one fixed
synthetic fit per turn; 1,536 maximum output tokens per request, bounded serialized
request bytes and response bytes, finite timeout, no retries. Reserve a conservative
rate-card ceiling before sending each request. A turn has a USD0.10 guard and the
whole workspace a USD1.00 lifetime guard. Actual available token usage is recorded;
token-based USD estimates are labelled estimates. Unknown usage/timeouts/interrupted
requests retain their full reservation. Restart must not reset the ledger. This
local guard does not replace provider billing limits or guarantee an invoice cap.

## Context, tools and persistence

External mode requires a preview and explicit confirmation for the exact current
question/context hash. The preview contains fixed synthetic project configuration,
selected/latest verified run references and at most two prior external turns from
the same project, explicitly labelled unverified interpretation/history. Raw local
notes, unexecuted proposals, bundles, source files and other projects are excluded.
Human-approved decision text is included only if explicitly selected for this
preview. Permission is for synthetic content only; users must not submit private
empirical data or credentials as questions. Recognizable credentials are rejected.

Only strict function schemas for existing tools are exposed. Names/arguments/run
ownership are checked locally. Tool results sent to OpenAI are bounded whitelisted
synthetic projections; `resume_workspace` never transmits its raw transcript/context.
Models cannot approve decisions, read paths, execute expressions, edit outputs or
modify software. Tool actions and evidence remain deterministic and persistent.

Schema version 2 adds AI turns and per-request budget/usage records through a
transactional version-1 migration. Existing records/bundles are preserved. New
assistant text has an explicit LLM-interpretation kind. Crashes mark incomplete
turns interrupted, retain uncertain charges and never retry automatically.

## Acceptance and verification

Required checks: project isolation, exact preview consent, bounded context and
history, strict tool rejection, tool/provider failures, interruption/restart,
secret safety, persistent budgets and existing MMM behavior. Provider fakes are
deterministic tests, not live evidence. Live verification requires a separately
configured runtime key, permitted synthetic preview and actual provider/tool IDs.
Commands, observed test/CI evidence and remaining limitations will be completed
after execution. The preserved Task 02 archive remains byte-identical.
