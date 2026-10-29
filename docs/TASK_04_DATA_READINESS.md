# Task 04 – Fehlende Daten und Beschaffungsweg

Stand 29.10.2026, **vor der ersten Schätzung**. Bezogen auf
[`REGIME_STATE_SPACE_PROTOCOL.md`](REGIME_STATE_SPACE_PROTOCOL.md),
Version `task-04-regimes/1.0.0`. Keine automatische analytische Zulassung,
keine Änderung früherer Source-Permits. Bestehende Originale zuerst prüfen,
statt Nutzer erneut um bereits vorhandene Dateien zu bitten.

**Priorität:** Stufe 1 ist auf Markt-/Tesla-/VW-Zerlegung, Kalender, Quartalsende
und Förderregime begrenzt. Die Markt-/Markenwerte liegen vor; Förderchronik und
Protokollfreigabe bleiben zu schließen. Benzin, Strom, Bestand, Wettbewerbspreise
und exakte China-Zuordnung sperren nur die benannten optionalen Stufe-2-Module,
nicht den Abschluss des Kerns. Die folgende vollständige Bedarfsliste ist keine
Aufforderung, all diese Daten vor Stufe 1 zu beschaffen.

## Was bereits belastbar vorliegt

- 69 offizielle BEV-/Pkw-Gesamtwerte und Tesla-/VW-Monatswerte 2021–2026-09.
  Die Marktsummen im Anhang wurden gegen die Gesamtzeilen korrigiert; der
  auditierte Rest wird nicht aus einer unvollständigen Einzelmarkensumme berechnet.
- Vorhandener empirischer Pilot: VPI, Konsumentenkredite, EUR/USD und Diesel
  normalisiert für 2018–2025. Ältere Recherchestatusdateien mit „nicht beschafft“
  sind nicht der aktuelle Pilotstatus. Der Normalisierungszeitraum beweist
  aber keine freigegebenen 2026-Monatswerte; native Originale separat prüfen.
- Das aktuelle Deutschland-Merkblatt des Weekly Oil Bulletin ist tatsächlich
  abgerufen. Es beschreibt Montags-Verbraucherpreise, arithmetisches Mittel,
  Marktdeckung über 70 % je Produkt und Benzin mit **bis zu 5 % Ethanol (E5)**.
  Das verlinkte Dokument heißt `2018_germany_notes.pdf`: Definition nicht als
  unabhängig geprüfte, unveränderte Produktgeschichte bis 2026 ausgeben.
- Neue Förderung 2026 samt offizieller Förderrichtlinie und FAQ verifiziert.
  Tesla-Q1-2025-Bericht im Original abgerufen: Modellwechsel aller vier
  Model-Y-Werke und mehrere Wochen Produktionsverlust beschrieben. Das ist
  keine taggenaue deutsche Werksstillstandsreihe.

Quellen-/Abruf-/Hashnachweise: [`primary_sources.json`](../data/task04_regimes/primary_sources.json).
KBA-Prüfungen: [`data_audit.json`](../data/task04_regimes/data_audit.json).

## Datenbedarf nach Modellbaustein

| Daten/Entscheidung | Konkreter Beschaffungs- oder Prüfweg | Sperrt aktuell |
|---|---|---|
| C17-Zuordnung und „Sonstige“ | KBA-Originale plus dokumentierte Reporting-/Markenhistorie; nicht separat berichtete Marken nicht null. Unter-/Obergrenzen liegen bereits vor. Herkunfts-/Eigentümerdefinition für Polestar, AIWAYS, Volvo, Smart, Lotus mit Hersteller-/Unternehmensquellen festlegen. | Exaktes Viergruppen-Punktmodell und Aussagen über den vollständigen Korb; G3 Tesla/VW/Rest bleibt möglich. |
| Euro-super-95 Deutschland, November 2020–September 2026 | Zuerst vorhandene Originalmappe prüfen: Blatt „Prices with taxes“, Deutschland-Länderkennung, Produktkopf, Datum, Einheiten, Fußnoten. Frühere Prüfung nennt BC als benachbarte Super95-Spalte; das ist ein Prüfansatz, keine automatische Zulassung. Sonst [offizieller Weekly Oil Bulletin](https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en), historische XLSX. | Primäre Benzinvergleiche M3a/b/c. |
| Benzin-Monatsableitung | EUR/1.000 Liter nur mit belegter Währungs-/Produkteinheit nach EUR/L umrechnen. Montagswert auf dessen sieben Kalendertage verteilen; Kalenderüberlappung in den Monat gewichten. Vollständige Monatsdeckung sonst null. Keine Überbrückung ausgelassener Wochen und keine Behauptung eines offiziellen Monatsmittels. Rechte/Anwendungsumfang neu für dieses Produkt prüfen; Dieselentscheidung nicht automatisch erweitern. | Verwendbare Preisreihe und Vergleich mit Diesel. |
| VPI/Kreditzins 2026 | Native bereits vorhandene Destatis-/ECB-Dateien zuerst auf ihre tatsächlichen letzten Monate prüfen. Sonst dieselbe offizielle Reihe mit neuer Vintage beschaffen. Gleiche Einheit, Saisonbereinigung und Zinsdefinition; Rückrevisionen erhalten. | Reale Benzinpreise bis September 2026; gegebenenfalls Makro-Sensitivität. |
| Strom/Ladestrom | Destatis/BDEW prüfen; zusätzlich offizielle Eurostat-Kandidatenquelle [nrg_pc_204](https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table?lang=en). Die Landingpage wurde erreicht, Daten/Filter noch nicht gelesen. Deutschland, Haushalt/Verbrauchsband, Steuern und EUR/kWh festlegen. Halbjahreswerte bleiben Periodenproxies; öffentliche Tarife separat. | Betriebskostenverhältnis, nicht die reine Benzinpreisvariante. |
| Verbrauch/Lademix | Vorab offengelegte Szenarien für L/100km, kWh/100km und Heim-/Öffentlich-Anteil; vorzugsweise dokumentierte Fahrzeug-/Nutzungsdaten. Keine aus Tesla-Absatz geschätzten Verbrauchswerte. | Interpretation als vergleichbare Betriebskosten, statt bloß Preisproxy. |
| Vollständige Förderchronik | BAFA/Bundeswirtschaftsministerium/BGBl: Kürzung Januar 2023, Ende gewerblicher Berechtigung September 2023, angekündigte Folgeregeln und Ende Dezember2023 jeweils mit Bekanntgabe-/Geltungsdatum und Zielgruppe. Aktuelle BAFA-Programmseite bestätigt Ende zum 18.12.2023; die übrigen historischen Details sind hier noch nicht primär vollständig belegt. | Als vollständig freigegebene Modellmatrix M2/M3; Ereignisse nicht aus Gedächtnis auffüllen. |
| Private/gewerbliche BEV-Zulassungen | Öffentliche KBA-Haltergruppen-/Antriebsstatistik auf monatliche Kreuztabellen prüfen. Nicht behaupten, dass eine Marke×BEV×Halter-Kreuztabelle bereits verfügbar sei. Einkommens-/Kinderberechtigung folgt daraus ohnehin nicht. | Individuelle Förderinterpretation; Gesamtmarkt-Regimezusammenhang bleibt deskriptiv. |
| Historische Kfz-Steuerregel | [KraftStG §3d](https://www.gesetze-im-internet.de/kraftstg/__3d.html) aktuell gelesen; Änderungen und damalige Bekanntgabe über BGBl rekonstruieren. Aktueller Text ist kein historischer Echtzeitstand. | Zeitlich belegter zusätzlicher Steuer-Interventionsterm. Konstante Begünstigung ist mit Interzept kollinear. |
| Juniper und Markenereignisse | Bestehendes Produktledger: deutscher Bestellstart 24.01.2025 sekundär belegt. Tesla-IR-Q1-Original bestätigt Produktionswechsel; genaue deutsche Produktion/Auslieferung und damalige Bekanntgabe fehlen. Politische Kontroverse mit datierten Originalen/seriösen Berichten, Reichweite und Deutschlandbezug erfassen. | Trennung Modellwechsel/Markenkontroverse; keine einzelne Ursache aus latentem Niveau ableiten. |
| Monatliche relative Neuwagenpreise | Bestehende 130 Belegzeilen/23 von 80 Modelljahren zuerst nutzen; für direkte Tesla-Substitute gleiche Variante, Batterie, MwSt., Preisart und Geltung schließen. Keine Interpolation aus seltenen Pressepreisen. Vorjahres-/vorab definierter Korb, keine Gewichtung mit zukünftigen Jahresabsätzen. | G2-Preisvergleich und quantitative Preiswettbewerbshypothese. |
| BEV-Bestand und Veröffentlichung | KBA-Bestand zum 1.1., Pkw und reine BEV exakt trennen. FZ27/FZ13-Angebot auf passende Definition prüfen; konkreten Tabellen-/Quellstand erst danach festschreiben. Anfangsbestand vor 2021 und jeweilige Veröffentlichung nötig. | Bestands-/Diffusionsvergleich D. Kumulierte Bruttozulassungen ersetzen den Bestand nicht. |
| Historische Datenverfügbarkeit | KBA-/Preis-/Förderpublikationsdaten und echte damalige Revisionen, soweit verfügbar. AGPI-Methodenbruch März 2025/Vintages getrennt halten; Portal-Gebrauchtpreise sind kein Ersatz für Neuwagenpreise. | Historischer Echtzeitanspruch; retrospektive Backtests bleiben klar benannt möglich. |

## Primär verifizierte Förderung 2026

- **Bekanntgabe 19.01.2026**, förderfähige Erstzulassungen **ab 01.01.2026**;
  Förderrichtlinie/Antragsstart **19.05.2026**. Drei unterschiedliche Datumsrollen.
- Privatpersonen, Kauf oder Leasing eines erstmals im Inland zugelassenen
  M1-Neufahrzeugs; BEV-Basis **3.000 EUR**, je Einkommen/Kinder bis **6.000 EUR**.
  Nicht jede BEV-Zulassung erhält denselben Zuschuss.
- Zu versteuerndes Haushaltseinkommen grundsätzlich höchstens **80.000 EUR**,
  Erhöhung um 5.000 EUR pro berücksichtigtem Kind, höchstens **90.000 EUR**.
  Aufschläge für Haushalte bis 60.000 bzw. 45.000 EUR und für bis zu zwei Kinder.
  Maßgebliche Einkommensnachweise sind nicht einfach das aktuelle Bruttogehalt.
- PHEV/Range-Extender besitzen andere Beträge/Kriterien. Ihre Basis 1.500 EUR
  wird nicht auf die reine BEV-Zielgröße angewendet.
- Primär wird nach Freigabe eine 2026-Regimestufe modelliert; Bekanntgabe und
  Portalöffnung sind Wissensdaten. Kein gleichzeitiges freies Schätzen dreier
  nahezu gleicher Förder-Dummies in neun 2026-Monaten. Eine Portalöffnungs-
  Sensitivität ersetzt die Hauptkodierung, statt sie ergebnisabhängig zu ergänzen.
- Government-Kommentare zum Erfolg des Programms sind keine hier übernommenen
  kausalen Wirksamkeitsnachweise. Ohne Berechtigtenmix ist der Koeffizient ein
  aggregierter Regimezusammenhang.

## Reihenfolge vor der späteren Umsetzung

1. Entwurf fachlich prüfen und Variablen/Priors/Gruppen festlegen.
2. Datenlücken und Ereignis-/Wissensdaten schließen, Provenienz/Anwendungsumfang
   prüfen; aktive/gesperrte Module **vor** dem Fit festschreiben.
3. Version samt Hash einfrieren. Nur danach Schätzcode mit gepinnten Paketen,
   isolierten privaten Ausgaben und passenden numerischen Prüfungen implementieren.
4. Modelle exakt auf den freigegebenen gemeinsamen Datenfenstern ausführen.
   Wenn H-D/H-C oder die Trennung von 2025-Ereignissen nicht identifizierbar ist,
   wird das als Ergebnis berichtet, nicht mit zusätzlichen Variablen kaschiert.

Dieser Schritt fordert noch keine neuen Dateien vom Nutzer an. Vorhandene
Originale und frei zugängliche Primärquellen haben Vorrang; falls danach eine
konkrete Datei fehlt, wird genau diese mit Quelle, Format und Zeitraum benannt.

## Abschluss Stufe-1-Datengate (29.10.2026)

Alle vier vorgesehenen Förderregime sind in policy_chronology.json mit Primärquellen
belegt; frühere Hinweise auf eine unvollständige Chronik dokumentieren den
Entwurfsstand, nicht eine weiterhin fehlende Stufe-1-Quelle. Bekanntgabetage alter
Regeln bleiben teilweise unbekannt; kein historischer Echtzeitanspruch.
Die kleine getrennte Wiederfindung ist abgeschlossen und in Abschnitt 9 des
Protokolls vollständig dokumentiert. SD 0.03 ist eine schwach begründete, vorab
regelgebundene Arbeitswahl; alle Varianten bleiben unsicher gegenüber bekanntem
Policy-Delta. Das Stufe-1-Datengate ist für die beauftragte retrospektive Analyse
geschlossen, Zusatzmodule bleiben gesperrt. Das Einfrieren autorisiert keine
neuen Quellen und keine Änderung früherer privater Zulassungsentscheidungen.
