# Tesla Germany campaign evidence, research cutoff 2026-10-23

`evidence.json` separates inspected source metadata, factual claims, activity category,
Germany evidence, publication/capture/ad-delivery dates, quality and decisions.
`research_log.json` preserves successful/failed public-source retrieval metadata;
search results and application shells are discovery only. Third-party rights remain
unverified; no raw articles, creative assets or page bodies are redistributed.

15 screened events include 9 campaign candidates and 6 context events. No campaign
currently has an independently identifiable and dated German paid run. The reported
November 2023 German Google listing remains **partial / hold**: a library observation
and its article date do not establish actual ad-delivery dates. The 2020 spending
claim is explicitly contested. Owned pages, US/Asia media and financing deadlines
are not transformed into German paid advertising.

`monthly_indicators.csv` covers all 106 months 2018-01–2026-10, including lags 0–3.
**Blank means unknown, never zero.** All current indicator/lag cells are unknown;
`summary.json` reports zero proven active months and zero proven inactive months.
These numbers do not mean zero Tesla advertising. No useful measured media time
series is established by this search. No missing values were filled.

Rebuild/check offline: `python3 -m campaigns.transform [--check]`.
Definitions, source links, search limitations and later research designs:
[Research report](../../docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md).
