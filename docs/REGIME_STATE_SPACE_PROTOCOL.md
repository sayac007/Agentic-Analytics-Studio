# Task 04 – Regime- und Zustandsraumprotokoll

**Version `task-04-regimes/1.0.0`, Stand 29.10.2026, Europe/Berlin.**
**Eingefroren vor dem ersten realen Task-04-Fit auf direkten Nutzerauftrag.**
Normativ ist ausschließlich Stufe 1; die erhaltenen Stufe-2-Entwürfe sind nicht
zur Ausführung freigegeben und brauchen später eine eigene Protokollversion.
Kleine synthetische Kalibrierung vor diesem Freeze ist ausdrücklich dokumentiert. Task 01G, 01I.3 und andere eingefrorene Protokolle bleiben
unverändert. Neue Ergebnisse erhalten später einen eigenen Task-04-Namensraum.

Die Entwicklungsdaten einschließlich der Muster 2025/2026 sind bereits bekannt.
Dies ist ein vor dem ersten Task-04-Fit festzulegender Analyseplan, keine
ergebnisblinde Präregistrierung vor Kenntnis der Daten. Keine Kausalbeweise,
keine synthetischen Ersatzdaten und keine Optimierung auf erwünschte Vorzeichen.

## 0. Abschluss in zwei Stufen

**Stufe 1 zuerst:** Kern ist die beobachtete Zerlegung
`Tesla-Zulassungen = BEV-Markt × Tesla-Anteil`, ergänzt um Kalender,
Quartalsende und belegte Förderregime. Marktmodelle M0/M1/M2 und G3 mit
G0/G1 bilden die fest abgegrenzte Familie. Kein Kraftstoff, keine Diffusion,
keine frei gesuchten zusätzlichen Treiber. G4 ist bei ungeklärtem China-Korb
kein Blocker für G3; Preis-/Launch-/Markenschockkoeffizienten gehören nicht zum
Stufe-1-Fit. Dokumentierte Ereignisse dürfen als Kontext markiert werden.

Planungsrahmen: **zwei bis drei Wochen (10–15 Arbeitstage)** für Datenabschluss,
Implementierung, Prüfung und Ergebnisdarstellung nach fachlicher Freigabe.
Das ist eine Zeitbegrenzung für den Arbeitsumfang, kein behaupteter Arbeitsbeginn
oder zugesagter Hintergrundlauf. Zuerst Zählwertzerlegung und Förderchronik,
dann Baselines/Zustandsmodell mit Rolling Origin, zuletzt Hypothesentabelle
und Grafiken. Am Ende auch ein begrenztes oder nicht entscheidbares Ergebnis
abschließen, statt den Umfang durch weitere Treibersuche zu vergrößern.

**Stufe 2 nur nach bewusster neuer Entscheidung:** M3a/b/c, Kraftstoff-/Makro-
Gegenprüfungen, Bestands-/Diffusionsmodell, Betriebskosten und G2/G4 nach
ihren jeweiligen Datenprüfungen. Die unten erhaltenen Spezifikationen hierfür
sind Entwürfe, keine automatische Ausführungserlaubnis und kein Stufe-1-Scope.
H-F/H-D/H-C bleiben in Stufe 1 offen, sofern kein dafür vorgesehener Test läuft.

Realistische Erwartung: Die Markt-/Anteilszerlegung ist bei geprüften Gesamt-
und Markenzahlen eine exakte Rechenidentität. Der bereits beobachtete Tesla-
Rückgang 2025 ist ein zu beschreibendes Ereignis, kein dadurch erklärter Treiber.
Juniper, Lieferbedingungen und Markenkontroverse können untrennbar bleiben.
Bei Kraftstoff/Förderung 2026 besteht wegen kurzer Reihe und noch fehlender
geprüfter Benzinreihe ein erhebliches Trennungsproblem. Das ist eine Grenze des
Designs, kein vorab festgelegtes negatives Ergebnis. „Nicht entscheidbar“ ist
gleichberechtigt mit gestützt oder geschwächt.

## 1. Ziel und korrigierte Datenbasis

Wir unterscheiden wachsende BEV-Nachfrage, veränderte Markenwahl und veränderte
Mess-/Angebotsbedingungen. Preisempfindlichere neue Käufer sind eine Hypothese;
Produktverbesserung, Förderung, Lieferfähigkeit und Markenereignisse sind
gleichberechtigte Alternativen. Latente Zustände sind keine direkt gemessenen
Motive oder psychologische Markenstärke.

Monatsraster Januar 2021–September 2026: **69 Zeitpunkte**, nicht 276 unabhängige
Monate durch vier Markengruppen. Der offizielle KBA-Gesamtmarkt enthält auch
nicht einzeln zugeordnete Marken. Die Nutzertabelle summiert dagegen numerisch
bekannte Einzelmarken und unterschätzt daher den Markt:

| Zeitraum | BEV laut Nutzertabelle/Einzelmarkensumme | Offizieller BEV-Markt |
|---|---:|---:|
| 2021 | 351.901 | 355.961 |
| 2022 | 465.202 | 470.559 |
| 2023 | 521.728 | 524.219 |
| 2024 | 378.546 | 380.609 |
| 2025 | 541.883 | 545.142 |
| Januar–September 2026 | 601.910 | 604.144 |

Markt- und Pkw-Nenner stammen aus den Gesamtzeilen der jeweiligen FZ10-Mappen;
Monatssummen werden gegen Dezember-/September-YTD geprüft. Tesla/VW sind jeweils
für alle 69 Monate numerisch vorhanden. Kein fehlender Einzelmarkenwert wird null.
Nachweis mit Quellen-/Inputhashes: [Datenaudit](../data/task04_regimes/data_audit.json).
Dieser unveränderte Datenaudit gehört zur Entwurfsfassung 0.1.0; die aktuelle
Umfangsänderung erzeugt keine neuen Daten oder rückdatierten Auditnachweise.

### Vier Gruppen und Grenzen des China-Korbs

Primärer **analytischer C17-Korb**, entsprechend der Nutzerhypothese:
BYD, MG ROEWE, LEAPMOTOR, XPENG, NIO, POLESTAR, GEELY, LYNK & CO, ZEEKR,
OMODA, JAECOO, DEEPAL, CHERY, GWM, DONGFENG, MAXUS, JAC.
Das ist keine vollständige/naturgegebene Nationalitätsvariable. Polestar bleibt
als vorgegebener Grenzfall enthalten. Nicht chinesische Produktion allein ist
das Kriterium; ein in China gefertigter VW wird dadurch nicht Teil dieses Korbs.
Eigentümer-/Markenhistorie ist vor G4-Freigabe quellengebunden zu dokumentieren.

Vorab benannte Sensitivitäten: **C18 = C17 + AIWAYS** (im KBA vorhanden, bisher
nicht im Nutzerkorb), **C21 = C18 + VOLVO + SMART + LOTUS**. Die Grenzfälle werden
nicht nach dem resultierenden Tesla-Zusammenhang ausgewählt. Alle Gruppen sind
disjunkt; der Rest ist offizieller Markt minus Tesla, VW und jeweiligem Korb.

Die C17-Zahlen der Nutzertabelle sind bekannte Teilsummen, keine bewiesenen
vollständigen Korbzulassungen: MG wird erst ab November 2021 separat ausgewiesen.
Nur drei Monate (Juli–September 2026) enthalten alle 17 Marken separat;
66 Monate haben ungeklärte Korbzuordnungen. Erste KBA-Zeile ist kein Launch.
Definiere `U_t = offizieller BEV-Markt − Summe numerischer benannter BEV-Marken`.
Bei unaufgelöster Korbzuordnung liegt der Korb zwischen bekannter Summe und
bekannter Summe plus U_t. Diese Schranken sind keine imputierten Einzelwerte.
Beispiel 2021: C17 mindestens 2.967, höchstens 7.027 nach diesem konservativen
Audit. Eine konkrete Aufteilung von „Sonstige“ ist daraus nicht bekannt.

**Gate:** Das geplante Viergruppenmodell G4 benötigt diese Zuordnung oder einen
vorab gesondert spezifizierten Messfehler-/Intervallansatz. Es wird mit unbekannten
Korbwerten nicht als Punktmodell geschätzt. G3 (Tesla, VW, alle übrigen BEV) ist
eine ausdrücklich benannte, vollständig beobachtete Teilanalyse über 69 Monate;
es beantwortet die China-Substitutionsfrage nicht. Untere/obere Korbschranken sind
zunächst deskriptive Sensitivitäten, keine heimlich vervollständigte Zeitreihe.

## 2. Hypothesen und entscheidende Gegenprüfungen

| ID | Hypothese | Vergleich und mögliche Schwächung |
|---|---|---|
| H-F | Kraftstoffpreise wirken 2026 persistenter auf den Markt als 2022 | Gleiche Stichprobe/Informationslage: Niveau und zeitvariable Wirkung gegen Preisänderung; Vorteil muss auch mit Förderung/Kalender bestehen. Neun Monate belegen keine dauerhafte Wirkung über Jahre. |
| H-D | Sichtbare BEV-Verbreitung trägt zum Marktwachstum bei | Vorperioden-Bestandsproxy gegen Trendmodell; nationale Zeittrends und Bestand können ununterscheidbar bleiben. Kein sozialer Normeffekt aus bloßer positiver Korrelation. |
| H-P | Datierte Förderung verbessert bedingte Marktprognosen | M2 gegen M0 und M1, beide Horizonte in beiden Jahren; samt Einzelmonatseinfluss. Keine individuelle/kausale Förderelastizität aus Gesamtzulassungen. |
| H-T | Der Einbruch 2025 enthält eine Tesla-spezifische Komponente | Markt- versus Tesla-Anteilsentwicklung, freies relatives Niveau gegen dokumentierte Intervention. Juniper, Politik und andere Tesla-Einflüsse können untrennbar bleiben. |
| H-C | Preis-/Angebotswettbewerb verändert Teslas relative Position | Nach Datenfreigabe relative Preise/Verfügbarkeit auf gemeinsamer Stichprobe gegen Modell ohne diese Größen. Fehlende Preisgeschichte lässt H-C unentscheidbar. |

Eine negative Tesla-/China-Anteilskorrelation ist **weder notwendig noch
hinreichend** für Preiswettbewerb: Anteile summieren sich auf eins, gemeinsame
Nenner erzeugen mechanische Zusammenhänge. Auch gleichzeitig steigende Anteile
schließen Substitution nicht aus, wenn andere Marken verlieren. Keine Regression
von Tesla-Zulassungen auf gleichzeitigen Konkurrenzanteil als exogenen Treiber.

„Kraftstoff wirkt nur auf den Markt“ ist eine zusätzliche Restriktion der
Primärspezifikation, kein Naturgesetz. Eine feste Kraftstoffladung in den
Anteilskoordinaten wird als benannte Sensitivität geprüft; deren Befund kann
die Markt-only-Restriktion schwächen, nicht den gesamten Kraftstoffmechanismus.

## 3. Kalender, Transformationen und Beobachtungsmodell

`M_t` = offizieller BEV-Markt, `A_t` = offizieller Pkw-Markt.
Primär `y_t = log(M_t)`, Robustheit `logit(M_t/A_t)`.
Keine `log(1+x)`-Ersetzung für positive Marktwerte und keine willkürlichen
Pseudocounts in Anteilen. Bei echten Nullgruppen stoppt der ALR-Zweig und
benötigt ein vorher separat festgelegtes Zähl-/Nullmodell.

Kalendervektor: eine jährliche Fourier-Paarung (K=1), Quartalsende (März, Juni,
September, Dezember) und zentrierte Wochentagszahl Montag–Freitag abzüglich
bundeseinheitlicher Feiertage. Letztere ist ein nationaler Kalenderproxy, keine
vollständige regional gewichtete Zahl geöffneter Zulassungsstellen.
Kein WKR-Einkaufskalender und keine internen Kalenderdaten.

**Keine zwölf Monatsdummies plus Quartalsende:** Quartalsende wäre dann exakt
kollinear. Auch Fourier-Frequenzen, die das Dreimonatsmuster vollständig
enthalten, dürfen nicht zusätzlich eingeführt werden. Rang und Kondition prüfen.
Der feste Trend gehört zur festen Baseline; das lokale Trendmodell bekommt
nicht zusätzlich denselben festen Zeittrend.

### Marktvarianten – M0/M1/M2 in Stufe 1, M3 nur optionale Stufe 2

| Modell | Spezifikation |
|---|---|
| M0 | Fester linearer Trend + Kalender, ohne externe Treiber |
| M1 | Lokaler linearer Trend + derselbe Kalender |
| M2 | M1 + vorab belegte Förderinterventionen |
| M3a | M2 + feste Wirkung der verzögerten realen Kraftstoffpreisänderung |
| M3b | M2 + feste Wirkung des verzögerten realen Kraftstoffpreisniveaus |
| M3c | M3b mit zeitvariablem statt festem Kraftstoffkoeffizienten |

Gemeinsame Zustandsgleichung von M1–M3:

```text
y_t = mu_t + calendar_t * b + policy_t * d + beta_t * x_t + e_t
mu_t = mu_(t-1) + slope_(t-1) + u_level,t
slope_t = slope_(t-1) + u_slope,t
```

Alle Koeffizientenvorzeichen sind frei. In M3a ist `x_t = Δlog(p_real,t-1)`;
in M3b/c `x_t = log(p_real,t-1)` minus ausschließlich im Training bestimmte
Zentrierung. `p_real = Benzinpreis / (VPI / VPI-Basis)`; keine zusätzliche
automatische VPI-Ladung desselben Mechanismus. Zwei Preis-Vormonate vor Januar
2021 sind für Änderung/Verzögerung erforderlich. Diesel ist eine getrennte
Robustheit, kein Benzinlabel. Alle drei Varianten auf gleicher vollständiger
Kovariatenmaske vergleichen. Keine Suche nach dem günstigsten Lag.

Die geplante Fördermatrix enthält nach vollständiger Primärbelegung Stufen ab
Januar 2023 (Kürzung), September 2023 (Ende gewerblicher Berechtigung), Januar
2024 (erster voller Monat nach Programmende) und Januar 2026 (neues Programm).
Hinzu kommen getrennte Einmonatspulse Dezember 2023 und Januar 2024 für den
Übergang. Der Dezemberpuls ist kein bereits bewiesener Vorzieheffekt: Das abrupte
Antragsende mitten im Monat kann unterschiedliche Mechanismen bündeln. Alle
Vorzeichen bleiben frei; kein zusätzlicher Augustpuls nach Ansicht der Ergebnisse.
Bekanntgabe 19. Januar und Portalöffnung 19. Mai 2026 sind getrennte Wissensdaten,
keine drei gleichzeitig freien Förderwirkungen. Eine vorab benannte Sensitivität
ersetzt den Januar- durch den Mai-2026-Schritt. Historische Quellenlücken sperren
die jeweilige Spalte bis zur Freigabe, nicht eine stillschweigende Ersatzkodierung.

HypoForge-Python bleibt für feste Differenzen und Verzögerungen vorgesehen:
die bereits auditierte `FeatureSpec`-/`evaluate`-API am Commit
`c47f636d24a39a820574a13133d6af693134a180`. Kein Hill-/Adstock-Zwang für Preise,
keine automatische Lag-Suche; Kalman-/Posteriorrechnung gehört in die ausdrücklich
spezifizierte Zustandsraumimplementierung. VARX ist nicht Teil dieser Primärfamilie.

M3c: `beta_t = beta_(t-1) + u_beta,t`. Entwurfswert
`SD(u_beta)=0,02` pro Monat **in ursprünglichen Log–Log-Koeffizienteneinheiten**,
nicht je beliebig skaliertem Rohpreis. Entspricht a priori einer jährlichen
Drift-SD von rund 0,069; dies ist eine Regularisierungsannahme, kein gemessener
Effekt. Sensitivitäten 0, 0,01 und 0,04. Keine nachträgliche Auswahl des
ansprechendsten Koeffizientenpfads. Ein verzögerter EWMA-Erwartungspreis ist
nicht gleichzeitig eine zusätzliche Primärvariante; dafür wäre eine vor dem
Fit festgeschriebene Erweiterung mit Initialisierung/Zeitskala nötig.

Benannte Makro-Gegenprüfung: M2 und jede M3-Variante zusätzlich mit dem um einen
Monat verzögerten, im Training zentrierten Konsumentenkreditzins. Einheit:
Prozentpunkte des jährlichen AAR/NDER-Zinses der bestehenden ECB-Reihe, nicht
Anteil 0–1; gemeinsamer vollständiger Vergleichszeitraum. Fester Koeffizient mit
`Normal(μ=0; σ=0.10)` je Prozentpunkt, ohne Vorzeichenrestriktion. Damit wird
geprüft, ob der Kraftstoffbefund nach Finanzierungskosten bestehen bleibt;
kein gleichzeitig zeitvariables Zinsmodell. Fehlende 2026-Beobachtungen sperren
diese Gegenprüfung. Der Logit-Zweig prüft zusätzlich die Pkw-Gesamtmarktrelation;
VPI wird für die reale Preisspezifikation benötigt. EUR/USD wird ohne konkreten
Importpreis-/Weitergabe-Nachweis nicht allein wegen seiner Verfügbarkeit ergänzt.

### Diffusion und Betriebskosten: getrennte, datenabhängige Prüfblöcke

Bevorzugter Verbreitungsproxy: veröffentlichter **Pkw-BEV-Bestandsanteil**,
zuletzt vor dem Prognosezeitpunkt verfügbarer Jahresanker. Jahreswerte werden
nicht in angeblich beobachtete Monatsbestände interpoliert. Kumulierte
Neuzulassungen sind wegen fehlendem Anfangsbestand, Exporten/Stilllegungen
kein tatsächlicher Fahrzeugbestand. Aktuelle Zulassungen im eigenen
Diffusionsregressor wären außerdem eine mechanische Zielgrößenverwendung;
höchstens kumulierte **Vorperioden** sind als klar benannter Proxy zulässig.

Ein glatter Bestandsproxy wird nicht zusätzlich zu frei driftendem Niveau und
Steigung als unabhängig identifizierter sozialer Normeffekt ausgegeben.
Geplanter D-Vergleich ersetzt den Trend durch den Logarithmus des zuletzt
veröffentlichten Pkw-BEV-Bestandsanteils plus Kalender/Interventionen, statt alle
Trendquellen zu stapeln. Log-BEV-Bestandszahl ist eine getrennt benannte
Sensitivität, kein gleichzeitig zusätzlicher Regressor. Dieser Vergleich ist ein
deskriptiver Funktionsvergleich, kein geschätztes Bass-Imitationsmodell.
Ohne Bestands-/Publikationsnachweise bleibt dieser Block gesperrt.

Betriebskostenverhältnis erst nach getrennt geprüften Strompreisen. Einheiten:
`Benzin_EUR/L * L/100km` und `Ladestrom_EUR/kWh * kWh/100km`.
Verbrauch und Heim-/Öffentlich-Lademix wären vorab offengelegte Szenarioannahmen,
keine beobachteten Flottenmittel. Halbjahres-Strompreise bleiben Halbjahresproxies;
ein allgemeiner VPI ist kein Ladetarif. Keine stillschweigende Monatsinterpolation.

## 4. Markenwahl, Kovarianz und 2025-Alternativen

Nach bestandenem Gruppen-Gate G4:
`z_T = log(T/Rest)`, `z_V = log(VW/Rest)`, `z_C = log(C17/Rest)`.
Je Koordinate lokales Random-Walk-Niveau plus derselbe geeignete Kalender;
Tesla-Quartalsende ist zwingend. Vollständige gemeinsame 3×3-Kovarianz der
Beobachtungsstörungen im Anteilsblock; diagonal regularisierte Zustandsinnovationen.
Keine gleichzeitig unbeschränkt freien vollen Q- und R-Matrizen bei 69 Monaten.
Kovarianz ist nicht der Beweis von Substitution.

G0: feste Anteilsniveaus + Kalender. G1: Random-Walk-Niveaus + Kalender.
G2: G1 plus dokumentierte relative Preise/Launches, **nur** auf freigegebener
gemeinsamer Datenbasis. Fehlende monatliche Preise sperren G2; sie werden
nicht aus heutigen Konfiguratoren zurückgeschrieben.

Stufe 1 beschreibt den freien Tesla-Niveaupfad; eine Variante mit gesondertem
Tesla-Interventionsterm gehört erst zur optionalen Stufe 2. Primärkontrast des
Pfads: Mittel 2025 minus Mittel 2024,
nicht nachträglich günstig gewählte Spitzenmonate. Er ist modellabhängig,
nicht selbst ein nachgewiesener Strukturbruch der Markenwahrnehmung.
Juniper wird als dokumentiertes Modellwechselereignis getrennt von einer
politischen Kontroverse geführt. Wenn beide dieselbe Monatskodierung haben,
sind ihre Einzeleffekte nicht identifiziert: keine zwei kollinearen Dummies.
Keine negative Wirkung vorgeben. Politische Kontroverse ohne datierte seriöse
Belege wird nicht als Ereigniskovariate verwendet.

Ein Marktmodell und ein Anteilsmodell liefern zusammenhängende Informationen.
Bevorzugt gemeinsame bayesianische Schätzung; Zustands-/Beobachtungskovarianzen
müssen dabei ausdrücklich definiert sein: für G4 gemeinsamer Beobachtungsvektor
`[log(M), z_T, z_V, z_C]` mit voller 4×4-Matrix R (darin der 3×3-Anteilsblock),
regularisiert durch LKJ(4). Für G3 entfallen China-Koordinate und zugehörige Zeile/
Spalte. Q bleibt diagonal für Niveau-, Steigungs-, Anteils- und gegebenenfalls
Kraftstoffkoeffizienten-Innovationen; keine zusätzlich freie volle Q-Matrix.
Damit wird die Markt-/Anteilsabhängigkeit ausdrücklich modelliert, nicht pauschal
auf null gesetzt. Dies ist eine Gauß-Approximation in Log-/ALR-Koordinaten,
kein exaktes multinomiales Zählmodell und keine Messung individueller Markenwahl.
Zweistufige Schätzung ist nur eine
benannte Approximation: gemeinsame Unsicherheitssimulation, Abhängigkeitsannahmen
und Sensitivität berichten. Nicht bloß zwei Punktschätzer/Intervallenden multiplizieren.
`DynamicFactor` ist kein automatisch passendes ALR-Modell; eine frequentistische
Referenz muss dieselben Gleichungen tatsächlich abbilden, ggf. als `MLEModel`.

## 5. Priors, Referenz und Abbruch

Entwurfswerte zur Prüfung **vor** dem Freeze, nicht datengetunte Wahrheiten.
In Stufe 1 sind die Random-Walk-SDs feste Konstanten: Markt-Niveau 0.03,
Markt-Steigung 0.01 und jedes Anteilsniveau 0.03 pro Monat; die Varianzen sind
0.0009, 0.0001 und 0.0009. Sie werden nicht aus der jeweils günstigsten Anpassung
oder dem Testfehler geschätzt. Eine Niveau-SD von 0.03 entspricht einem
einmonatigen Log-Schritt von ungefähr 3 % und ohne Steigungsbeitrag einer
Zwölfmonats-SD von rund 0.104; das erlaubt Anpassung, ohne jede Spitze frei zu
verfolgen. Es ist eine Skalierungs-/Regularisierungsannahme, kein empirischer
Parameterbeleg. Fest benannte Niveau-SDs 0.03/0.05/0.10/0.20 bei stets gleicher Steigungs-SD
0.01; kein Vollraster oder Auswahl des besten echten Ergebnis-/Prognosepfads.
Ein Prognoseverlust gegenüber der festen Baseline bleibt ein negatives Ergebnis.

| Größe | Prior/Regularisierung und Einheit |
|---|---|
| Markt-Anfangsniveau | Normal(μ=log(50000); σ=1.5), log monatliche Zulassungen; breite Größenordnung, kein beobachteter Startwert |
| Anfangssteigung / feste M0-Steigung | Normal(μ=0; σ=0.05), Logänderung/Monat |
| SD Niveau / Steigung | Fest 0.03 / 0.01, monatliche Zustandsinnovationen |
| Markt-Beobachtungs-SD | HalfNormal(σ=0.25), Logzählwert |
| Fourier / Förderstufen | Normal(μ=0; σ=0.5), Ziel-Logeinheiten |
| Quartalsende / einzelne Pulse | Normal(μ=0; σ=1), Ziel-Logeinheiten; keine Vorzeichenrestriktion |
| Wochentagskoeffizient | Normal(μ=0; σ=0.05), je zusätzlichem definiertem Tag |
| Fester bzw. Anfangs-Kraftstoffkoeffizient | Normal(μ=0; σ=1), ursprüngliche Log–Log-Einheiten |
| Anteil-Anfangsniveau | Normal(μ=0; σ=2), ALR-Koordinate |
| Anteil-Zustands-SD / Beobachtungs-SD | Zustand fest 0.03; Beobachtung HalfNormal(σ=0.5), ALR-Einheiten |
| Gemeinsame Beobachtungskorrelation | LKJ(η=4), Regularisierung zur schwächeren Korrelation |

Dezimalpunkte in den Verteilungsparametern vermeiden Mehrdeutigkeit; σ bezeichnet
die SD, nicht die Varianz. Die Priors sind teils bewusst informativ regularisierend. Ihre
Identifikationsleistung darf nicht als zusätzliche empirische Information gelten.
Prior-Predictive-Plausibilität zuerst; danach keine Priorkorrektur für gewünschte
Ergebnisse. Änderungen benötigen neue Protokollversion vor einem neuen Fit.
Stufe-1-Sensitivitäten: feste Niveau-SDs, Portalstart statt rückwirkender
Förderberechtigung und Logit-BEV-Anteil. Kraftstoff-SDs, C17/C18/C21, nominal/real,
Diesel/Benzin und mit/ohne 2026 sind ausschließlich mögliche spätere Stufe-2-Entwürfe; kein Vollraster und
keine Auswahl der besten Sensitivität als neues Hauptergebnis.

Bayesianische Referenz: PyMC, künftig exakt gepinnte Version, vier Ketten,
je 2.000 Warm-up/2.000 Ziehungen, Seeds 20261029–20261032, `target_accept=0,95`.
Keine Package-/Implementierungsverfügbarkeit wird in diesem Entwurf behauptet.
Abbruch/kein erfolgreicher Fit: Divergenzen, R-hat >1,01 oder Bulk-/Tail-ESS <400
bei berichteten Größen, nicht endliche Werte, Rang-/Definitionsfehler oder
unaufgelöste Beobachtungsgruppen. Technische Probleme transparent lösen;
keine wissenschaftliche Spezifikation zur Erzeugung eines Effekts ändern.
Priorabhängige oder schwach identifizierte Effekte bleiben unentscheidbar.

Frequentistische Referenz: gleiche feste Transformationen/Kalender und möglichst
gleiche lineare Gauß-Zustandsstruktur. Unterschiedliche Prior-/MLE-Behandlung
kann unterschiedliche Aussagen erzeugen. Übereinstimmung ist **kein**
Abnahmekriterium; Unterschiede dokumentieren statt durch Tuning beseitigen.
Markov-Switching gehört wegen kurzer Reihe und konkurrierender Trendquellen
nicht zur Primärfamilie; eine spätere Zwei-Zustands-Robustheit benötigt vorab
eine eigene eingegrenzte Spezifikation, keine freie Regimesuche in diesem Entwurf.

## 6. Rolling Origin und Diagnostik

Mindestens 48 Referenzmonate Training bis Dezember 2024. Vergleich in
Originaleinheiten, gleiche Masken und Informationsannahmen:

- h=1: Januar 2025–September 2026, 21 Zielmonate.
- h=3: März 2025–September 2026, 19 Zielmonate; letztes Origin Juni 2026.
- Das sind überlappende, abhängige Prognosefehler, keine unabhängigen Wiederholungen.
  Pro Origin/Ziel/Horizont Ergebnis, Trainingsumfang, Maske und Kovariatenpfad ausgeben.

Dies sind **retrospektive Referenzmonat-Backtests**, keine historisch nachgewiesenen
Echtzeitprognosen: heutige Quellvintages und teilweise nur monatsgenaue
Publikationsangaben erlauben diese stärkere Behauptung nicht. Operativ ist ein
Schritt nach letzter KBA-Veröffentlichung oft bereits ein Nowcast im Folgemonat.
Für echte Echtzeittests erst Veröffentlichungs-/Revisionsvintages beschaffen.

Zukünftige Kraftstoff-/Zins-/Preiswerte nicht als bekannt verwenden: primär
Persistenz des letzten zum Origin verfügbaren Werts als **Prognoseszenario**,
keine Auffüllung historischer Lücken. Preisänderungs-Szenario entsprechend aus
diesem Preisniveaupfad ableiten. Kalender ist bekannt; Politik nur, soweit am
Origin angekündigt. Eine neue Förderstufe kann vor Auftreten nicht aus
Nullspalten geschätzt werden. Realisierte Zukunftskovariaten höchstens als
gesondert benannte bedingte Oracle-Auswertung, nicht als Hauptprognose.
Beim Logit-Marktanteilsmodell wird für Zählwertprognosen ein vorher festgelegter
saisonaler naiver Pkw-Gesamtmarkt verwendet (`A_(T+h-12)`), nicht dessen
realisierte Zukunft. Ansonsten Anteile separat bewerten.

Kovariatenlücken: Monatsraster erhalten, keine Zeitkompression/Interpolation.
Die Treibermodelle und eine passende Basis nutzen dieselbe Beobachtungsmaske;
eine zusätzlich auf allen Beobachtungen geschätzte Basis bleibt separat sichtbar.
Zustandsfortschreibung über eine Lücke ist ein Modellschritt, keine neue Messung.
Die fünf bekannten Diesel-Monatslücken 2021/2022 und zusätzliche Lagverluste
explizit ausweisen; Benzin muss unabhängig geprüft werden.

Kennzahlen: RMSE, MAE, MASE gegen saisonal-naive Basis, Intervallbreite und
beobachtete Prognoseintervallabdeckung, je Horizont/Jahr und einzeln pro Fenster.
Punktprognose primär posterior-prädiktiver Mittelwert; keine Auswahl zwischen
Mittel/Median nach Testfehler. Einfluss einzelner Zielmonate auf Gesamtmetriken
berichten, nicht nachträglich problematische Monate entfernen.

ADF/KPSS auf Logziel und ALR je Trainingsfenster, deterministische Spezifikation
vorab: ADF mit Konstante/Trend und drei Lags, KPSS mit Trend und drei Lags.
Nichtstationäre Zielniveaus schließen einen lokalen Trend nicht aus und lösen
keine automatische Differenzierung aus. Innovationsdiagnostik auf standardisierten
**Ein-Schritt-Filterfehlern**, nicht nur geglätteten Residuen; initiale zwölf
Trainingsmonate aus dieser Diagnostik ausschließen. ADF/KPSS dort mit Konstante;
Ljung–Box bei 3/6/12 Lags, Holm innerhalb dieser Diagnosefamilie. Reihen mit
Lücken werden für diese Tests nicht zeitlich zusammengeschoben:
jeweils das längste zusammenhängende Segment verwenden (bei Innovationen nach
dem Diagnose-Burn-in),
bei Gleichstand das frühere; unter 24 Monaten Diagnose als nicht berechnet
kennzeichnen. Segment und effektives n berichten; insbesondere Lag 12 bleibt bei
kurzen Segmenten unsicher. Diese Schwelle ist eine Diagnose-Mindestlänge, keine
statistische Identifikations- oder Powergarantie. Zusätzlich:
Autokorrelationsgrafik, Ausreißer-/Varianz-/Ereignisprüfung. Geringe Teststärke
und kleine Abdeckungsstichprobe bleiben Grenzen; keine validierte 95-%-Abdeckung
oder empirische Power behaupten.

Prädiktive Unterstützung für H-F: Niveau/TVC muss gegenüber Änderung **und**
entsprechender Basis 2026 bei beiden Horizonten geringeren RMSE zeigen;
Einzelfenster und Weglassen je eines Zielfehlers dürfen keinen versteckten
Einzelmonatssieg verschleiern. Sonst gemischt/unentscheidbar statt Siegeretikett.
Für TVC zusätzlich die mittleren beta-Werte Januar–September 2026 minus
Januar–September 2022 sowie minus Januar–September 2024 mit vollständiger
gemeinsamer Unsicherheit und Priorvergleich berichten. Keine nachträgliche
Auswahl eines einzigen positiven Kontrasts. Auch ein Prognosesieg identifiziert
keinen dauerhaft kausalen Kraftstoffeffekt.

2022 liegt bei diesem 2021 beginnenden Datenfenster und mindestens 48
Trainingsmonaten ausschließlich im Trainingsbereich. Es gibt deshalb keinen
gleichwertigen unabhängigen 2022-Prognosetest. Der Vergleich „2022 nur kurzfristig,
2026 dauerhaft“ bleibt teilweise deskriptiv und kann unentscheidbar sein;
Kraftstoff, allgemeine Inflation, Lieferbedingungen und Politik sind konkurrierend.
Ein geglätteter Zustandsverlauf nutzt spätere Daten und kann einen Wendepunkt
zeitlich vorverlegen. Filterzustände und Vollstichproben-Glättung in Grafiken
trennen; geglättete Wendepunkte nicht als damals erkennbare Regime ausgeben.

## 7. Zerlegung und Ergebnisumfang

Beobachtet gilt `Tesla = M * s_T`. Jahresanteil ist Summe Tesla / Summe Markt,
nicht Mittel der Monatsanteile. Die exakte symmetrische Veränderungszerlegung
lautet `ΔTesla = Mittel(s_alt,s_neu)*ΔM + Mittel(M_alt,M_neu)*Δs`.
Das ist buchhalterisch, keine Ursachenzerlegung. Administrative Zählwerte bekommen
keine erfundenen Stichproben-Konfidenzbänder.

Modellbasierte Unsicherheit folgt gemeinsamen Posterior-/Prognoseziehungen:
je Ziehung `Tesla_t = M_t * s_T,t`, dann Zeiträume aggregieren und zerlegen.
Nicht Produkt der Erwartungswerte und nicht Produkt marginaler Intervallgrenzen.
Latente Credible Intervals von Prognoseintervallen künftiger Zulassungen trennen.
2026 ausschließlich Januar–September gegen denselben Vorjahreszeitraum.

Erwartet: Markt-/Anteilszerlegung, beschriftete Zustands-/Koeffizientenpfade,
Fensterprognosen, Diagnostik, Tabelle H-F/H-D/H-P/H-T/H-C mit gestützt,
geschwächt oder unentscheidbar und eine fünf Sätze lange verständliche Einordnung.
Die berichtete Tabelle hat genau die Spalten **Hypothese | Test | Ergebnis
(gestützt / geschwächt / offen) | Begründung in einem Satz**. Nicht ausgeführte
Stufe-2-Prüfungen erhalten „offen – nicht untersucht“ und kein impliziertes
Ergebnis. H-T bezeichnet die relative Tesla-Entwicklung, nicht deren politische
oder produktbezogene Ursache. Keine Phase automatisch „Early Adopter“ nennen. Ergebnisartefakte später mit
Protokollhash, Quellvintage, Software, Seeds und tatsächlich ausgeführten Checks.

## 8. Datenstand beim Freeze

Die [Datenbereitschaft](TASK_04_DATA_READINESS.md) trennt den freigegebenen
Stufe-1-Kern von gesperrten Zusatzmodulen. Markt-/Tesla-/VW-Werte sind vollständig,
die vier vorgesehenen Förderregime sind mit Primärquellen belegt
([Chronik](../data/task04_regimes/policy_chronology.json)).
Exakte alte Bekanntgabetage bleiben unbekannt; Jahresrückblicke sind kein
historischer Publikationszeitnachweis. Korb-/Benzin-/Preis-/Strom-/Bestandslücken
sperren nur ihre jeweiligen Stufe-2-Blöcke. Kein echtes Echtzeit-/As-of-Versprechen.

## 9. Abgeschlossene kleine Wiederfindungsprüfung und SD-Entscheidung

Vor dem ersten realen Fit wurde der
[Plan](../data/task04_regimes/recovery_plan.json) committed: vier künstliche Fälle
(zwei Seeds × wahre Niveau-SD 0.03/0.10), bekanntes Markt-Förderdelta −0.30
Logeinheiten, dieselbe M2/G1-Struktur und unbekanntes volles R.
Steigungs-SD stets 0.01. Vier Ketten, je 1.000 Warm-up/1.000 Ziehungen.
Die drei Niveaukandidaten 0.10/0.05/0.03 wurden in jedem Fall geprüft;
keine beobachtete KBA-Zielgröße floss in diese Auswahl ein.

| Niveau-SD | Mittlerer absoluter Medianfehler | Wahrheit im 95-%-Intervall | Intervall ohne null | Konvergent |
|---|---:|---:|---:|---:|
| 0.10 | 0.165277 | 4/4 | 0/4 | 4/4 |
| 0.05 | 0.162991 | 4/4 | 0/4 | 4/4 |
| 0.03 | 0.161265 | 4/4 | 0/4 | 4/4 |

**Alle zwölf Intervalle enthalten null.** Der bekannte von null verschiedene
Effekt wird damit nicht überzeugend präzise wiedergefunden. Wahrheit im Intervall
ist bei diesen breiten Bändern kein Beweis guter Identifikation oder validierter
95-%-Abdeckung. Der Fehlerunterschied der SDs ist sehr klein; er etabliert keinen
statistisch belegten Überlegenheitsnachweis.

Nach dem vorab festgelegten kleinsten mittleren absoluten Medianfehler wird
**0.03 als primäre Niveau-SD** verwendet, nicht als validierte tatsächliche
Tesla-/Marktvarianz. Steigung bleibt 0.01. Dies begrenzt die Glättungsfreiheit;
alle drei weiteren SDs bleiben sichtbar. Kein nachträglicher Wechsel der
Primärvariante anhand echter Testfehler oder erwünschter Förderkoeffizienten.

Alle [zwölf Einzelfits](../results/task04/recovery/fits.json),
[Zusammenfassung](../results/task04/recovery/summary.csv) und
[Ausführungsnotizen](../results/task04/recovery/execution_notes.json) bleiben
erhalten. Drei erste serielle Fits wurden aus Laufzeitgründen durch die vollständige
Parallel-Ausführung ersetzt und getrennt dokumentiert, nicht zur Auswahl gemischt.
Eine Tracer-Initialisierungsstörung erzeugte keine numerische Ergebniszeile und
wurde vor dem vollständigen Lauf behoben. Modell, Priors, Fälle und wissenschaftliche
Entscheidungsregel blieben gleich. Vier künstliche Fälle sind keine Power-/MDE-
oder empirische Coverage-Studie und ersetzen keine realen Beobachtungen.

## 10. Verbindliche Implementierungs- und Prüfdetails der Stufe 1

- Gemeinsamer G3-Beobachtungsvektor log(BEV), log(Tesla/Rest), log(VW/Rest);
  Rest = offizieller BEV-Markt minus Tesla minus VW. VW ist eine einzelne Marke,
  nicht der Konzern. G4/China bleibt gesperrt. Förderung wird nur auf den Markt
  geladen; unterschiedliche Förderberechtigung nach Marke kann im Anteilsniveau
  verbleiben. Ein relativer Tesla-Effekt beweist deshalb keinen Imageeffekt.
- M0/G0, M1/G1, M2/G1 als Kern; zusätzlich M2 mit Niveau-SDs 0.05/0.10/0.20,
  M2 mit Mai- statt Januar-2026-Schritt und M2 mit Logit-Marktziel. Genau acht
  Spezifikationen; keine nicht registrierte Treibersuche. Portalöffnung gilt in
  Prognosen erst ab Bekanntheit 19.05.2026, Januar-Regel erst ab 19.01.2026.
- Kalenderkoeffizienten in allen drei Koordinaten: Normal-SDs 0.5/0.5/1/0.05
  für sin/cos/Quartalsende/nationale Wochentage. Wochentage nur mit Trainingsmittel
  zentrieren. Markt-Förderstufen Normal-SD 0.5, Pulse 1.0. Keine zusätzlichen
  festen Trends neben dem lokalen Trend; keine zwölf Monatsdummies neben QE.
- Volles R mit PyMC-LKJ(eta=4) und HalfNormal-SDs 0.25/0.5/0.5, diagonales
  festes Q. Initialzustand/Regressionskoeffizienten haben die angegebenen proper
  Normal-Priors und werden analytisch im Kalman-Filter integriert. NumPyro-NUTS
  zieht nur sechs R-Koordinaten aus derselben PyMC-Priordichte; die Hilfs-Normaldichte
  wird exakt aufgehoben. Gemeinsame bedingte Gaußziehungen stellen beta und
  vollständige Zustände/Unsicherheit wieder her. Keine Plug-in-OLS-Unsicherheit.
- Vier parallele CPU-Ketten, adaptierte dichte 6×6-Massenmatrix, Float64,
  je 2.000 Warm-up/2.000 Ziehungen, target_accept=0.95, max_tree_depth=10 und
  Seeds 20261029/30/31/32. Eine rein numerische Budgetverdoppelung auf 4.000/4.000
  bei misslungenen MC-Diagnosen ist höchstens einmal erlaubt, mit beiden
  Diagnosen; kein Wechsel der Priors/SDs/Daten nach Vorzeichen oder Testfehlern.
- Vollstichproben-NUTS bleibt von Rolling Origin getrennt. Dort darf ein
  Wichtigkeitsupdate ausschließlich R-Partikel aus demselben (andere Variante)
  oder unmittelbar vorherigen Trainingspräfix verwenden. Neue Gewichte sind
  ungeglättete exakte marginale Likelihoodquotienten × alte Gewichte.
  Zulässig nur bei Gewichts-ESS mindestens N/2 (normal 4.000 von 8.000) und
  Pareto-k ≤0.5; sonst neues NUTS mit Trainingsdaten. Keine R-hat-Angabe für
  gewichtete aktuelle Partikel erfinden: ursprüngliche NUTS-Diagnosen, ESS,
  Pareto-k und Proposaltyp pro Fenster getrennt berichten.
- JIT-Code darf wiederverwendet werden, Vollstichproben-Warm-up/-Posterior nie
  für frühere Prognosen. Die Schätzschnittstelle nimmt ausschließlich das
  Trainingspräfix entgegen; strukturelle Null-Padding-Slots sind keine
  Beobachtungsimputation und werden aus der Likelihood ausgeschlossen.
- Alle acht Varianten: 21 h=1- und 19 h=3-Prognosen, vier kohärente Zählgrößen
  BEV/Tesla/VW/Rest, insgesamt 1.280 Zeilen. Vorhersagepunkt = Mittel gemeinsamer
  posterior-prädiktiver Zählwertziehungen; Intervalle schließen Zukunftsrauschen
  ein. MASE-Nenner nur saisonal-naive Trainingsfehler, kein Testdatennachschlagen.
- H-P prädiktiv gestützt nur bei kleinerem Markt-RMSE gegen M0 und M1 in allen
  vier Jahr-/Horizontkombinationen und unverändertem Vorteil beim Weglassen
  jedes einzelnen Zielfehlers aus der Kennzahl (keine Neuschätzung/Beobachtungslöschung).
  In allen vier Gruppen schlechter gegen beide Basen: geschwächt; sonst offen.
  Selbst gestützt bedeutet weder kausale Policy-Wirkung noch identifizierte
  einzelne Förderkoeffizienten. Vollständige Fensterfehler/Einflussgrenzen berichten.
- Innovationsdiagnostik verwendet fehler_i/sqrt(S_ii), keine umsortierte
  Cholesky-Komponente. R ist hier der Voll-Trainingsposterior-Mittelwert;
  die Filterdiagnose ist bedingt, kein damaliger Echtzeitfilter. ADF/KPSS mit
  Konstante und drei Lags auf Innovationen nach zwölf Monaten Burn-in;
  auf beobachteten Zielkoordinaten Konstante/Trend und drei Lags.
  Ljung–Box 3/6/12, Holm je Serie. Warnungen und Rand-p-Werte erhalten.
- Die statsmodels-Referenz maximiert marginale Likelihood für R bei identischer
  proper-Gauß-Initialisierung/Regression. Sie ist keine unregularisierte klassische
  OLS und kein Kausaltest. Alle Ergebnisse/Fehler werden berichtet, keine
  Übereinstimmung mit Bayes erzwingen.
- Hashgebundene private Sampling-Checkpoints dienen nur identischer Fortsetzung;
  numerische Tabellen/Grafiken/Manifest werden eigenständig versioniert.
  Keine API-Schlüssel, fremden Rohdaten oder Source-Permits in Ergebnisartefakten.
