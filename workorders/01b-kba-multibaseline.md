# Codex Workorder – Task 01B: KBA Multi-Baseline Acquisition

Repository: `sayac007/Agentic-Analytics-Studio`

## Ausgangslage

Task 00.5 hat die Statistical Contracts v0.2.0 etabliert. Task 01A implementiert die synthetische MMM-Pipeline mit Oracle-Transformationen, OLS, HAC-Unsicherheit und Recovery-Evaluation.

Der erste synthetische Lauf zeigte schlechte Recovery trotz korrekter Transformationen. Dieses Ergebnis darf nicht durch nachträgliches Tuning korrigiert werden.

Unser nächstes Ziel ist die Erweiterung des Benchmarks um mehrere **amtlich dokumentierte monatliche KBA-Baselines**.

## 0. Branch und Arbeitsregeln

1. Prüfe zunächst den aktuellen Zustand von `main` und PR #3.
2. Beginne erst, wenn PR #3 vollständig gemergt ist. Falls nicht, stoppe und melde den Blocker. Verwende keinen ungemergten Feature-Branch als Ausgangsbasis.
3. Lies `AGENTS.md`, `docs/STATISTICAL_CONTRACTS.md`, `docs/SOURCE_CATALOG.md`, `docs/TASK_01_READINESS.md`, `docs/DECISIONS.md` und die bestehenden Provenienzverträge.
4. Erstelle `data/task-01b-kba-multibaseline` von `main`.
5. Arbeite in einem eigenen Draft-PR. Nicht selbst mergen.

Keine Änderungen an WKR, HypoForge oder Kinderwelt.

## 1. Offizielle KBA-Daten erschließen

Recherchiere systematisch die offiziellen KBA-Veröffentlichungen, insbesondere FZ 10 sowie gegebenenfalls weitere passende amtliche Monatsstatistiken.

Wichtig: Verifiziere zunächst, ob FZ 10 tatsächlich alle benötigten historischen Monatsreihen und die BEV-Abgrenzung enthält. Nutze gegebenenfalls weitere KBA-Primärquellen mit eigener Quellen- und Lizenzdokumentation. Keine unbestätigte Annahme, dass alle Reihen aus einer einzigen Tabelle stammen.

Prüfe für jede relevante Veröffentlichung:

- Berichtsmonat und Veröffentlichungsdatum.
- Primär-URL und tatsächlich verfügbare Rohdatei.
- Dateiformat, Tabellenblatt und genaue Tabellenposition.
- SHA-256 der Rohdatei.
- Veröffentlichungsstand und mögliche Revisionen.
- Lizenz, Nutzungs- und Weiterverbreitungsrechte.
- Konsistenz der Definitionen über die Zeit.

Erstelle einen maschinenlesbaren Quellenkatalog.

Archivlisten oder Suchergebnisse allein gelten nicht als verifizierte Monatsbeobachtungen.

## 2. Vier Baseline-Kandidaten

Prüfe die Verfügbarkeit folgender Reihen:

**A. Tesla Deutschland**

Monatliche Neuzulassungen der Marke Tesla, möglichst über einen langen zusammenhängenden Zeitraum.

**B. BEV-Gesamtmarkt Deutschland**

Monatliche Neuzulassungen batterieelektrischer Pkw über alle Marken, sofern die amtliche Quelle eine konsistente Definition erlaubt.

**C. Vergleichsmarke mit ruhigerem Verlauf**

Wähle aus den tatsächlich verfügbaren Marken anhand vorab festgelegter deskriptiver Kriterien.

**D. Zweite Vergleichsmarke mit anderem Profil**

Wähle eine weitere Marke, die hinsichtlich Volumen, Saison oder Volatilität einen informativen Kontrast bietet.

Für C und D gilt: Die Auswahl muss erfolgen, bevor irgendeine MMM-Recovery auf diesen Reihen untersucht wird. Kein Cherry-Picking nach Modellergebnissen.

Dokumentiere ausdrücklich, ob eine Markenreihe sämtliche Antriebsarten oder ausschließlich BEV umfasst. Solche Definitionen dürfen nicht verwechselt werden.

## 3. Reproduzierbare Extraktion

Implementiere eine kleine Python-Datenpipeline:

- Originaldateien unverändert referenzieren oder, sofern zulässig, archivieren.
- Daten aus verifizierten Tabellen extrahieren.
- Monatsindex im Format `YYYY-MM`.
- Einheitliche Spalten für Monat, Wert, Reihe, Quelle und Vintage.
- Ganzzahlige, nichtnegative Zulassungswerte.
- Prüfung auf doppelte, fehlende oder widersprüchliche Monate.
- Keine Interpolation, kein Forward-Fill und keine stillschweigende Nullsetzung.
- Rohdaten-Hash und normalisierten Daten-Hash getrennt speichern.
- Reproduzierbare Ergebnisse bei wiederholter Extraktion.

Falls die amtlichen Dateien unterschiedliche Layouts verwenden, implementiere explizite, versionierte Parser-Profile statt heuristischer Tabellenannahmen.

Ein Parser darf bei unbekanntem Layout nicht stillschweigend Werte aus möglicherweise falschen Zellen übernehmen.

## 4. Datenabdeckung und Benchmark-Zulassung

Erstelle für jede Reihe einen Coverage-Bericht:

- frühester und letzter verifizierter Monat;
- Anzahl verifizierter Beobachtungen;
- fehlende Monate;
- längstes zusammenhängendes Zeitfenster;
- Quellen- und Lizenzstatus;
- Eignung für die bestehenden Benchmark-Anforderungen.

Beachte die Mindestanforderungen aus v0.2.0:

- mindestens 48 Trainingsmonate;
- mindestens 12 zusammenhängende Holdout-Monate;
- ausreichende Residual-Freiheitsgrade;
- vollständige Provenienz und Rechteprüfung.

Verwende die Statuswerte:

- `admitted`: Anforderungen vollständig nachgewiesen;
- `insufficient_coverage`: zu wenige zusammenhängende Monate;
- `blocked`: andere ungeklärte Voraussetzungen, insbesondere Herkunft, Definition oder Nutzungsrechte.

Diese Statuswerte sind als Datenzulassung zu verstehen, nicht als wissenschaftliche Validierung der MMM-Recovery.

Eine unvollständige Tesla-Reihe bleibt unvollständig. Sie darf nicht durch synthetische Werte als beobachtete Reihe verlängert werden.

## 5. Baseline-Charakterisierung

Berechne für ausreichend lange, tatsächlich verifizierte Reihen deskriptive Kennzahlen:

- Mittelwert und Standardabweichung;
- Variationskoeffizient;
- Trendindikatoren;
- Monats- und Quartalsendmuster;
- robuste Ausreißerkennzahlen;
- mögliche Strukturbrüche als explorative Hinweise.

Nutze nach Möglichkeit ein gemeinsames Kalenderfenster für den Vergleich. Falls das nicht möglich ist, dokumentiere den Einfluss unterschiedlicher Zeitfenster.

Eine ruhige Reihe ist nicht automatisch eine kausal einfachere Reihe.

Strukturbruchhinweise sind keine bewiesenen Ursachen. Ereignisse wie Förderänderungen, Lieferwellen oder Preisänderungen dürfen nur mit gesonderter Evidenz als solche bezeichnet werden.

## 6. Forschungsprotokoll für Multi-Baseline-Recovery

Erstelle `docs/MULTIBASELINE_RECOVERY_PROTOCOL.md`.

Definiere, wie wir später denselben semi-synthetischen Media-Effekt und dieselbe Schätzmethode auf verschiedenen Baselines vergleichen.

Unterscheide dabei zwei Experimente:

**Experiment A – Relative Effektskala**

Der injizierte Effekt wird relativ zum jeweiligen Baseline-Niveau skaliert. Dadurch prüfen wir Recovery unter vergleichbaren relativen Effekten.

**Experiment B – Absolute Effektskala**

Der injizierte Effekt wird in denselben absoluten Count-Equivalent-Einheiten auf alle Baselines angewendet. Dadurch prüfen wir, wie sich unterschiedliche Signal-Rausch-Verhältnisse auswirken.

Spezifiziere außerdem:

- gemeinsame oder bewusst vergleichbare Beobachtungsfenster;
- identische Transformationen und Modellspezifikationen;
- vorab festgelegte Media- und Noise-Generierung;
- gepaarte Zufallsstreams beziehungsweise Common Random Numbers;
- explizite Confounding-Szenarien;
- Recovery-Fehler für Beiträge und Response-Kurven;
- Intervallabdeckung und Detection-Raten in späteren Replikationen;
- Berücksichtigung gescheiterter Fits;
- keine Baseline-Auswahl anhand der Recovery.

Das Protokoll soll auf die spätere Stufe C vorbereiten.

Noch keine umfangreichen Monte-Carlo-Simulationen und keine MDE-Behauptungen implementieren.

## 7. Integration in Agentic Analytics Studio

Prüfe, wie die verifizierten KBA-Baselines später als private Generator-Referenzen verwendet werden können.

Behalte die strikte Trennung bei:

KBA-Referenz → Generator → semi-synthetisches Outcome → isolierter Estimator → Evaluator.

Die echten Zulassungen dürfen niemals als zusätzlicher Estimator-Regressor eingeschleust werden.

Verwende die vorhandenen Statistical Contracts v0.2.0. Falls Erweiterungen nötig erscheinen, dokumentiere sie als Vorschlag; führe keine inkompatiblen Schemaänderungen ohne Begründung ein.

## 8. Tests und CI

Implementiere Offline-Tests für:

- Parser-Profile und fehlerhafte Tabellenlayouts;
- exakte Monats- und Markenidentifikation;
- BEV-vs.-Gesamtmarken-Abgrenzung;
- Rohdaten- und Output-Hashes;
- doppelte und fehlende Monate;
- Vintage-Konflikte;
- Coverage und Admission-Gates;
- deterministische Extraktion.

Keine Live-Downloads als Voraussetzung für die GitHub-Actions-Tests.

Falls der Zugriff auf historische KBA-Dateien scheitert, liefere einen funktionsfähigen Extraktionsrahmen mit klar gekennzeichneten Test-Fixtures und einem ehrlichen Blocker-Bericht. Keine erfundenen historischen Beobachtungen.

## 9. Deliverables

Erstelle:

1. `docs/KBA_MULTIBASELINE.md` – Quellen, Abdeckung, Definitionen, Auswahl und Blocker.
2. `docs/MULTIBASELINE_RECOVERY_PROTOCOL.md` – vorab festgelegtes Forschungsdesign.
3. Einen maschinenlesbaren Quellen-/Vintage-Katalog.
4. Einen reproduzierbaren Extraktor mit dokumentierten Parser-Profilen.
5. Datenqualitäts- und Admission-Reports.
6. Tests, CI-Erweiterungen und Reproduktionsanleitung.

Wenn echte historische Dateien rechtlich weitergegeben werden dürfen, können verifizierte abgeleitete Reihen ins Repository aufgenommen werden. Andernfalls dokumentiere den reproduzierbaren Beschaffungsweg, die benötigten Quelldateien und deren Hashes.

## 10. Abschlussbericht

Erstelle einen Draft-PR gegen `main`.

Berichte ausdrücklich:

- Welche Baselines wurden tatsächlich verifiziert?
- Wie viele zusammenhängende Monate liegen jeweils vor?
- Welche sind für den Benchmark zugelassen?
- Welche bleiben blockiert und warum?
- Wie viele Tests wurden tatsächlich ausgeführt?
- Welche GitHub-Actions-Läufe sind erfolgreich?
- Welche Daten können später ohne wissenschaftliche Überinterpretation in Stufe C verwendet werden?

Keine MMM-Engine-Änderungen, keine UI, kein MCP-Server, keine Bayesian- oder Geo-Test-Implementierung.

Nicht selbst mergen.
## Ausführung und Abnahme — Task 01B

- [x] PR #3 vor Beginn als vollständig gemergt geprüft; Branch von aktuellem main.
- [x] 96 reale FZ-10-Dateien verifiziert; getrennte Roh-/Output-Hashes und Vintage-Katalog.
- [x] Tesla/Toyota/VW je 96, ausdrücklich definierter BEV-Gesamtmarkt 60 Monate.
- [x] Deskriptive Markenauswahl vor jedem Recovery-Lauf; vollständiger Auswahlpool erhalten.
- [x] Vier Parser-Profile, dokumentierte Sonderfälle, Offline-Fixtures ohne Coverbilder.
- [x] Coverage-, Qualitäts-, Charakterisierungs- und Jahresabgleichberichte.
- [x] 99 lokale Tests bestanden, einschließlich 26 neuer KBA-Tests; vollständige Rohdaten-Reextraktion geprüft.
- [x] Forschungsprotokoll für relative/absolute Skalen und gepaarte spätere Simulationen.
- [x] Alle vier Referenzen ehrlich `blocked`: Veröffentlichungstag nicht lückenlos belegt.
- [x] Keine Engine-/Schema-/Upstream-Änderung, kein beobachteter MMM-Lauf oder MDE-Claim.
- [ ] Draft-PR und genauer Remote-CI-Status: siehe zugehörigen Pull Request; nicht selbst mergen.

Details und ausgeführte Befehle: `docs/KBA_MULTIBASELINE.md`.
