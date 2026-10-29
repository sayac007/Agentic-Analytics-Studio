# Preis, Käufergruppen und BEV-Nachfrage: recherchierte Evidenz

Recherche vom **29.10.2026**, nach dem gemergten PR 40. Die Preis-/Kostenfrage
ist wissenschaftlich gut begründet. Ein Wechsel Deutschlands von Marken- zu
Preismotiven ist damit noch nicht nachgewiesen: Käuferzusammensetzung,
individuelle Präferenzen und verbesserte Produkte sind verschiedene Mechanismen.

## Portalstatistiken: drei unterschiedliche Arten von Beobachtungen

| Quelle | Tatsächlich belegter Befund | Messung und Zeitraum |
|---|---|---|
| [mobile.de / m.Q](https://newsroom.mobile.de/chinesische-e-autos-vor-allem-der-preis-ueberzeugt/) | 55,4 % nennen Anschaffungskosten als Hauptgrund gegen ein E-Auto; 29,8 % stehen in der Antwortkategorie eines notwendigen Preisvorteils von20 % für ein chinesisches Modell | Umfrage Juli2026, Gesamt-n=2.008 laut Report; Veröffentlichung15.10.2026. Hypothetische Bereitschaft, keine realisierten Käufe |
| [DAT Barometer Juni2025](https://www.dat.de/barometer/dat-barometer-juni-2025/) | 66 % vermissen bezahlbare neue BEV; 60 % sehen ohne Laden zuhause keine BEV-Option; 57 % priorisieren günstige/einheitliche Ladestrompreise gegenüber einer Kaufpreisförderung | 1.081 private Kaufplaner, GfK-CAWI28.04.–06.05.2025; laut DAT gewichtet nach KBA-Bestand/Marke/Motorart |
| [AutoScout24 März2026](https://www.autoscout24.de/unternehmen/agpi/spritpreise-treiben-nachfrage-nach-gebrauchten-e-autos-deutlich-an/) | +38,91 % BEV-Kaufanfragen gegenüber Februar, im Artikel auf39 % gerundet und dem Kraftstoffpreisschock zugeordnet | Plattformanfragen, keine abgeschlossenen Verkäufe oder isolierte kausale Benzinpreiswirkung |
| [AutoScout24 September2026](https://www.autoscout24.de/unternehmen/agpi/agpi-september-nachfrage-nach-gebrauchten-e-autos-steigt-deutlich-an/) | Beigefügte Tabelle nennt39.006 EUR mittleren BEV-Angebotspreis | Gebrauchtwagen-Inserate; kein Neuwagenpreis und kein qualitätsbereinigter Preisindex |

Die DAT-Fragen zeigen, dass Anschaffung, laufende Kosten und Lademöglichkeit
gemeinsam betrachtet werden müssen. Sie beweisen nicht, dass Förderung
wirkungslos wäre. Unterschiedliche Untergruppen/Mehrfachnennungen sind keine
gemeinsame Nachfragewahrscheinlichkeit. AutoScout 24 berichtet zusätzlich eine
Umfrage mit 800 deutschen Befragten aus **Februar 2026**; diese ist nicht dieselbe
Erhebung wie die März-Anfragen und kein nachträgliches Experiment zum Preisschock.

Der [vollständige öffentliche m.Q-Report](https://promo.mobile.de/b2b/wp-content/uploads/m.Q-Der-Datenreport-von-mobile.de-Oktober-2026.pdf)
wurde einschließlich der Quellen auf PDF-Seiten 25–27 gelesen. Seine
Herstellergruppen sind ausgewählt: „Europa“ Audi, BMW, Ford, Mercedes-Benz,
Opel, VW; „China“ BYD, Geely, Leapmotor, MG, Smart, Xpeng. Tesla gehört nicht
zu der dort genannten europäischen Vergleichsgruppe. Diese Definition ist keine
universelle Nationalitätsklassifikation. Ein Preisabstand ohne gleiche Alters-,
Segment-, Ausstattungs- und Laufleistungsmischung beweist kein gleichwertiges
günstigeres Auto. Der Vergleich unterschiedlich alter Gebrauchtwagen mit aktuellen
Neuwagen ist keine beobachtete Preisbahn desselben Fahrzeugs über drei Jahre.

## Wichtiger Datenfund: AGPI-Methodenbruch im März 2025

Die Originalgrafiken nennen eine **Änderung der Berechnungsmethode zum März 2025**
wegen der Harmonisierung innerhalb der AutoScout 24-Gruppe.

| Beobachteter Monat | Veröffentlichungsstand | Mittlerer BEV-Angebotspreis |
|---|---|---:|
| Januar2025 | [Januar-Grafik, veröffentlicht30.01.2025](https://cms-assets.autoscout24.com/uaddx06iwzdz/70qTm6iFqrQqpqRBQ827qn/a5e18f32d7e1c648d1afa50bfd64ee23/Grafik_AGPI_Januar_2025.pdf) | 29.630 EUR |
| Januar2025 | [Rückgerechnete April-Grafik, veröffentlicht29.04.2025](https://cms-assets.autoscout24.com/uaddx06iwzdz/3B9gjl9JiZTzutJsltjr4a/fbf104d2d37869336508e2da2b9a6622/Grafik_AGPI_April_2025.pdf) | 34.910 EUR |

Differenz: **5.280 EUR bzw.17,82 %**, mit Python/Decimal aus den Quellen berechnet.
Es sind verschiedene Veröffentlichungsstände **desselben Monats**, keine
beobachtete Verteuerung zwischen zwei Monaten. Die Quellen zerlegen die Differenz
nicht vollständig in Methoden- und sonstige Revisionseffekte.

Die alte Beschreibung nennt rund 1 Mio. Inserate, höchstens 18 Wochen
Inseratsalter, Preis höchstens 250.000 EUR und unbegrenztes Fahrzeugalter.
Die neue nennt rund 700.000 Fahrzeuge, denselben Preisdeckel und unbegrenztes
Fahrzeugalter; die 18-Wochen-Regel wird dort nicht mehr genannt. Auch innerhalb
der späteren Methode unterscheiden sich einzelne historische Werte zwischen
Releases. Ein Datumsschnitt allein ersetzt daher keine Vintage-Verwaltung.

Ein Kalman-Modell könnte den Messbruch als Nachfragezustand oder driftende
Preisempfindlichkeit aufnehmen. Ein pauschaler Bruch-Dummy garantiert keine
Reparatur: Zusammensetzung und Berechnung können mehr als das Niveau ändern.
Benötigt werden vergleichbare Vintages oder ein stabiler Methodenzeitraum.

Privat wurden **54 Quellbeobachtungen zu 31 verschiedenen Monaten Januar 2024
bis September 2026** erfasst: aktuelle Monatstabellen und zwei getrennte
historische Chart-Vintages. Kein fertiges 31-Zeilen-Panel. Oktober/Dezember 2025
fehlen in dieser Auswahl; keine Interpolation. Die Anfragenkennzahl einer
unvollständigen Mai 2024-Tabelle bleibt leer. Das öffentliche Archiv reicht weiter
zurück; eine vollständige 2018–2026-Portalreihe wird hier nicht behauptet.

## Wissenschaft: Unterstützung und Gegenbefunde

**Forsythe, Gillingham, Michalek & Whitefoot (2023), PNAS:**
[Technology advancement is driving electric vehicle adoption](https://doi.org/10.1073/pnas.2219396120).
[Volltext](https://pmc.ncbi.nlm.nih.gov/articles/PMC10265978/) direkt über Europe-PMC gelesen.
Gewichtete US-Neuwagenkäufer-Discrete-Choice-Erhebungen 2012/13 und 2020/21;
spätere Stichprobe 734 Pkw- und 862 SUV-Antworten. Verbesserte Reichweite und
geringere BEV-Preisaufschläge erklären mehr als veränderte Präferenzen; im
Hauptvergleich keine statistisch signifikanten Präferenzänderungen. Das ist
kein Beweis identischer Präferenzen und kein Deutschlandbefund. Es spricht
dafür, Produktfortschritt zu kontrollieren, bevor Koeffizientendrift als Wandel
der Käufer interpretiert wird. Hypothetische Wahlaufgaben sind keine Käufe;
2030-Szenarien keine beobachteten Marktanteile.

**Jenn, Lee, Hardman & Tal (2020), Transportation Research A:**
[An in-depth examination of electric vehicle incentives: Consumer heterogeneity and changing response over time](https://doi.org/10.1016/j.tra.2019.11.004).
[Artikelabstract über RePEc](https://ideas.repec.org/a/eee/transa/v132y2020icp97-109.html)
gelesen, nicht der paywallgeschützte Volltext. Über 14.000 kalifornische
EV-Käufer 2010–2017; Förderanreize gewinnen laut Studie mit der Marktentwicklung
an Bedeutung. Unterstützung für wechselnde aggregierte Reaktionen, keine
deutsche Elastizität. Rückblickend selbstberichtete Reaktionen auf hypothetisch
fehlende Förderung sind kein Preisexperiment. Dies widerspricht PNAS nicht
zwingend: Zusammensetzung/Förderrelevanz und individuelle Präferenzen sind
unterschiedliche Größen.

**Zarazua de Rubens (2019), Energy:**
[Who will buy electric vehicles after early adopters?](https://doi.org/10.1016/j.energy.2019.01.114).
[Akzeptiertes Manuskript](https://pure.au.dk/ws/files/144290932/Who_will_buy_electric_vehicles_after_early_adopters_Using_machine_learning_to_identify_the_electric_vehicle_mainstream_market.pdf)
im Volltext konsultiert.5.067 Befragte in fünf nordischen Ländern, sechs
k-means-Cluster. Preis zentral für potenzielle Mainstream-Gruppen; Technik und
Status bleiben wichtig. Querschnittssegmente/Kaufinteresse, kein beobachteter
deutscher Phasenwechsel. Historische nominale Preisgrenzen sind keine heutigen
deutschen Schwellenwerte.

**Hackbarth & Madlener (2016), Transportation Research A:**
[Willingness-to-pay for alternative fuel vehicle characteristics: A stated choice study for Germany](https://doi.org/10.1016/j.tra.2015.12.005).
[Abstract](https://ideas.repec.org/a/eee/transa/v85y2016icp89-111.html) und bibliografische
Metadaten geprüft.711 potenzielle deutsche Käufer, sechs latente Klassen;
Zahlungsbereitschaften und Mindestanforderungen unterscheiden sich. Deshalb
Preis und Reichweite separat führen: EUR/100 km Reichweite bildet weder
Mindestreichweite noch Ladezugang ab. Keine hier gelesenen Volltext-Koeffizienten.

**Wolff & Madlener (2019), FCN Working Paper 3/2019:**
[Charged up? Preferences for Electric Vehicle Charging and Implications for Charging Infrastructure Planning](https://www.fcn.eonerc.rwth-aachen.de/global/show_document.asp?id=aaaaaaaaaijinij).
Volltext konsultiert.4.101 deutsche Befragte, hypothetische Ladeangebote,
Conditional Logit mit Teilnehmer-Fixed-Effects. Ladeort, Zeit und Warten werden
gemeinsam mit Kosten bewertet. Kein Neuzulassungs-Preiseffekt. Der anfängliche
Suchtreffer war einem anderen Titel zugeordnet; dieser PDF-Inhalt wurde nicht
als Hackbarth 2016 ausgegeben.

**Trommer, Jarass & Kolarova (2015):**
[Early adopters of electric vehicles in Germany unveiled](https://doi.org/10.3390/wevj7040722).
Volltext konsultiert.3.111 Halterantworten aus Dezember 2013–Februar 2014, mehr
als 9.200 Halter kontaktiert; BEV/PHEV/leichte EV getrennte Gruppen.
Heterogenität tatsächlicher früher Nutzer; Antwortselektion und historische
Population verhindern Übertragung als heutiger Käufermix.

**Wesche, Plötz & Dütschke (2016), Fraunhofer Working Paper:**
[How to trigger mass market adoption of electric vehicles?](https://www.isi.fraunhofer.de/content/dam/isi/dokumente/sustainability-innovation/2016/WP07-2016_How-to-trigger-mass-market-adoption-of-electric-vehicles.pdf).
Volltext konsultiert. DatenApril 2013,1.017 Erwachsene. Technikaffinität und
wahrgenommene Alltagstauglichkeit hängen mit Interesse zusammen. Nur 14 Personen
in der frühen Nutzergruppe; Interesse ersetzt keinen Kauf. Manuelle schrittweise
Variablenauswahl und explorative Cluster begrenzen die Inferenz zusätzlich.
Keine Übernahme der Koeffizienten oder Gruppenanteile als heutige Priors.

**Springel (2021), AEJ: Economic Policy:**
[Network Externality and Subsidy Structure in Two-Sided Markets](https://www.aeaweb.org/articles?id=10.1257/pol.20190131).
Verlagsabstract gelesen. Norwegische Register-/Infrastrukturdaten 2010–2015,
zweiseitiger Marktansatz: Preisförderung und Ladeinfrastruktur wirken gemeinsam.
Volltext/strukturelle Identifikation hier nicht repliziert; der vermeintliche
PDF-Endpunkt lieferte HTML. Keine ausländische Elastizität als deutscher Befund.

Maschinenlesbare Lesestände, Stichproben und Einschränkungen:
[`literature.json`](../data/ev_demand_research/literature.json).

## Konsequenz für die nächste Analyse

1. **Technologie vor Präferenzdrift prüfen:** Preis, Reichweite, Ladefähigkeit,
   Segment, Modell-/Faceliftverfügbarkeit und Förderregeln zusammen erfassen.
   Ein günstiger Neueintritt ist etwas anderes als die Preissenkung desselben Autos.
2. **Preis und Betriebskosten verbinden:** Relative Tesla-Preise und Fahrkosten
   mit wenigen begründeten Interaktionen prüfen. Heimladen/Finanzierung begrenzen
   den Zugang. Der vorhandene Dieselpreis ist kein Benzinpreis. Portal-Anfragen
   sind ein Interessenssignal, keine realisierten Tesla-Käufe.
3. **Markt und Substitution trennen:** BEV-Gesamtmarkt, Tesla-Anteil darin und
   Modellsegmente betrachten. Gleichzeitige Konkurrenzzulassungen sind keine
   exogenen Wettbewerbsschocks.
4. **Feste gegen variable Koeffizienten vergleichen:** Erst mit geklärter
   Messdefinition und genügend gemeinsamer Historie denselben sparsamen Ansatz
   mit konstanten bzw. ein bis zwei variablen Koeffizienten vergleichen.
   Kalman bleibt ein Kandidat; diese Arbeiten validieren kein Tesla-Deutschland-
   State-Space-Modell. Stationaritäts-/Residualdiagnostik und Preisendogenität
   bleiben relevant. Ein Messbruch darf kein latenter Nachfragezustand werden.
5. **Veröffentlichungsstände beachten:** Rückgerechnete Werte dürfen vor ihrem
   Publikationsdatum nicht in Prognosetests einfließen. Die kurze, mehrvintagige
   private Sammlung rechtfertigt noch kein umfangreiches dynamisches Modell.

Neue Ergebnisse: belegter Preis-/Ladezugangsmechanismus, wissenschaftliche
Evidenz für und gegen eine reine Präferenzwandel-Erklärung und ein nachgewiesener
Messbruch. Keine neue Modellschätzung oder Optimierung auf Signifikanz.
