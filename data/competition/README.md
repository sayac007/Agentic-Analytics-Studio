# Wettbewerbsdaten und Preis-/Reichweitenbelege

Recherchevintage **29.10.2026**. Beobachtete deutsche Pkw-Zulassungen und
datierte Angebotsbelege, keine synthetischen Ersatzdaten und keine neue Schätzung.

## Zulassungen

72 tatsächlich bezogene KBA-FZ10-Arbeitsmappen: Dezember 2018–2020 sowie alle
69 Monate Januar 2021–September 2026. Die 63 historischen Dateien stimmen mit
den bereits eingefrorenen Quell-Hashes überein; neun 2026-Dateien ergänzen sie.
Quellen, Bytes, SHA-256 und tatsächliche Abrufpräzision: [kba_sources.json](kba_sources.json).
Der erste Abruf der Dezember-2025-Datei wurde nur tagesgenau dokumentiert;
dafür wird kein nachträglicher sekundengenauer Zeitpunkt erfunden.

| Datei | Inhalt |
|---|---|
| `brand_monthly_2021_2026.csv` | Alle separat veröffentlichten Marken, monatliche und YTD-Spalten, alle Antriebe und explizite BEV getrennt; Quellenzellen |
| `brand_annual_2018_2025.csv` | Dezember-YTD als Jahreswert; Marktanteil innerhalb derselben Antriebsdefinition |
| `brand_ytd_comparison.csv` | Januar–September 2026 gegen Januar–September 2025, keine Ganzjahres/YTD-Vermischung |
| `brand_release_observations.csv` | Vollständiger extrahierter Markenbestand aller 72 Releases, einschließlich der drei alten Dezemberpunkte |
| `model_annual_electric.csv` | 3.078 jährliche Modellreihenzeilen, inklusive Null-/unterdrückter Werte und BEV-Teilspalte |
| `model_year_top10.csv` | 80 dynamisch ausgewählte Modellreihen: zehn je Jahr 2018–2025 |
| `kba_checks.json` | Monats-/YTD-Abgleiche, Tabellenköpfe, Symbole, Veröffentlichungspräzision, Rang-Ambiguitätsprüfung |

Im monatlichen 2021–2026-Bestand erscheinen 73 benannte Marken über die Zeit,
zusätzlich `SONSTIGE`. Das bedeutet **alle separat berichteten Marken**, nicht
Identifikation jeder im Sammelposten verborgenen Kleinstmarke. 2025 erscheinen
68 benannte Marken, September 2026 69. Frühere monatliche **Gesamtzulassungen**
2018–2020 bleiben zusätzlich im vorhandenen
[`data/kba/derived/observations.csv`](../kba/derived/observations.csv); dieser neue
BEV-Extrakt behauptet dafür keine vollständige monatliche Antriebsaufteilung.

2018–2020 heißt die elektrische Spalte nur `mit Elektroantrieb`.
Ihre 30 Top-10-Zeilen sind deshalb ausdrücklich
`electric_legacy_unverified_bev`, bis die damalige Definition zusätzlich belegt
ist. Ab 2021 lautet der Kopf ausdrücklich `mit Elektroantrieb (BEV)`.
Auswahl: positive elektrische YTD-Zahl, absteigend, dann Marken-/Modellname als
deterministische Gleichstandsregel. `SONSTIGE` wird nicht als Modell verkauft.
Unterdrückte Modellzahlen werden mit veröffentlichten nichtnegativen
Marken-/Markt-Restmengen begrenzt; alle acht Jahresranglisten bestehen diese
Rangprüfung. Es werden dabei **keine** fehlenden Einzelzahlen ergänzt.

Alle 288 Markenabgleiche: 270 vollständige numerische Summenabgleiche bestanden,
acht wegen unterdrückter/ungeklärter Symbolzellen unvollständig, zehn wegen
nicht veröffentlichter YTD-Gesamtsummen nicht ausführbar. Diese Ausnahmen sind
sichtbar, keine pauschale Behauptung vollständiger Daten. Ein `-` wird nur bei
nachgewiesener Symboldefinition derselben Mappe null; sonst bleibt es fehlend.
`X`, `/`, Leerfelder und nicht separat berichtete Marken werden nicht null.
Einzelmarken ohne Modelluntergliederung, etwa MORGAN, werden mit erfasst.

KGM ist laut KBA ab 01.04.2025 die Umbenennung von SSANGYONG, kein belegter
Markteintritt. CUPRA Born/Tavascan werden im KBA unter SEAT geführt. MG heißt
dort MG ROEWE; dessen Modell `4` ist der MG4. BEV-Teilreihen BMW X1, Mercedes
GLA und Audi A6 dürfen keine Preise ihrer Verbrennervarianten erhalten.
ID.4/ID.5 sind ab 2022 gemeinsam berichtet; Einzelvariantenpreise ergeben ohne
weitere Gewichte keinen Absatzmittelpreis dieser Gruppe. Markenname ist weder
Produktionsland noch Eigentümernationalität.

**Quelle/Weiterverwendung:** Kraftfahrt-Bundesamt, Flensburg, FZ10;
Datenlizenz Deutschland – Namensnennung – Version 2.0,
<https://www.govdata.de/dl-de/by-2-0>. Eigene Extraktion/Berechnung/Darstellung.
Die Originalmappen bleiben außerhalb Git. Beobachtungsraster: Monat;
Revisionen sind durch konkrete Bytes gebunden, keine historischen Echtzeitvintages.

## Preise und Reichweiten

130 Belegzeilen aus **46 direkt abgerufenen Quellen**, darunter 16
Herstellerveröffentlichungen, zwei Hersteller-Preiskarten auf Händlerseiten und
28 datierte Sekundärquellen. 125 Zeilen enthalten einen Preis oder eine explizite
Preisobergrenze; fünf nur eine Reichweite. 64 enthalten eine zur genannten
Variante zugeordnete Reichweite. 30 benannte Modellfamilien einschließlich
ergänzender Tesla- und günstiger Herausforderermodelle. Mehrere Ausstattungen,
Karosserien oder Listen-/Aktionspreise sind **keine unabhängigen Marktbeobachtungen**.

- [price_observations.json](price_observations.json): kuratierte numerische Fakten,
  Datum mit Präzision, Variante, Preisart, Batterie-/MwSt.-Status, Norm,
  Quellen-/Textstellenbezug und Einschränkungen.
- [price_sources.json](price_sources.json): URL, tatsächliche Ziel-URL, Abrufzeit,
  Originalhash und Evidenzart. Zahlen sind veröffentlichte Angebote, keine Käufe.
- [prices_and_ranges.csv](prices_and_ranges.csv): lesbare Ansicht einschließlich
  Quellenlink und konservativ berechenbarer Preis-/Reichweitenrelation.
- [price_coverage_by_model_year.csv](price_coverage_by_model_year.csv): ehrliche
  80-Zeilen-Abdeckungsmatrix zur jährlichen Top-10-Auswahl.

**Historische Abdeckung ist unvollständig:** Nur 23 der 80 ausgewählten
Modell-Jahre haben bislang mindestens einen datierten exakten Preisbeleg;
zehn haben mindestens ein Preis-/Variantenreichweitenpaar. Damit ist weder ein
lückenloses Einstiegs-/Topvariantenpanel noch ein monatlicher Wettbewerbsindex
fertig. 2026-Elroq-Preise bleiben ein getrenntes aktuelles Anhangs-Snapshot.
Ein Modelljahr 2024, das 2023 angekündigt wurde, zählt nicht automatisch als
2024-Preisbeobachtung. Fehlende Jahre bleiben leer; keine Fortschreibung.

`role_in_source_snapshot` bezeichnet die Rolle **im damaligen Quellenumfang**,
nicht die günstigste/teuerste Variante des gesamten Jahres. Maximale Reichweite
und höchster Preis sind verschiedene Größen: Tavascan Endurance 2024
56.210 EUR/549 km, VZ 60.780 EUR/517 km. Januar-2025-Enyaq-Topausstattung schließt
den erst später eingeführten RS nicht ein. S6 wird im Audi-Marketing zusammen
mit A6 e-tron verglichen; daraus folgt keine separat belegte KBA-S6-Zahl.

Erhaltene problematische Belege:

- ZOE 2019 ab 21.900 EUR **ohne Batteriekauf**, Kaufdifferenz 8.090 EUR;
  daraus abgeleitete Gesamtpreise sind als Berechnung gekennzeichnet.
- ZOE 2020/2021 19.990 EUR **nach** Hersteller- und Staatsförderung;
  Fiat 500 2024 hat einen getrennten 5.000-EUR-Hersteller-/Händlerrabatt.
- Tesla-Konfiguratorpreise Januar 2023 enthalten bereits den Herstelleranteil
  am Umweltbonus; Bearbeitungsgebühr zusätzlich. Keine ungeprüfte Gleichsetzung
  mit unsubventionierten Listenpreisen.
- MG4-Preiskarten Januar 2023 enthalten 2.677,50 EUR Herstellerrabatt,
  weitere Staatsförderung nicht abgezogen, 999 EUR Lieferung zusätzlich.
- MG4-Karte mit Aufdruck Januar 2025 wurde laut PDF erst Oktober erstellt;
  ihre Farbpreiszuordnung ist widersprüchlich. Die konkrete weiße Variante
  35.640 EUR bleibt markiert erhalten, **kein** zugelassener Einstiegspreisindex.
- MINI-Veröffentlichung 2019 nennt auf NEFZ zurückgerechnete Reichweite;
  sie wird nicht zu einer WLTP-Zahl umetikettiert.
- VW-Webseiten enthalten aktuelle Werbebanner neben historischen Artikeln.
  Wo nötig wurde das datierte Original-PDF ausgewertet. Ein HTTP-200-Redirect
  alter Škoda-/SEAT-Links auf heutige Presselisten ist kein alter Preisbeleg.

`Preis × 100 / deklarierte Reichweite` ist eine **Anschaffungspreisrelation**,
keine Fahrtkostenkennzahl. Der konservative Export berechnet nur zwölf
brutto- und batterieinklusive Listenpreis-/WLTP-Variantenhüllen. Reichweitenspannen
bleiben Spannen; ein „mehr als“-Wert wird nicht als exakter Nenner benutzt.
Ein Basispreis mit der besten Reichweite einer Ausstattungshülle ist kein
verbindliches Angebot eines exakt konfigurierten Fahrzeugs. Vorläufige
Homologation bleibt markiert. Nicht zulässige Paarungen erhalten einen Grund,
keinen geschätzten Ersatzwert. Keine Absatzgewichtung und kein Marktmittel.

Die Quellenbelege sind retrospektiv recherchiert. Publikationsdatum ist kein
Beweis damaliger maschinenlesbarer Verfügbarkeit. Hersteller-/Pressetexte und
PDFs werden nicht ins öffentliche Repo kopiert; Rohtextrechte wurden nicht
pauschal freigegeben. Hier stehen zitierte numerische Fakten und eigene
Berechnungen. Keine automatische Rohdaten-Weitergabe.

## Destatis und andere Preisstatistik

Direkt geprüft: Destatis Preismonitor „Auto/Verkehr“, eigene Destatis-Suchen
„Elektroautos Preise“, „Elektroautos Reichweite“ und „Elektroautos Preisindex“
sowie die Außenhandelsmitteilung
<https://www.destatis.de/DE/Presse/Pressemitteilungen/2024/05/PD24_N020_46_51.html>.
Die Reichweitensuche lieferte keinen exakten Treffer, sondern unpassende
Ersatztreffer zur industriellen Auftragsreichweite; diese sind kein Datenbeleg.
Im geprüften Angebot wurde **kein belegter Elektroauto-Kaufpreis je 100 km
Reichweite** gefunden. Das beweist nicht, dass jede Destatis-Tabelle geprüft wäre.
Der bisherige Konjunkturindikatorenbereich weist auf Einstellung seit KW43/2026 hin.

Die Mitteilung enthält Stück und Außenhandelswerte, z.B. 446.000 importierte
BEV/14,1 Mrd. EUR 2023. Ein Quotient daraus wäre ein Importstückwert, **kein**
deutscher Endkundenpreis und enthält keine Reichweite. VPI-Preisindizes sind
Preisänderungsmaße, keine EUR-Niveaus je Autovariante.

Eine ergänzende, direkt gelesene Primärveröffentlichung von T&E berichtet
EU-weit für 2025 42.700 EUR Durchschnittspreis, 1.800 EUR bzw. 4 % weniger;
für 2020–2024 berichtet sie zuvor +5.000 EUR. Das ist **nicht Destatis**, nicht
Deutschland, keine Tesla-Elastizität und keine Preis-pro-Reichweite-Reihe.
Ihre politikbezogene Kausalinterpretation wird hier nicht übernommen.
<https://www.transportenvironment.org/te-deutschland/articles/hersteller-bringen-wegen-co2-zielen-billigere-e-autos-auf-den-markt-durchschnittspreis-um-1-800-euro-gesunken>.
Weitere Quellen-/Suchnachweise: [research_sources.json](research_sources.json).

## Reproduktion

Python 3.12, vorhandene `requirements-kba.lock`; keine neue Abhängigkeit.
`openpyxl==3.1.5`. Quellenmappen und Quellseiten in einem privaten Ordner mit den
in beiden Katalogen genannten Dateinamen bereitstellen. Das ist **keine**
Anforderung, private Studien oder Source-Permits zu übertragen.

```sh
python3 -m competition.kba --catalog data/competition/kba_sources.json \
  --raw-dir /path/to/private/source-snapshots --output /tmp/competition-replay
# Kuratierte Preisfakten/Quellkatalog für den Replay bereitstellen:
cp data/competition/price_observations.json data/competition/price_sources.json /tmp/competition-replay/
python3 -m competition.derive --data-dir /tmp/competition-replay
# Optional: Originalhashes beider Kataloge prüfen (118 Dateien, kein Netz):
python3 -m competition.derive --raw-dir /path/to/private/source-snapshots
python3 -m unittest discover -s tests -p test_competition.py -v
```

Ohne Originale kann jeder Reviewer die versionierten Zahlen, Preise, Lücken
und Quellen lesen und `python3 -m competition.derive --output /tmp/views`
offline ausführen. Die Preisfakten sind manuelle Transkriptionen mit Fundstellen;
kein universeller automatischer HTML-Preisparser wird behauptet. Für eine
Wiederbeschaffung sind die Original-URLs angegeben: bei Hashänderung neue Vintage
prüfen, nicht alte Hashes ersetzen. Ergebnisdateien: [sha256.json](sha256.json).
Tatsächlich ausgeführte Prüfungen stehen im fokussierten PR und in
[VERIFICATION.md](VERIFICATION.md).
