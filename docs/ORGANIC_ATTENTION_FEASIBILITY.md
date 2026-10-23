# Task 01E — Organic Attention Data Feasibility

Research date: **2026-10-23**. Target: **2018-01–2025-12 (96 months)**;
Tesla/BEV common window: **2021-01–2025-12 (60 months)**.
Start condition verified: [PR #6](https://github.com/sayac007/Agentic-Analytics-Studio/pull/6)
merged at 2026-10-23 09:36:23 UTC, merge
`e8b261d90d9495702c73e9c6d288e49d785dfb6e`; branch starts from that current main.

## Finding and decision

**No real historical attention observations were obtained.** The default dataset is
explicitly **`not empirically populated`**, not an empirical series of zeros. All
96 months are unknown; all 60 common-window months are unknown. No real video,
comment, view counter, Trends value, author or sentiment score is redistributed.
There is currently **no empirically validated Organic-Attention series** to join to KBA.

There are plausible conditional routes, especially a lawful Google Trends DE export
and a fixed-channel YouTube publication inventory. Their measurement semantics are
useful, but **complete 2018–2025 availability, lawful retention and empirical
reproducibility are not established by this task's access tests**. Environment
restrictions and missing credentials are distinct from global source unavailability.
Do not conclude that a German attention series is impossible, or that attention was
absent. Historical German audience/view reach is a substantially harder requirement
than retrospectively counting surviving German-language publications.

A small executable offline YouTube-shape adapter and synthetic fixtures demonstrate
monthly timestamp handling and safeguards. This is the workorder's explicit fallback,
not a manufactured empirical prototype. It does not add a network collector, sentiment
model, social-listening platform, regression or simulation.

## Evidence and actual access tests

The machine-readable [source catalog](../data/organic_attention/sources.json) records
provider, official URLs, authentication, cost/rate-limit uncertainty, reuse conditions,
historical coverage, geography/language, timestamps, reproducibility and bias for
**11 candidate signals in 8 source families** (YouTube, Trends, Reddit, GDELT,
Media Cloud, Mastodon, Meta and Wikimedia). YouTube Data/Analytics are separate
access products. [Access log](../data/organic_attention/access_log.json) records exact
URLs/parameters, response hashes for retrieved documents and errors; day precision
is retained because individual request times were not logged. Raw HTML stays outside Git.

| Tested route | Actual outcome | What this establishes |
|---|---|---|
| Google Trends Help FAQ and export/citation instructions | HTTP 200, substantive help text read | Sampling/normalization/UTC semantics and supported manual CSV export; **not a Tesla DE series** |
| Official [GoogleTrends/data archive](https://github.com/GoogleTrends/data): README, LICENSE and full nontruncated 590-entry path listing | HTTP 200; repository CC BY 4.0 license read | Lawful public archive exists, but no Tesla-named export identified in filename screening; unrelated German energy/football datasets not substituted. Not an exhaustive file-content search |
| Trends Explore, query `Tesla`, `geo=DE`, `date=2018-01-01 2025-12-31` | HTTP **429**, no data; not retried after rate limiting | Current access failure, no historical observations or returned resolution |
| Canonical YouTube docs and Data API search | Environment proxy CONNECT 403 | Service did not supply a data/error response; do **not** claim YouTube rejected a key or query |
| Candidate Tesla, nextmove and DW Deutsch YouTube video pages | Environment proxy CONNECT 403 | No channel inventory, resolved channel ID, ownership audit or video selection obtained |
| Google's own public GitHub client reference: videos, commentThreads, Analytics reports and service index | HTTP 200, references read and hashed | Public field shapes, comment pagination and owner-report distinction; **not** current quota/pricing/terms verification or platform data access |
| Reddit official help/terms and unauthenticated Tesla query in r/Elektroautos | Environment proxy CONNECT 403 | No posts/comments, no Reddit-side access decision observed |
| GDELT official DOC documentation and January 2025 German-language Tesla timeline query | Environment proxy CONNECT 403 | Historical search horizon and historical results remain unverified |
| Wikimedia docs/legal and exact German Tesla article monthly pageview query, 2018–2025 | Environment proxy CONNECT 403 | No pageview series, response schema or redistribution-license confirmation |
| Media Cloud and Mastodon documentation | Environment proxy CONNECT 403 | No authorized API/instance query performed |
| Meta Content Library | **not tested**; official documentation URL catalogued | No access eligibility, dataset or historical coverage claim |

The official Google GitHub material was public documentation available through the
existing allowed route, not a substitute data endpoint or a way around an API block.
Canonical developer-policy and quota pages remain unread here. Their current legal
conditions/numeric allocations are **NOT VERIFIED**; no memorized quota or price is
presented as a checked 2026 fact. Five relevant variable names were checked for presence
only (`YOUTUBE_API_KEY`, `GOOGLE_API_KEY`, `REDDIT_CLIENT_ID`,
`REDDIT_CLIENT_SECRET`, `MEDIACLOUD_API_KEY`): absent. No secret values were inspected,
requested in chat or committed. No owner/researcher authorization was available.

An additive environment network draft preserves existing domains and adds the official
documentation/API hosts listed in the access log plus `www.mediacloud.org` and
`docs.joinmastodon.org`. Saving that draft does not activate/publish it; subsequent
bounded checks still showed CONNECT denials. Broader egress permission alone did not
resolve them. Environment settings must be reviewed/saved and published to activate
configuration changes. No paywall, CAPTCHA, platform restriction or API ban was bypassed.
No messages to creators/platforms were sent.

## Comparable feasibility matrix

Statuses describe **usable data in this run**, not a claim about all possible future
access. Definitions: `historically_observed` requires a lawful dated measurement
witness; `retrospectively_reconstructable` describes reconstruction from surviving
records or retrospective historical queries, not real-time vintage availability;
`current_snapshot_only` means a retrieval-time measure; `unavailable` means no usable
series under tested conditions; `not_tested` means no adequate data query/verification.
The catalog keeps actual and conditional potential classifications separate.

| Candidate signal | Actual / conditional measurement class | Auth/cost gate | History and geography | Reuse/next gate |
|---|---|---|---|---|
| YouTube publication frequency, Owned/Earned/Community separately | unavailable / retrospectively_reconstructable | Configured API access missing; current quota/cost unverified | Surviving original publication times could cover historical months; no complete inventory or DE audience proved | Review developer storage/refresh/deletion/redistribution policy, freeze real channel IDs and paginate uploads |
| YouTube current views | unavailable / current_snapshot_only | Same Data API prerequisite | Cumulative at retrieval, never 2018–2025 monthly reach; no country audience from public counter | No historical conversion; current counter storage also subject to platform policy |
| YouTube historical views/country report | unavailable / not_tested | Separate owner/content-owner authorization, not public third-party data | Owner report may have date/country dimensions; no public historical third-party panel verified | Lawful owner grant/export and report timezone/privacy review |
| YouTube dated comments | unavailable / retrospectively_reconstructable | Project/API access and enabled comments; current limits unverified | Surviving published comments are engagement, not reach; language/context not author residence | Privacy, deletions, moderation and text/metadata retention assessment; paginate replies separately |
| Google Trends DE | unavailable / retrospectively_reconstructable | Public CSV route documented; actual 429; API access/terms not verified | Geo=DE search origin; sampled normalized interest; exact eight-year returned coverage/granularity unverified | Lawful manual export plus terms/citation review, fixed query/topic/window and repeat-sample assessment |
| Reddit discussions | unavailable / not_tested | Approved app/OAuth and applicable research/commercial terms unverified | Historical census not established; German community is not German audience | Review API/research/deletion/privacy conditions; no third-party archive substituted |
| GDELT news | unavailable / not_tested | Expected public route, not verified here; no numeric limit claim | DOC rolling horizon cannot be assumed to cover 2018; archives/Events/GKG are distinct products; German language != DE readership | Read official historical-product specs; counts/URLs do not license publisher full text |
| Media Cloud news | not_tested / not_tested | Account/key and collection rights unresolved | Actual collection date/source coverage unknown | Review collection access, export and publisher rights |
| Mastodon discussions | not_tested / not_tested | Instance-specific access, rates and rules | No global historical corpus; federation/migration creates gaps | Select lawful instances and inspect pagination/deletion constraints |
| Meta/social-listening research datasets | not_tested / not_tested | Research eligibility/export approval; current costs/rates unknown | No German Tesla archive demonstrated; no commercial listening dataset licensed | Official approval/terms and reproducible dataset version required |
| German Wikipedia Tesla readership | unavailable / not_tested | Public aggregate route expected, request blocked | German project language != German audience; moves/redirects need review | Verify aggregate-data license separately from article text and test actual historical response |

For **each row**, actually obtained coverage is **0/96** and **0/60** months. This is
unknown coverage, not observed inactivity. No source qualifies as
`historically_observed` in this run. No independent-creator or editorial feed has yet
been empirically populated. Candidate handles are discovery targets, not verified
channel IDs or a representative sample; nextmove's commercial operator context and
creator sponsorships require review rather than automatic classification as unpaid Earned.

## Measurement and legal rules

### YouTube publication, snapshot, history and comments

Keep four timestamps/measures distinct:

- `published_at`: original video publication metadata, subject to upload/private/public
  lifecycle review; group by declared calendar timezone.
- `views_at_retrieval`: current cumulative `statistics.viewCount` with retrieval time.
  **Never assign it to the publication month or treat it as past monthly views.**
- `views_at_time_t`: requires an actual historical dated witness/report; none obtained.
  Multiple future snapshots cannot reconstruct the missing past.
- `comments_published_at`: each surviving comment's own publication time, not the
  video's time, current `commentCount`, or comment edit time.

The adapter counts only unique surviving video IDs or top-level comment IDs from a
fixed synthetic channel selection. It ignores limited embedded replies, text and
current counters in aggregation. Real acquisition would need all lawful pagination,
recorded page failures and an explicit reply protocol; a first/empty page never proves
completeness. Deleted/private videos, disabled/moderated comments and unknown original
inventory make retrospective zero and historical audience assertions unsafe.

Owned video supply, independently reviewed creator/editorial Earned supply and
Community supply remain separate. Public-thread comment participation is classified
as Community regardless of host channel; that describes thread engagement, **not
verified independent author identity**. A creator sponsorship must not silently become
organic Earned activity. The fixture categories are synthetic annotations only.

### Geography

Store independent fields for evidence of **audience country**, **German content
context**, **publication language**, and evidence/rationale. Unknown audience country
stays `unknown`, even for German speech about German Tesla deliveries. A channel's
country, availability in DE, German query/community and `regionCode=DE` are not measured
German reach. Trends `geo=DE` is a stronger provider search-origin filter but still
neither audience of a particular creator nor a sample of Tesla buyers. There is no
measured German audience in the prototype.

### Google Trends

Official Help documents sampling, normalization by all searches in the specified
geography/time, subsequent 0–100 scaling, low-volume zeros and statistical noise.
A displayed 0 is not zero searches. Equal indices are not equal absolute search volumes.
Long windows (>=30 days) use UTC, including monthly observations; preserve the returned
monthly bucket semantics instead of moving a monthly index to Berlin by guessing a day.

Proposed frozen specification: automotive Tesla topic **after verifying its actual
ID**, compared separately with literal `Tesla` for ambiguity; geo=DE, web search,
category=0, 2018-01-01–2025-12-31. Do not invent a topic ID. Record exact CSV headers,
frequency, partial-period flags, query URL, retrieval, terms and raw hash. If resolution
is weekly, a separately declared day-weighted monthly index is needed; do not sum
normalized percentages or splice independently scaled downloads. A legal repeated
export protocol must quantify sampling/revision stability; none executed after 429.
The separate API announcement was inaccessible; no verified claim about an API's
alpha eligibility, rolling history horizon or full eight-year coverage is made.

### Sentiment, discussion volume and rights

No suitable historical text corpus was obtained, so **no sentiment or topic series**
is produced. Mention counts are not sentiment. A future text study must predeclare a
lawful corpus, sample/deduplication and deletion rules, language detection, a pinned
German-capable classifier/model/license, **positive/neutral/negative plus uncertain or
unclassifiable** categories, Tesla-entity disambiguation, sarcasm/negation handling and
human-reviewed validation with disagreement/uncertainty. Validate across time and
sources before aggregating; do not represent GDELT tone or a generic model as validated
German Tesla sentiment. No classifier or model is implemented here.

Public visibility is not an open-data license. Real API retention, refresh/deletion,
personal data, commercial/research permissions and redistribution must be reviewed for
each source. Documentation access or permission to download a CSV alone does not
license platform texts, usernames, thumbnails, transcripts or publisher articles.
The GoogleTrends/data repository LICENSE was actually read and is CC BY 4.0; this
applies to that published repository material, not automatically every Trends UI
export. Its archive tree SHA is recorded; no suitable Tesla export was identified
by filename screening. Only our own factual access metadata and synthetic fixtures
are shared. Later lawful
reproduction may use Google-documented exports or approved API queries **after** the
missing policy/access checks; exact future data equality is not guaranteed after edits,
deletions, resampling or revisions.

## Executable fallback and quality diagnostics

```sh
# Python 3.12, no new dependencies, from repository root:
python3 -m attention.transform
python3 -m attention.transform --check
python3 -m unittest discover -s tests -p test_attention.py -v

# Explicitly synthetic positive example; outputs remain outside empirical data:
task01e_tmp=$(mktemp -d)
python3 -m attention.transform \
  --input tests/fixtures/attention/youtube_synthetic.json \
  --output "$task01e_tmp/monthly.csv" --summary "$task01e_tmp/summary.json"
```

Input contract: version 1.0.0; exact month window, declared `aggregation_timezone`,
explicit status, source/category/rights/geographic annotations and dated API-shaped
`videos` or `commentThreads` batches. Only `synthetic_fixture` sources are supported
for populated adapter input; `not empirically populated` requires no sources/batches.
**Real ingestion deliberately fails closed** until policy/retention/rights review and
an independently reviewed empirical input path. This is a bounded offline feasibility
adapter, not a credentialed acquisition implementation.

Output is one row per calendar month, with separate category-specific video and
comment publication counts. Positive synthetic counts describe only selected surviving
content; no observed records means blank, never 0. All `*_historical_views` columns
are intentionally unsupported/blank: current counters are validated but excluded.
Default CSV has 96 rows and no numeric attention observations; `summary.json` reports
both coverage windows and `not empirically populated`. Deterministic `--check` detects
stale/tampered output; CI runs this and tests offline, never research requests.

Quality diagnostics on the **actual** dataset:

| Check | Result |
|---|---|
| Observed / missing months 2018–2025 | 0 / 96 |
| Observed / missing months 2021–2025 | 0 / 60 |
| Observed zero months | None; zeros never inferred |
| Distinct observed sources/channels/authors | 0 / 0 / not measured; no author data |
| Temporal variation / event concentration | Not measurable; empty data is not a flat zero series |
| Platform coverage changes / deletion losses | Not quantifiable from failed single-date access; no original census |
| German audience evidence | None obtained |
| Sentiment / historical views | Unavailable, no synthetic scores presented as data |

The synthetic fixtures exercise leap/DST/month boundaries and duplicates; their
positive counts are software checks, not empirical attention, channel-quality or
representativeness evidence. No KBA join, correlation, registration-derived query
selection or model execution on attention data occurs.

## Follow-up protocol only — empirical prediction/association

A separate authorized task should first secure legal access, populate and freeze the
source universe/version, validate coverage/zeros/geography/timing, and admit a lawful
series. Prefer Trends DE and a modest fixed-channel publication inventory evaluated
separately, with predefined sensitivity to survivorship and creator selection. Do not
combine Owned, Earned, Community and search into an arbitrary aggregate index.

Then predeclare monthly Tesla registrations 2018–2025 and an optional **separate**
Tesla-versus-BEV comparison in the common 2021–2025 window. Review trend, seasonality,
quarter ends, structural changes and stationarity; report transformations before
cross-correlations. Explore **attention lags 0–6 months** with an explicit lag/sign
convention, effective sample sizes and multiplicity warning. Use a parsimonious
predeclared distributed-lag specification or train-only inner selection, not six
independently optimized lags chosen on a favorable holdout.

Freeze an outer time holdout, e.g. January–December 2025, before specification and
keep selection/scaling/imputation (if ever defensible) entirely inside training.
Compare calendar-only forecasts with the same forecasts plus separate attention
variables on identical dated observations, using a declared metric and failed/missing
forecast accounting. New prices, launches, subsidy events and supply constraints
require independent evidence available to the intended analysis; no residual-driven
dummies. Supply/registration delay and reverse causality are central: registrations,
launches and news can themselves generate attention. A lag does not establish causality.

**Contemporaneous attention is not automatically available for a month-ahead forecast.**
Declare forecast origin and availability lags separately from retrospective explanatory
association; use only measurements available by origin. Full-window Trends rescaling,
modern surviving YouTube inventories and late retrievals require special care: they
are not historical real-time data. Existing KBA **Point-in-time blocks remain unchanged**;
a holdout on current retrospectively reconstructed data must be labeled a retrospective
out-of-time exercise, never an as-of/vintage-valid backtest. Proven availability of
both target and predictor vintages is required for that stronger claim.

Forecast improvement, statistical association and causal advertising effect are
separate questions. This follow-up has **no known causal Ground Truth** and cannot
establish real marketing ROI. The existing semi-synthetic pipeline and its estimator
contract are untouched; no attention column is injected into that interface here.

## Verification

Local Python 3.12 validation on 2026-10-23:

- Full suite: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests -v`: **147 tests passed**, including **16 new attention tests** (31.077 seconds).
- `python3 -m attention.transform --check`: default empty CSV/summary reproduce exactly; synthetic CLI reproduction and tamper rejection also exercised by tests.
- Existing campaign-artifact check, both estimator/generator example validators and `python3 -m kba audit`: passed unchanged.
- Ruff check on new Python files and `git diff --check`: passed.

No new runtime dependencies were added. These are offline software/data-integrity
checks, not evidence of empirical attention coverage. Remote CI is only reported
successful in the Draft PR after the exact commit's Actions runs have completed.
