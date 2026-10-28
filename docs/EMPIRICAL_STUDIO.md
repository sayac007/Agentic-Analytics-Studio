# Empirischer Studio-Pilot

Das Produkt untersucht reale monatliche Registrierungsentwicklung und verfügbare
Treiber. Der synthetische Benchmark bleibt ein unverändertes separates Archiv.
Die vom Nutzer am 2026-10-28 gewünschte Methodik steht vor Ausführung der neuen
Fits in [03c](../workorders/03c-empirical-live.md), einschließlich Amendment 1.1.
Task 01G/01I.3 und ihre historischen Originalergebnisse werden nicht verändert.

## Daten und Rechenweg

2018-01–2025-12: KBA Tesla alle Antriebe als Registrierungsziel, Destatis nationaler
CPI 2020=100, ECB Konsumentenkredit-AAR/NDER, ECB USD/EUR sowie qualifizierte EC-
Dieselpreise. Diesel ist eine Wochen-zu-Monats-Approximation; 13 Monate fehlen.
Kein E10-Ersatz, Brent, synthetischer Spend oder erfundener Launch-Index.
Quellenzuordnung, Einheiten, Credits und ursprüngliche Snapshots bleiben erhalten.
Die aktuelle Nutzeranweisung autorisiert diese separate private Exploration;
der alte QA-only-Manifeststatus und frühere source-spezifische Ausnahmen bleiben
historische Belege und werden nicht als neue öffentliche Freigabe umgeschrieben.

Das zuvor archivierte Quellenpaket kann privat eingebunden werden:

```sh
AAS_EMPIRICAL_SOURCE_DIR=/PRIVATE/source-archive .venv/bin/python -m demo
```

Ohne diesen Pfad lädt die Schaltfläche nur die sechs benötigten Originaldateien
über die im bestehenden Manifest dokumentierten offiziellen HTTPS-URLs nach.
Jede Datei muss dem bereits geprüften SHA-256 entsprechen. Neue/andere Vintages
werden nicht automatisch aufgenommen. Die Normalisierung muss wiederum alle
vier ursprünglichen CSV-Hashes reproduzieren. Originale Quellen-/Rechteprüfungen
bleiben als gebundene historische Datensätze im Manifest erhalten; das behauptet
keinen erneuten Abruf ihrer alten HTML-Bytes. Frische Datenabrufzeiten stehen
separat in `restoration.json`. Die historischen Originalabrufzeiten bleiben erhalten.
Fehlt ein identischer Abruf, kann der Besitzer die entsprechende Originaldatei
privat auswählen; die gleiche Hashprüfung gilt. Keine Ersatz- oder interpolierten Werte.

Bei lokalem Start aus dem Checkout liegen Quelldateien und Ergebnisversionen im
privaten Schwesterordner `.aas-private/` außerhalb des Repositorys. Der bestehende
SQLite-Workspace wird dabei nicht verschoben. Bei einem bereits außerhalb des
Repositorys konfigurierten `AAS_WORKSPACE_DIR` liegen Quellen unter `observed-sources/`
und nach Protokoll/Implementierung getrennte Ergebnisversionen unter `empirical/`.
`AAS_WORKSPACE_DIR` steuert den Workspace; `AAS_EMPIRICAL_DIR` kann für einen
vorhandenen unveränderlichen Ergebnisordner explizit gesetzt werden. Keine Datei
wird aus Nutzereingaben als beliebiger Serverpfad geöffnet. Alte Ergebnisse
werden nicht überschrieben. Jede Anzeige prüft ihren Snapshot erneut.

## Modelle und Pflichtdiagnostik

Ziel ist `Δlog(1 + Registrierungen)`. Die acht Varianten umfassen Kalender,
Kalender plus vorherige Zielveränderung, sowie zwei Makrovarianten jeweils mit
festem gemeinsamem exogenem Lag 1, 2 oder 3. CPI und FX werden logarithmisch
verändert; Kreditzinsen in Prozentpunkten, Diesel als logarithmische Änderung.
HypoForge `FeatureSpec/evaluate` führt `diff` und `lag` tatsächlich aus, am
gepinnten Commit `c47f636d24a39a820574a13133d6af693134a180`.
Ein Vollkalender erhält fehlende Monate und deren Auswirkungen auf Differenzen/Lags.
Es wird weder ein Lag pro Variable gesucht noch die beste Holdout-Spalte gewählt.

Vor der Beurteilung stehen ADF/KPSS für Originalzulassungen, log1p-Niveaus und
modellierte Veränderungen. Jedes Modell erhält zusätzlich Trainings- und
Gesamtfenster-Residuenprüfungen. Feste drei Lags, kein Autolag, `ct` bei Niveaus,
`c` bei Veränderungen/Residuen. Bei Lücken wird das längste tatsächlich
zusammenhängende Segment verwendet, frühestes bei Gleichstand; unter 27 Monaten
bleibt die Prüfung ausdrücklich nicht schätzbar. Niemals Zeilen zusammenrücken.

ADF prüft die Nullhypothese Einheitswurzel; KPSS prüft Stationarität. P-Wert-Grenzen
und Warnungen werden erhalten. Unterstützende, widersprüchliche, adverse und
uneindeutige Ergebnisse führen zu keiner automatischen Spezifikationsänderung.
Übliche Test-p-Werte geschätzter OLS-Residuen sind explorativ, kein kalibrierter
residuenbasierter Kointegrationstest. Stationarität bedeutet weder weißes Rauschen
noch Exogenität. Diagnosehinweise sind keine automatische Modellabnahme.

R² bezieht sich auf monatliche Log-Veränderungen im ausgewiesenen Fenster.
Die 2025-Vorhersagen verwenden davon getrennte Fits bis 2024-12 und die tatsächlich
bekannten Zulassungen des jeweiligen Vormonats. Es handelt sich um retrospektive
bedingte Ein-Monats-Prognosen. Historische Verfügbarkeit/Revisionsstände sind nicht
nachgewiesen; 2025 war bereits Gegenstand früherer Forschung. Kein unberührter
prospektiver Test und keine Dezember-Prognose für zwölf folgende Monate. Die
Rücktransformation liefert nicht automatisch einen unverzerrten erwarteten Count;
es werden keine nachträglichen, holdout-optimierten Korrekturen angewendet.
Jeder Zusatzvergleich verwendet dieselben Trainings-/Testmonate. Insbesondere
kann die Dieselvariante wegen der anderen Trainingsmaske nicht unpaarig als
zusätzlicher Diesel-Nutzen interpretiert werden. Negative Ergebnisse bleiben sichtbar.

VARX ist eine optionale multivariate Erweiterung bei mehreren gemeinsam zu
modellierenden endogenen Reihen. Sie bleibt vom Standardmodell getrennt und
ist hier noch nicht als ausführbare Methode implementiert. Eine spätere Wahl
braucht einen festgelegten kleinen Variablen-/Lagraum, Stationaritäts-/gegebenenfalls
Kointegrationsprüfung und Vergleich gegen die einfache dynamische Basis.

## Gespräch und Datenschutz

Die empirische Oberfläche besitzt einen eigenen Kontext-/Freigabepfad.
Übermittelt werden nur Frage, ausgewählte Modellkennzahlen, Koeffizienten,
Diagnosezusammenfassung und Grenzen. Keine Rohdateien, vollständigen Monatsarrays,
Quellen-Permits, anderen Projekte oder versteckten Notizen. Der Nutzer prüft die
sichtbare Projektion und erlaubt ausdrücklich diesen kostenpflichtigen Versand
beobachteter privater Ergebnisse. Die synthetische Archivfreigabe gilt dafür nicht.

Ein Provider-Aufruf je Anfrage, keine Tools, Shell, autonomen Fits oder Webzugriffe.
Bisheriger dauerhafter Budgetschutz wird über dieselbe SQLite-Buchführung genutzt;
unbekannte Nutzung behält die Reservierung. Neue Fragen sind keine automatische
Erlaubnis zum Mitsenden älterer Fragen. Das bisherige Gespräch bleibt lokal erhalten.
Modelltext ist Interpretation; konkrete Zahlen und Diagnose kommen aus dem
verifizierten Snapshot. Die Datenqualität hängt nicht von einem aktiven API-Key ab.
`store:false` ist nicht null Speicherung. Kein umfassendes DLP- oder Rechnungsversprechen.

## Tatsächlich ausführbare Prüfungen

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -p test_empirical.py -v
# Nur mit einem bereits vorhandenen privaten, geprüften Quellenarchiv:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/empirical_browser_smoke.py --source-archive /PRIVATE/source-archive
```

Software-Tests verwenden ausdrücklich konstruierte Test-Fixtures, keine versteckten
empirischen Belege. Das tatsächliche private Ausführen, die Wiederherstellung
identischer Originalbytes, Browser-/Containerprüfungen und Azure-Live-Status
werden separat im PR berichtet. Keine realen Werte oder privaten Ergebnisse
werden zu GitHub CI hochgeladen. Eine grüne CI belegt keinen echten Azure- oder
OpenAI-Aufruf. [Azure-Anleitung](AZURE_PRIVATE_STUDIO.md).

Lokal am 2026-10-28 ausgeführt: vollständige Suite mit **405 bestandenen Tests**;
nach der letzten Kontext-Präzisierung nochmals alle **16 empirischen Tests**.
Der echte Browser-Smoke mit dem geprüften privaten Quellenpaket bestand für alle
acht Modelle einschließlich Pflichtdiagnostik, Kontextvorschau und Neustart ohne
Änderung der gespeicherten Ergebnisbytes. Der gebaute Container bestand zusätzlich
mit UID 10001, schreibgeschütztem Root-Dateisystem, 1536-MiB-Limit und ausgeschaltetem
Netzwerk; private Quellen lagen auf einem separaten Volume, Ergebnis-Hash blieb
nach Neustart identisch. Ein zunächst voller lokaler Docker-Speicher erforderte
Cache-Bereinigung und Wiederholung; das war kein erfolgreicher erster Testlauf.
Kein tatsächlicher OpenAI-Aufruf oder Azure-Deployment wird damit behauptet.
