# Agentic Analytics Studio

Ein privater Arbeitsbereich für **beobachtete Absatzentwicklung und ihre Treiber**:
Kalender und Saisonalität, Neuzulassungen, makroökonomische Größen, Kraftstoffpreise
und dokumentierte Ereignisse. Ziel sind nachvollziehbare Erklärung, bedingte
Prognosen und die Recherche unerklärter Spitzen. Es gibt kein vorgegebenes R²
oder erwünschtes Vorzeichen und keine erfundenen Media-Ausgaben.

## Empirischer Live-Pilot

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-empirical.lock
.venv/bin/python -m demo
```

`http://127.0.0.1:8000` öffnet die **reale Datenansicht**. „Vorhandene Quellen prüfen
& Modelle öffnen“ stellt die bereits geprüften 2018–2025-Snapshots direkt aus den
Originalquellen wieder her; nur exakt passende Hashes werden angenommen. Alternativ
kann ein vorhandenes privates Quellenarchiv konfiguriert werden. Es gibt keinen
synthetischen Ersatz bei fehlenden Daten. Beobachtungen und Ergebnisse bleiben
außerhalb von Git und Docker-Images im privaten Workspace gespeichert.

- KBA-Tesla-Neuzulassungen, nationaler CPI, Konsumentenkreditzinsen, EUR/USD und
  qualifizierte Diesel-Monatsapproximation; 13 Diesellücken bleiben ungefüllt.
- Acht festgelegte Kalender-/Dynamik-/Makromodelle; HypoForge erzeugt Differenzen
  und gemeinsame exogene Verzögerungen von 1/2/3 Monaten, ohne automatische Suche.
- Pflichtdiagnostik zur Stationarität der Absatzreihe, ihrer Zieltransformation und
  der Modellresiduen. Widersprüche und kurze zusammenhängende Segmente bleiben sichtbar.
- Vergleich mit einer Basis auf identischen Monaten; retrospektive Ein-Monats-
  Vorhersagen für 2025, keine historische Echtzeit- oder feste Zwölf-Monats-Prognose.
- Auffällige Trainings-Restfehler mit dokumentierten Ereigniskandidaten aus dem
  Monat und den drei Vormonaten. Kandidaten sind Hypothesen, keine bewiesenen Ursachen.
- Optionale OpenAI-Interpretation ausschließlich nach eigener Vorschau/Freigabe
  der beobachteten Ergebnisse; begrenzter Kontext, persistente Nutzung/Kosten,
  keine automatischen Daten- oder Modelländerungen. Keine Schlüssel im Browser.

[Empirische Bedienung und Grenzen](docs/EMPIRICAL_STUDIO.md) ·
[Festgelegte Methodik](workorders/03c-empirical-live.md) ·
[Azure-Einrichtung, vorhandener Key Vault und Fehlerbehebung](docs/AZURE_PRIVATE_STUDIO.md)

VARX bleibt eine optionale multivariate Erweiterung; der Live-Pilot beginnt mit
überschaubarer dynamischer Einzelreihen-Regression. Statistische Zusammenhänge und
Verbesserungen einer bedingten Prognose sind kein Nachweis kausaler Launch-,
Promotion- oder Preiseffekte. Keine öffentlichen privaten Roh-/Ergebnisdaten.

## Archiv und bisherige Bestandteile

Die synthetischen Entwicklungsbenchmarks ersetzen keine realen Beobachtungen.
Ihre vorhandenen Ergebnisse und eingefrorenen Protokolle bleiben unverändert
archiviert: [Task-02-Originale](results/task02/) mit
[Verifikationsnachweisen](docs/IDENTIFIABILITY_RESEARCH.md). Die frühere
synthetische Oberfläche ist getrennt unter `/archive/synthetic` erreichbar.
Die gestoppten README-/Nullkalibrierungsentwürfe wurden nur lokal beiseitegelegt.

<details>
<summary>Frühere Entwicklungsstufen, synthetische Demo und Datenarbeit</summary>

Die folgenden historischen Statusangaben beschreiben ihre jeweiligen Arbeitsschritte;
sie sind keine neue Bewertung des heutigen empirischen Datenbestands.

### Local persistent workspace — Task 03A

Python 3.12 + Git, from repository root (Linux):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-demo.lock
.venv/bin/python -m demo
```

Open `http://127.0.0.1:8000/archive/synthetic`: choose a project, save a note, run **Synthetic MMM Demo**,
compare the predefined models or export the synthetic report. Stop and restart the
app: the conversation, proposals and original validated results remain available.
**Wo haben wir aufgehört?** retrieves real stored context and rechecks the latest run.
The two projects share one synthetic monthly asset with different default models;
their conversations and results are separate. Free text is an unverified note,
not a general AI conversation. Optional Task 03B adds a real OpenAI Responses
conversation after server configuration, context preview and explicit consent;
local mode still needs no key or cloud account. ChatGPT subscriptions do not cover
these separately billed API calls. [Setup, limits and live-verification status](docs/CONVERSATIONAL_AGENT.md).

State is local in Git-ignored `.aas-workspace/`; keep this folder to resume.
[Usage and limits](docs/LOCAL_DEMO.md) · [critical architecture assessment](docs/PERSISTENT_WORKSPACE.md).

For a protected single-owner instance in your own Azure account, see the
[PowerShell deployment and exact Key Vault secret instructions](docs/AZURE_PRIVATE_STUDIO.md).
Azure hosting and a live API call still require verification in that account.

### Run the synthetic pipeline

Python 3.12 and Git are required. From repository root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-kba.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m studio run --output artifacts/task01a-run1
.venv/bin/python -m studio verify artifacts/task01a-run1
```

Choose a new output directory for each run. Both include/omit-quarter-end models use
the same 72-month synthetic dataset, 60/12 split, fixed oracle transforms and common
spend grid. No parameters are searched and no fit is tuned to improve recovery.

Read [Run instructions and limitations](docs/RUN_SYNTHETIC_MMM.md),
[Statistical Contracts: v0.2.1 provenance / v0.2.0 estimation](docs/STATISTICAL_CONTRACTS.md),
[Readiness](docs/TASK_01_READINESS.md), and the generated
[Example report](examples/task-01a/report.md).

### Validate

```sh
.venv/bin/python contracts/validate.py
.venv/bin/python contracts/validate.py contracts/examples/generator.json --kind generator
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -v
```

CI runs these checks plus an end-to-end smoke test. The estimator runs in a fresh
process/directory without private reference/truth files; those are available only to
generation/evaluation. All output hashes and implementation/runtime identities are
saved. The example has poor recovery, which remains visible rather than corrected.

### Scope

The Stage-A pipeline has fixed transformations. The separate research Task 02
benchmark evaluates a preregistered synthetic scenario grid; the product workspace
does not search or tune models. The optional conversational model can use only the
existing analytics tools. No MCP server, Bayesian model, geo-test,
validated MDE or real causal marketing ROI is claimed. WKR, HypoForge and Kinderwelt remain independent;
HypoForge is consumed only as a dependency pinned to its audited Git commit.

Research Task 02's [complete original results](results/task02/) are permanently
versioned in Git; [provenance, verification and scientific limits](docs/IDENTIFIABILITY_RESEARCH.md#permanent-full-results-original-ci-execution-not-a-reconstruction)
remain available independently of GitHub Actions artifact retention.

See [Source audit](docs/SOURCE_CATALOG.md) and [Contracts](contracts/README.md).

Task 01B adds [verified KBA multi-baseline acquisition](docs/KBA_MULTIBASELINE.md)
and a [future paired recovery protocol](docs/MULTIBASELINE_RECOVERY_PROTOCOL.md).
Tesla/Toyota/VW each have 96 verified consecutive months; the explicit BEV total has
60. [Task 01B.1](docs/PUBLICATION_PRECISION.md) admits them as retrospective immutable
generator references, while historical Point-in-time use remains blocked pending
vintage-specific availability evidence. Run `python -m kba audit` offline.

Task 01D adds a [Tesla Germany campaign evidence ledger](docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md)
for 2018-01–2026-10. No dated German paid campaign is verified yet: all 106 media
months remain unknown, with disputed/foreign/owned/promotion candidates kept separate.
Run `python3 -m campaigns.transform --check` offline. No model is estimated.

Task 01E adds [organic-attention data feasibility](docs/ORGANIC_ATTENTION_FEASIBILITY.md).
No real historical attention observations were obtained: all 96 months 2018–2025
remain unknown, including all 60 months 2021–2025. A small offline YouTube-shape
adapter uses explicitly synthetic fixtures; current views never become historical views.
Run `python3 -m attention.transform --check`. No association or model is estimated.

Task 01F adds a [private manual Google Trends import path](docs/FIRST_REAL_ATTENTION_OBSERVATION.md).
The official request returned HTTP 429; **no real attention observations were acquired**.
Coverage remains 0/96 (2018–2025) and 0/60 (2021–2025), with unknown months preserved.
Run `python3 -m attention.import_trends --check-blocked`; use the documented sidecar
and private import command for a lawful user-supplied monthly CSV. No values are invented.

Task 01F.1 adds [extended Trends-window import](docs/GOOGLE_TRENDS_EXTENDED_IMPORT.md).
The private upload is present and hash-checked (274 months); URL and settings are
evidenced by the user screenshot. Exact download time and rights review remain pending. Version 1.1 preserves source-wide
normalization while selecting 96/60-month subsets and flagging partial periods.
No real-value CSV is published or empirically admitted; existing empty artifacts remain.

Task 01G freezes an [exploratory protocol](docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md)
and adds a private diagnostics CLI; [first results](docs/TESLA_ATTENTION_FIRST_RESULTS.md)
are **blocked on exact retrieval evidence**. The user has confirmed lawful private
analytical use; publication of values remains a separate review.
No real Trends/KBA analysis was performed. Install `requirements-attention.lock`;
only the documented synthetic-fixture path has executed successfully.

Task 01G.1 proposes [qualified local-timestamp admission](docs/LOCAL_TIMESTAMP_ADMISSION.md).
[Current status](docs/LOCAL_TIMESTAMP_STATUS.md): raw identity verified; private use
confirmed; explicit human acceptance of the workorder-described local creation-time
basis is pending. No real diagnostics ran and no Google-confirmed download time is claimed.

Task 01H adds a [German product/availability/recall ledger](docs/TESLA_PRODUCT_RECALL_RESEARCH.md):
17 curated phase records (10 verified narrow claims, 6 partial, 1 excluded), with
announcement/order/delivery and notice/remedy kept separate. All 96 availability-index
months remain unknown; isolated snapshots are insufficient. Run
`python3 -m product_events.transform --check` offline. No outcome analysis is performed.

Task 01H-M adds [German macro-control feasibility and offline preparation](docs/GERMAN_MACRO_CONTROLS.md).
Official metadata/rights requests are proxy-blocked; no real macro observations are
admitted (0/96 and 0/60 verified months for each candidate). Monthly earnings are
**unverified**, not assumed unavailable. Run `python3 -m macro_controls.pipeline --check`;
synthetic fixtures exercise native-frequency normalization, provenance and calendar
arithmetic. No expanded model, outcome join or frozen-protocol change is included.

Task 01I adds [fuel/oil/FX acquisition and private/manual handoff](docs/GERMAN_FUEL_OIL_ACQUISITION.md).
All ten official requests are proxy-blocked; no real observations acquired or admitted
(0/96 frozen and 0/105 extended verified months per candidate). E10 is not substituted
with Euro-super 95. Run `python -m fuel_oil.fetch_fuel_oil --check` offline; tests use
synthetic fixtures only. No model, frozen-protocol or Macro admission change.

Task 01I.1 adds [actual-format energy upload adapters and private QA](docs/REAL_ENERGY_DATA_IMPORT.md).
ECB and Brent have 96/105 complete source-native months; diesel has 83/92 months
with complete temporal weekly overlap (13 gaps). All analytical admissions remain
blocked: ECB/EIA rights and diesel derived-use review remain unresolved.
The user-cited official unit convention enables private EUR/litre and monthly QA.
No real observations are committed. Run `python -m fuel_oil.import_energy --check-metadata`.

Task 01I.2 adds an [energy rights/admission matrix](docs/ENERGY_RIGHTS_ADMISSION.md).
Explicit human review accepts ECB and qualified EC diesel for private retrospective
research; exactly two hash-bound private permits were generated. EIA/RBRTE retains
`not_verified` third-party rights (Refinitiv/LSEG); no unconditional permit is created.
All 13 diesel gaps remain unfilled. No public release, historical as-of approval or
Task 01J execution. Run `python -m fuel_oil.rights_admission --check` offline.

Task 01I.3 implements the separately authorised [scoped private energy study](docs/SCOPED_ENERGY_STUDY_STATUS.md)
under its [frozen preregistered protocol](docs/SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md).
Only admitted ECB FX, qualified EC diesel and audited retrospective Tesla counts are
used; no Brent or 2026 outcomes. Real outputs stay private; CI uses synthetic fixtures.
This does not execute Task 01J or change Task 01G.

Task 02A–02C adds a [local synthetic browser demo](docs/LOCAL_DEMO.md). Install
`requirements-demo.lock`, then run `python -m demo` and open `http://127.0.0.1:8000`.
Only project-generated synthetic data are available; no keys or cloud setup required.
The demo includes a matched model comparison, synthetic Markdown report export,
and four rule-based language requests backed by allowlisted tools (no LLM or MCP server).

### Synthetic result export — package 1

Successful **Contract validation** runs expose `synthetic-stage-a-<commit>` under
GitHub Actions → selected run → **Artifacts** (GitHub login may be required).
Download and extract that artifact for the complete Stage-A report, both fitted
models, predictions, comparisons, synthetic truth/reference, runtime and existing
hash inventory. It is retained for seven days; failed checks publish nothing.

Everything in this export is **SYNTHETIC / NOT EMPIRICAL**, including files under
`private/` (an estimator-access boundary, not private empirical observations).
The export gate validates original hashes/contracts and exact membership, and
rejects observed/uncleared provenance. KBA, Trends, energy studies, permits, keys
and unrelated workspace files are excluded. No backup export branch is needed.
Locally verify an extracted bundle with `python -m studio.export <directory>`.
No statistical method, frozen protocol or private empirical result changes.

Package 3 adds [primary-source macro/energy acquisition and QA](DATA_SOURCES.md):
consumer-credit AAR/NDER, national CPI, EUR/USD and qualified German diesel.
Actual raw snapshots/normalized values stay private; Brent remains rights-blocked.
No new model or historical-protocol change.

</details>
