# Task 04, Stufe 1 – beobachtete Markt-/Anteilsentwicklung

KBA-Monatsdaten Januar 2021–September 2026; keine Energie-/Aufmerksamkeitsdaten und keine synthetischen Ersatzbeobachtungen.
Die gesonderte kleine synthetische Wiederfindung diente ausschließlich der Modellprüfung vor dem Freeze.

## Fünf Sätze

1. 2025 sanken Teslas deutsche Zulassungen um 48.4 %, während der BEV-Markt um 43.2 % wuchs.
2. Die exakte Jahreszerlegung ordnet +11,048 Zulassungen der Marktveränderung und -29,232 der Tesla-Anteilsveränderung zu; das ist Buchhaltung, keine Ursachenmessung.
3. Januar–September 2026 stiegen Teslas Zulassungen gegenüber denselben Vorjahresmonaten um 201.9 %; Markt- und Anteilsbeiträge bleiben getrennt ausgewiesen.
4. Ob Förderung die Prognose verbessert, ist anhand aller Jahr-/Horizontvergleiche zu lesen: Ergebnis offen; ein bedingter Koeffizient ist kein kausaler Fördereffekt.
5. Image, Modellwechsel, Preise und Konkurrenz sind mit dieser Stufe nicht als einzelne Ursachen identifiziert; Kraftstoff und Diffusion bleiben ausdrücklich ununtersucht.

## Exakte Jahreszerlegung

| Jahr | Monate | Tesla-Veränderung | Marktkomponente | Anteilskomponente |
|---|---:|---:|---:|---:|
| 2022 | 12 | +30249 | +14912.0 | +15337.0 |
| 2023 | 12 | -6278 | +7248.6 | -13526.6 |
| 2024 | 12 | -26111 | -15811.9 | -10299.1 |
| 2025 | 12 | -18184 | +11047.5 | -29231.5 |
| 2026 | 9 | +29965 | +12541.0 | +17424.0 |

2026 jeweils Januar–September gegen Januar–September, keine YTD-/Ganzjahresvermischung.

## Hypothesen

| Hypothese | Test | Ergebnis | Begründung |
|---|---|---|---|
| 2025 ist Tesla-spezifisch relativ zum BEV-Markt | Exakte Markt-/Anteilszerlegung 2025 gegen 2024 | gestützt | Tesla -48.4 %, BEV-Markt +43.2 %; das erklärt keine einzelne Ursache. |
| Das latente Tesla-Niveau liegt 2025 niedriger als 2024 | Primärmodell M2/G1: Jahresmittelkontrast der ALR-Niveaus | offen | Kontrast -0.142, 95-%-Intervall [-0.297, 0.014]; modellabhängig, kein Image-/Juniper-Beweis. |
| Förderregime verbessern die bedingte Marktprognose | M2 gegen M0 und M1, 2025/2026, h=1/3 | offen | Kein über Jahr/Horizont und Einzelmonatseinfluss stabiler Prognosevorteil gegen M0 und M1; Koeffizienten bleiben bedingte Zusammenhänge. |
| China-Preiswettbewerb erklärt Tesla | Nicht durchgeführt in Stufe 1 | offen | Korbzuordnung/vergleichbare Preisgeschichte unvollständig; negative Anteilskorrelation wäre kein Beweis. |
| Kraftstoff wirkt 2026 nachhaltig | Nicht durchgeführt in Stufe 1 | offen | Kein Kraftstoff im Kernmodell; kurze Reihe und neue Förderung erlauben keine vorweggenommene Trennung. |
| Diffusion bzw. veränderte Käufertypen treiben den Markt | Nicht durchgeführt in Stufe 1 | offen | Ohne beobachteten Bestands-/Käuferproxy keine gemessene soziale Norm oder Preisempfindlichkeit. |

## Baseline und Erweiterungen – alle Marktprognosen

| Modell | Jahr | Horizont | n | RMSE | Differenz zu M0 | MAE | MASE | Intervallabdeckung |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M2 | 2025 | 1 | 12 | 7839.6 | +422.5 | 6434.3 | 0.483 | 1.000 |
| M2 | 2025 | 3 | 10 | 8970.2 | +681.3 | 6830.7 | 0.513 | 1.000 |
| M2 | 2026 | 3 | 9 | 9905.0 | -7720.3 | 9005.7 | 0.659 | 1.000 |
| M2 | 2026 | 1 | 9 | 8715.3 | -6991.0 | 7054.6 | 0.501 | 1.000 |
| M0 | 2025 | 1 | 12 | 7417.1 | +0.0 | 5777.2 | 0.435 | 1.000 |
| M0 | 2025 | 3 | 10 | 8288.9 | +0.0 | 6620.8 | 0.497 | 1.000 |
| M0 | 2026 | 3 | 9 | 17625.3 | +0.0 | 15944.1 | 1.165 | 1.000 |
| M0 | 2026 | 1 | 9 | 15706.3 | +0.0 | 14100.9 | 1.010 | 1.000 |
| M1 | 2025 | 1 | 12 | 10016.4 | +2599.3 | 9103.4 | 0.682 | 1.000 |
| M1 | 2025 | 3 | 10 | 12164.7 | +3875.8 | 10205.7 | 0.763 | 0.900 |
| M1 | 2026 | 3 | 9 | 13449.0 | -4176.2 | 9932.8 | 0.718 | 1.000 |
| M1 | 2026 | 1 | 9 | 11479.8 | -4226.5 | 8851.1 | 0.623 | 1.000 |
| M2_sd0.05 | 2025 | 1 | 12 | 7939.5 | +522.4 | 6498.9 | 0.488 | 1.000 |
| M2_sd0.05 | 2025 | 3 | 10 | 9235.2 | +946.3 | 6925.9 | 0.520 | 1.000 |
| M2_sd0.05 | 2026 | 3 | 9 | 10571.6 | -7053.6 | 9726.3 | 0.713 | 1.000 |
| M2_sd0.05 | 2026 | 1 | 9 | 8700.7 | -7005.7 | 7065.4 | 0.503 | 1.000 |
| M2_sd0.10 | 2025 | 1 | 12 | 8439.9 | +1022.7 | 7153.2 | 0.537 | 1.000 |
| M2_sd0.10 | 2025 | 3 | 10 | 10065.6 | +1776.7 | 7705.8 | 0.579 | 1.000 |
| M2_sd0.10 | 2026 | 3 | 9 | 12389.5 | -5235.8 | 11243.9 | 0.827 | 1.000 |
| M2_sd0.10 | 2026 | 1 | 9 | 8056.6 | -7649.7 | 6686.7 | 0.480 | 1.000 |
| M2_sd0.20 | 2025 | 1 | 12 | 9184.5 | +1767.4 | 7298.2 | 0.547 | 1.000 |
| M2_sd0.20 | 2025 | 3 | 10 | 11273.4 | +2984.5 | 8790.6 | 0.660 | 1.000 |
| M2_sd0.20 | 2026 | 3 | 9 | 16249.5 | -1375.8 | 13647.1 | 1.004 | 1.000 |
| M2_sd0.20 | 2026 | 1 | 9 | 6527.8 | -9178.5 | 5562.9 | 0.400 | 1.000 |
| M2_portal | 2025 | 1 | 12 | 7847.4 | +430.3 | 6396.6 | 0.480 | 1.000 |
| M2_portal | 2025 | 3 | 10 | 8998.3 | +709.4 | 6899.9 | 0.518 | 1.000 |
| M2_portal | 2026 | 3 | 9 | 9680.6 | -7944.7 | 8985.0 | 0.657 | 1.000 |
| M2_portal | 2026 | 1 | 9 | 8943.9 | -6762.5 | 8092.7 | 0.576 | 1.000 |
| M2_logit | 2025 | 1 | 12 | 5400.7 | -2016.4 | 4068.3 | 0.304 | 1.000 |
| M2_logit | 2025 | 3 | 10 | 6625.9 | -1663.0 | 5668.4 | 0.424 | 1.000 |
| M2_logit | 2026 | 3 | 9 | 9928.7 | -7696.6 | 8530.8 | 0.623 | 1.000 |
| M2_logit | 2026 | 1 | 9 | 7143.3 | -8563.0 | 5719.2 | 0.413 | 1.000 |

Alle Tesla-/VW-/Rest-Fehler ebenfalls in metrics.csv; jedes einzelne Fenster in predictions.csv.
Negative Verbesserungen bedeuten kleinere RMSE. Überlappende Dreimonatsfehler sind abhängig; neun 2026-Zielmonate validieren keine 95-%-Abdeckung.

## Koeffizienten, Zustände und Grenzen

coefficients.csv enthält alle Koeffizienten und Intervalle, states.csv alle Zustände, contrasts.csv die Jahreskontraste.
diagnostics.json berichtet ADF/KPSS, Warnungen und Ljung–Box/Holm ohne automatische Modelländerung.
frequentist_reference.json ist eine marginale ML-Kovarianzreferenz bei derselben proper-Gauß-Initialisierung; keine unregularisierte OLS-Parität.
rolling_inference.json unterscheidet NUTS-Neuschätzungen von geprüften Wichtigkeitsupdates (ESS/Pareto-k), ohne aktuelle R-hat-Werte dafür zu erfinden.
Latente Bänder sind modellabhängige Posteriorintervalle; Filterspalte konditioniert auf Vollstichproben-R, kein historischer Echtzeitfilter.
Die Logit-Robustheit verwendet für unbekannte zukünftige Pkw-Gesamtwerte die saisonal-naive Vorjahreszahl.
VW bezeichnet die einzelne KBA-Marke, nicht den Volkswagenkonzern. Förderung wird primär nur auf den Markt geladen; unterschiedliche Markenberechtigung kann im Anteilsniveau verbleiben.
Förderstufen sind aggregierte Regimeproxies, keine individuelle Behandlungsdosis; kurze Reihe, Trend-/Interventionskonkurrenz, Lieferwellen und fehlende Preise begrenzen die Identifikation.
Keine Aussage über kausalen Tesla-ROI, soziale Normen, validierte MDE oder empirisch bestätigte Intervallabdeckung.

Source: Kraftfahrt-Bundesamt, Flensburg, FZ10; own calculation; Datenlizenz Deutschland – Namensnennung – Version 2.0.

## Kleine synthetische Wiederfindungsprüfung vor dem Freeze

Vier künstliche Fälle, kein empirischer Wirkungsnachweis und keine validierte Coverage/Power.
| Niveau-SD | Mittlerer absoluter Medianfehler | Wahrheit im 95-%-Intervall | Intervall schließt null aus | Konvergiert |
|---|---:|---:|---:|---:|
| 0.10 | 0.1653 | 4/4 | 0/4 | 4/4 |
| 0.05 | 0.1630 | 4/4 | 0/4 | 4/4 |
| 0.03 | 0.1613 | 4/4 | 0/4 | 4/4 |

Primäre Niveau-SD: 0.03, ausschließlich nach dem festgelegten künstlichen Prüfplan gewählt; keine Validierung der echten Zustandsvarianz.
Die Fehlerunterschiede sind klein und alle zwölf Intervalle enthalten auch null: keine überzeugende Wiederfindung eines von null getrennten Fördereffekts. Die Wahl legitimiert keine kausale Policy-Aussage.
