> Historical Task 00 snapshot below. Task 01B supersedes its one-month coverage
> assessment with [96 verified releases and explicit remaining admission blockers](KBA_MULTIBASELINE.md).
> No campaign/proxy evidence below is expanded by that acquisition.

# Source catalog — primary-source audit, 2026-10-22

Successful retrievals and failures are recorded in [source-evidence.json](source-evidence.json)
with URLs, HTTP outcomes and SHA-256 for retrieved bytes. Source downloads remain
outside this repository under `/tmp/audit-*`; no real dataset or copyrighted web page
is committed. The six-row contract fixture is independently hand-authored and synthetic.
Initial proxy CONNECT 403 errors resolved on later requests. Successful current-source
inspection below supersedes the initial access failures, not the remaining limits.

## KBA observed registration reference

Primary entry point, HTTP 200:
<https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/MonatlicheNeuzulassungen/monatl_neuzulassungen_node.html>.
The retrieved page is an **archive view for January 2025**, not a current October
2026 release. Its year selector lists 2008–2025; this is discovery evidence only,
not proof that every year/month has a complete Tesla-brand series.

The page directly links **FZ 10, January 2025**, retrieved successfully:
<https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ10/fz10_2025_01.xlsx?__blob=publicationFile&v=2>.
SHA-256: `777366bf2a9c6ca4b0f62e5c106ea56dd7d61490b60f7377af041be81ca9332d`.
The workbook `Impressum` declares January 2025 as reporting period, February 2025
as publication month, monthly periodicity and KBA as publisher. Exact publication day
and later revision history remain unverified; retain URL version `v=2` and checksum.

Verified extraction location: sheet `FZ 10.1`, `B394 = TESLA ZUSAMMEN`,
`D394 = 1277`; D9 identifies January 2025. Rows 390–393 contain Model 3 (272),
Model S (13), Model X (13) and Model Y (979). A local assertion verified that these
sum to 1,277. This is **German passenger-car new registrations**, not sales, orders,
media spend or a causal marketing outcome. Use the monthly total column, not a
cumulative or percentage column. Current verified coverage is **one month only**;
a multi-year input series still needs per-release retrieval and validation.

Rights: workbook `Impressum!C26` explicitly states **Datenlizenz Deutschland –
Namensnennung – Version 2.0** and links this successfully retrieved KBA license:
<https://www.kba.de/DE/Service/Hinweise/Datenlizenz/datenlizenz_pdf.pdf?__blob=publicationFile&v=6>.
The PDF permits commercial/noncommercial copying, alteration, combination and
transmission with attribution, license reference and dataset URI; mark modifications.
License URL: <https://www.govdata.de/dl-de/by-2-0> (referenced by KBA; not separately fetched).
Proposed attribution: `Datenquelle: Kraftfahrt-Bundesamt, FZ 10 Januar 2025,
Abruf 2026-10-22; dl-de/by-2-0; [dataset URI]; eigene Berechnung` where transformed.
**Commit eligibility:** this inspected KBA data can be redistributed under those
conditions. No download is committed in Task 00; verify each additional release's
terms/vintage before constructing the immutable observed input for Task 01.

## Tesla Germany prices and financing promotions

Primary source: <https://www.tesla.com/de_de>, HTTP 200 on 2026-10-22.
The German page's financing footnotes contain the following terms. These are a
**current retrieved snapshot**, not proof of previous prices or a dated price cut.

| Snapshot / event | Terms observed in primary text | Timing and scope | Provenance and uncertainty |
|---|---|---|---|
| Model Y Hinterradantrieb example | Purchase price €40,970; nominal fixed interest 1.99%, effective annual interest 2.01%, maximum 60 months | Applications from **2026-10-02**; delivery by **2026-12-31** with stated Tesla-delay exception. Promotional rate also names Model Y Premium Maximale Reichweite Allradantrieb and Performance | `proxy` promotion context; German private/small-business financing example, not spend or realized transaction prices |
| Model 3 Hinterradantrieb example | Purchase price €37,970; nominal fixed and effective annual interest 0.99%, maximum 60 months | Applications from **2026-10-02**; delivery by **2026-12-31** with stated delay exception. Rate also names Premium Maximale Reichweite rear/all-wheel drive | `proxy`; limited availability, while stocks last, not combinable with other discounts/offers |

The page states that quoted prices include current VAT and vehicle delivery costs,
exclude registration costs, and are nonbinding recommended prices; lender is
Openbank Deutschland AG. Vehicle eligibility, application date, delivery deadline,
term, down payment and final instalment matter: comparing headline monthly payments
alone would misrepresent price changes. Publication date and historical offer path
were not established. Capture snapshot date separately from application start and
delivery deadline; no assumption that an offer was active before October 2.

The page also mentions a possible government subsidy. This is a Tesla statement,
**not independently verified government policy**; do not use it as authoritative
subsidy evidence without a dated ministry/BAFA primary source.

Rights: no open-data license verified. Attempts to retrieve
<https://www.tesla.com/de_de/legal> and
<https://www.tesla.com/de_de/support/incentives> returned HTTP 403.
Commit source URL, retrieval metadata and concise factual summaries; do not
redistribute scraped page bodies, creatives or a historical price dataset without
rights review. Monthly model features would be event counts or eligible-day fractions
with declared rules, not media spend. These 2026 offers cannot be joined to the
January 2025 KBA observation as a contemporaneous effect.

## Campaign evidence and media proxies

No paid Tesla Germany TV, OOH or online campaign interval or budget has been
verified. A publicly advertised financing promotion does not establish where/when
paid media ran. Absence of verified evidence is not evidence of no campaign.

- **Google Ads Transparency Center**, <https://adstransparency.google.com/>:
  HTTP 200, but retrieved HTML text is an application shell. No advertiser identity,
  German delivery window or creative-level result was obtained. Further interactive
  advertiser/region inspection and dated evidence are needed; no campaign claim.
- **Meta Ad Library**, attempted DE/Tesla query:
  <https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=DE&q=Tesla&search_type=keyword_unordered>:
  HTTP 403. No ad history, coverage or spend inference. Do not scrape gated content.
- A dated Tesla official announcement, broadcaster/OOH operator or advertiser case
  study may corroborate a campaign only if it explicitly establishes DE market,
  medium and dates. No such dated primary source was verified in this audit.

Creative presence/dates would be `proxy`, not measured spend or full reach. Rights,
retention windows and export permissions need per-platform verification. Do not
encode unverified periods as zero activity.

## Google Trends feasibility

Successfully read primary documentation:

- <https://support.google.com/trends/answer/4365533?hl=de>: sampled and aggregated
  searches, normalized by total searches for the time/place, then scaled 0–100.
  Equal scores across regions do not mean equal volumes. Low-volume queries may
  appear as zero; sampling, filtering and statistical noise limit interpretation.
- <https://support.google.com/trends/answer/4365538?hl=de>: CSV chart export,
  embedding and citation are supported; reuse follows Google's terms and requires
  identifying Google Trends as source. Google Trends and Google Ads must not be
  cited as a single data source. No blanket open-data license was established.

Attempted reproducible query:
<https://trends.google.com/trends/explore?date=2020-01-01%202024-12-31&geo=DE&q=Tesla>
returned **HTTP 429**. No CSV export or actual returned granularity is claimed.
Intended coverage: 2020-01 through 2024-12, DE, literal search term `Tesla`, web search,
all categories; record these and distinguish a topic ID from a term. Actual frequency
must be checked in the export before monthly aggregation. Avoid stitching differently
normalized windows without an explicit scaling rule. Search interest is a `proxy`
for attention, not impressions, spending, real demand or a causal effect. Archive a
licensed/export-permitted raw response and request metadata; do not commit data yet.

## Optional controls and event admission

BAFA <https://www.bafa.de/> and DWD <https://www.dwd.de/> remain **unfetched leads**,
not verified sources in this audit. Policy events need dated primary notices;
weather requires station/product selection, source frequency, monthly aggregation,
missing-day handling and dataset-specific rights. These controls are optional and
outside the minimal initial model contract.

For each later verified event record save `event_id`, publisher, primary URL, evidence
hash, retrieval time, publication date, start/end dates, date precision, country,
model/trim, medium, event type, terms, rights/redistribution and uncertainty.
Unknown dates stay null; never substitute publication for airing/delivery dates.
For all actual input columns record class (`observed`, `synthetic`, `proxy`),
source/generator, vintage, geography, unit, grain, transformations, gaps and rights.
Keep raw observed data immutable and bind the analysis CSV by checksum. WKR's
market CSV is not a substitute for independently verified Tesla-brand releases.
