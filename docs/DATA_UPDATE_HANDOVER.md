# Daten pflegen und prüfen – Übergabe für die gemeinsame Einarbeitung

Stand: 28.10.2026; geprüft gegen Repository-Stand `b5a5d4051224bd1169d24c89fcd68b9198d9172c`.

Ziel: Eine Kollegin kann Daten finden, einen Monatsnachtrag nachvollziehen und
Änderungen gegenüber dem bisherigen Bestand prüfen. Dafür braucht sie weder das
Studio noch R. Zuerst gemeinsam die [KBA-Übung](examples/kba-update/README.md)
durchgehen; danach beurteilen wir anhand ihrer eigenen Durchführung, was sie
selbstständig übernehmen kann. Eine einsatzbereite Firmenlösung ist damit noch
nicht nachgewiesen.

Als Arbeitsweg ist **Excel Desktop mit Power Query** vorgesehen. Ob diese Funktionen
und Microsoft 365 Copilot im Unternehmen verfügbar und freigegeben sind, ist noch
zu klären. Copilot ist optional; die Datenprüfung muss auch ohne ihn nachvollziehbar
bleiben. Firmeninterne Dateien bleiben in den dafür freigegebenen Ablagen und
Werkzeugen. Eine private Studio-Instanz oder ein privater KI-Account ist dafür kein
Ersatz.

## 1. Welche Daten liegen wo?

Repository-Pfade sind relativ zur Projektwurzel. Ein Link zu Metadaten bedeutet
nicht, dass die zugehörigen privaten Beobachtungen im Repository stehen.

| Daten | Vorhandener geprüfter Stand | Ablage / Nachweis | Wichtige Bedeutung |
|---|---|---|---|
| KBA Tesla, Toyota, VW | Je 96 Monate, 2018-01–2025-12 | Öffentliche Werte: [`observations.csv`](../data/kba/derived/observations.csv); Original-URLs/Versionen: [`sources.json`](../data/kba/sources.json) | Pkw-Neuzulassungen nach Marke, **alle Antriebe**; keine Verkäufe, Bestellungen oder reinen BEV-Markenwerte |
| Deutscher BEV-Gesamtmarkt | 60 Monate, 2021-01–2025-12 | Gleiche CSV, `series=market:BEV`, `powertrain=BEV_only` | Frühere 36 Monate nicht unter derselben Definition verifiziert; keine Nullen ergänzen |
| Verbraucherpreisindex | 96 Monate, 2018-01–2025-12 | Privat: `cpi.normalized.csv`; öffentlicher [Quellen-/Hashnachweis](../data/verified_sources/manifest.json) | Destatis 61111-0002, Deutschland, **Index 2020=100**; nicht die Inflationsrate |
| Konsumentenkreditzins | 96 Monate, gleicher Zeitraum | Privat: `consumer_credit.normalized.csv`; gleicher Nachweis | ECB `MIR.M.DE.B.A2B.A.R.A.2250.EUR.N`, AAR/NDER in % pro Jahr; kein APRC |
| EUR/USD | 96 Monate, gleicher Zeitraum | Privat: `eurusd.normalized.csv`; gleicher Nachweis | ECB `EXR.M.USD.EUR.SP00.A`, **USD je EUR**, monatlicher Referenzkurs |
| Deutscher Dieselpreis | 83 von 96 Monaten, gleicher Zeitraum | Privat: Original-Wochenarbeitsmappe und `diesel_de.normalized.csv`; gleicher Nachweis | Mit Steuern, EUR/1.000 Liter → EUR/Liter; abgeleitete Monatsapproximation, keine amtliche Monatsmessung |
| Tesla-Launches, Verfügbarkeit, Rückrufe | 17 recherchierte Einträge, Zeitraum 2018–2025 | [`evidence.json`](../data/tesla_product_events/evidence.json), [`monthly_indicators.csv`](../data/tesla_product_events/monthly_indicators.csv), [Datenwörterbuch](../data/tesla_product_events/DATA_DICTIONARY.md) | 10 eng gefasste Aussagen verifiziert, 6 teilweise, 1 ausgeschlossen; **keine vollständige Ereignisreihe** |
| Kampagnen und Promotions | Recherchierte Belege, keine vollständige Media-Messung | [`evidence.json`](../data/tesla_campaigns/evidence.json), [Erläuterung](../data/tesla_campaigns/README.md) | Fehlender Beleg bedeutet unbekannt, nicht „keine Werbung/Promotion“ |
| Google Trends | Privater manueller Export; empirische Aufnahme noch offen | [Importanleitung](GOOGLE_TRENDS_EXTENDED_IMPORT.md), [dokumentierter Prüfstand](../data/organic_attention/task01g1_status.json) | Suchinteresse 0–100, kein Suchvolumen oder Spend; nicht als bereits freigegebene Modellreihe behandeln |
| Kalender | Aus dem Monatsschlüssel berechenbar | `period` im Format `YYYY-MM` | Monat, Jahr, Quartalsende; fehlende Monate bleiben im Kalender sichtbar |

**Private Ablage noch festlegen:** Die vier Makro-/Energie-CSV-Dateien und ihre
Originale liegen außerhalb von Git. Es gibt noch keinen hier bestätigten,
für die Kollegin zugänglichen Firmenpfad. Beim ersten Termin tragen wir den
tatsächlichen freigegebenen Ort und die zuständige Person ein. Private
Forschungsfreigaben sind keine Freigabe für eine Unternehmensnutzung oder
öffentliche Weitergabe. Brent ist wegen offener Drittrechte kein regulärer Input.

## 2. Quellen finden und neue Lieferungen vorbereiten

| Quelle | Vorgehen beim manuellen Update | Vor Übernahme prüfen |
|---|---|---|
| [KBA Monatsarchiv](https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/MonatlicheNeuzulassungen/monatl_neuzulassungen_node.html) | Gewünschten Berichtsmonat und FZ 10 wählen; Originaldatei unverändert ablegen. Die dokumentierte Marken-Gesamtsumme übernehmen, nicht Modellzeilen addieren. | Monatsanzahl statt kumulierter Jahreszahl oder Marktanteil; exakte Marke, Antriebsdefinition, Tabellenüberschrift und etwaige Korrekturhinweise. Für vorhandene Monate stehen geprüfte Blatt-/Zelladressen in [`locations.json`](../data/kba/derived/locations.json). Neue Layouts gemeinsam prüfen. |
| [Destatis 61111-0002](https://genesis.destatis.de/datenbank/online/statistic/61111/table/61111-0002) | Deutschland, monatlichen Gesamtindex auswählen und Originalexport speichern. | Index **2020=100** statt Monats-/Jahresveränderung; bei neuer Indexbasis gesamte Historie separat abgleichen, nicht Reihen verschiedener Basen aneinanderhängen. |
| [ECB Konsumentenkredit](https://data.ecb.europa.eu/data/datasets/MIR/MIR.M.DE.B.A2B.A.R.A.2250.EUR.N) | Exakte Reihenkennung öffnen, Zeitraum auswählen, CSV exportieren; `TIME_PERIOD`, `OBS_VALUE` und Status erhalten. | Reihenkennung und Einheit unverändert; APRC und AAR/NDER nicht verwechseln; vorläufige/revidierte Werte kennzeichnen. |
| [ECB EUR/USD](https://data.ecb.europa.eu/data/datasets/EXR/EXR.M.USD.EUR.SP00.A) | Monatliche Reihe auswählen und Original-CSV erhalten. | USD je EUR; keine Tageswerte, inversen Kurse oder anderen Aggregationen unter gleichem Namen ergänzen. |
| [EC Weekly Oil Bulletin](https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en) | Original der historischen Wochenarbeitsmappe separat speichern. | Deutschland, Automotive Gas Oil, mit Steuern und EUR/1.000 Liter anhand der Kopfzeilen prüfen. `Prices with taxes!BD` gilt für den geprüften alten Snapshot, nicht automatisch für neue Dateien. Monatsaggregation beim ersten Update gemeinsam reproduzieren. |
| Ereignisse / Trends | Datierte Originalbelege bzw. manuellen Trends-Export mit vollständigen Einstellungen erhalten. | Ereignisdatum von Veröffentlichungsdatum unterscheiden; DE-Bezug und Aussageumfang belegen. Trends-Abfragen haben eigene Skalierung und ggf. unvollständige letzte Monate; Exporte nicht ungeprüft zusammensetzen. |

Die Links stammen aus dem bestehenden Quellenbestand; ihre heutige Erreichbarkeit
wurde für diese Übergabe nicht erneut getestet. Die erste Übung braucht keinen
neuen Download.

**Für jede echte neue Lieferung:** Quelle/URL, Reihenkennung und Definition,
Einheit, Berichtszeitraum, Veröffentlichungsdatum mit bekannter Genauigkeit,
tatsächlichen Abrufzeitpunkt mit Zeitzone, Originaldateiname, Version/Revision und
Nutzungsumfang festhalten. Ein unbekanntes Datum bleibt unbekannt. Bei neuen Dateien
werden neue Prüfsummen erfasst; alte Hashes werden nicht auf neue Dateien übertragen.

## 3. Ein kleiner, wiederholbarer Monatsablauf

Die folgenden Ordner sind ein Vorschlag innerhalb der **noch festzulegenden**
freigegebenen Projektablage:

```text
<freigegebene Projektablage>/Datenpflege/<tatsächliches Abrufdatum>/
    01_Originale/      unveränderte Lieferung plus bisheriger Vergleichsstand
    02_Aufbereitung/   Excel-Arbeitsmappe mit gespeicherten Power-Query-Schritten
    03_Pruefung/       neue Monate, Revisionen, Fehler und kurze Entscheidung
```

1. **Bestand sichern und Lieferung getrennt importieren.** In Excel über
   „Daten → Aus Text/CSV“ laden, Trennzeichen und Datentypen bewusst wählen.
   Monatsschlüssel als Text erhalten; Dezimalpunkt/-komma nach Quelle behandeln.
   Automatische Typänderungen vor dem Laden prüfen. Originale nicht überschreiben;
   den ursprünglichen Wert zusätzlich als Textspalte erhalten.
2. **Definition und Struktur vergleichen.** Gleiche Quelle, Region, Einheit,
   zeitliche Auflösung und Kennzahl? Pflichtfelder vollständig? Werte wirklich
   Zahlen statt Text oder Fehler? KBA-Anzahlen müssen ganzzahlig und nicht negativ
   sein. Ganzzahligkeit **vor** der Umwandlung in eine Ganzzahl prüfen, damit eine
   Typumwandlung keine Nachkommastellen wegrundet. Monatsschlüssel müssen einen
   gültigen Monat 01–12 enthalten. Für andere Reihen gelten deren eigene Regeln; ein Zins darf grundsätzlich
   negativ sein. Fehlende Werte und Quellsymbole nicht in Null umwandeln.
3. **Eindeutigkeit innerhalb jeder Lieferung prüfen.** Schlüssel ist hier
   `period + series + powertrain`. Für andere Datensätze müssen alle fachlichen
   Dimensionen in den Schlüssel. `source` und `vintage` dokumentieren Herkunft,
   sie machen zwei widersprüchliche Werte desselben Monats nicht zu zwei Messungen.
4. **Bestand und Lieferung abgleichen.** Neue Schlüssel separat ausgeben.
   Überlappende Schlüssel auf Wertänderungen und Quellenstatus prüfen: identisch,
   dokumentierte Revision oder ungeklärter Konflikt? Nicht einfach Dateien
   anhängen und „Duplikate entfernen“; dadurch könnte eine Revision verschwinden.
5. **Kalender vollständig prüfen.** Jeden erwarteten Monat je Reihe aufführen
   und gegen die Daten abgleichen. Bekannte Lücken getrennt von neuen Lücken
   ausweisen. Lags beziehen sich auf Kalendermonate, nicht auf die vorherige
   verfügbare Zeile. Neue unvollständige Monate nicht als vollständige übernehmen.
6. **Plausibilität gegen Historie prüfen.** Verlauf ansehen, neuen Monat mit
   Vormonat und gleichem Vorjahresmonat vergleichen, Quartalsenden beachten.
   Bei Nenner Null keine Prozentänderung berechnen. Auffälligkeiten mit Quelle und
   Revisionen prüfen; ein Peak ist kein Beweis für einen Datenfehler. Keine Werte
   glätten, löschen oder verändern, damit eine Kurve besser aussieht.
7. **Geprüften neuen Stand getrennt speichern.** Neue Monate erst nach den
   Prüfungen übernehmen. Revisionen mit Altwert, Neuwert, Beleg und Entscheidung
   protokollieren. Bei ungeklärtem Konflikt bleibt der bisherige Stand erhalten.
   Neue Dateiversion und tatsächliche Prüfergebnisse gemeinsam festhalten.

Minimaler Abschlussvermerk zum Kopieren:

```text
Quelle / Reihe / Einheit:
Originaldatei / URL / Abruf mit Zeitzone / Versionshinweis:
Alter Zeitraum / neuer Zeitraum:
Neue Monate / identische Überlappungen / geänderte historische Werte:
Fehlende Werte / Monatslücken / doppelte Schlüssel / ungültige Werte:
Auffälligkeiten, Erklärung mit Beleg oder ausdrücklich noch offen:
Entscheidung / bearbeitende Person / Datum / Ort des neuen Standes:
```

## 4. Wobei Copilot helfen kann

Nur den im Unternehmen freigegebenen Copilot und zugelassene Dateien verwenden.
Eine Pfadangabe im Chat gibt Copilot noch keinen Zugriff. Excel-Copilot-Funktionen,
Dateiformate und Berechtigungen hängen von Lizenz und Unternehmenskonfiguration ab.
Die folgenden Prompts sind Vorlagen, keine bereits getestete Integration.

**Prüfschritte vorbereiten:**

> Ich prüfe zwei Tabellen „Historie“ und „Lieferung“ mit den Spalten period, value,
> series, source, vintage, powertrain. period ist Text YYYY-MM, value eine
> nichtnegative ganze Anzahl. Erkläre mir schrittweise Power-Query-Abfragen für
> fehlende Pflichtfelder, Typfehler und doppelte Schlüssel innerhalb jeder Tabelle.
> Der fachliche Schlüssel ist period, series, powertrain. Beschreibe die erwarteten
> Ausgabetabellen. Ändere keine Originalwerte. Wenn du die Tabellen nicht lesen oder
> Schritte nicht ausführen kannst, sage es ausdrücklich; erfinde keine Prüfergebnisse.

**Lieferung mit Historie abgleichen:**

> Zeige mir, wie ich in Power Query neue Schlüssel mit einem linken Anti-Join von
> Lieferung gegen Historie und überlappende Schlüssel mit einem inneren Join finde.
> Vergleiche dort value und Herkunft; historische Revisionen sollen sichtbar bleiben.
> Ergänze eine Prüfung auf alle erwarteten Kalendermonate je Reihe. Gib die
> Arbeitsschritte an und erkläre jeden Schritt, damit ich ihn selbst kontrollieren
> kann. Keine automatische Deduplizierung oder Ersetzung von fehlenden Werten.

**Auffälligkeiten einordnen:**

> Nutze ausschließlich diese tatsächlich berechnete Prüftabelle: [freigegebene
> Tabelle auswählen]. Trenne Datenfehler, mögliche Revisionen und fachliche
> Auffälligkeiten. Vergleiche Vormonat, Vorjahresmonat und bekannte Kalendermuster.
> Liefere für offene Punkte konkrete Prüfaufträge. Behaupte keine Ursache aus einer
> zeitlichen Übereinstimmung. Nenne fehlende Informationen statt sie zu ergänzen.

Berechnungen werden in Excel/Power Query ausgeführt und an bekannten Werten
kontrolliert. Copilot erklärt und unterstützt bei den Schritten; eine gut klingende
Antwort ersetzt weder den Datenabgleich noch Quellenbelege. ADF/KPSS, p-Werte und
Modellergebnisse lassen wir nicht aus Freitext schätzen.

## 5. Drei gemeinsame Durchgänge statt einer angenommenen Selbstständigkeit

| Durchgang | Wer arbeitet? | Nachweis am Ende |
|---|---|---|
| 1: Historischen Monatsnachtrag üben | Gemeinsam; Kollegin bedient Excel | [KBA-Übung](examples/kba-update/README.md) ergibt die dort genannten Kontrollwerte; offene Bedienungsfragen notiert |
| 2: Eine echte neue Lieferung prüfen | Kollegin führt, Unterstützung bei Fragen | Quelle/Definition selbst gefunden, Revisionen und Lücken nachvollziehbar ausgewiesen; gleiche Prüfung nach erneutem Aktualisieren reproduzierbar |
| 3: Nächstes Update wiederholen | Kollegin zunächst selbstständig | Anderer Mensch kann ihren Abschlussvermerk und die gespeicherten Abfrageschritte nachvollziehen; verbleibende Hilfe konkret benannt |

Nach jedem Durchgang festhalten: **allein möglich / mit Anleitung möglich /
technische Unterstützung nötig**. R-Kenntnisse sind für diese Datenpflegeübung
nicht erforderlich. Ob darüber hinaus eine vollständige statistische Analyse ohne
Programmierkenntnisse praktikabel ist, ist eine separate Frage.

Bei neuer Datenstruktur, Indexbasis, Einheit oder ungeklärter Revision ist ein
gemeinsamer fachlich-technischer Schritt nötig. Eine Datenprüfung allein gibt
noch kein Modell frei: Stationarität der Ziel- und Residuenreihen, Autokorrelation,
Stabilität, kalendergerechte Lags und Prognosevalidierung bleiben erforderlich.
HypoForge kann dokumentierte Transformationen unterstützen; es ersetzt diese
Beurteilung nicht. VARX ist eine optionale spätere Methodenentscheidung.

## Technischer Anhang für die betreuende Person

Die Kollegin muss diese Python-Kommandos nicht ausführen. Sie zeigen, wie der
vorhandene Projektstand erzeugt wurde und was ein technischer Maintainer prüfen
kann. Voraussetzungen stehen in den verlinkten Fachanleitungen.

| Vorhandener Weg | Was er tatsächlich leistet / Grenze |
|---|---|
| [`python -m kba audit`](KBA_MULTIBASELINE.md#reproduce-and-verify) | Prüft versionierte KBA-Ergebnisse offline gegen Katalog/Plan; keine neuen Monate |
| `python -m kba fetch --raw-dir artifacts/kba-raw`, danach `extract` und `verify` mit demselben `--raw-dir` und separatem `--output` | Stellt katalogisierte Originale wieder her und extrahiert sie mit geprüften Parserprofilen; siehe vollständige [Anleitung](KBA_MULTIBASELINE.md#reproduce-and-verify). Abweichende Original-Hashes werden abgewiesen. |
| [`source_acquisition/normalize.py`](../source_acquisition/normalize.py): `python -m source_acquisition.normalize /PFAD/ZUM/PRIVATEN/ARCHIV` | Benötigt Originale und Erwerbsmanifest mit passenden Hashes; erzeugt vier normalisierte CSVs und aktualisiert den QA-Nachweis außerhalb von Git. Festes Fenster 2018–2025; keine Modellfreigabe. |
| [`empirical/restore.py`](../empirical/restore.py): `python -m empirical restore --source-archive /PFAD/ZUM/PRIVATEN/ARCHIV` | Stellt ausschließlich exakt geprüfte alte Quelldateien wieder her; ist **kein Update-Dienst**. Keine Analyse für diese Übergabe ausführen. |
| `python -m product_events.transform --check` und `python -m campaigns.transform --check` | Prüfen vorhandene Ableitungen gegen die recherchierten Belege; recherchieren keine neuen Ereignisse. |

Die Dieselableitung setzt jeden vorhandenen Montagswert als ausdrücklich markierte
Approximation für Montag bis Sonntag an und gewichtet nach den Tagen im jeweiligen
Monat. Nur vollständig abgedeckte, abgeschlossene Monate erhalten einen Wert;
fehlende Wochen werden nicht verlängert. Im geprüften Stand bleiben 13 Monate leer:
2018-04, 2018-12, 2019-01, 2019-04, 2019-12, 2020-01, 2020-04, 2020-12,
2021-01, 2021-04, 2021-12, 2022-01, 2022-04.

**Echte Erweiterung in 2026:** Neue Originale und Revisionen brauchen einen neuen,
nachvollziehbar geprüften Datenstand. KBA-Katalog/Parser und das feste Makrofenster
sind dafür noch anzupassen; bisherige Hash-/Herkunftsprüfungen nicht abschalten.
Bestehende Forschungsprotokolle, Originalergebnisse und private Freigaben bleiben
unverändert. Eine solche Erweiterung wurde für diese Übergabe nicht implementiert.

**Tatsächlich geprüft:** Repository-Quellenbestand, Abdeckung der vier genannten
KBA-Reihen, unveränderte Herkunft der Übungszeilen und rechnerische Sollwerte der
Übung. Excel-Bedienung, Power-Query-Ausführung und Copilot wurden hier nicht getestet;
genau das soll der erste gemeinsame Durchgang klären.
