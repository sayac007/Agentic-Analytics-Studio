# Codex Workorder – Task 01B.1: Publication-Date Precision Contract

Repository: `sayac007/Agentic-Analytics-Studio`

## Ausgangslage

PR #4 wurde erfolgreich nach `main` gemergt (Merge-Commit `8bb51c967f011df5db45be659001dce593a3045d`).

Task 01B hat vier reale, reproduzierbar extrahierte KBA-Baselines geliefert:

- Tesla: 96 Monate, 2018–2025, alle Antriebsarten
- Toyota: 96 Monate, 2018–2025, alle Antriebsarten
- VW: 96 Monate, 2018–2025, alle Antriebsarten
- Deutscher BEV-Gesamtmarkt: 60 Monate, 2021–2025

Alle vier bleiben `blocked`, weil Statistical Contracts v0.2.0 in Release Records ein vollständiges `published_on`-Datum verlangt. Zahlreiche historische KBA-Veröffentlichungen enthalten jedoch nur Monatspräzision oder gar kein belastbares Veröffentlichungsdatum.

**Aufgabe:** Löse diesen Vertragskonflikt minimalinvasiv und wissenschaftlich nachvollziehbar. Keine Veröffentlichungstage erfinden.

## 1. Vorbereitung

1. Prüfe, dass PR #4 tatsächlich in `main` enthalten ist.
2. Lies `AGENTS.md`, `docs/STATISTICAL_CONTRACTS.md`, `docs/KBA_MULTIBASELINE.md`, `docs/TASK_01_READINESS.md`, die vorhandenen Release-Schemas, Validatoren und KBA-Qualitätsberichte.
3. Erstelle Branch `contracts/task-01b1-publication-precision` vom aktuellen `main`.
4. Arbeite ausschließlich an Provenienz-, Admission- und Dokumentationsregeln.

Keine Änderungen an der MMM-Engine, am synthetischen Referenzfall oder an anderen Repositories.

## 2. Wissenschaftliche Unterscheidung

Trenne folgende Sachverhalte ausdrücklich:

- `reporting_period`: Monat, für den die KBA-Statistik gilt.
- `publication_date`: tatsächlich belegtes Veröffentlichungsdatum mit expliziter Präzision.
- `retrieved_at`: Zeitpunkt des eigenen Downloads.
- `vintage`: unveränderlich identifizierter Quellenstand, insbesondere SHA-256.
- `available_as_of`: frühester belastbar belegter Verfügbarkeitszeitpunkt, sofern nachweisbar.

Ein Abrufdatum ist kein Veröffentlichungsdatum.

Ein Dateiname oder URL-Versionsparameter beweist keinen Veröffentlichungstag.

Ein bekannter späterer Download beweist nicht, dass derselbe Datenstand bereits zu einem früheren Zeitpunkt verfügbar war.

## 3. Minimale Vertragserweiterung

Erweitere den bestehenden Vertrag so, dass Release Records dokumentierte Datumspräzision unterstützen:

- `day`: vollständiges, belegtes ISO-Datum.
- `month`: belegter Veröffentlichungsmonat ohne behaupteten Tag.
- `unknown`: Veröffentlichungsdatum nicht belastbar bekannt.

Bewahre den vorhandenen vollständigen Datumsfall rückwärtskompatibel, soweit technisch möglich.

Verwende keine synthetischen Platzhalter wie den ersten oder letzten Tag eines Monats als angeblich beobachtete Veröffentlichung.

Versioniere die Änderung explizit, beispielsweise als Statistical Contracts v0.2.1, sofern die bestehende Versionierung dies erlaubt.

## 4. Zwei unterschiedliche Admission-Regime

**A. Retrospective immutable-reference admission**

Für eine retrospektive semi-synthetische Generator-Referenz darf die genaue historische Veröffentlichungstagsangabe fehlen, wenn:

- Berichtsmonat und Definition eindeutig sind;
- die reale Beobachtung aus einer überprüften offiziellen Quelle stammt;
- der tatsächlich verwendete Quellenstand durch Hash und Provenienz fixiert ist;
- Nutzungsrechte und Serienkontinuität dokumentiert sind;
- keine konkurrierenden Vintages unaufgelöst bleiben;
- die Engineering-Mindestanforderungen erfüllt sind.

Der Status darf in diesem Modus `admitted` sein, auch wenn die Veröffentlichung nur auf Monatspräzision oder gar nicht datiert ist.

**B. Historical point-in-time / as-of admission**

Für historische Prognose-, Backtest- oder Informationsmengenanalysen muss die tatsächliche zeitliche Verfügbarkeit ausreichend belegt sein.

Bei fehlendem oder unzureichend präzisem Veröffentlichungsdatum bleibt der betreffende historische Informationsstand `blocked` beziehungsweise `not_verified`.

Retrospektive Zulassung darf niemals als historische Echtzeitverfügbarkeit interpretiert werden.

Die beiden Regime müssen maschinenlesbar unterscheidbar sein.

## 5. KBA-Baselines neu evaluieren

Wende die neue Regel auf die vier vorhandenen KBA-Kandidaten an.

Nutze ausschließlich die bereits verifizierten Daten und den vorhandenen Quellenkatalog.

Erstelle einen deterministischen Admission-Report mit:

- Baseline-ID und Definition;
- geprüftem Zeitraum;
- Datenlänge und möglichem Train-/Holdout-Split;
- Provenienz- und Vintage-Status;
- Veröffentlichungstagspräzision;
- retrospektivem Admission-Status;
- Point-in-time-Admission-Status;
- expliziten Gründen für jede Zulassung oder Sperre.

Erwartung, **keine erzwungene Testvorgabe**: Wenn keine weiteren Blocker existieren, sollten die vier Baselines für den retrospektiven Generatorgebrauch zugelassen werden können. Für historische As-of-Analysen bleiben die Einschränkungen bestehen.

Insbesondere die 60-monatige BEV-Reihe darf nicht künstlich bis 2018 verlängert werden.

## 6. Technische Grenzen

- Keine Dateninterpolation.
- Keine Änderung der originalen KBA-Beobachtungen.
- Keine erfundenen Veröffentlichungstage.
- Keine Änderung der bestehenden synthetischen MMM-Ergebnisse.
- Keine Monte-Carlo-Simulation.
- Keine Modellschätzung.
- Keine Veränderung der Estimator-Isolation.
- Keine automatische Freigabe bei ungeklärten Lizenz-, Hash- oder Definitionskonflikten.

Behalte den bestehenden Fail-closed-Ansatz bei.

## 7. Tests und Dokumentation

Ergänze gezielte Tests für:

- belegte Tagespräzision;
- Monatspräzision;
- unbekanntes Veröffentlichungsdatum;
- rückwärtskompatible alte Release Records;
- retrospektive Zulassung bei vollständiger übriger Provenienz;
- Point-in-time-Sperre bei fehlender zeitlicher Evidenz;
- Sperre bei Hash-, Lizenz-, Definitions- oder Kontinuitätsproblemen;
- korrekte Trennung der beiden Admission-Regime.

Aktualisiere die relevanten Statistik- und KBA-Dokumente.

Halte die Implementierung klein. Keine generische Metadatenplattform und keine unnötige Ausweitung der bestehenden Sicherheitsinfrastruktur.

## 8. Abschluss und PR

Erstelle einen Draft-PR gegen `main`.

Berichte:

1. Welche Vertragsfelder und Regeln wurden verändert?
2. Welche Rückwärtskompatibilität wurde geprüft?
3. Welchen Status haben die vier Baselines in beiden Admission-Regimen?
4. Welche Blocker bleiben bestehen?
5. Welche Tests wurden tatsächlich ausgeführt?
6. Ist die CI für den exakten PR-Head erfolgreich?

Keine automatischen Merges.

**Wissenschaftliches Abnahmekriterium:** Retrospektive Verwendbarkeit und historische Informationsverfügbarkeit sind sauber getrennt. Keine fehlende Information wurde durch Scheingenauigkeit ersetzt.
## Umsetzung und lokale Abnahme

- [x] PR #4 als gemergt geprüft; Branch vom aktuellen main `8bb51c9`.
- [x] Generator-Provenienz v0.2.1 mit day/month/unknown; v0.2.0 und alte Tagesrecords weiter validierbar.
- [x] Veröffentlichung, Abruf, Quellen-Hash und belegte Vintage-Verfügbarkeit getrennt.
- [x] Zwei explizite Regime; retrospektiv alle vier zugelassen, historisch alle vier gesperrt.
- [x] Deterministischer Bericht mit Definition, Zeitraum, Split, Datumspräzision, Hash-Bindungen und Gründen.
- [x] 115 lokale Tests bestanden, darunter 16 neue Tests; Cache-Reextraktion und Offline-Audit bestanden.
- [x] Keine neuen Daten, unveränderte Originalbeobachtungen, MMM-Implementierung und synthetische Ergebnisse.
- Draft-Review und tatsächliche CI-Läufe für den exakten Head werden im zugehörigen PR dokumentiert.

Details: `docs/PUBLICATION_PRECISION.md`. Nicht selbst mergen.
