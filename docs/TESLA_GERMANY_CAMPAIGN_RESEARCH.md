# Tesla Germany campaign evidence research — Task 01D

Research cutoff: **2026-10-23**. Requested calendar: **2018-01–2026-10** (106 months).
October 2026 is incomplete; no observations are projected into October 24–31.
Basis: current `main` at merged PR #5, `0c15e4ab7e950b2fc372a8baf75f502041e9562a`.
This task changes no Statistical Contracts, KBA observations, MMM results or estimator
isolation. No regression, campaign-effect estimate, new MMM study or ROI claim is made.

## Findings, including the negative result

[`evidence.json`](../data/tesla_campaigns/evidence.json) contains **15 screened events**:
**9 campaign candidates** and **6 context events** (archived owned pages, promotions,
product announcement). Categories are paid_media, owned_media, earned_media_pr,
sales_promotion, product_event and unknown. Evidence classes verified, partial,
unverified and excluded are separate from the activity category and inclusion decision.

- **0** individually identified, dated, verified German Paid-Media campaigns.
- **0** verified German Paid-Media records with documented complete start/end.
- **0** months with dated verified Paid-Media activity; **106 unknown months**.
- **0** months with proven inactivity. Unknown does **not** mean no advertising.
- No adequately varying measured Media time series is established. The committed CSV
  deliberately contains missing indicators and missing lags, not synthetic zeros.
  This is an evidence limitation, not a finding that Tesla never advertised in Germany.

The important partial positive is a **specific secondary report of German-targeted
Google text ads** in a library listing described in November 2023. The missing step
is dated delivery/first-last-shown evidence and an identifiable campaign. This finding
is retained explicitly, not discarded because it cannot yet produce an indicator.

### Decisions that prevent false positives

| Candidate | Inspected evidence | Decision and reason |
|---|---|---|
| German digital advertising in 2020 | [Teslamag, 2020-09-30](https://teslamag.de/news/bericht-erstmals-bezahlte-tesla-werbung-deutschland-elektroauto-budgets-steigen-30258) reports Nielsen-derived spending and an explicit Tesla Germany denial in the updated article | **partial / hold**. Approximate cumulative spend claim is marked contested, not a media-spend observation; original Nielsen data were not accessed. Neither report nor denial establishes a flight or monthly zero. |
| Times Square Tesla footage, 2021 | [Teslamag, 2021-07-18](https://teslamag.de/news/tesla-werbung-times-square-bildschirm-100000-dollar-tag-fan-video-39197) identifies New York displays but uncertain payer | **excluded** from German Paid Media. Fan content, rate-card price and Tesla-funded media are different facts. |
| AdQuick Times Square placement, 2022 | [Teslamag, 2022-02-07](https://teslamag.de/news/update-kein-rueckruf-riesiger-bildschirm-tesla-klarstellung-times-square-45501) reports direct confirmation by agency VP Chris Gadek that AdQuick paid on its own account | **excluded**: US, self-funded agency action. AdQuick is **not** recorded as a commissioned Tesla media agency. |
| Musk's advertising intention | [Teslamag, 2023-05-17](https://teslamag.de/news/tesla-werbung-musk-hauptversammlung-test-bezahlte-anzeigen-58550) | Context only: intention/PR does not establish a placement, Germany or exposure dates. |
| Asia testimonial mistaken for TV advertising | [Teslamag, 2023-05-24](https://teslamag.de/news/tesla-video-asien-falsch-erster-tv-werbespot-58684) discusses Tesla Asia's May 19 owned post and the misleading TV interpretation | **owned_media / excluded**. No German paid placement established. The reported owned-post date remains separate from campaign dates. |
| Initial Google search ads | [Teslamag, 2023-06-28](https://teslamag.de/news/bezahlte-tesla-werbung-google-anzeigen-fuer-model-y-in-grossbritannien-und-solar-in-usa-59363) reports Model Y ads for GB and solar ads for US | **excluded** from Germany. Foreign creative first-seen dates cannot be imported as German flight dates. |
| Google listing with German targeting | [Teslamag, 2023-11-26](https://teslamag.de/news/tesla-werbung-bezahlte-platzierungen-youtube-videos-entdeckt-62601) says some of 300 listed text ads were intended for Germany, also in English | **partial / hold**. Global creative count is neither German campaign count nor impressions. “Am Dienstag” is the reported library observation; it is not converted into an ad delivery day or November exposure. |
| YouTube placements in the same November article | US screenshots/US federal-tax-credit price examples | **excluded** from Germany. Same publisher/article does not give the US video evidence the geographic scope of the German search-ad statement. |
| Super Bowl spillover, 2022 | [Teslamag, 2022-04-21](https://teslamag.de/news/super-bowl-effekt-tesla-tv-werbung-nicht-selbst-bezahlen-47932) discusses competitor advertising and Tesla-reported attention | **earned_media_pr / excluded**. Not Tesla-funded German media. |

Context additionally includes retrieved German homepage archive bodies for January
2018, September 2020 and November 2023; Tesla's global
[Model 3 Performance announcement](https://www.tesla.com/blog/introducing-new-model-3-performance)
on 2024-04-23; and two current German financing promotions on the
[official German homepage](https://www.tesla.com/de_de). Their terms distinguish
applications from 2026-10-02 and conditional delivery by 2026-12-31. Those are **not
Paid-Media flight bounds**, nor proof that the offer remained continuously available.
Promotion end, stock availability, original posting date and paid distribution remain
unknown. The government-subsidy wording on the current page is not independently
verified policy evidence and is not encoded as such.

## Research route and limitations

[`research_log.json`](../data/tesla_campaigns/research_log.json) records URLs, retrieval
outcomes, final URLs and SHA-256 of retrieved responses. Raw page bodies remain
outside the repository; source records retain source type, publisher, publication
versus retrieval date, and source-content status. SHA fingerprints identify the
retrieved response, not evidence of a historical campaign or a guarantee that a
mutable page will be available unchanged later.

Research combined:

1. Year-specific searches for 2018 through 2026 and broad paid/Google/YouTube/TV terms.
   Bing RSS returned essentially generic Tesla results even for year-qualified queries;
   Google returned a redirect/application page. Neither is treated as substantive
   evidence or as an exhaustive search of that year.
2. Correctly parameterized publisher searches at Teslamag and HORIZONT, plus electrive
   and t3n; paid-ad, Germany, agency, outdoor, campaign and 2024–2026 follow-ups.
   Article bodies, not just snippets/headlines, supported the decisions above.
   Recent unrelated product/political news was not converted into campaign candidates.
3. Official Tesla German pages, blog/product page, events page, an investor-relations
   release and Tesla Europe on X. Reaching an owned channel does not identify a paid
   post. The events page/application shell did not yield an ad flight calendar.
4. [Google advertiser record AR17828074650563772417](https://adstransparency.google.com/advertiser/AR17828074650563772417?region=DE),
   reached through the article's primary link: HTTP 200, but only an application shell
   in the retrieved response, without the historical German delivery records required.
   [Meta DE library query](https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=DE&q=Tesla&search_type=keyword_unordered)
   returned 403; YouTube channel retrieval was blocked; Reuters search returned 401.
   No inaccessible records, impressions or budgets are claimed inspected.
5. Internet Archive CDX discovery followed by **actual archived German homepage bodies**
   at three selected captures. The index alone was not accepted as an observation.
   Those bodies show owned marketing, not evidence of paid distribution. They do not
   establish uninterrupted page content or activity between captures.

Initial proxy CONNECT denials restricted several domains. Additional domains were
saved as an environment configuration **draft**, preserving existing custom domains
and presets; draft persistence is not publication or proof of live activation.
Subsequent requests independently verified access to several extra publishers and
archives. Remaining failures are recorded, not used as evidence of inactivity. No
paywall, authentication or access restriction was bypassed. Source selection is biased
toward publicly retrievable text, especially Teslamag; independent verification of the
German Google record is still missing. This is a documented public-source search,
**not a complete census of Tesla advertising** or a proof that no agency campaign exists.

Next useful evidence would be lawful library exports with advertiser/creative IDs,
German targeting and actual first/last shown information, archived creative-detail
pages, broadcaster/operator flight confirmations, or explicit advertiser/agency case
studies identifying Germany and dates. Even first/last shown bounds do not by themselves
prove activity **every intervening day**; daily continuity needs evidence. A media
monitoring product would need separate access, rights and coverage assessment. No
messages or requests to third parties were sent in this task.

## Indicator meanings and deterministic transformation

Run from repository root, Python 3.12; the transformer uses **standard library only**:

```sh
python3 -m campaigns.transform
python3 -m campaigns.transform --check
python3 -m unittest discover -s tests -p test_campaigns.py -v
```

`--check` recomputes exact CSV/summary bytes offline. Existing CI runs all new tests
and an explicit campaign-artifact check. No live research is executed in CI. The
research and current evidence are in JSON; generated CSV/summary are deterministic.

Eligibility requires paid_media + verified + include_paid_indicator + explicit German
scope and a substantive linked source. A search page/application shell, contested claim,
non-German example, promotion or owned post is insufficient. Event IDs link the CSV
back to the ledger. Known bounds need date-specific sources and meaningful roles;
application/delivery deadlines cannot masquerade as campaign bounds. Unknown dates
stay null; month/year precision never expands to fictional first/last days.

| Column | Definition / limitations |
|---|---|
| `verified_paid_activity` | 1 when an admissible, explicitly dated German paid activity observation or documented continuous run intersects the month; otherwise blank/unknown. No source establishes complete inactivity, so this version emits no inferred 0. |
| `active_day_share` | Union of calendar days in documented, continuous **completed** paid runs divided by all days of the month; inclusive endpoints. Null without exact documented runs. This is documented-campaign coverage/lower-bound activity, not total-market advertising intensity or impressions. |
| `active_campaign_count` | Maximum number of simultaneously observed **individually identified** documented campaigns on any observed day in the month; deduplicated by stable campaign ID. It is a lower bound, not the monthly sum of campaign IDs or global creative count. Unknown identity gives null, not one. |
| `supporting_event_ids` | IDs that genuinely support that month's eligible paid observation. No article-date-only IDs are inserted. |
| `*_lag0` through `*_lag3` | Exact calendar-month shifts of the corresponding indicator; lag0 equals the original. Missing history/values remain missing; an explicitly supplied zero is never converted to missing by the lag operation. |

Point observations never bridge gaps or generate a full flight. Explicit observations
with month precision may support only that month **if they actually describe activity**;
an article's month or the date a historic ad was listed in a library is not such an
observation. Exact individual snapshots do not generate continuous active-day shares.
For a future completed-run dataset, overlaps use a day union for share and daily peak
concurrency for count. Future schedules/snapshots cannot be treated as observed actual
runs; the research cutoff and output window are enforced. No record is assumed inactive
before a first snapshot or after its last snapshot.

There are no complete verified German runs here, so no uniform/start-heavy/end-heavy
hypothetical exposure profiles are added. Such profiles, if separately authorized later,
would be **synthetic allocations**, not measured impressions, spending or adstock.
The current adequacy assessment is an authored research conclusion, not an automatic
power/variance threshold or a guarantee about possible future evidence.

## Two later research designs, kept separate

### Empirical event study / distributed lag

First obtain dates with actual German scope, resolve revisions/availability and freeze
an evidence/version cutoff before looking for favorable registration effects. Use the
observed KBA series in a **separate, authorized empirical analysis**, not by adding
columns to the existing semi-synthetic estimator interface. Define the estimand and
expected lag structure before fitting, report campaign-date uncertainty and distinguish
announcement, contact, order, delivery and registration dates. The monthly aggregation
cannot identify an exact within-month mechanism.

Ad contact may affect orders quickly but registrations only after waiting lists,
production, shipping, delivery and administrative registration. Quarter-end delivery
waves can dominate the timing. Concurrent price cuts, financing, launches, subsidy
changes, supply constraints and publicity require independently evidenced controls
and careful identification, not residual-driven dummies. The current promotion
eligibility/delivery terms illustrate that even official dates have different roles.

Campaign starts may respond to weak demand, creating reverse causation. Organic Tesla
publicity, Musk news and paid advertising can coincide, so a pre/post difference is not
an ad effect. With few campaigns, overlapping windows and trend/season/quarter-end
controls, identification may be weak or absent; adding multiple lags can consume most
information and increase collinearity. No public evidence is not an admissible zero
control month. Placebos/pretrends and sensitivity to window/controls/lag definitions
would be needed, without selecting only successful tests. The all-missing media series
here does **not** support estimation. This empirical approach has **no known causal
Ground Truth** and cannot establish real ROI from this ledger alone.

### Semi-synthetic recovery

Use independently frozen, actually documented timing as a future **private generator**
input; inject known effects, keep immutable reference/truth apart, and expose only the
approved safe generated inputs to the isolated estimator. If dates remain uncertain,
predeclare alternative timing scenarios; do not choose dates or intensities that
improve recovery. Arbitrary uniform/start/end weights and lag kernels are generator
assumptions to be recorded as synthetic, not observed Tesla exposure.

Pair seeds/noise and transformations across scenario comparisons and keep holdout,
search rules, failure accounting and recovery metrics predeclared. Measure contribution
and response recovery, interval coverage/detection in a separately reviewed replicated
protocol; do not infer a calibrated MDE from a sparse event list. **Only this injected
semi-synthetic setting has known Ground Truth.** Contracts remain unchanged here;
future campaign-derived generator features or empirical regressors need explicit review.

## Executed validation

Local Python 3.12 validation on 2026-10-23:

- `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests -v`: **131 tests passed**, including 15 new offline campaign tests (32.186 seconds).
- `python3 -m campaigns.transform --check`: committed CSV and summary reproduce exactly.
- `python3 contracts/validate.py` and the separate generator-example validation: passed.
- `python3 -m kba audit`: existing normalized observations/provenance audit passed.
- Ruff check of the new Python files and `git diff --check`: passed.

The campaign tests use explicitly synthetic calendar fixtures for positive cases,
not invented real Tesla campaigns. They cover date precision, leap/month boundaries,
inclusive days, overlaps/concurrency, identity deduplication, snapshots versus runs,
missing history/lags, foreign/owned/promotion exclusions, source linkage, future-run
rejection, deterministic output and the real ledger's deliberate missingness.
Remote CI status is reported in the Draft PR after the exact commit's checks finish;
local success alone is not represented as a successful GitHub Actions run.
