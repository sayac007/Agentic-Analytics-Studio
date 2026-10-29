# Task 04, Stufe 1: wissenschaftliche Einordnung

Stand: 29. Oktober 2026. Diese Lesesicht verwendet ausschließlich die gespeicherten,
tatsächlich geschätzten Ergebnisse von `task-04-regimes/1.0.0`.
Keine neue Schätzung, keine Modell-/Prior-Auswahl anhand dieser Ergebnisse.
[Rechenbericht](stage1/report.md), [sämtliche Kennzahlen](stage1/metrics.csv),
[Hypothesentabelle](stage1/hypotheses.csv), [Hash-/Ausführungsnachweis](verification.json).

**Fazit des begrenzten Schritts:** Die beobachtete Markt-/Anteilsentwicklung ist
klar. Quartalsenden sind ein stabiler bedingter Kalenderzusammenhang.
Die Förderungsspezifikation hilft bei den Marktprognosen 2026, aber nicht
einheitlich gegenüber beiden Baselines in beiden Jahren. Das enge Primärmodell
beschreibt die Markendynamik nicht ausreichend; weder seine latenten Niveaus
noch seine Förderkoeffizienten liefern eine abgesicherte kausale Ursachenrangliste.

## 1. Was die Zählwerte tatsächlich zeigen

Tesla 2025: 19.390 statt 37.574 Zulassungen; offizieller BEV-Markt 545.142 statt
380.609. Teslas BEV-Anteil fiel von 9,8721 % auf 3,5569 %.
Die symmetrische Jahreszerlegung ergibt +11.047,52 Markt- und −29.231,52
Anteilskomponente, zusammen −18.184. Das sind keine kausalen Effektbeiträge.

2026 ausschließlich Januar–September: Tesla 44.810 statt 14.845,
BEV-Markt 604.144 statt 382.202; Tesla-Anteil 7,4171 % statt 3,8841 %.
+12.541,03 Markt- und +17.423,97 Anteilskomponente ergeben +29.965.
Der niedrige Vorjahresvergleich ist sichtbar; keine Gleichsetzung mit einem
vollständigen Jahr. Bereits 2023: Tesla −8,97 %, BEV-Markt +11,40 %.
Ein allein auf 2025 datierter Mechanismus erklärt diese längere relative
Entwicklung nicht.

[Alle fünf Jahres-/YTD-Zerlegungen](stage1/decomposition.csv), ohne erfundene
Stichprobenintervalle um administrative Zählwerte.
[Gemeinsame latente Zerlegungen mit Unsicherheit](stage1/model_decomposition.csv)
sind davon getrennt: Mittel der Komponenten addieren sich, marginale
Intervallgrenzen nicht zwingend.

## 2. Kalender und Förderkoeffizienten

M2-Quartalsende, Median und bedingtes 95-%-Posteriorintervall:

| Koordinate | Koeffizient [95-%-Intervall] |
| --- | --- |
| log BEV | +0.165 [+0.062, +0.264] |
| log Tesla/Rest | +0.734 [+0.340, +1.123] |
| log VW/Rest | +0.016 [-0.147, +0.179] |

Der Tesla-Quartalsendkoeffizient ist in allen acht Spezifikationen positiv,
einschließlich der jeweiligen Intervalle. Er misst eine bedingte ALR-Assoziation,
keine prozentuale kausale Absatzsteigerung. Liefer-/Zulassungsrhythmen sind damit
vereinbar. Bei VW ist der entsprechende Primärkoeffizient nicht von null getrennt.
Die übrigen Fourier-/Wochentagsintervalle des Primärmodells enthalten null.

Förderschritte sind **inkrementelle** Log-Koeffizienten bei kumulierten Dummies,
bedingt auf dieselben Kalender-/Zustandsannahmen. Keine individuelle Förderdosierung,
keine Preiselastizität und keine eigenständigen kausalen Effekte:

| Modell | Kürzung Jan 2023 | Privat ab Sep 2023 | Post-Ende Jan 2024 | Programm 2026 |
| --- | --- | --- | --- | --- |
| M2 | -0.760 [-1.088, -0.387] | -0.486 [-0.815, -0.145] | -0.575 [-0.949, -0.189] | -0.097 [-0.435, +0.251] |
| M2_sd0.05 | -0.876 [-1.218, -0.490] | -0.543 [-0.864, -0.193] | -0.590 [-0.981, -0.196] | -0.142 [-0.478, +0.200] |
| M2_sd0.10 | -1.174 [-1.548, -0.768] | -0.691 [-1.034, -0.329] | -0.571 [-1.028, -0.117] | -0.226 [-0.570, +0.131] |
| M2_sd0.20 | -1.414 [-1.822, -0.947] | -0.884 [-1.290, -0.428] | -0.462 [-1.053, +0.154] | -0.178 [-0.597, +0.232] |
| M2_portal | -0.741 [-1.072, -0.377] | -0.496 [-0.818, -0.147] | -0.566 [-0.937, -0.190] | +0.115 [-0.215, +0.449] |
| M2_logit | -0.681 [-0.992, -0.361] | -0.611 [-0.912, -0.291] | -0.511 [-0.862, -0.159] | +0.045 [-0.262, +0.365] |

Bei `M2_portal` ersetzt Mai den Januar-2026-Schritt; der kanonische
Spaltenname bleibt im CSV erhalten. Der Logit-Zweig verwendet Logit- statt
Log-Markteinheiten. Diese Koeffizienten sind deshalb nicht unverändert dieselbe
Elastizität. Der Primärkoeffizient 2026 umfasst null und begründet keinen isolierten
Fördernachweis, obwohl das Gesamtmodell 2026 bessere Marktprognosen erzielt.

Primäre Übergangspulse:

| Puls | Median [95-%-Intervall] |
| --- | --- |
| transition_2023_12 | +0.244 [-0.188, +0.669] |
| transition_2024_01 | -0.061 [-0.470, +0.361] |

Alle 132 Koeffizienten einschließlich Unsicherheiten, Priorrelationen und
aller übrigen Varianten stehen unverändert in [coefficients.csv](stage1/coefficients.csv).

## 3. Der latente Tesla-Rückgang hängt stark von der Niveau-SD ab

| Modell | 2025 minus 2024: Tesla/Rest-Niveau [95-%-Intervall] |
| --- | --- |
| M1 | -0.145 [-0.297, +0.010] |
| M2 | -0.142 [-0.297, +0.014] |
| M2_sd0.05 | -0.282 [-0.504, -0.051] |
| M2_sd0.10 | -0.517 [-0.839, -0.181] |
| M2_sd0.20 | -0.739 [-1.159, -0.303] |
| M2_portal | -0.144 [-0.292, +0.006] |
| M2_logit | -0.144 [-0.298, +0.012] |

Mit der primären SD 0,03 umfasst das Intervall null; mit 0,05/0,10/0,20
ist es vollständig negativ und der Median wird deutlich stärker negativ.
Das widerlegt den beobachteten Anteilsverlust nicht. Es zeigt, wie stark das
Modell ihn einer langsam driftenden Niveaukomponente oder dem übrigen Fehler
zuordnet. M0 erzwingt konstante relative Zustandsniveaus; sein Nullkontrast ist
eine Restriktion, kein empirischer Gegenbeweis.

Die vor dem Fit gewählte SD 0,03 erhält ihre Rolle. Es wird nicht nachträglich
auf eine Variante mit gewünschtem Vorzeichen/Intervall gewechselt. Die kleine
Wiederfindung mit vier künstlichen Fällen war dafür kein belastbarer
Validierungsnachweis: alle zwölf Policy-Intervalle enthielten null.

## 4. Prognosen: Marktverbesserung 2026, kein einheitlicher Fördergewinn

RMSE in Zulassungen; n = Zahl der jeweiligen Zielmonate:

| Jahr | h | n | M0 fest | M1 lokal | M2 + Förderung |
| --- | --- | --- | --- | --- | --- |
| 2025 | 1 | 12 | 7417.1 | 10016.4 | 7839.6 |
| 2025 | 3 | 10 | 8288.9 | 12164.7 | 8970.2 |
| 2026 | 1 | 9 | 15706.3 | 11479.8 | 8715.3 |
| 2026 | 3 | 9 | 17625.3 | 13449.0 | 9905.0 |

M2 schlägt M1 in allen vier Gruppen, verliert 2025 aber gegen M0.
2026 bleibt sein Vorteil gegenüber beiden Baselines auch nach Weglassen jedes
einzelnen Zielfehlers aus der Kennzahl bestehen. 2025/h=1 wechselt der Vergleich
gegen M0 beim Weglassen einzelner Fehler das Vorzeichen; bei h=3 bleibt M2
schlechter. H-P bleibt nach der vorab festgelegten Gesamtregel **offen**.
Kein Beobachtungsmonat wurde dafür aus einer Schätzung entfernt.

Die anderen vorab festgelegten Varianten liefern keinen universellen Sieger:
SD 0,20 verbessert 2026/h=1 den Markt-RMSE auf 6.527,8, verschlechtert h=3 aber
auf 16.249,5 gegenüber 9.905,0 im Primärmodell. Logit erreicht 2025 Markt-RMSE
5.400,7/6.625,9 und 2026 7.143,3/9.928,7. Das ist eine interessante vorab benannte
Robustheit, kein Anlass, nach Ergebnisansicht die Primärdefinition umzubenennen.
Bei Logit ist die Pkw-Zukunft an das saisonal-naive Szenario gebunden, ihre
eigene Prognoseunsicherheit wird nicht zusätzlich modelliert.

Tesla-Prognosen zeigen ein anderes Bild:

| Jahr | h | M0 RMSE | M1 RMSE | M2 RMSE | M2 MASE | M2 mittlere 95-%-Breite | M2 Trefferanteil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2025 | 1 | 4292.7 | 3357.6 | 3862.9 | 1.129 | 15244.0 | 1.000 |
| 2025 | 3 | 4730.2 | 3703.1 | 4315.0 | 1.267 | 16922.5 | 0.900 |
| 2026 | 1 | 2071.4 | 2290.0 | 2298.6 | 0.654 | 18541.0 | 0.889 |
| 2026 | 3 | 2069.8 | 2333.3 | 2213.0 | 0.614 | 18942.6 | 0.889 |

2025 ist M1 für Tesla besser als M2; 2026 ist M0 in beiden Horizonten besser
als M2. Die Marktverbesserung ist damit kein allgemeiner Tesla-Prognosegewinn.
MASE skaliert an saisonal-naiven **Trainingsfehlern**; es ist kein separat
getesteter saisonal-naiver Zukunftsforecast. Die sehr breiten Tesla-Intervalle
(2025/h=1 durchschnittlich 15.244 Zulassungen bei etwa 1.616 Monatszulassungen)
begrenzen den praktischen Planungsnutzen erheblich. 8/9 oder 9/9 Treffer bei
neun Zielmonaten validieren keine 95-%-Abdeckung. Dreimonatsfehler überlappen.

[Alle 128 Kennzahlenzeilen](stage1/metrics.csv), einschließlich VW/Rest, MAE,
MASE, Breite und Einzelmonatseinfluss; [alle 1.280 Prognosezeilen](stage1/predictions.csv).
M2 und Portal sind im 2025-Training strukturell identisch: kleine
Prognosedifferenzen dort entstehen durch unterschiedliche feste Monte-Carlo-Seeds,
nicht durch eine damals schon wirksame 2026-Förderregel.

## 5. Stationarität und Innovationen

| Reihe | Koordinate | n | ADF eff. n | ADF p | KPSS p |
| --- | --- | --- | --- | --- | --- |
| Zielniveau | Markt | 69 | 65 | 0.2961 | 0.0454 |
| Zielniveau | Tesla/Rest | 69 | 65 | 0.0457 | 0.0178 |
| Zielniveau | VW/Rest | 69 | 65 | 0.3160 | 0.0536 |
| Innovation | Markt | 57 | 53 | 0.0441 | >0.100 |
| Innovation | Tesla/Rest | 57 | 53 | 0.1296 | 0.0286 |
| Innovation | VW/Rest | 57 | 53 | 0.0101 | >0.100 |

ADF-Null: Einheitswurzel; KPSS-Null: Trendstationarität bei Zielniveaus,
Niveaustationarität bei Innovationen. Beide mit fest drei Lags; Innovationen
nach zwölf Monaten Diagnose-Burn-in. Rand-p-Werte sind als Grenzen markiert.
Die Tesla-Niveau-Tests widersprechen einander; Brüche und geringe Teststärke
lassen keine einfache Stationaritätsgeschichte zu.

Bei Tesla verwirft ADF die Einheitswurzel nicht, während KPSS
Niveaustationarität verwirft. Das ist mit verbleibender
Persistenz/Instabilität vereinbar und ein konkretes Spezifikationsproblem.
VW-Innovationen können stationär und dennoch stark autokorreliert sein:

| Koordinate | Ljung–Box p, Lag 3 | Holm 3 | Holm 6 | Holm 12 |
| --- | --- | --- | --- | --- |
| Markt | 0.030928 | 0.09278 | 0.09278 | 0.09278 |
| Tesla/Rest | 0.009430 | 0.01886 | 0.005733 | 0.01914 |
| VW/Rest | 0.000000 | 1.715e-10 | 3.413e-10 | 1.167e-09 |

Beim Markt sind die unadjustierten p-Werte teilweise klein, nach Holm aber
nicht unter 0,05. Tesla und insbesondere VW behalten deutliche Serialkorrelation.
Das sind bedingte Diagnosen am Voll-Trainingsmittel der Kovarianz, keine
kalibrierten Spezifikationstests oder historischen Echtzeitfilter.

Die Glättungssensitivität ist auch hier materiell:

| Modell | Tesla ADF p | Tesla KPSS p | Tesla min. Holm-LB p | VW min. Holm-LB p |
| --- | --- | --- | --- | --- |
| M2 | 0.1296 | 0.0286 | 0.005733 | 1.715e-10 |
| M2_sd0.05 | 0.0755 | 0.0713 | 0.1198 | 5.28e-07 |
| M2_sd0.10 | 0.0210 | >0.100 | 1 | 0.09867 |
| M2_sd0.20 | 0.0021 | >0.100 | 1 | 1 |

SD 0,10/0,20 schwächen diese Innovationsprobleme deutlich. Das ist kein
Freibrief: Die breite Variante verschlechtert gleichzeitig die Marktprognose
über drei Monate. Das Primärmodell ist trotz guter MCMC-Diagnosen kein ausreichend
validiertes operatives Tesla-Absatzmodell.

[ACF und Filter-/Glättungsvergleich](diagnostics/innovation_acf.png);
[alle Fensterdiagnosen](stage1/rolling_inference.json).
Die Filterkurve konditioniert auf Vollstichproben-R; die Glättung nutzt spätere
Beobachtungen. Keine der beiden wird als damals verfügbare Live-Schätzung ausgegeben.

## 6. Auffällige Monate, Streuung und beobachtete Ereignisse

| Koordinate | Monat | Standardisierte Innovation |
| --- | --- | --- |
| market coordinate | 2022-12 | 2.868 |
| market coordinate | 2022-01 | -2.738 |
| market coordinate | 2023-08 | 2.177 |
| log Tesla/Rest | 2026-07 | -2.970 |
| log Tesla/Rest | 2022-05 | -2.089 |
| log Tesla/Rest | 2025-10 | -2.081 |
| log VW/Rest | 2022-04 | -3.098 |
| log VW/Rest | 2022-03 | -3.041 |
| log VW/Rest | 2023-09 | -1.969 |

Dezember 2022 und August 2023 liegen vor dokumentierten Förderumstellungen;
die BAFA-Chronik nennt hohe August-Antragszahlen. Zeitliches Zusammentreffen
beweist keine vollständige Ursachenaufklärung und Registrierungen sind keine
Anträge. Die übrigen auffälligen Monate erhalten keine nachträglich erfundenen
Ereigniserklärungen oder neuen Dummies. Alle Beobachtungen bleiben erhalten.

Die mittlere standardisierte Tesla-Innovation beträgt 2025 −1,126 bei SD 0,425,
2026 Jan–Sep −0,245 bei SD 1,140. Beim Markt ändern sich Jahres-SDs von 1,499
(2022) über 0,609 (2024) auf 0,512 (2026, neun Monate). Das sind deskriptive
ungleiche Fenster, kein neu eingeführter Varianzbruchtest.
[Alle 120 Einträge der Top-5-Listen](diagnostics/largest_innovations.csv) und
[alle Jahresfenster](diagnostics/annual_innovation_variation.csv).

## 7. Besonders wichtige Grenze der latenten Marktgrafik

Für September 2026 beträgt `exp(mu)` im Primärmodell im Median 538.438,
95-%-Intervall [215.782; 1.276.463]. Tatsächlich beobachtet: BEV 88.599,
Pkw insgesamt 256.774. Die expliziten Förder- und Kalenderterme sind in dieser Baselinegrafik
entfernt. Insbesondere kumulierte negative Förderstufen und Trend kompensieren sich stark.
Diese algebraische Komponente ist **kein Marktpotenzial und kein belastbarer
„ohne Förderung“-Gegenverlauf**. Die Größe oberhalb des gesamten Pkw-Markts ist
ein Warnsignal für die strukturelle Interpretation, nicht eine behauptete
Nachfrageprognose. Die Grafik wird nicht beschönigt oder ausgeblendet.

## 8. Rechenprüfung, kleine Wiederfindung und Abschluss

Alle acht Vollstichprobenmodelle und ihre gemeinsamen Zustand-/Koeffizientenziehungen
haben die vorab festgelegten MC-Grenzen bestanden. Für R: höchstes R-hat 1,00260,
kleinste Bulk-ESS 3.785,65, Tail-ESS 1.771,42, keine Divergenzen.
168 Rolling-Auswertungen: 22 eigene NUTS-Fits und 146 zulässige Gewichtsupdates;
minimal akzeptierte Gewichts-ESS 4.057,09, maximaler akzeptierter Pareto-k 0,2440.
Alle acht marginalen ML-Referenzen wurden geschätzt; keine behauptete OLS-Parität.
Numerische Konvergenz löst die beschriebenen Identifikations-/Residualprobleme nicht.

Vor dem Freeze: 4 künstliche Fälle × 3 SDs, bekannter Förderkoeffizient −0,30.
Mittlere absolute Medianfehler: 0,165277 / 0,162991 / 0,161265 bei
SD 0,10 / 0,05 / 0,03. Alle zwölf Intervalle enthalten null.
Kein validierter MDE-/Power-/Coverage-Nachweis; keine echten Outcomes ersetzt.

Nach Sichtprüfung wurde ausschließlich die Breite der monatlichen Balken
korrigiert (explizite Tage statt impliziter Monate). Zwei Bilddateien wurden
neu gezeichnet; sämtliche 16 anderen Stage1-Payloads und alle diagnostischen
Payloads bleiben bytegleich. Ursprüngliche und korrigierte Hashes stehen im
[Manifest](stage1/manifest.json). Keine neue Modellschätzung, kein geänderter
Zahlenwert, keine geänderte Primärdefinition.

**Stufe 1 ist als begrenzte Studie abgeschlossen, nicht als Ursachenrangliste
oder produktionsreife Tesla-Prognose.** Preis-/Liefer-/Modellmixdaten und die
Trennung von Förderberechtigung nach Käufergruppen bleiben wissenschaftliche
offene Punkte. Stufe 2, weitere Treiber und eine neue Primärdefinition benötigen
einen bewusst neu festgelegten Vergleich; heute erfolgt keine automatische
Nachschätzung. Danach folgen ausschließlich die freigegebenen Aufräum- und
README-PRs.

Source: Kraftfahrt-Bundesamt, Flensburg, FZ10, own calculations;
Datenlizenz Deutschland – Namensnennung – Version 2.0.
