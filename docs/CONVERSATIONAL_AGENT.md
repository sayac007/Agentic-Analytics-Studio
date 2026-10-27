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
Requests explicitly use `service_tier:default`. Responses with a different model
or tier stop the loop and keep their uncertain reservation rather than silently
pricing another service. The input guard reserves UTF-8 request bytes plus a
4,096-token structural allowance, checks actual returned usage and stops on any
overrun. It is a conservative local estimate, not exact preflight API tokenization.

## Context, tools and persistence

External mode requires a preview and explicit confirmation for the exact current
question/context hash. The preview contains fixed synthetic project configuration,
selected/latest verified run references and at most two prior external turns from
the same project, explicitly labelled unverified interpretation/history. Raw local
notes, unexecuted proposals, bundles, source files and other projects are excluded.
Human-approved decision text is included only if explicitly selected for this
preview. Permission is for synthetic content only; users must not submit private
empirical data or credentials as questions. Recognizable credentials are rejected.
History is selected by UTF-8 byte budget, dropping oldest selected turns with an
explicit omitted/truncated indicator, so long histories cannot permanently block
new questions. Secret-pattern checks are a secondary guard, not a general-purpose
private-data detector: the user's synthetic-only confirmation remains required.

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

## Start locally or configure a genuine provider call

Install the existing `requirements-demo.lock` and run `python -m demo` as before.
Local mode remains the default. Stop the server before changing configuration.
Back up an existing workspace directory while stopped before first schema-2 startup;
the additive migration is transactional and tested, not a downgrade mechanism.

Linux/Bash, in a private terminal, with a separately billed OpenAI API account:

```sh
export AAS_OPENAI_ENABLED=1
read -r -s -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
.venv/bin/python -m demo
```

Do not paste keys into chat, browser fields, source files or shell command literals.
No API key was supplied for this implementation, so no live request was executed.
The model snapshot/endpoint/rate card are fixed in the server; prompts or browser
requests cannot select another model, endpoint, tariff tier or statistical method.

Open the selected project, run the local synthetic analysis, choose OpenAI and ask
“Warum ist der Mediaeffekt so unsicher?”. The first submit only creates a local
preview. Inspect it, optionally select up to three approved decisions, certify
synthetic-only content, then use the separate paid-send button. Changing the
question, selection, run or project invalidates the preview/consent. A changed
server-side snapshot also requires fresh confirmation.

Ask “Vergleiche das mit dem anderen Modell.” in the next round. Inspect the actual
tool execution references, coefficient/interval/comparison evidence and reported
usage. Stop/restart using the same workspace and continue in English or German;
at most two previous completed external rounds are selected, never the entire local
transcript. Local decision approval does not authorize external transmission.

The UI separates model-generated interpretation, deterministic tool evidence,
reported token usage and estimated USD. Incomplete/refused/malformed/failed replies
are errors, not fabricated local answers. Completed tool work remains recorded even
if later provider/interpretation processing fails. Provider request IDs, exact
selected context hash and usage/cost records persist. Unknown reservations stay
charged against the workspace-wide guard across project switches and restarts.
There is no UI budget reset, automatic retry or automatic model/statistics tuning.

For genuine live acceptance, record the completed round, real provider response ID,
actual tool ID and usage after these steps. A success requires the external service;
the tests below use fakes and do not establish live availability or account access.
Human review remains necessary for model prose. The archived numerical files and
validated tool outputs remain the authority, not statements generated by the model.

## Observed implementation verification

Linux, Python 3.12.14, existing pinned runtime; no new runtime dependency:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v
python scripts/workspace_browser_smoke.py
python scripts/conversation_browser_smoke.py
python -m research_benchmark.verify results/task02
```

- Full suite: **375 passed in 91.173s**. New checks include schema-1 migration with
  unchanged rows/bundle bytes, concurrent workspace/turn budgets, unknown usage
  after restart, hash-bound context, excluded notes and foreign IDs, strict tools,
  one-fit/two-tool/three-request limits, failure linkage, secret/error sanitization,
  model/tier checks, Unicode history bounds and real HTTP orchestration.
- The real HTTP conversation test uses a real application and fresh synthetic fit,
  with a deliberately injected fake provider. It verifies actual coefficient/interval
  evidence and durable model-text labels. It does not establish provider language
  quality, live account access or a real billed conversation.
- Existing workspace Chromium smoke passed, including actual fits, real process
  restart, project separation, comparison and byte-identical report.
- Conversation Chromium smoke passed with a real local app/fit and explicitly
  TEST-FAKE provider endpoints: preview/consent/hash binding, optional approved
  decision selection, state changes, escaped interpretation/evidence/usage, timeout
  reservation display, no retry/fallback and 390px layout. **NO LIVE OPENAI REQUEST.**
- Both manifest/generator example checks, JavaScript syntax, diff checks and
  `pip check` passed. The preserved archive passed its unchanged full verifier:
  18,000 truth rows, 36,000 evaluations, 36 summaries. Git comparison confirmed
  `results/task02`, protocols, statistical engine/contracts/config unchanged.

Remote CI is reported in the PR only after observed completion. Current scope is
the existing synthetic demo and allowlisted tools; no automatic access to the
Research Task 02 archive, private empirical studies or arbitrary datasets is added.
**Remaining live acceptance: LIVE API NOT VERIFIED because no runtime key exists.**
The manual steps above are required before claiming a genuine provider-backed
conversation succeeded. No API credentials should be sent through this chat.
