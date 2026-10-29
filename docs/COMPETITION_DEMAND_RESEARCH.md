# Interaktionen und zeitlich veränderliche Tesla-Nachfrage

Die [anschließende Literatur-/Portalrecherche](EV_DEMAND_LITERATURE_AND_PORTALS.md)
liefert passende Käuferbefragungen und einen Gegenbefund zu einer reinen
Präferenzwandel-Erklärung. Zudem wurde ein AGPI-Methodenbruch im März2025 mit
unterschiedlichen Werten desselben Monats nachgewiesen. Produktverbesserungen
und Messvintages müssen vor der Interpretation variabler Koeffizienten geprüft
werden; keine zusätzliche Modellschätzung wurde damit freigegeben.

Nutzerhypothese vom 29.10.2026: Mit wachsender Marktreife könnte Nachfrage
weniger innovations-/markengetrieben und stärker preisgetrieben werden;
günstigere BEV-Angebote, Kraftstoffpreise und neue Wettbewerber könnten
zusammenwirken. **Hypothese, kein bereits identifizierter Effekt.**
Dieser Auftrag sammelt Daten und definiert den nächsten Vergleich. Keine neue
Schätzung, kein automatisches Tuning, keine Änderung eingefrorener Protokolle.

## Zuerst Markt und Markenwahl trennen

1. Entwicklung des gesamten deutschen BEV-Marktes gegenüber Pkw insgesamt.
2. Teslas Zulassungsentwicklung und Anteil innerhalb des BEV-Marktes.
3. Zusammensetzung nach Modell, Preisklasse und verfügbarem Angebot.

Günstige Kleinwagen sind nicht dieselben Substitute für Model Y wie elektrische
SUV. Herkunft eines Markeneigentümers ersetzt weder Segmentzugehörigkeit noch
Produktionsland. Neue KBA-Marken können zudem Umbenennungen oder erstmalige
separate Ausweisung sein; eine erste Zeile beweist keinen Launch.

Die direkt erhobenen KBA-Punkte widersprechen einer pauschalen aktuellen
Verdrängungserzählung: Januar–September 2025/2026 Tesla 14.845/44.810 (+201,85 %),
BEV-Markt 382.202/604.144 (+58,07 %), Tesla-Anteil 3,8841/7,4171 %.
Gleichzeitig wachsen BYD-BEV 7.146/16.355 (+128,87 %), Leapmotor-BEV
3.826/15.128 (+295,40 %). Es können mehrere Anbieter in einem wachsenden Markt
wachsen. Das widerlegt einzelne Substitutionseffekte nicht und beweist keine
Ursache für Teslas Wachstum.

## Benötigte beobachtete Größen

- Vergleichbare deutsche Fahrzeugpreise: gleiche Preisart, Batterie enthalten,
  Steuern/Förderung/Lieferung getrennt, Segment und Variante, datierter Geltungsstand.
  Preisabstand zu einem vorab definierten Wettbewerberkorb, optional real
  deflationiert; Reichweite zusätzlich statt ausschließlich Preis/Reichweite.
- Tatsächliche regionale Kraftstoffreihe und Haushalts-/Ladestrompreis, falls
  verfügbar. Bisher beschaffter Diesel ist **kein Benzinpreis**. Ein kontinuierlicher
  Anstieg wird nicht angenommen. Strom-/Kraftstoffvergleich erfordert konsistente
  Einheiten, Verbrauch und Lade-Mix; Kaufpreisrelation ist keine Betriebskostenreihe.
- Datiertes verfügbares Modellangebot/Launches, Lieferfähigkeit, Modellwechsel,
  dokumentierte Förder-/Steuerregeln, Kredit-/Finanzierungskosten und Einkommen/
  Inflation soweit bereits rechtmäßig zugänglich und qualitätsgeprüft.
- Kalender, Saison, Quartalsende und dokumentierte Liefer-/Produktionsstörungen
  bleiben Muss-Kontrollen. Preis und Launch können Reaktionen auf schwache
  Nachfrage sein. Registrierungen messen Zulassungen und Lieferungen, keine
  isolierten Kaufentscheidungen.

Die neue Preisrecherche deckt bisher nur 23/80 jährliche Top-10-Modelljahre mit
einem exakten Preis ab. Daraus wird **noch kein vollständiger Monatsindex**.
Keine Interpolation oder mehrjährige Fortschreibung ohne belegte Gültigkeit.
Jahres-Top-10 eignen sich für die Beschreibung. Eine damit im selben Jahr
gewichtete Prognose würde zukünftige Absätze verwenden: Für Prognosen Korb/
Gewichte aus vor dem Prognosezeitpunkt verfügbaren Daten einfrieren und neue
Modelle erst ab belegter Verfügbarkeit aufnehmen. Die retrospektiv gefundenen
Quellen sind keine historisch verifizierten Echtzeitvintages.

## Sparsamer Modellvergleich nach Datenprüfung

**A – feste Beziehungen:** Bestehende dynamische Kalenderbaseline ergänzen um
wenige vorab festgelegte Preis-/Betriebskostenvariablen und kurze sachlich
begründete Lags. Zuerst Stationarität der Ziel- und erklärenden Reihen prüfen;
Log-/Differenzdarstellung bzw. Fehlerkorrektur nur mit passenden Diagnosen.
Residualstationarität und verbleibende Autokorrelation prüfen. Kalenderkontrollen
allein machen eine trendende Preisregression nicht sicher.

**B – Interaktionen:** Kleine, fachlich begründete Auswahl, etwa relativer
BEV-Anschaffungspreis × relative Betriebskosten und relativer Tesla-Preis ×
belegtes substitutives Modellangebot. Haupteffekte bleiben enthalten; Skalierung,
Zeitpunkt und Lags werden vor Ergebnisbetrachtung festgelegt. Nicht gleichzeitig
alle Preise, Trends, Markteintritte und deren Kreuzprodukte in eine kurze Reihe
werfen. Zeittrend/BEV-Anteil sind nur unvollständige Reife-Proxys.

**C – State Space:** Dieselben beobachteten Größen mit lokalem Niveau/Trend und
höchstens ein bis zwei zeitvariierenden Koeffizienten vergleichen, zuerst die
relative Preisempfindlichkeit. Beispielhafte Struktur:

```text
g(y_t) = Kalender_t + lokales_Niveau_t + beta_P,t * relativer_Preis_t
         + beta_C * relative_Betriebskosten_t + dokumentierte_Kontrollen_t + e_t
beta_P,t = beta_P,t-1 + u_t
```

Kalman-Filter schätzt rekursiv den Zustand; ein Kalman-Smoother nutzt spätere
Beobachtungen und darf nicht als damalige Prognoseleistung ausgegeben werden.
Prozessvarianz null entspricht einem konstanten Preiseffekt und ist ein
ernsthafter Vergleichsfall. Ein lokales Niveau plus driftender Koeffizient und
trendender Preis kann schwach identifiziert sein: Unsicherheit, Kollinearität,
Sensitivität und Abhängigkeit von Restriktionen berichten. Keine erzwungenen
negativen Preiseffekte oder vorgegebenen Phasenübergänge. Der latente Zustand
ist kein direkt gemessener Early-Adopter-Anteil und kann auch Angebotsstörungen
aufnehmen. Ein komplexeres Modell ist kein Beleg für „breite Masse“.

Vergleich auf identischen zulässigen Monaten und vorab festgelegten rollierenden
Prognosefenstern; naive/dynamische Baseline, Fehler und Intervalle, Residuen,
Parameterstabilität und praktische Größenordnungen berichten. Zeitgleich
realisierter Konkurrenzabsatz und `1 − Tesla-BEV-Anteil` sind gemeinsame Outcomes
bzw. algebraisch an Tesla gebunden, keine exogenen Wettbewerbstreiber. Für eine
Prognose stehen zukünftige Preise/Angebote nur als explizite Szenarien zur Verfügung.

HypoForge bleibt für nachgewiesen passende Lag-/Transformationsfunktionen am
bereits auditierten Commit nutzbar; keine willkürliche Media-Hill-Transformation
von Autopreisen. VARX/VECM sind spätere Optionen bei ausreichender Länge,
Integrations-/Kointegrationsdiagnostik und passender Frage, kein Standardzwang.

## Was danach behauptet werden darf

Vorzeichen und Interaktionen sind zunächst bedingte Zusammenhänge. Zusätzliche
Prognosegüte ist eigener Befund. Kausale Substitution, steigende Preiselastizität
wegen veränderter Käufergruppen oder ein Markenwertverlust benötigen weitergehende
Identifikation: Käufer-/Privat-Flottenmix, exogene Preis-/Fördervariation und
Kontrolle gemeinsamer Nachfrage-/Angebotsschocks. Diese Probleme löst weder ein
Kalman-Filter noch hohe erklärte Varianz.

**Nächster fachlicher Schritt:** Preis-/Angebotshistorie zuerst für die relevanten
Tesla-Segmente schließen, bereits beschaffte reale Kraftstoff-/Makroreihen
zeitlich konsistent danebenlegen, danach A gegen B und erst anschließend C
vergleichen. Die vollständige historische Preisabdeckung ist eine konkrete
Datenlücke; der State-Space-Vergleich wird hier nicht als schon ausgeführt ausgegeben.
