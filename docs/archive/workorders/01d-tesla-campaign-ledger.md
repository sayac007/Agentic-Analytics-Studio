# Codex Workorder – Task 01D: Tesla Germany Campaign Evidence Ledger

Repository: `sayac007/Agentic-Analytics-Studio`

## Forschungsziel

Rekonstruiere für Januar 2018 bis Oktober 2026 einen quellenbasierten Kalender von Tesla-Marketingaktivitäten mit Deutschlandbezug.

Der Schwerpunkt liegt auf **bezahlter Werbung (Paid Media)** und ihren dokumentierten Laufzeiten. Ziel ist, daraus später monatliche Kampagnenindikatoren und verzögerte Expositionsvariablen für ökonometrische Analysen abzuleiten.

**Noch keine Regressionsschätzung, keine MMM-Simulation und keine kausalen ROI-Behauptungen.**

## 1. Branch und Voraussetzungen

- Prüfe, dass PR #5 in `main` enthalten ist.
- Lies `AGENTS.md`, `docs/STATISTICAL_CONTRACTS.md`, `docs/PUBLICATION_PRECISION.md` und `docs/KBA_MULTIBASELINE.md`.
- Erstelle vom aktuellen `main` den Branch `research/task-01d-tesla-campaign-ledger`.
- Arbeite ausschließlich im Repository `Agentic-Analytics-Studio`.
- Erstelle am Ende einen Draft-PR gegen `main`. Nicht selbst mergen.

## 2. Recherche

Suche systematisch nach öffentlich belegten Tesla-Kampagnen mit möglichem Deutschlandbezug zwischen 2018 und Oktober 2026.

Berücksichtige offizielle Tesla-Quellen, Anzeigenbibliotheken, Branchenmedien, Agentur-Case-Studies, archivierte Kampagnenseiten und dokumentierte Anzeigen auf Google, YouTube, Meta, X sowie klassischen Medienkanälen.

Unterscheide strikt:

- `paid_media`
- `owned_media`
- `earned_media_pr`
- `sales_promotion`
- `product_event`
- `unknown`

Eine internationale Kampagne ist nicht automatisch eine deutsche Kampagne. Eine Social-Media-Veröffentlichung ist nicht automatisch bezahlte Werbung.

Agenturbeauftragungen, Werbeausgaben und Impressionen nur dokumentieren, wenn dafür konkrete Quellen existieren.

## 3. Evidence Ledger

Erstelle `data/tesla_campaigns/evidence.json` mit mindestens:

- Ereignis-ID und Titel
- Aktivitätskategorie
- Tesla-Modell oder beworbenes Angebot
- geografische Reichweite und Deutschlandnachweis
- Medienkanäle
- dokumentierter Start und dokumentiertes Ende
- Datumspräzision und mögliche Unsicherheit
- beobachtete Anzeigentage, falls nur Snapshots vorliegen
- Quellen-URLs, Herausgeber und Abrufdatum
- Primär- oder Sekundärquellenstatus
- konkret belegte Aussage
- Evidenzqualität
- Aufnahme- oder Ausschlussentscheidung

Verwende die Evidenzklassen `verified`, `partial`, `unverified` und `excluded`.

**Wichtig:** Artikeldatum, Anzeigen-Snapshot, Kampagnenstart und Kampagnenende sind unterschiedliche Sachverhalte. Keine fehlenden Datumswerte erfinden.

## 4. Monatliche Indikatoren

Erzeuge mit einem kleinen deterministischen Python-Transformer für 2018-01 bis 2026-10:

1. `verified_paid_activity`: belegte deutsche Paid-Media-Aktivität.
2. `active_day_share`: Anteil aktiver Tage, sofern eine vollständige Kampagnenlaufzeit belegt ist.
3. `active_campaign_count`: Anzahl belegter gleichzeitig aktiver Kampagnen.

Bewahre die Unterscheidung zwischen `0` und `unknown`. Keine öffentliche Evidenz bedeutet nicht nachgewiesene Inaktivität.

Bei lediglich punktueller Evidenz darf keine durchgehende Kampagnenlaufzeit angenommen werden.

Erzeuge zusätzlich Lags von 0 bis 3 Monaten für zulässige Indikatoren. Fehlende Werte bleiben fehlend.

Falls vollständige Laufzeiten vorliegen, können drei ausdrücklich hypothetische Verteilungsprofile ergänzt werden: gleichmäßig, startbetont und endbetont. Diese sind **keine gemessenen Impressions**.

## 5. Methodische Dokumentation

Erstelle `docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md`.

Diskutiere insbesondere:

- mögliche Verzögerung zwischen Werbekontakt, Bestellung, Auslieferung und Zulassung;
- endogene Kampagnenstarts bei schwacher Nachfrage;
- gleichzeitige Preisänderungen, Produktstarts und Fördermaßnahmen;
- Überschneidungen zwischen Paid Media und organischer Tesla-Publicity;
- Unsicherheit über tatsächliche Werbeintensität;
- Identifizierbarkeit bei wenigen oder überlappenden Kampagnen.

Skizziere zwei strikt getrennte spätere Forschungsansätze:

**Empirisch:** Event-Study oder Distributed-Lag-Analyse der Tesla-Zulassungen.

**Semi-synthetisch:** Dokumentierte Kampagnenzeitpunkte als Generatorinput verwenden, bekannte Effekte injizieren und deren Recovery prüfen.

Nur der semi-synthetische Ansatz besitzt bekannte Ground Truth.

## 6. Tests und Umfang

Implementiere fokussierte Offline-Tests für Datumspräzision, Monatsgrenzen, Überlappungen, Missing Values, Lag-Verschiebungen und den Ausschluss ungeeigneter Ereignisse.

Keine Live-Recherche in CI.

Keine Änderungen an KBA-Beobachtungen, bestehenden MMM-Ergebnissen, Estimator-Isolation oder Statistical Contracts.

Keine zusätzliche generische Provenienzplattform entwickeln. **Wissenschaftlicher Erkenntnisgewinn hat Vorrang vor unnötiger Engineering-Komplexität.**

## 7. Deliverables

- `data/tesla_campaigns/evidence.json`
- `data/tesla_campaigns/monthly_indicators.csv`
- kleiner Python-Transformer und Tests
- `docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md`
- kurze Ergebnisübersicht im Draft-PR

Berichte zum Abschluss:

1. Anzahl gefundener Kampagnenkandidaten.
2. Anzahl verifizierter deutscher Paid-Media-Kampagnen.
3. Anzahl mit belegtem Start und Ende.
4. Monate mit nachgewiesener Aktivität.
5. Monate mit unbekannter Aktivität.
6. Verfügbarkeit einer ausreichend variierenden Media-Zeitreihe.
7. Tatsächlich bestandene Tests und CI-Status.

**Abnahmekriterium:** Ein überprüfbarer Kampagnenkalender, der keine unbeobachteten Media-Aktivitäten oder Werbevolumina als Tatsachen ausgibt.

Falls sich nur wenige Kampagnen nachweisen lassen, ist das ein gültiges Forschungsergebnis.

Draft-PR erstellen, nicht automatisch mergen.

## Execution record — 2026-10-23

- Started from current main including merged PR #5 (`0c15e4a`), on `research/task-01d-tesla-campaign-ledger`.
- Delivered source-linked ledger, research log/report, deterministic monthly transformer, offline tests and CI artifact check.
- Screened 9 campaign candidates plus 6 context events. Verified dated German paid campaigns: 0; complete runs: 0; evidenced activity months: 0; unknown months: 106; evidenced inactive months: 0.
- German Google targeting is reported by a November 2023 secondary article, but lacks independently verifiable dated delivery/campaign identity. It remains partial/hold, not an exposure observation.
- No adequately varying measured media series, empirical effect, real ROI or absence of advertising is inferred.
- Local full suite: 131 passing tests (15 new campaign tests); offline artifact reproduction, manifest/generator validation, KBA audit, Ruff and whitespace checks passed. See research report for commands.
- No Statistical Contract, KBA observation, MMM result or estimator-isolation changes. Draft PR only; no merge. Remote CI evidence is maintained in the PR description.
