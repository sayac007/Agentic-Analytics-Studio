# Agentic Analytics Studio

**Was erklärt die Entwicklung der Tesla-Neuzulassungen in Deutschland —
BEV-Gesamtmarkt, Markenanteil, Kalender oder staatliche Förderung?**

Die abgeschlossene **Task-04-Stufe-1-Analyse** verwendet 69 reale KBA-Monate
von Januar 2021 bis September 2026. Acht vorab festgelegte gemeinsame
Zustandsraummodelle trennen Markt und relative Markenentwicklung.
Diese README fasst die Ergebnisse vollständig zusammen; Tabellen und neue
Grafiken vom **30. Oktober 2026** lesen ausschließlich den gespeicherten Lauf
vom **29. Oktober 2026**. Es wurde dafür kein Modell neu geschätzt.

Die wichtigsten Antworten:

- **2025 verliert Tesla Anteil in einem wachsenden Markt:** −48,4 % Tesla,
  +43,2 % BEV-Markt. Eine allgemeine Marktschwäche erklärt den Tesla-Rückgang nicht.
- **Quartalsenden sind der robusteste modellierte Tesla-Zusammenhang:** positive
  bedingte Koeffizienten mit 95-%-Posteriorintervallen ohne null in allen acht Varianten.
- **Förderregime verbessern die Marktprognose 2026, aber nicht einheitlich 2025
  und nicht generell die Tesla-Prognose.** Eine abgesicherte kausale Rangliste
  „Förderung, Preise, China“ ergibt sich daraus nicht.
- **Benzinpreise, Fahrzeugpreise und China-Wettbewerb wurden in dieser Stufe
  nicht geschätzt.** Ihre Hypothesen sind offen, nicht widerlegt. Der latente
  Tesla-Pfad hängt wesentlich von Glättungsannahmen ab; Restfehler bleiben problematisch.

[Beobachtete Entwicklung](#1-was-sich-tatsächlich-verändert-hat) ·
[Acht Modelle](#2-was-die-acht-zustandsraummodelle-prüfen) ·
[Treiber und Intervalle](#3-welche-treiber-statistisch-auffallen) ·
[RMSE-Vergleich](#4-wie-gut-prognostizieren-die-modelle-rmse-aller-acht-varianten) ·
[Hypothesen](#7-welche-hypothesen-sind-gestützt-und-welche-offen) ·
[Vollständiger Tabellenanhang](results/task04/presentation/DETAILS.md)

<!-- BEGIN TASK04 COMPUTED RESULTS -->

## 1. Was sich tatsächlich verändert hat

| Vergleich zum Vorjahr | Tesla-Zulassungen | Tesla Δ | BEV-Markt Δ | Tesla-BEV-Anteil | Marktkomponente | Anteilskomponente | Tesla Δ absolut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 69.963 | +76,2 % | +32,2 % | 14,87 % | +14.912 | +15.337 | +30.249 |
| 2023 | 63.685 | −9,0 % | +11,4 % | 12,15 % | +7.249 | −13.527 | −6.278 |
| 2024 | 37.574 | −41,0 % | −27,4 % | 9,87 % | −15.812 | −10.299 | −26.111 |
| 2025 | 19.390 | −48,4 % | +43,2 % | 3,56 % | +11.048 | −29.232 | −18.184 |
| 2026 Jan–Sep | 44.810 | +201,9 % | +58,1 % | 7,42 % | +12.541 | +17.424 | +29.965 |

Alle Jahre vollständig außer **2026: Januar–September gegen Januar–September 2025**.
2025: Tesla 19.390 statt 37.574; BEV-Markt 545.142 statt 380.609.
Teslas BEV-Anteil fällt von 9,87 % auf 3,56 %. Der wachsende Markt kompensiert
rechnerisch einen Teil des Anteilsverlusts. Bereits 2023 sinkt Teslas Anteil.
2026 steigen sowohl der Markt als auch Teslas Anteil gegenüber dem niedrigen Vorjahr.

![Tesla in Deutschland: jährliche Markt- und Anteilskomponenten](results/task04/presentation/annual_market_share.png)

Quelle: gespeicherte KBA-FZ10-Auswertung vom 29.10.2026; eigene Darstellung, keine Neuschätzung. Die symmetrische Zerlegung addiert sich exakt vor Rundung:
`ΔTesla = Mittel(Anteil) × ΔMarkt + Mittel(Markt) × ΔAnteil`.
Sie ordnet Veränderungen rechnerisch zu und identifiziert keine Ursachen.
Die Bildunterschriften vermeiden deshalb die unbewiesene Aussage, ein einzelnes
Förderereignis habe den gesamten Marktrückgang verursacht.

![Monatliche Tesla-Zulassungen und Markt-/Anteilszerlegung](results/task04/stage1/market_share_decomposition.png)

Quelle: Kraftfahrt-Bundesamt, FZ10, eigene Berechnung. Politikmarkierungen sind
Kontext; der global berichtete Model-Y-Wechsel in Q1 2025 ist kein exakt datiertes
deutsches Lieferereignis. Verwaltungszählwerte erhalten keine erfundenen Stichprobenintervalle.

## 2. Was die acht Zustandsraummodelle prüfen

| Modell | Spezifikation | Monatliche Niveau-SD | Förderkodierung / Besonderheit |
| --- | --- | --- | --- |
| M0 | Fester Markttrend; konstante relative Markenniveaus | 0 | Keine |
| M1 | Lokaler Markttrend und relative Markenniveaus | 0,03 | Keine |
| M2 **primär** | M1 + Förderstufen und Übergangspulse | 0,03 | Berechtigung ab Januar 2026 |
| M2_sd0.05 | M2; beweglichere Zustände | 0,05 | Wie M2 |
| M2_sd0.10 | M2; beweglichere Zustände | 0,10 | Wie M2 |
| M2_sd0.20 | M2; beweglichste Zustände | 0,20 | Wie M2 |
| M2_portal | M2; alternativer Beginn der Förderung 2026 | 0,03 | Portalstart Mai statt Januar 2026 |
| M2_logit | M2; Logit(BEV/Pkw) statt log(BEV) | 0,03 | Wie M2; saisonal-naiver Pkw-Prognosenenner |

Alle Varianten enthalten eine jährliche Sinus-/Kosinus-Saison, Quartalsende und
nationale Wochentage abzüglich bundeseinheitlicher Feiertage. M0 setzt alle
Zustandsinnovationen auf null; bei den dynamischen Modellen bleibt die Steigungs-SD
0,01. Eine größere Niveau-SD erlaubt beweglichere latente Zustände und verändert
damit die Zuordnung von Schwankungen, nicht die beobachteten Zulassungen.

Gemeinsam modelliert werden Markt sowie `log(Tesla/Rest)` und `log(VW/Rest)`;
Rest = offizieller BEV-Markt minus Tesla minus VW. **VW bedeutet Marke, nicht Konzern.**
Die acht Spezifikationen waren vor dem realen Fit festgelegt. Die nachträglich
beste RMSE-Variante ersetzt das Primärmodell nicht.

## 3. Welche Treiber statistisch auffallen

Die Schätzung ist bayesianisch. **† bedeutet: Das bedingte, punktweise
95-%-Posteriorintervall enthält null nicht.** Das ist kein frequentistischer
p-Wert, kein multiplikitätsbereinigter Signifikanztest und kein Kausalnachweis.
Die folgenden beiden Tabellen enthalten sämtliche Koeffiziententypen, die in
mindestens einer Variante dieses Kriterium erfüllen; negative und instabile
Zusammenhänge bleiben sichtbar. Alle **132 Koeffizienten**, einschließlich
Posterior-SD und Intervallen auch ohne †, stehen im
[vollständigen Tabellenanhang](results/task04/presentation/DETAILS.md).

### Kalender: Median [95-%-Posteriorintervall]

| Modell | Quartalsende Tesla/Rest | Quartalsende Markt | Nationale Wochentage Markt | Sinus-Saison Markt | Koeffizienten mit † insgesamt |
| --- | --- | --- | --- | --- | --- |
| M0 | +0,730 [+0,301; +1,141] **†** | +0,216 [+0,065; +0,368] **†** | +0,0219 [−0,0326; +0,0748] | −0,067 [−0,170; +0,033] | 2 |
| M1 | +0,739 [+0,349; +1,129] **†** | +0,207 [+0,079; +0,335] **†** | +0,0201 [−0,0276; +0,0668] | −0,061 [−0,155; +0,031] | 2 |
| M2 | +0,734 [+0,340; +1,123] **†** | +0,165 [+0,062; +0,264] **†** | +0,0396 [−0,0005; +0,0780] | +0,014 [−0,073; +0,103] | 5 |
| M2_sd0.05 | +0,746 [+0,356; +1,120] **†** | +0,161 [+0,068; +0,257] **†** | +0,0410 [+0,0022; +0,0778] **†** | +0,025 [−0,066; +0,111] | 6 |
| M2_sd0.10 | +0,751 [+0,396; +1,103] **†** | +0,155 [+0,076; +0,234] **†** | +0,0441 [+0,0103; +0,0764] **†** | +0,043 [−0,054; +0,139] | 6 |
| M2_sd0.20 | +0,750 [+0,396; +1,091] **†** | +0,156 [+0,080; +0,233] **†** | +0,0444 [+0,0118; +0,0760] **†** | +0,042 [−0,103; +0,188] | 5 |
| M2_portal | +0,738 [+0,345; +1,126] **†** | +0,166 [+0,068; +0,271] **†** | +0,0400 [−0,0000; +0,0794] | +0,008 [−0,075; +0,086] | 5 |
| M2_logit | +0,737 [+0,343; +1,120] **†** | +0,062 [−0,025; +0,152] | +0,0110 [−0,0237; +0,0454] | −0,090 [−0,167; −0,014] **†** | 5 |

**Stabilster gemessener Zusammenhang: Tesla-Quartalsende, positiv in allen acht
Varianten.** Das ist mit Liefer-/Zulassungswellen vereinbar. Der primäre Wert
+0,734 [+0,340; +1,123] steht in Log-Verhältniseinheiten und
ist keine pauschale prozentuale Tesla-Absatzwirkung. VW-Quartalsende, sämtliche
VW-Kalenderterme, Tesla-Sinus/Kosinus/Wochentage und Markt-Kosinus enthalten in
allen Varianten null. Der Markt-Wochentagszusammenhang erscheint erst bei den
größeren Niveau-SDs; die negative Markt-Sinuskomponente nur im Logit-Zweig.

### Staatliche Förderung: Median [95-%-Posteriorintervall]

| Modell | Kürzung Januar 2023 | Ende gewerbliche Berechtigung September 2023 | Nach Förderende: Januar 2024 | Programm 2026 |
| --- | --- | --- | --- | --- |
| M2 | −0,760 [−1,088; −0,387] **†** | −0,486 [−0,815; −0,145] **†** | −0,575 [−0,949; −0,189] **†** | −0,097 [−0,435; +0,251] |
| M2_sd0.05 | −0,876 [−1,218; −0,490] **†** | −0,543 [−0,864; −0,193] **†** | −0,590 [−0,981; −0,196] **†** | −0,142 [−0,478; +0,200] |
| M2_sd0.10 | −1,174 [−1,548; −0,768] **†** | −0,691 [−1,034; −0,329] **†** | −0,571 [−1,028; −0,117] **†** | −0,226 [−0,570; +0,131] |
| M2_sd0.20 | −1,414 [−1,822; −0,947] **†** | −0,884 [−1,290; −0,428] **†** | −0,462 [−1,053; +0,154] | −0,178 [−0,597; +0,232] |
| M2_portal | −0,741 [−1,072; −0,377] **†** | −0,496 [−0,818; −0,147] **†** | −0,566 [−0,937; −0,190] **†** | +0,115 [−0,215; +0,449] |
| M2_logit | −0,681 [−0,992; −0,361] **†** | −0,611 [−0,912; −0,291] **†** | −0,511 [−0,862; −0,159] **†** | +0,045 [−0,262; +0,365] |

M0/M1 haben keine Förderkoeffizienten. Die Schritte sind **inkrementelle
Koeffizienten kumulierter Dummies**, ausschließlich in der Marktgleichung.
Beim Portalmodell beginnt der letzte Schritt im Mai 2026; der kanonische
CSV-Termname bleibt `grant_2026_01`. Logit-Koeffizienten sind Log-Odds des
BEV-Anteils am Pkw-Markt; die übrigen Marktkoeffizienten sind Log-Zählwerteinheiten.
Sie dürfen nicht als dieselbe Elastizität verglichen werden.

Kürzung und Ende der gewerblichen Berechtigung sind in allen sechs Policy-Varianten
negativ mit Intervall ohne null. Beim Post-Ende-Schritt umfasst SD 0,20 null.
**Das Programm 2026 enthält in jeder Variante null**, bei wechselndem Vorzeichen.
Die Übergangspulse Dezember 2023 und Januar 2024 enthalten ebenfalls in allen
Varianten null; primär +0,244 [−0,188; +0,669] bzw.
−0,061 [−0,470; +0,361].

Die historischen Policy-Koeffizienten sind bedingte Assoziationen mit sich
kompensierenden Trends/Zuständen. Ein negativer Koeffizient identifiziert weder
den isolierten Fördereffekt noch dessen kausale Absatzhöhe.
[Primärquellen und Förderchronik](data/task04_regimes/policy_chronology.json).

## 4. Wie gut prognostizieren die Modelle? RMSE aller acht Varianten

RMSE = Wurzel des mittleren quadrierten Prognosefehlers, **in Zulassungen pro
Monat; kleiner ist besser**. Mindestens 48 Trainingsmonate; strikt vergangene
Trainingspräfixe. h=1 umfasst 2025 zwölf und 2026 neun Zielmonate; h=3 umfasst
2025 zehn und 2026 neun Zielmonate. Dreimonatsprognosen sind jeweils Prognosen
des dritten Zielmonats, keine Summe der folgenden drei Monate. Sie überlappen.
2026 bedeutet hier immer Januar–September.

### Offizieller BEV-Markt

| Modell | 2025 · h=1 | 2025 · h=3 | 2026 · h=1 | 2026 · h=3 |
| --- | --- | --- | --- | --- |
| M0 | 7.417,1 | 8.288,9 | 15.706,3 | 17.625,3 |
| M1 | 10.016,4 | 12.164,7 | 11.479,8 | 13.449,0 |
| M2 | 7.839,6 | 8.970,2 | 8.715,3 | 9.905,0 |
| M2_sd0.05 | 7.939,5 | 9.235,2 | 8.700,7 | 10.571,6 |
| M2_sd0.10 | 8.439,9 | 10.065,6 | 8.056,6 | 12.389,5 |
| M2_sd0.20 | 9.184,5 | 11.273,4 | 6.527,8 | 16.249,5 |
| M2_portal | 7.847,4 | 8.998,3 | 8.943,9 | 9.680,6 |
| M2_logit | 5.400,7 | 6.625,9 | 7.143,3 | 9.928,7 |

### Tesla

| Modell | 2025 · h=1 | 2025 · h=3 | 2026 · h=1 | 2026 · h=3 |
| --- | --- | --- | --- | --- |
| M0 | 4.292,7 | 4.730,2 | 2.071,4 | 2.069,8 |
| M1 | 3.357,6 | 3.703,1 | 2.290,0 | 2.333,3 |
| M2 | 3.862,9 | 4.315,0 | 2.298,6 | 2.213,0 |
| M2_sd0.05 | 3.263,0 | 3.754,5 | 2.310,5 | 2.158,3 |
| M2_sd0.10 | 2.384,7 | 2.945,4 | 2.755,3 | 2.435,2 |
| M2_sd0.20 | 1.791,7 | 2.415,8 | 3.023,3 | 2.748,2 |
| M2_portal | 3.867,2 | 4.356,1 | 2.362,8 | 2.206,7 |
| M2_logit | 3.517,9 | 4.042,9 | 2.196,8 | 2.243,7 |

![RMSE aller acht Modelle für Markt und Tesla, einschließlich Verschlechterungen](results/task04/presentation/rmse_comparison.png)

Quelle: gespeicherte KBA-FZ10-Auswertung vom 29.10.2026; eigene Darstellung, keine Neuschätzung. Jede Zelle zeigt RMSE und prozentuale Änderung gegen M0 auf denselben
Zielmonaten; Blau = kleinerer Fehler, Orange = größerer Fehler. Farben sind keine
Signifikanztests. Eine gemeinsame Skala begrenzt die Farbsättigung bei ±60 %;
Zahlenwerte werden nicht begrenzt.

### Was bringt die Förderspezifikation M2 gegenüber den Baselines?

| Ziel | Jahr | h | n | RMSE M2 − M0 (relativ) | RMSE M2 − M1 (relativ) |
| --- | --- | --- | --- | --- | --- |
| BEV-Markt | 2025 | 1 | 12 | +422,5 (+5,7 %) | −2.176,8 (−21,7 %) |
| BEV-Markt | 2025 | 3 | 10 | +681,3 (+8,2 %) | −3.194,5 (−26,3 %) |
| BEV-Markt | 2026 | 1 | 9 | −6.991,0 (−44,5 %) | −2.764,6 (−24,1 %) |
| BEV-Markt | 2026 | 3 | 9 | −7.720,3 (−43,8 %) | −3.544,0 (−26,4 %) |
| Tesla | 2025 | 1 | 12 | −429,8 (−10,0 %) | +505,3 (+15,1 %) |
| Tesla | 2025 | 3 | 10 | −415,2 (−8,8 %) | +611,9 (+16,5 %) |
| Tesla | 2026 | 1 | 9 | +227,2 (+11,0 %) | +8,6 (+0,4 %) |
| Tesla | 2026 | 3 | 9 | +143,2 (+6,9 %) | −120,3 (−5,2 %) |

**Negative Differenz bedeutet Verbesserung; positive Differenz Verschlechterung.**
Der Wechsel M1 → M2 ergänzt gemeinsam vier Förderstufen und zwei Übergangspulse.
Er erlaubt keine separate RMSE-Zuordnung zu einem einzelnen Förderereignis.
Auch für Quartalsende ist keine Variante ohne diesen Term vorhanden: sein
isolierter zusätzlicher RMSE-Nutzen wurde nicht geschätzt.

M2 verbessert Marktprognosen gegenüber M1 in allen vier Gruppen, verliert 2025
gegen M0. 2026 bleibt der Vorteil gegen beide Baselines auch bei Weglassen jedes
einzelnen Zielfehlers aus der Kennzahl erhalten. Die vorab festgelegte H-P-Regel
fordert den Vorteil in beiden Jahren und Horizonten; **H-P bleibt offen**.
Für Tesla ist 2025 M1 besser als M2 und 2026 M0 besser als M2. Bessere Marktprognosen
sind somit kein allgemeiner Tesla-Prognosegewinn.

Die Sensitivitäten liefern keinen universellen Sieger: SD 0,20 verbessert den
Markt-RMSE 2026/h=1, verschlechtert 2026/h=3 aber deutlich gegen das Primärmodell.
Der Logit-Zweig verbessert die Marktprognosen 2025 und verwendet dabei einen
saisonal-naiven Pkw-Nenner; dessen Unsicherheit wird nicht zusätzlich modelliert.
M2 und Portal sind in den 2025-Trainingsfenstern strukturell gleich; kleine
Unterschiede stammen von festen unterschiedlichen Monte-Carlo-Seeds.

<details>
<summary>Alle acht Modelle für VW und Rest</summary>

**VW:**

| Modell | 2025 · h=1 | 2025 · h=3 | 2026 · h=1 | 2026 · h=3 |
| --- | --- | --- | --- | --- |
| M0 | 2.160,6 | 2.079,8 | 1.411,6 | 1.359,3 |
| M1 | 2.789,5 | 2.851,7 | 4.103,2 | 4.256,5 |
| M2 | 2.237,6 | 2.080,7 | 3.522,8 | 3.694,9 |
| M2_sd0.05 | 2.285,8 | 2.242,2 | 2.948,3 | 3.594,6 |
| M2_sd0.10 | 2.348,6 | 2.664,0 | 1.969,1 | 3.172,6 |
| M2_sd0.20 | 2.461,7 | 2.974,5 | 1.627,2 | 3.949,6 |
| M2_portal | 2.238,6 | 2.087,7 | 3.804,2 | 3.784,0 |
| M2_logit | 2.126,8 | 2.011,2 | 2.094,6 | 2.004,6 |

**Rest des BEV-Markts:**

| Modell | 2025 · h=1 | 2025 · h=3 | 2026 · h=1 | 2026 · h=3 |
| --- | --- | --- | --- | --- |
| M0 | 6.362,3 | 7.421,7 | 16.349,7 | 17.962,3 |
| M1 | 8.032,5 | 10.297,2 | 8.209,1 | 10.540,6 |
| M2 | 5.501,0 | 7.042,7 | 6.731,5 | 8.809,4 |
| M2_sd0.05 | 5.379,8 | 6.919,2 | 6.831,9 | 8.994,7 |
| M2_sd0.10 | 5.566,7 | 7.091,0 | 6.447,0 | 10.009,4 |
| M2_sd0.20 | 6.198,7 | 7.964,6 | 5.457,5 | 12.223,0 |
| M2_portal | 5.513,8 | 7.061,4 | 6.004,2 | 8.433,3 |
| M2_logit | 4.463,3 | 5.647,8 | 8.396,5 | 11.005,7 |

Auch bei VW ist M0 2026 besser als sämtliche dynamischen Varianten.
Rest ist eine rechnerische Restgruppe, kein gemessener China-Korb.

</details>

Das sind retrospektive Backtests mit heutigem Quellstand, keine historisch
rekonstruierten Echtzeitprognosen. Zukünftige Förderregeln werden nur verwendet,
soweit am Prognoseursprung bekannt. Breite Intervalle begrenzen den Nutzen:
für Tesla M2 2025/h=1 durchschnittlich **15.244,0**
Zulassungen Intervallbreite bei ungefähr 1.616 beobachteten Zulassungen im Monat.
Der Trefferanteil von 100,0 %
validiert angesichts zwölf Zielmonaten und breiter Bänder keine 95-%-Abdeckung.
[Alle 128 Kennzahlenzeilen](results/task04/stage1/metrics.csv) einschließlich
MAE, MASE und Intervallbreiten; [1.280 Prognosezeilen](results/task04/stage1/predictions.csv).

## 5. Wie robust ist das latente Tesla-Niveau?

| Modell | Jahresmittel 2025 − 2024: Tesla/Rest-Niveau [95-%-Intervall] | Einordnung |
| --- | --- | --- |
| M0 | +0,000 [+0,000; +0,000] | Fest auf null gesetzt |
| M1 | −0,145 [−0,297; +0,010] | Intervall enthält null |
| M2 | −0,142 [−0,297; +0,014] | Intervall enthält null |
| M2_sd0.05 | −0,282 [−0,504; −0,051] | Negativ, Intervall ohne null |
| M2_sd0.10 | −0,517 [−0,839; −0,181] | Negativ, Intervall ohne null |
| M2_sd0.20 | −0,739 [−1,159; −0,303] | Negativ, Intervall ohne null |
| M2_portal | −0,144 [−0,292; +0,006] | Intervall enthält null |
| M2_logit | −0,144 [−0,298; +0,012] | Intervall enthält null |

![Robuster Quartalsendzusammenhang und priorabhängiger Tesla-Niveaukontrast](results/task04/presentation/tesla_robustness.png)

Quelle: gespeicherte KBA-FZ10-Auswertung vom 29.10.2026; eigene Darstellung, keine Neuschätzung. Im Primärmodell umfasst der Niveaukontrast null; erst die beweglicheren
SD-Varianten ergeben vollständig negative Intervalle. Der beobachtete
Anteilsverlust bleibt unbestritten, seine Zuordnung zum latenten Niveau ist
modellabhängig. M0 erzwingt einen Nullkontrast; das ist kein empirischer Gegenbeweis.
Ein latenter Zustand misst weder Markenimage noch einen isolierten Model-Y-Effekt.

## 6. Stationarität, Restfehler und Grenzen der Absicherung

Im Primärmodell: Markt-Zielniveau ADF p=0,2961 / KPSS p=0,0454;
Tesla/Rest-Zielniveau 0,0457 / 0,0178; VW/Rest 0,3160 / 0,0536.
Die widersprüchlichen Tesla-Niveautests erlauben keine einfache Stationaritätsaussage.
Zielniveaus: 69 Monate, ADF effektiv 65; feste drei Lags und Konstante/Trend.

**Diagnostik der Ein-Schritt-Filterinnovationen aller Varianten:** nach zwölf
Monaten Burn-in bleiben 57 Werte, ADF effektiv 53; Konstante und drei Lags.

| Modell | Tesla ADF p | Tesla KPSS p | Tesla min. Holm-Ljung–Box p | VW min. Holm-Ljung–Box p |
| --- | --- | --- | --- | --- |
| M0 | 0,2024 | 0,0139 | 8,791e-05 | 1,063e-12 |
| M1 | 0,1297 | 0,0285 | 0,005744 | 1,641e-10 |
| M2 | 0,1296 | 0,0286 | 0,005733 | 1,715e-10 |
| M2_sd0.05 | 0,0755 | 0,0713 | 0,1198 | 5,28e-07 |
| M2_sd0.10 | 0,0210 | >0,1000 | 1 | 0,09867 |
| M2_sd0.20 | 0,0021 | >0,1000 | 1 | 1 |
| M2_portal | 0,1296 | 0,0286 | 0,005719 | 1,701e-10 |
| M2_logit | 0,1298 | 0,0286 | 0,005714 | 1,671e-10 |

ADF prüft die Nullhypothese einer Einheitswurzel; KPSS die Niveaustationarität
der Innovationen. Holm wird innerhalb der drei Ljung–Box-Lags 3/6/12 pro Reihe
angewandt. Das Minimum oben dient der vollständigen Diagnoseübersicht, nicht
der nachträglichen Lagauswahl. Vollständige Roh-/Holm-Werte stehen im
[Anhang](results/task04/presentation/DETAILS.md).

**Tesla behält im Primärmodell Persistenz und Serialkorrelation; VW deutliche
Serialkorrelation.** Größere SDs mildern diese Befunde, können aber Prognosen
verschlechtern. Numerische Konvergenz ersetzt keine angemessene Modellspezifikation.
Beim Primärmarkt ist der kleinste Holm-Ljung–Box-p-Wert 0,0928.

![Primäre Innovations-ACF und Filter-/Glättungsvergleich](results/task04/diagnostics/innovation_acf.png)

Quelle: gespeicherte KBA-Modellinnovationen. Diagnose bedingt auf die im gesamten
Trainingsfenster geschätzte Kovarianz; keine kalibrierten Spezifikationstests.
Die geglätteten Zustände rechts nutzen spätere Beobachtungen, auch die gezeigte
Filterkurve konditioniert auf Vollstichproben-Kovarianz. Keine historische Live-Sicht.
Die [wissenschaftliche Einordnung](results/task04/SCIENTIFIC_REVIEW.md) enthält
auffällige Monate, Streuungsänderungen und alternative Erklärungen.

Eine besonders wichtige Warnung: `exp(mu)` der kalender-/policybereinigten
Marktkomponente beträgt September 2026 im Primärmodell 538.438, Intervall
[215.782; 1.276.463], bei tatsächlich 88.599 BEV und 256.774 Pkw insgesamt.
Große kompensierende Zustands-/Förderterme machen diese algebraische Komponente
**ungeeignet als Marktpotenzial oder kausalen Ohne-Förderung-Gegenverlauf**.
Die [Originalgrafik](results/task04/stage1/latent_market.png) bleibt zugänglich.

<!-- END TASK04 COMPUTED RESULTS -->

## 7. Welche Hypothesen sind gestützt und welche offen?

| Hypothese | Tatsächlicher Test | Ergebnis | Was sich daraus ableiten lässt |
| --- | --- | --- | --- |
| H-T: Tesla verliert 2025 relativ zum BEV-Markt | Exakte Markt-/Anteilszerlegung | **Gestützt, deskriptiv** | Tesla −48,4 %, Markt +43,2 %; das Muster ist markenspezifisch relativ zum Markt, seine Ursache bleibt unbestimmt. |
| H-T: Das latente Tesla-Niveau liegt 2025 unter 2024 | Jahresmittelkontrast im primären M2 | **Offen** | −0,142 [−0,297; +0,014]; negativ erst ohne null bei beweglicheren SD-Varianten. |
| H-P: Förderregime verbessern Marktprognosen robust | M2 gegen M0 und M1, beide Jahre und Horizonte, Einzelmonatseinfluss | **Offen, gemischte Evidenz** | M2 gewinnt 2026 gegen beide, 2025 nur gegen M1; die vorab festgelegte Gesamtregel ist nicht erfüllt. |
| Einzelne Förderumstellungen erklären kausal den Absatz | Kein kausal identifizierendes Design vorhanden | **Nicht nachgewiesen** | Historische negative Stufenkoeffizienten allein trennen Förderung nicht von parallelen Veränderungen und Zustandsdrift. |
| Das Förderprogramm 2026 hat einen eigenständig positiven Koeffizienten | Sechs vorab festgelegte Policy-Varianten | **Nicht statistisch abgesichert** | Sämtliche 95-%-Posteriorintervalle enthalten null, Vorzeichen wechseln. Das beweist keine Wirkungslosigkeit. |
| H-F: Höhere Benzinpreise treiben BEV/Tesla nachhaltig | **Nicht untersucht** in Stufe 1 | **Offen** | Keine geprüfte vollständige Benzinreihe in diesem Fit; vorhandene private Dieselbeobachtungen messen nicht Benzin. |
| Günstigere Fahrzeugpreise treiben Absatz und Markenwechsel | **Nicht untersucht** in Stufe 1 | **Offen** | Vergleichbare Preisbelege für 23/80 recherchierte jährliche Top-10-Modelljahre bilden keinen vollständigen monatlichen relativen Preisindex. |
| H-C: Wachstum chinesischer Anbieter erklärt Teslas Anteil | **Nicht untersucht** in Stufe 1 | **Offen** | C17-Korbzuordnung in 66/69 Monaten unvollständig; Rest darf nicht als China ausgegeben werden. |
| H-D: Übergang von Early Adopters zu preissensibleren Käufern | **Nicht untersucht** in Stufe 1 | **Offen** | Keine beobachtete Käufergruppen-/Bestandsvariable im Modell; ein latenter Zustand misst keinen Käufertyp. |

Die ersten drei und H-F/H-C/H-D entsprechen den
[gespeicherten Hypothesenentscheidungen](results/task04/stage1/hypotheses.csv).
Die zusätzlichen Zeilen präzisieren die hier erfragten Preis- und Förderaussagen;
sie sind keine nachträglich ausgeführten Hypothesentests. Keine der in Stufe 1
nicht untersuchten Hypothesen darf als widerlegt oder als bestätigter Treiber
erscheinen. **Es gibt noch keine belastbare Rangfolge der kausalen Tesla-Treiber.**

## 8. Was kann man damit anfangen — und was fehlt?

Für die Analyse lässt sich bereits unterscheiden, ob eine Absatzveränderung
mit dem Gesamtmarkt oder mit dem eigenen Anteil zusammenhängt. Das verhindert
beispielsweise, den Tesla-Einbruch 2025 allein auf einen schrumpfenden BEV-Markt
zurückzuführen. Der starke Quartalsendrhythmus gehört in Liefer-/Zulassungsplanung
und Prognose-Baselines. Die Markt- und Markenmodelle müssen getrennt bewertet
werden: ein besseres Marktmodell ist noch kein besseres Tesla-Modell.

Für eine operative Absatzplanung sind die breiten Intervalle und verbleibenden
Restfehler konkrete Einschränkungen. Förderung kann mit diesen Ergebnissen nicht
als isolierter Absatzhebel budgetiert werden. Zulassungen messen außerdem
Registrierung/Lieferung, nicht den Zeitpunkt der Kaufentscheidung.

Der nächste **fachliche** Schritt wäre ein separat festgelegter Vergleich mit
monatlich vergleichbaren relativen Fahrzeugpreisen, einem aufgelösten
Wettbewerberkorb, dokumentiertem Modellangebot und einer geeigneten
Betriebskostenreihe. Dafür zuerst Verfügbarkeit und Definitionen prüfen, dann
wenige feste Verzögerungen und Baselines auf identischen Monaten vergleichen.
Gleichzeitige Wettbewerberzulassungen sind selbst Marktergebnisse, keine
exogenen Konkurrenzschocks. Preis × Betriebskosten-Interaktionen brauchen eigene
Haupteffekte und ausreichend Variation; sie sind hier noch nicht geschätzt.
[Konkrete Datenlücken](docs/TASK_04_DATA_READINESS.md) ·
[Preis-/Wettbewerbsrecherche](data/competition/README.md) ·
[Wissenschaft und Portalstatistiken](docs/EV_DEMAND_LITERATURE_AND_PORTALS.md).
Dieser README-Schritt führt keine weitere Analyse automatisch aus.

## 9. Daten, Reproduzierbarkeit und wissenschaftliche Absicherung

Quelle: **Kraftfahrt-Bundesamt, Flensburg, FZ10; eigene Berechnung;
Datenlizenz Deutschland – Namensnennung – Version 2.0.** Der offizielle
BEV-Markt stammt aus den Gesamtzeilen und nicht aus der unvollständigen Summe
bekannter Einzelmarken. Die 69 gemeinsamen Monate sind vollständig; fehlende
Wettbewerberwerte wurden nicht null gesetzt. Kein synthetischer Ersatz fließt
in diese reale Studie ein. Quellvintages und Referenzmonate sind dokumentiert;
historische Veröffentlichungs-/Revisionsstände wurden nicht rekonstruiert.

Das [eingefrorene Protokoll](docs/REGIME_STATE_SPACE_PROTOCOL.md)
`task-04-regimes/1.0.0` und der [Freeze-Nachweis](data/task04_regimes/freeze.json)
liegen vor dem ersten realen Fit. Die Entwicklungsmuster waren bereits bekannt;
das ist keine ergebnisblinde Präregistrierung. Die kleine vorherige synthetische
Wiederfindung hatte bei allen zwölf Fits Intervalle mit null. SD 0,03 war nach
der festgelegten Fehlerregel knapp vorn; das validiert weder die tatsächliche
Zustandsvarianz noch Power oder 95-%-Abdeckung.

Alle acht Vollstichprobenmodelle bestehen die festgelegten Monte-Carlo-Grenzen:
keine Divergenzen, maximaler R-hat der Kovarianzparameter 1,00260.
168 historische Trainingspräfixe verwenden 22 eigene NUTS-Fits und 146 geprüfte
Gewichtsupdates. Insgesamt sind 1.280 Prognosezeilen und 128 Kennzahlenzeilen
versioniert. Diese numerische Prüfung beseitigt die oben berichteten
Spezifikations- und Identifikationsprobleme nicht.

Die neue Darstellung ist direkt aus CSV/JSON erzeugt. Der
[Darstellungsnachweis](results/task04/presentation/manifest.json) bindet
Originaldateien, Skript, Tabellenabschnitt und PNG/SVG-Dateien per SHA-256.
Er prüft alle 128 RMSE-Werte anhand der 1.280 gespeicherten Prognosefehler.
Originaltabellen, Protokolle, Modelle und Originalgrafiken bleiben unverändert.

Python 3.12, aus dem Repository; die reine Ergebnisprüfung schätzt kein Modell:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-regimes.lock
.venv/bin/python -m regimes.verify results/task04/stage1
.venv/bin/python -m scripts.task04_results_presentation --check
```

Die Tabellen und Grafiken bleiben ohne GitHub-Actions-Artefakte lesbar.
Die [vollständigen Reproduktionsbefehle](results/task04/README.md),
[ursprünglichen Prüfungen und Softwareversionen](results/task04/verification.json),
[alle Koeffizienten](results/task04/stage1/coefficients.csv),
[alle Prognosen](results/task04/stage1/predictions.csv) und die
[ausführliche wissenschaftliche Einordnung](results/task04/SCIENTIFIC_REVIEW.md)
bleiben zugänglich. Zusätzliche private Energie-/Trends-Studien sind nicht Teil
dieser veröffentlichten Ergebnisdarstellung.

## Weitere Bestandteile und Studio starten

Der vorhandene Browserpilot ist ein separater Arbeitsbereich für Datenauftrag,
Baseline-Treiber, monatlichen CSV-Upload mit historischem Abgleich, Analyse und
Ergebnisübergabe. Optional kommentiert OpenAI ausdrücklich freigegebene
Zusammenfassungen. Der gespeicherte Task-04-Forschungslauf wird dadurch weder
neu geschätzt noch automatisch in ein operatives Modell umgewandelt.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-empirical.lock
.venv/bin/python -m demo
```

Öffne http://127.0.0.1:8000. Für reale Pilotanalysen braucht es die dokumentierten
privaten Quellen; es gibt keinen synthetischen Ersatz bei fehlenden Daten.
[Bedienung und Grenzen](docs/EMPIRICAL_STUDIO.md) ·
[CSV- und Arbeitsablauf](docs/RESEARCH_WORKFLOW.md) ·
[Copilot-Präsentationsanleitung](docs/COPILOT_RESULT_PRESENTATION.md) ·
[Azure-Bereitstellung](docs/AZURE_PRIVATE_STUDIO.md) ·
[Secret-Speicherorte ohne Werte](docs/SECRET_INVENTORY.md).

**Frühere synthetische Forschung:** Task 02 untersuchte Identifizierbarkeit über
1.000 Seeds je Szenario. Im getesteten Design waren Always-on-Effekte schwer
wiederzufinden; fehlende Quartalskontrollen erzeugten falsche Sicherheit.
Nullfehlerquoten und Intervallabdeckung waren unzureichend kalibriert. Für die
fachliche Tesla-Analyse wurden synthetische Ersatzdaten verworfen.
[Originalbefunde und Einschränkungen](docs/IDENTIFIABILITY_RESEARCH.md) ·
[Unveränderte Originalergebnisse](results/task02/).

[Verträge](contracts/README.md), [Quellenkatalog](docs/SOURCE_CATALOG.md) und
[Architektur](docs/ARCHITECTURE.md) dokumentieren weitere Entwicklungsstufen.
WKR, HypoForge und Kinderwelt sind unabhängige Repositories und bleiben unverändert.
