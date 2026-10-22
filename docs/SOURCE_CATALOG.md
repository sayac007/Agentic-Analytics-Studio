# Source catalog and research access ledger

Audit date: **2026-10-22**. No external dataset, Tesla campaign, price-change date,
or promotion event has been verified or imported. The table distinguishes proposed
research entry points from retrieved primary-source evidence. Do not cite proposed
URLs as proof of their current contents, coverage, or license.

## Observed retrieval evidence

Stdlib `urllib.request.urlopen(url, timeout=20)` requests to the following URLs
failed with `Tunnel connection failed: 403 Forbidden` (proxy CONNECT denial):

- <https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/MonatlicheNeuzulassungen/monatl_neuzulassungen_node.html>
- <https://www.tesla.com/de_de>
- <https://support.google.com/trends/answer/4365533?hl=de>
- <https://api.github.com/users/sayac007/repos?per_page=100>

The KBA request was retried once after saving the domain draft and still failed.
A draft save therefore did not establish runtime access. These are access attempts,
not successful retrieval dates. No source page body or source license was inspected.
GitHub HTML and native HTTPS Git worked; that does not establish access to unrelated
hosts or the GitHub API.

## Candidate sources — contents NOT VERIFIED

| Candidate primary publisher / entry point | Intended variable / provenance | Intended grain and time coverage | Rights / commit decision | Uncertainty and next verification |
|---|---|---|---|---|
| KBA, monthly new registrations URL above | Tesla-brand passenger-car new registrations in Germany; `observed` once verified | Monthly; exact available start/end, release dates and revisions NOT VERIFIED | Exact table terms and required attribution NOT VERIFIED; do not commit downloads | Select Tesla brand, passenger cars, DE; distinguish brand/model, registrations/sales, monthly/cumulative values; retain raw release and checksum; reconcile totals and corrections |
| Tesla Germany, <https://www.tesla.com/de_de> | Public list prices, financing offers, inventory incentives; `proxy` context, not media exposure/spend | Event/date or captured price snapshot; no historical coverage verified | Public viewing does not establish redistribution rights; no scraped/captured dataset committed | A current page cannot establish historical prices. Need dated German primary offer terms, model/trim, gross/net price, eligibility, delivery/order deadline, finance APR/term and archived evidence |
| Tesla official dated communications, discovered from its DE site after access | Campaign announcement or promotion evidence; `proxy` | Dated events; no start/end dates verified | Per-asset rights and archive permissions unresolved | Distinguish announcement, booking window, airing dates and delivery; a promotion is not proof of a paid TV/OOH campaign |
| Google Ads Transparency Center, <https://adstransparency.google.com/> | Advertiser/creative presence and any explicitly shown delivery dates/regions; `proxy` | Creative/event-level if available; historical coverage NOT VERIFIED | Platform terms, export availability and reuse rights NOT VERIFIED; no dataset committed | Check advertiser identity and DE delivery. Archive dated query/evidence. Do not infer spend, impressions or complete campaign reach from creative presence |
| Meta Ad Library, <https://www.facebook.com/ads/library/> | Observable ad creative/activity; `proxy` | Creative/event-level; coverage and historical retention NOT VERIFIED | Access/export/redistribution terms NOT VERIFIED; no dataset committed | Confirm country and advertiser; ordinary commercial ads may have different disclosure/retention than political ads. Never scrape gated content |
| Google Trends, <https://trends.google.com/trends/> and help URL above | Relative search interest, e.g. Tesla topic versus explicit search term; `proxy` | Requested DE monthly series; returned resolution, sampling and date range must be verified | Terms/export permissions NOT VERIFIED; no data committed | Record query/topic ID, geo=DE, category, search property, full request window, export time and normalization. Search interest is not spend or causal demand. Overlapping exports need an explicit scaling rule; zeros may reflect low volume |
| BAFA, <https://www.bafa.de/> | Official subsidy/eligibility change context; `proxy` | Dated policy events; no event dates verified | Exact notice rights NOT VERIFIED; metadata-only until checked | Verify primary dated notice and distinction between announcement, application cutoff and registration eligibility |
| DWD, <https://www.dwd.de/> | Weather controls; `observed` measurements after verification | Source-native station/day data, proposed monthly DE aggregation; actual coverage unverified | Dataset-specific terms and attribution NOT VERIFIED | Define stations, weights, missing-day handling, product version and aggregation; national average is not automatically vehicle-buyer exposure |

All proposed entry points other than the four requests listed above are **not
fetched**. They are leads, not evidence of availability. No TV, online or OOH
campaign is asserted; lack of accessible evidence is not evidence of no campaign.
No numeric Tesla prices or promotions are inferred from memory or secondary reports.

## Event-record contract for later source research

For each verified event record: `event_id`, `publisher`, `primary_url`,
`evidence_sha256`, `retrieved_at`, `publication_date`, `start_date`, `end_date`,
`date_precision`, `country`, `model_trim`, `medium`, `event_type`, `offer_terms`,
`rights`, `redistribution`, `uncertainty`, and `class=proxy`. Unknown dates stay null;
do not silently substitute publication dates for delivery or campaign start dates.
At monthly aggregation, declare whether an event contributes a count, eligible-day
fraction or a separately justified intensity. An unverified month is missing, not
zero. Keep these optional covariates outside the initial minimal model contract.

## Dataset admission and lineage gate

Before admitting a real series: verify publisher and primary file; save release URL,
access date, coverage, geographic scope, frequency, unit, revision/vintage and
checksum; record each column's transformations, gaps and license text/reference.
Keep the raw download immutable and build a separately hashed analysis CSV. No
automatic redistribution when rights are unknown. Do not copy WKR's market CSV:
its own source note states that extraction vintages and some attributions have not
been independently verified, and it is not a verified Tesla-brand dataset.

The committed six-row fixture is hand-authored by this project, contains no external
observations, and is explicitly `synthetic_fixture`. Its field named
`observed_registrations` is a structural stand-in only, with `class=synthetic`.
It establishes schema behavior, not observed registrations, a generated DGP,
statistical fit, causal effect, or a completed source-research milestone.
