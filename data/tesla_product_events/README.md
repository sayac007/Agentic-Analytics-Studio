# Tesla Germany product, availability and recall evidence

Focused initial pass, accessed 2026-10-24, event window 2018-01–2025-12.

- `evidence.json`: curated versioned factual claims, parents, source citations and provisional offering taxonomy; missing/conflicting details remain explicit.
- `search_log.json`: bounded searches, actual response hashes/timestamps, failed URL guesses and regulator access denials. Raw HTML/articles/images stay outside Git.
- `monthly_indicators.csv`: 96 months of **documented parent-milestone lower-bound counts**, separated by event type. Empty means unknown, never confirmed inactivity.
- `summary.json`: computed counts and canonical-ledger/CSV hash bindings. Record counts describe this ledger, not all Tesla events.

17 records, 11 underlying parents, 16 sources: **10 verified narrow claims**, **6 partial**, **1 excluded**. Nine verified phases explicitly concern Germany; one is dated German manufacturer recall-remedy guidance, not a German affected-VIN census. No regulator reference/count is invented.

Positive dated records occur in 7 months; the other 89 months have no verified dated record in this pass, **not evidence of no event**. The entire period lacks exhaustive event coverage. All 96 Model Availability Index cells are null: isolated configurator evidence does not establish a continuous monthly census. No TDP, physical stock, supply capacity, spend, recall exposure or causal effect is inferred.

Rebuild/check offline:

```sh
python3 -m product_events.transform
python3 -m product_events.transform --check
python3 -m unittest discover -s tests -p test_product_events.py -v
```

Native source excerpts are short and attributed; all explanatory documentation is English. Third-party rights are not assumed open. No raw articles, full configurator payloads, pictures, private Trends values or KBA outcomes are republished by this task.

[Research report](../../docs/TESLA_PRODUCT_RECALL_RESEARCH.md) · [Data dictionary](DATA_DICTIONARY.md)
