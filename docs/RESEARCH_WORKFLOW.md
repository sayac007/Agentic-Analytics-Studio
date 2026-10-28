# Vom Datenauftrag zur Ergebnispräsentation

Das Studio führt durch sechs Aufgabenblöcke. Empfänger können Business, Sales,
Supply Chain oder Operations sein. Der vorhandene ausführbare Anwendungsfall bleibt
Tesla Deutschland, monatlich 2018–2025. Ein frei konfigurierbarer Daten-/Modellbaukasten
für andere Projekte ist mit dieser Oberfläche nicht implementiert.

## 1. Daten und Datenschnittstellen definieren

Frage, Empfänger, Entscheidungsbezug und gewünschte Datenlieferungen beschreiben.
Bei einer zusätzlichen Schnittstelle mindestens Quelle/Verantwortliche, Variable,
Region, Einheit, Monatsdefinition, Liefertermin, Revisionsregeln und Umgang mit
Lücken festhalten. Keine Zugangsdaten eintragen. „Speichern“ hält diesen Auftrag
privat in `workspace.sqlite3`, beim beobachteten Projekt in `provenance_json`.
UTC-Änderungszeit wird gespeichert und im Browser lokal angezeigt. Ein vorbelegter
Auftrag ist als Vorlage erkennbar; seine Anlage wird nicht als menschliche Freigabe
ausgegeben. Die Mindestbasis ist eine feste methodische Vorgabe, keine KI-Auswahl.

Aktuelle tatsächlich ausführbare Schnittstellen:

| Reihe | Vorhandener Rechenweg | Analyse-Einheit / Schlüssel |
|---|---|---|
| Tesla-Zulassungen | auditierter KBA-Beobachtungsbestand → Auswahl Marke Tesla, alle Antriebe | Anzahl Neuzulassungen; `YYYY-MM`, Deutschland |
| CPI | gebundene Destatis-Originaldateien mit Dimensions-/Einheitenbelegen → `cpi.normalized.csv` | Index 2020=100; `period,value,unit` |
| Konsumentenkreditzins | gebundener ECB-MIR-CSV-Snapshot → `consumer_credit.normalized.csv` | Prozent pro Jahr, AAR/NDER; `period,value,unit` |
| FX | gebundener ECB-EXR-CSV-Snapshot → `eurusd.normalized.csv` | USD je EUR; `period,value,unit` |
| Diesel | gebundene originale EC-Wochenarbeitsmappe → `diesel_de.normalized.csv` | EUR/Liter, Kalenderüberlappungs-Monatsapproximation; `period,value,unit` |

Native Originalbytes und normalisierte Dateien bleiben hashgebunden. Der Join erfolgt
auf dem vollständigen Monatskalender, ohne Duplikate zu aggregieren oder Lücken
aufzufüllen. Die Wiederherstellung verarbeitet nur die bereits geprüften Snapshots;
neue Vintages und frei beschriebene Schnittstellen werden hier nicht automatisch
angeschlossen. Ihre Aufnahme ist ein eigener fachlicher Arbeitsschritt.

## 2. Muss-Baseline-Treiber

Kalendersaisonalität und vorherige Zielveränderung bilden die feste Mindestbasis.
Zusätzliche Anforderungen können Makrogrößen, Energiepreise, Lieferfähigkeit,
Launches, Promotions, Marktumfeld oder dokumentierte Strukturbrüche sein.
Der Soll-Ist-Abgleich listet die tatsächlich schätzbaren Modelle mit diesen Termen.

Ein Häkchen fügt keine Variable hinzu. Ein Modell ohne geforderten Treiber bleibt
exploratives Referenzergebnis und erfüllt den fachlichen Auftrag nicht vollständig.
Das reine Kalendermodell bleibt als bewusst reduzierte Vergleichsbasis sichtbar.
Quartalsende ist im aktuellen Pilot kein separater Term; Monatssaisonalität ist
kein direkter Lieferfähigkeitsnachweis. Ereignisse sind Recherchekandidaten,
keine vollständige Expositionsreihe und keine automatisch aufgenommenen Regressoren.

## 3–4. Zusammenstellen und analysieren

„Vorhandene Quellen prüfen & Modelle öffnen“ nutzt den bisherigen Rechenweg.
Speichern eines Auftrags oder Erzeugen der Ergebnisübergabe startet keine Fits,
beschafft keine Daten und verändert keine historischen Ergebnisse. Die feste
Methodik, HypoForge-Lags und Pflichtprüfungen bleiben in
[03c](../workorders/03c-empirical-live.md) unverändert.

## 5. Qualität und KI-Kommentierung

Die lokale Checkliste prüft Monatsfolge, endliche Werte und Übereinstimmung der
Lücken mit den gespeicherten Quellmetadaten. Sie zeigt Muss-Treiber-Lücken,
Rang/Endlichkeit, Stichprobenzahlen der gepaarten Basis, Trainings-/Testgrenzen,
negative Vorhersagen und die vorhandenen Stationaritätsbefunde.
Hash-/Protokollprüfung erfolgt über den bestehenden `service.read` vor Anzeige.
Die Liste ist keine neue Rohdatenvalidierung und prüft die Vergleichsstichprobe
anhand gespeicherter n-Werte, nicht durch unabhängige Neuschätzung. Die tatsächlichen
Monatsmengen und Berechnungen bleiben im vorhandenen Ergebnisnachweis nachprüfbar.
Ein technischer Prüfstatus ist keine wissenschaftliche Freigabe.

„Daten erklären“, „Qualität kritisch prüfen“ und „Ergebnisse kommentieren“ bereiten
konkrete Fragen vor. Sie senden nichts. Erst Vorschau, Checkbox und Senden erlauben
den vorhandenen begrenzten API-Aufruf. Der Kontext enthält jetzt den gespeicherten
fachlichen Auftrag (ohne freie Schnittstellennotiz) und die ausgewählte lokale
Qualitätsübersicht. Änderungen am enthaltenen Auftrag widerrufen die bisherige
Kontextbindung. Maximal 11.000 Kontextbytes und weiterhin 16.384 Requestbytes;
keine neuen Provider-Tools, Hintergrundaufrufe oder Budgetänderungen.

## 6. Microsoft-Copilot-Übergabe

„Ergebnisübergabe erstellen“ liest ausschließlich den geprüften Snapshot. Der
Text enthält alle acht Vergleichsvarianten, auch nicht schätzbare oder schlechtere,
Herkunft/Einheiten/Lücken, Muss-Treiber, ausgewählte Koeffizienten mit HAC-Intervallen,
Ziel-/Residuenbefunde, Stichprobenmonate, Grenzen und Snapshot-/Protokoll-Hashes.
Zahlen werden aus den Ergebnissen ohne zusätzliche Anzeigerundung übernommen;
es handelt sich um eine Textprojektion, nicht um ein vollständiges Rohdatenarchiv.
Gespeicherte KI-Texte werden nicht ungeprüft als Evidenz übernommen.

Die [ausführliche Copilot-Anleitung](COPILOT_RESULT_PRESENTATION.md) funktioniert
auch ohne API-Key und ohne verfügbare Ergebnisdateien. Sie enthält einen dreistufigen
Arbeitsauftrag: kritische Evidenzprüfung, sieben Folien mit Sprechernotizen und
abschließender Zahlen-/Aussagenabgleich. Copilot darf fehlende Daten nicht ergänzen
oder eine PowerPoint-Datei behaupten, die seine Umgebung nicht erzeugen kann.

Kopieren nutzt nur die lokale Zwischenablage. Keine automatische Übertragung an
Microsoft, keine Veröffentlichung und keine implizite Freigabe der privaten
Projektergebnisse. Im Unternehmen nur die dafür freigegebene Copilot-Umgebung nutzen.
Die bestehende OpenAI-Konfiguration und ihr zuletzt beobachteter 401-Fehler werden
durch diese Änderung nicht repariert; Schlüsselwechsel und Azure-Live-Test folgen
im nächsten gemeinsamen Termin.

## Reproduzierbare Softwareprüfungen

Mit der vorhandenen Python-3.12-Umgebung und `requirements-empirical.lock`:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v
# Optionaler Browser-Smoke in einer lokalen Umgebung mit Playwright und Chromium:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/research_workflow_browser_smoke.py
```

Der Browser-Smoke nutzt ausdrücklich konstruierte Software-Fixtures in temporären
privaten Verzeichnissen, sperrt Provider-POSTs und prüft, dass keine externen
Browseranfragen erfolgen. Er prüft Desktop/Mobilansicht, Auftrag und Muss-Treiber,
Präsentationsübergabe, gescheiterten Fit, Kontextbindung und Prozessneustart bei
unveränderten Snapshotbytes. Er behauptet weder echte empirische Ergebnisse noch
eine erfolgreiche Live-Antwort von OpenAI.

Am 28.10.2026 lokal ausgeführt: **426 Tests bestanden** (99,643 s), dazu der
Browser-Smoke mit konstruierten Fixtures einschließlich Prozessneustart und
unveränderten Ergebnisbytes. Keine neuen realen Modellfits, keine echten
Provider-Aufrufe und kein Azure-Deployment für diese Änderung.
