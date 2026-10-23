# Codex Workorder – Task 01E: Organic Attention Data Feasibility

Repository: `sayac007/Agentic-Analytics-Studio`

## 0. Ausgangspunkt und Startbedingung

Der bisherige Tesla-Germany-Campaign-Ledger hat neun Kampagnenkandidaten und sechs Kontext-Ereignisse dokumentiert, aber keine vollständig datierte und verifizierte deutsche Paid-Media-Kampagne gefunden.

Die daraus abgeleitete Paid-Media-Zeitreihe ist nicht empirisch verwendbar: 106 Monate `unknown`, nicht 106 Monate ohne Werbung.

**Prüfe zuerst, ob der unmittelbar vorhergehende Tesla-Campaign-Ledger-PR vollständig nach `main` gemergt wurde.**

- Falls ja: aktuellen `main` auschecken und Branch `research/task-01e-organic-attention-feasibility` erstellen.
- Falls nein: nicht auf einem veralteten Branch beginnen. Stoppen und den fehlenden Merge melden.
- Lies `AGENTS.md`, die Statistical Contracts, KBA-Dokumentation und den Tesla-Kampagnenbericht.
- Keine anderen Repositories verändern.

## 1. Forschungsfrage

Untersuche, ob öffentlich zugängliche, historisch datierbare **organische Aufmerksamkeitssignale** für Tesla in Deutschland zwischen Januar 2018 und Dezember 2025 verfügbar sind.

Ziel ist eine spätere Prüfung, ob solche Signale zusätzliche Erklärungskraft oder Prognosekraft für monatliche deutsche Tesla-Neuzulassungen besitzen.

Dies ist eine **Datenmachbarkeitsstudie**, keine Wirkungsanalyse.

Berücksichtige ausdrücklich:

1. Tesla-eigene YouTube- und Social-Media-Inhalte (Owned Media).
2. Unabhängige deutschsprachige Tesla- und Elektroauto-Creator.
3. Redaktionelle YouTube-Beiträge und Nachrichtenberichte.
4. Öffentlich beobachtbare Diskussionen und Erwähnungen.
5. Social Sentiment und Themenentwicklung, soweit reproduzierbar messbar.
6. Google Trends als separaten, potenziell hilfreichen Aufmerksamkeitsindikator.

Unterscheide Owned, Earned und Community Attention. Vermische sie nicht automatisch zu einem einzigen Index.

## 2. Datenquellen und rechtliche Machbarkeit

Prüfe beispielsweise:

- YouTube Data API: Video-Veröffentlichungszeitpunkte, Kanal, Titel, Beschreibung, aktuelle Statistiken.
- Verfügbarkeit historischer View- oder Kommentar-Zeitreihen.
- YouTube-Kommentare mit tatsächlichen Zeitstempeln, soweit API und Rechte dies erlauben.
- Google Trends: geografischer Bezug Deutschland, zeitliche Auflösung, Skalierung und Stichprobenstabilität.
- Reddit: öffentliche, datierte Posts und Kommentare mit Tesla- beziehungsweise Deutschlandbezug.
- Öffentlich verfügbare Social-Listening-Datensätze und zulässige APIs.
- Weitere seriöse historische Such- oder Nachrichtenindizes.

Für jede Quelle dokumentieren:

- Anbieter und offizielle Dokumentation;
- Authentifizierung, Kosten und Rate Limits;
- zulässige Erhebung und Weitergabe;
- historische Abdeckung;
- geografische und sprachliche Selektivität;
- Zeitstempelqualität;
- Reproduzierbarkeit;
- bekannte Verzerrungen;
- Datenverfügbarkeit ohne kostenpflichtigen Zugang;
- tatsächliches Ergebnis eines kleinen Zugriffstests, sofern technisch möglich.

**Keine Umgehung von API-Sperren, Paywalls, Captchas oder Plattformbeschränkungen. Keine Zugangsdaten committen.**

Wenn ein API-Schlüssel erforderlich und nicht vorhanden ist, dokumentiere den Blocker und stelle einen Offline-Test mit ausdrücklich synthetischen Fixtures bereit.

## 3. Besonders wichtige Messregeln

### YouTube

Unterscheide strikt:

- `published_at`: Zeitpunkt der Veröffentlichung.
- `views_at_retrieval`: heutiger kumulierter View-Zähler.
- `views_at_time_t`: historisch belegte Views zum Zeitpunkt t.
- `comments_published_at`: Zeitpunkte einzelner Kommentare.

**Heutige kumulierte Views dürfen niemals rückwirkend als historische Monats-Views ausgegeben werden.**

Eine monatliche Anzahl veröffentlichter Videos kann ein historisch datierbarer Content-Supply-Indikator sein, sofern die Videoauswahl reproduzierbar ist.

Eine monatliche Anzahl datierter Kommentare kann ein beobachtetes Engagement-Signal sein, aber keine vollständige historische Reichweite.

### Deutschlandbezug

Deutschsprachiger Content ist nicht gleich deutsche Reichweite.

Kennzeichne getrennt:

- geografisch nachgewiesenes deutsches Publikum;
- Deutschlandbezug des Inhalts;
- deutschsprachige Veröffentlichung;
- geografische Reichweite unbekannt.

### Social Sentiment

Trenne Erwähnungsvolumen und Sentiment.

Dokumentiere Sprachmodell beziehungsweise Klassifikationsverfahren, Stichprobenregeln, Neutral-Kategorie und Unsicherheit.

Keine Sentiment-Zeitreihe erzeugen, wenn dafür keine geeigneten historischen Texte verfügbar sind.

## 4. Machbarkeitsmatrix

Erstelle `docs/ORGANIC_ATTENTION_FEASIBILITY.md` mit einer vergleichbaren Bewertung aller geprüften Datenquellen.

Für jede potenzielle Zeitreihe unterscheide:

- `historically_observed`
- `retrospectively_reconstructable`
- `current_snapshot_only`
- `unavailable`
- `not_tested`

Beurteile, ob eine Monatsreihe 2018–2025 tatsächlich erzeugbar ist.

Melde separat die Abdeckung für das gemeinsame Tesla-/BEV-Fenster 2021–2025.

Eine fehlende Beobachtung ist kein Nullwert.

## 5. Kleiner empirischer Datenprototyp

Falls mindestens eine Quelle technisch und rechtlich zugänglich ist:

- Erhebe einen kleinen, klar begrenzten realen Beispieldatensatz.
- Dokumentiere Suchbegriffe, Auswahlkriterien, Abfragezeitpunkt, API-Parameter und Provenienz.
- Verwende möglichst deutschlandspezifische oder deutschsprachige Tesla-Inhalte.
- Speichere nur Daten, deren Speicherung und Weitergabe zulässig ist.
- Erzeuge daraus mit einem deterministischen Transformer einen kleinen Monatsindikator.

Bevorzugte Prototypen:

1. Veröffentlichungsfrequenz ausgewählter unabhängiger YouTube-Kanäle.
2. Monatlich datierte Tesla-Kommentare oder Diskussionen.
3. Ein dokumentierter Google-Trends-Indikator für Deutschland.

**Kein Zwang, alle drei zu liefern.** Ein einziger sauber belegter Prototyp ist besser als mehrere fragwürdige.

Falls kein realer Zugriff möglich ist, liefere stattdessen einen ausführbaren Adapter mit synthetischen Test-Fixtures und kennzeichne ihn ausdrücklich als `not empirically populated`.

## 6. Explorative Diagnostik – nur Datenqualität

Für tatsächlich vorhandene Zeitreihen untersuche:

- beobachtete Monate und Lücken;
- Nullwerte gegenüber fehlenden Werten;
- Anzahl eindeutiger Quellen, Kanäle oder Autoren;
- Konzentration auf einzelne Großereignisse;
- zeitliche Variation;
- Änderung der Plattformabdeckung;
- rückwirkend gelöschte oder nicht mehr auffindbare Inhalte;
- mögliche Auswahlverzerrung.

**Keine Korrelation mit Zulassungen berechnen, bevor die Datenqualität und Zeitzuordnung dokumentiert sind.**

Keine Regression, keine Kausalinterpretation, keine MMM-Modellierung und keine Monte-Carlo-Simulation.

## 7. Späteres ökonometrisches Design – nur als Protokoll

Skizziere einen möglichen Folgeauftrag mit:

- monatlichen Tesla-Neuzulassungen 2018–2025;
- optionalem Vergleich zum deutschen BEV-Markt 2021–2025;
- Saisonalität und Trenddiagnostik;
- Cross-Correlation mit vorab definierten Lags 0–6;
- sparsamem Distributed-Lag-Modell;
- Kontrollen für Preise, Produktstarts, Förderung und Lieferengpässe, sofern später verfügbar;
- zeitlich sauberem Holdout;
- Vergleich der Prognoseleistung mit und ohne Attention-Variablen.

Achte besonders auf Reverse Causality: Zulassungen und Produkteinführungen können selbst Aufmerksamkeit erzeugen.

Unterscheide Prognosezusammenhang, statistische Assoziation und kausale Werbewirkung.

Die bestehenden KBA-Point-in-time-Sperren bleiben unverändert. Ein retrospektiver Datensatz darf nicht als historisch echtzeitverfügbarer Backtest ausgegeben werden.

## 8. Implementierung und Tests

Begrenze den Umfang auf einen Quellenkatalog, einen kleinen Adapter/Transformer, Tests und einen Forschungsbericht.

Tests sollen mindestens prüfen:

- korrekte Monatsaggregation;
- Zeitzonen und Monatsgrenzen;
- Deduplizierung;
- fehlende Werte;
- Ausschluss aktueller View-Snapshots aus historischen View-Zeitreihen;
- getrennte Owned-/Earned-/Community-Kategorien;
- geografische Evidenzkennzeichnung;
- deterministische Offline-Reproduktion.

Keine Live-API-Abfragen in CI.

Keine Änderungen an KBA-Originaldaten, Statistical Contracts, MMM-Engine, bestehenden Simulationsergebnissen oder Estimator-Isolation.

Keine generische Data-Lake- oder Social-Listening-Plattform entwickeln.

## 9. Abschluss

Erstelle einen Draft-PR gegen `main`, ohne automatischen Merge.

Der PR-Bericht soll beantworten:

1. Welche Quellen wurden tatsächlich geprüft?
2. Welche Zugriffe haben funktioniert?
3. Welche realen historischen Beobachtungen wurden gewonnen?
4. Welche Indikatoren lassen sich wissenschaftlich vertretbar bilden?
5. Welche Monate sind abgedeckt und welche bleiben unbekannt?
6. Wie stark ist der nachweisbare Deutschlandbezug?
7. Welche Daten können später legal reproduziert werden?
8. Welche Tests und CI-Läufe sind tatsächlich erfolgreich?

**Wissenschaftliches Abnahmekriterium:** Wir wissen nach diesem Auftrag, ob eine empirische Organic-Attention-Zeitreihe realistisch aufgebaut werden kann, ohne historische Reichweite, geografische Zielgruppen oder fehlende Daten zu erfinden.

Auch das Ergebnis „derzeit nicht reproduzierbar verfügbar“ ist ausdrücklich zulässig.

Keine automatischen Merges.

## Execution and acceptance record — 2026-10-23

- [x] Confirmed previous PR #6 merged; current main `e8b261d` is the branch base.
- [x] Delivered 11-signal source catalog, actual access log, research/rights/measurement report and bounded offline adapter with explicitly synthetic API fixtures.
- [x] No real historical observations obtained. Default status `not empirically populated`; 96/96 months unknown, including 60/60 common-window months. No zero or German-audience inference.
- [x] Trends Help and official Google GitHub reference/archive access worked. Trends Explore returned 429; other provider data tests encountered environment CONNECT denials. No key among checked variable names; required approvals/rights remain unresolved.
- [x] Official Trends archive README/CC BY 4.0 license and 590-entry index read; no suitable Tesla export found by filename screening, not an exhaustive contents search.
- [x] Publication/comments and cumulative-view snapshots kept separate; no historical views, sentiment, KBA association, regression, causal claims or new simulations.
- [x] Local full suite: 147 tests passed (16 new); offline outputs, existing campaign check, contract examples, KBA audit, Ruff and whitespace checks passed.
- [x] Existing KBA/Statistical Contracts/MMM artifacts/estimator isolation and external repositories unchanged.
- [ ] Current-commit remote CI: actual outcome/links maintained in Draft PR.
- [ ] Real-data prerequisite for a future task: supported access/credentials, source-specific legal/retention assessment, actual historical inventory/export and coverage validation. This is an acknowledged scientific blocker, not a completed empirical series.

Draft PR against main only; no automatic merge.
