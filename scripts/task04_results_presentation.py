"""Present preserved Task04 outputs in German; no fitting, tuning or downloads.

Run with --check to verify the committed tables, figures and their source hashes.
Only the marked README section and results/task04/presentation may be written.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/aas-task04-presentation-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/aas-task04-presentation-cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FuncFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/task04/stage1"
OUTPUT = ROOT / "results/task04/presentation"
BEGIN = "<!-- BEGIN TASK04 COMPUTED RESULTS -->"
END = "<!-- END TASK04 COMPUTED RESULTS -->"
MODELS = ("M0", "M1", "M2", "M2_sd0.05", "M2_sd0.10", "M2_sd0.20", "M2_portal", "M2_logit")
PAIRS = ((2025, 1), (2025, 3), (2026, 1), (2026, 3))
BLUE, GOLD = "#0072B2", "#E69F00"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def number(value, digits=1, signed=False):
    text = format(float(value), ("+" if signed else "") + f",.{digits}f")
    return text.translate(str.maketrans({",": ".", ".": ",", "-": "−"}))


def table(headers, rows):
    def line(row):
        return "| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |"
    return "\n".join([line(headers), line(["---"] * len(headers)), *[line(r) for r in rows]])


def interval(row, digits=3, mark=False):
    text = (f"{number(row['median'], digits, True)} "
            f"[{number(row['lower95'], digits, True)}; {number(row['upper95'], digits, True)}]")
    return text + (" **†**" if mark and excludes_zero(row) else "")


def excludes_zero(row):
    return float(row["lower95"]) > 0 or float(row["upper95"]) < 0


def load():
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    # Every original output and every bound public input stays immutable.
    for name, expected in manifest["files"].items():
        if sha((SOURCE / name).read_bytes()) != expected:
            raise ValueError("Original result hash mismatch: " + name)
    for name, expected in manifest["input_hashes"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Original input hash mismatch: " + name)
    names = ("coefficients.csv", "metrics.csv", "decomposition.csv", "contrasts.csv", "predictions.csv")
    data = {name: list(csv.DictReader((SOURCE / name).open(newline=""))) for name in names}
    c, metrics, predictions = data["coefficients.csv"], data["metrics.csv"], data["predictions.csv"]
    if len(c) != 132 or len(metrics) != 128 or len(predictions) != 1280:
        raise ValueError("Incomplete preserved study")
    if {r["model"] for r in c} != set(MODELS):
        raise ValueError("Unexpected model family")
    grouped = defaultdict(list)
    for p in predictions:
        key = (p["model"], p["outcome"], int(p["year"]), int(p["horizon"]))
        if not math.isclose(float(p["error"]), float(p["prediction_mean"]) - float(p["actual"]), abs_tol=1e-8):
            raise ValueError("Prediction/error disagreement")
        grouped[key].append(p)
    seen = set()
    for m in metrics:
        key = (m["model"], m["outcome"], int(m["year"]), int(m["horizon"]))
        ps = grouped[key]
        if key in seen or len(ps) != int(m["n"]) or len({p["target"] for p in ps}) != len(ps):
            raise ValueError("Invalid comparison mask")
        seen.add(key)
        rmse = math.sqrt(sum(float(p["error"]) ** 2 for p in ps) / len(ps))
        if not math.isclose(rmse, float(m["rmse"]), rel_tol=1e-12):
            raise ValueError("Saved RMSE does not match saved prediction errors")
    masks = defaultdict(set)
    for (model, outcome, year, h), ps in grouped.items():
        masks[(outcome, year, h)].add(tuple(sorted(p["target"] for p in ps)))
    if any(len(x) != 1 for x in masks.values()) or len(seen) != len(grouped):
        raise ValueError("Models do not use identical forecast targets")
    data["diagnostics"] = json.loads((SOURCE / "diagnostics.json").read_text())
    data["audit"] = json.loads((ROOT / "data/task04_regimes/data_audit.json").read_text())
    data["manifest"] = manifest
    data["coef"] = {(r["model"], r["term"]): r for r in c}
    data["metric"] = {(r["model"], r["outcome"], int(r["year"]), int(r["horizon"])): r for r in metrics}
    return data


def rmse_table(data, outcome):
    get = data["metric"]
    return table(["Modell", "2025 · h=1", "2025 · h=3", "2026 · h=1", "2026 · h=3"],
                 [[m, *[number(get[(m, outcome, y, h)]["rmse"]) for y, h in PAIRS]] for m in MODELS])


def diagnostic_p(result, test):
    p = result[test]["p"]
    if test == "kpss" and p == .1 and any("greater" in w for w in result["warnings"]):
        return ">0,1000"
    if test == "kpss" and p == .01 and any("smaller" in w for w in result["warnings"]):
        return "<0,0100"
    return number(p, 4)


def tables(data):
    c, metrics = data["coef"], data["metric"]
    annual = []
    for r in data["decomposition.csv"]:
        annual.append([r["year"] + (" Jan–Sep" if r["months"] == "9" else ""),
                       number(r["Tesla_after"], 0),
                       number(100 * (float(r["Tesla_after"]) / float(r["Tesla_before"]) - 1), 1, True) + " %",
                       number(100 * (float(r["market_after"]) / float(r["market_before"]) - 1), 1, True) + " %",
                       number(100 * float(r["share_after"]), 2) + " %",
                       *[number(r[k], 0, True) for k in ("market_component", "share_component", "Tesla_change")]])
    specs = [
        ["M0", "Fester Markttrend; konstante relative Markenniveaus", "0", "Keine"],
        ["M1", "Lokaler Markttrend und relative Markenniveaus", "0,03", "Keine"],
        ["M2 **primär**", "M1 + Förderstufen und Übergangspulse", "0,03", "Berechtigung ab Januar 2026"],
        ["M2_sd0.05", "M2; beweglichere Zustände", "0,05", "Wie M2"],
        ["M2_sd0.10", "M2; beweglichere Zustände", "0,10", "Wie M2"],
        ["M2_sd0.20", "M2; beweglichste Zustände", "0,20", "Wie M2"],
        ["M2_portal", "M2; alternativer Beginn der Förderung 2026", "0,03", "Portalstart Mai statt Januar 2026"],
        ["M2_logit", "M2; Logit(BEV/Pkw) statt log(BEV)", "0,03", "Wie M2; saisonal-naiver Pkw-Prognosenenner"],
    ]
    calendar = []
    for m in MODELS:
        calendar.append([m, interval(c[(m, "Tesla:quarter_end")], mark=True),
                         interval(c[(m, "market:quarter_end")], mark=True),
                         interval(c[(m, "market:national_weekdays")], 4, mark=True),
                         interval(c[(m, "market:sin_12")], mark=True),
                         str(sum(excludes_zero(r) for r in data["coefficients.csv"] if r["model"] == m))])
    policy = []
    for m in MODELS[2:]:
        policy.append([m, *[interval(c[(m, "market:" + term)], mark=True) for term in
                           ("grant_cut_2023_01", "business_end_2023_09", "post_end_2024_01", "grant_2026_01")]])
    delta = []
    for outcome in ("BEV_market", "Tesla"):
        for y, h in PAIRS:
            row = metrics[("M2", outcome, y, h)]
            cells = ["BEV-Markt" if outcome == "BEV_market" else outcome, y, h, row["n"]]
            for base in ("M0", "M1"):
                old = float(metrics[(base, outcome, y, h)]["rmse"])
                diff = float(row["rmse"]) - old
                cells.append(f"{number(diff, 1, True)} ({number(100 * diff / old, 1, True)} %)")
            delta.append(cells)
    contrasts = [[r["model"], interval(r),
                  "Fest auf null gesetzt" if r["model"] == "M0" else
                  "Negativ, Intervall ohne null" if excludes_zero(r) else "Intervall enthält null"]
                 for r in data["contrasts.csv"] if r["group"] == "Tesla"]
    diag = []
    for m in MODELS:
        d = data["diagnostics"][m]
        t = d["innovations"]["1"]
        lb = min(x["p_holm"] for x in t["ljung_box"])
        vw = min(x["p_holm"] for x in d["innovations"]["2"]["ljung_box"])
        diag.append([m, diagnostic_p(t, "adf"), diagnostic_p(t, "kpss"),
                     f"{lb:.4g}".replace(".", ","), f"{vw:.4g}".replace(".", ",")])
    sources = "Quelle: gespeicherte KBA-FZ10-Auswertung vom 29.10.2026; eigene Darstellung, keine Neuschätzung."
    return f"""## 1. Was sich tatsächlich verändert hat

{table(['Vergleich zum Vorjahr', 'Tesla-Zulassungen', 'Tesla Δ', 'BEV-Markt Δ', 'Tesla-BEV-Anteil', 'Marktkomponente', 'Anteilskomponente', 'Tesla Δ absolut'], annual)}

Alle Jahre vollständig außer **2026: Januar–September gegen Januar–September 2025**.
2025: Tesla 19.390 statt 37.574; BEV-Markt 545.142 statt 380.609.
Teslas BEV-Anteil fällt von 9,87 % auf 3,56 %. Der wachsende Markt kompensiert
rechnerisch einen Teil des Anteilsverlusts. Bereits 2023 sinkt Teslas Anteil.
2026 steigen sowohl der Markt als auch Teslas Anteil gegenüber dem niedrigen Vorjahr.

![Tesla in Deutschland: jährliche Markt- und Anteilskomponenten](results/task04/presentation/annual_market_share.png)

{sources} Die symmetrische Zerlegung addiert sich exakt vor Rundung:
`ΔTesla = Mittel(Anteil) × ΔMarkt + Mittel(Markt) × ΔAnteil`.
Sie ordnet Veränderungen rechnerisch zu und identifiziert keine Ursachen.
Die Bildunterschriften vermeiden deshalb die unbewiesene Aussage, ein einzelnes
Förderereignis habe den gesamten Marktrückgang verursacht.

![Monatliche Tesla-Zulassungen und Markt-/Anteilszerlegung](results/task04/stage1/market_share_decomposition.png)

Quelle: Kraftfahrt-Bundesamt, FZ10, eigene Berechnung. Politikmarkierungen sind
Kontext; der global berichtete Model-Y-Wechsel in Q1 2025 ist kein exakt datiertes
deutsches Lieferereignis. Verwaltungszählwerte erhalten keine erfundenen Stichprobenintervalle.

## 2. Was die acht Zustandsraummodelle prüfen

{table(['Modell', 'Spezifikation', 'Monatliche Niveau-SD', 'Förderkodierung / Besonderheit'], specs)}

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

{table(['Modell', 'Quartalsende Tesla/Rest', 'Quartalsende Markt', 'Nationale Wochentage Markt', 'Sinus-Saison Markt', 'Koeffizienten mit † insgesamt'], calendar)}

**Stabilster gemessener Zusammenhang: Tesla-Quartalsende, positiv in allen acht
Varianten.** Das ist mit Liefer-/Zulassungswellen vereinbar. Der primäre Wert
{interval(c[('M2','Tesla:quarter_end')])} steht in Log-Verhältniseinheiten und
ist keine pauschale prozentuale Tesla-Absatzwirkung. VW-Quartalsende, sämtliche
VW-Kalenderterme, Tesla-Sinus/Kosinus/Wochentage und Markt-Kosinus enthalten in
allen Varianten null. Der Markt-Wochentagszusammenhang erscheint erst bei den
größeren Niveau-SDs; die negative Markt-Sinuskomponente nur im Logit-Zweig.

### Staatliche Förderung: Median [95-%-Posteriorintervall]

{table(['Modell', 'Kürzung Januar 2023', 'Ende gewerbliche Berechtigung September 2023', 'Nach Förderende: Januar 2024', 'Programm 2026'], policy)}

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
Varianten null; primär {interval(c[('M2','market:transition_2023_12')])} bzw.
{interval(c[('M2','market:transition_2024_01')])}.

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

{rmse_table(data, 'BEV_market')}

### Tesla

{rmse_table(data, 'Tesla')}

![RMSE aller acht Modelle für Markt und Tesla, einschließlich Verschlechterungen](results/task04/presentation/rmse_comparison.png)

{sources} Jede Zelle zeigt RMSE und prozentuale Änderung gegen M0 auf denselben
Zielmonaten; Blau = kleinerer Fehler, Orange = größerer Fehler. Farben sind keine
Signifikanztests. Eine gemeinsame Skala begrenzt die Farbsättigung bei ±60 %;
Zahlenwerte werden nicht begrenzt.

### Was bringt die Förderspezifikation M2 gegenüber den Baselines?

{table(['Ziel', 'Jahr', 'h', 'n', 'RMSE M2 − M0 (relativ)', 'RMSE M2 − M1 (relativ)'], delta)}

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

{rmse_table(data, 'VW')}

**Rest des BEV-Markts:**

{rmse_table(data, 'Rest')}

Auch bei VW ist M0 2026 besser als sämtliche dynamischen Varianten.
Rest ist eine rechnerische Restgruppe, kein gemessener China-Korb.

</details>

Das sind retrospektive Backtests mit heutigem Quellstand, keine historisch
rekonstruierten Echtzeitprognosen. Zukünftige Förderregeln werden nur verwendet,
soweit am Prognoseursprung bekannt. Breite Intervalle begrenzen den Nutzen:
für Tesla M2 2025/h=1 durchschnittlich **{number(metrics[('M2','Tesla',2025,1)]['mean_interval_width'])}**
Zulassungen Intervallbreite bei ungefähr 1.616 beobachteten Zulassungen im Monat.
Der Trefferanteil von {number(100*float(metrics[('M2','Tesla',2025,1)]['coverage95']),1)} %
validiert angesichts zwölf Zielmonaten und breiter Bänder keine 95-%-Abdeckung.
[Alle 128 Kennzahlenzeilen](results/task04/stage1/metrics.csv) einschließlich
MAE, MASE und Intervallbreiten; [1.280 Prognosezeilen](results/task04/stage1/predictions.csv).

## 5. Wie robust ist das latente Tesla-Niveau?

{table(['Modell', 'Jahresmittel 2025 − 2024: Tesla/Rest-Niveau [95-%-Intervall]', 'Einordnung'], contrasts)}

![Robuster Quartalsendzusammenhang und priorabhängiger Tesla-Niveaukontrast](results/task04/presentation/tesla_robustness.png)

{sources} Im Primärmodell umfasst der Niveaukontrast null; erst die beweglicheren
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

{table(['Modell', 'Tesla ADF p', 'Tesla KPSS p', 'Tesla min. Holm-Ljung–Box p', 'VW min. Holm-Ljung–Box p'], diag)}

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
"""


def details(data):
    text = """# Task 04: vollständige Tabellen zur Ergebnis-README

Darstellung vom 30.10.2026, ausschließlich aus den archivierten Ergebnissen vom
29.10.2026. Keine Modellschätzung oder neue Hypothesenprüfung. Zahlen sind hier
gerundet; Original-CSV/JSON behalten die gesamte numerische Präzision.

## Alle 132 Koeffizienten

Posterior-SD ist die Streuung des bedingten Posteriors, kein HAC-Standardfehler.
† = punktweises 95-%-Posteriorintervall ohne null, ohne Kausal- oder
frequentistischen Signifikanzanspruch. Alle nicht markierten Koeffizienten
bleiben sichtbar. Marktterme in Log-Zählwerten, im Logit-Zweig in Log-Odds;
Tesla/VW in Log-Verhältnissen zur Restgruppe. Im Portalzweig gilt der kanonische
Term `grant_2026_01` ab Mai, nicht Januar 2026.

"""
    for m in MODELS:
        rows = [r for r in data["coefficients.csv"] if r["model"] == m]
        text += f"### {m}\n\n" + table(["Term", "Median [95-%-Intervall]", "Posterior-SD", "Monate mit aktivem Term"],
                 [[r["term"], interval(r, 4, mark=True), number(r["posterior_sd"], 4), r["observed_nonzero_months"]] for r in rows]) + "\n\n"
    text += "## Alle 128 Prognosevergleiche\n\nRMSE/MAE/Breite in Zulassungen. MASE skaliert an saisonal-naiven Trainingsfehlern; kein separat getesteter naiver Zukunftsforecast. Trefferanteile sind deskriptiv. Negative RMSE-Differenz = Verbesserung.\n\n"
    for m in MODELS:
        rows = [r for r in data["metrics.csv"] if r["model"] == m]
        text += f"### {m}\n\n" + table(["Ziel", "Jahr", "h", "n", "RMSE", "Δ M0", "Δ M1", "MAE", "MASE", "95-%-Treffer", "Mittl. Intervallbreite"],
                 [[r["outcome"], r["year"], r["horizon"], r["n"], number(r["rmse"]), number(r["rmse_difference"], 1, True),
                   number(r["rmse_difference_vs_M1"], 1, True), number(r["mae"]), number(r["mase"], 3),
                   number(100*float(r["coverage95"]), 1)+" %", number(r["mean_interval_width"])] for r in rows]) + "\n\n"
    text += "## ADF, KPSS und Ljung–Box: alle acht Modelle\n\nADF/KPSS mit fest drei Lags; Niveaus mit Trend, Innovationen mit Konstante nach zwölf Monaten Burn-in. Holm innerhalb der drei Ljung–Box-Lags pro Reihe. Es werden keine Diagnoselags ausgewählt.\n\n"
    for m in MODELS:
        rows = []
        for kind in ("levels", "innovations"):
            for j, group in enumerate(("Markt", "Tesla/Rest", "VW/Rest")):
                r = data["diagnostics"][m][kind][str(j)]
                lb = r.get("ljung_box", [])
                rows.append([kind + " " + group, r["n"], r["adf"]["effective_n"], diagnostic_p(r, "adf"), diagnostic_p(r, "kpss"),
                             *[f"{v['p']:.6g} / {v['p_holm']:.6g}".replace(".", ",") for v in lb]] + (["—"]*3 if not lb else []))
        text += f"### {m}\n\n" + table(["Reihe", "n", "ADF eff. n", "ADF p", "KPSS p", "LB 3 roh / Holm", "LB 6 roh / Holm", "LB 12 roh / Holm"], rows) + "\n\n"
    text += "Originale: [Koeffizienten](../stage1/coefficients.csv), [Kennzahlen](../stage1/metrics.csv), [Diagnostik](../stage1/diagnostics.json), [Manifest](../stage1/manifest.json). [Zur README](../../../README.md).\n"
    return text


def figures(data):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "task04-german-results-v1"})
    files = {}

    def save(fig, name):
        for ext in ("png", "svg"):
            buf = io.BytesIO()
            fig.savefig(buf, format=ext, dpi=160, metadata={"Software": "Matplotlib"} if ext == "png" else {"Date": None})
            files[f"{name}.{ext}"] = buf.getvalue()
        plt.close(fig)

    r = data["decomposition.csv"]
    market = np.array([float(x["market_component"]) for x in r])
    share = np.array([float(x["share_component"]) for x in r])
    total = np.array([float(x["Tesla_change"]) for x in r])
    x = np.arange(len(r))
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(left=.11, right=.97, top=.77, bottom=.20)
    fig.text(.055, .94, "Tesla in Deutschland: Markt oder Marke?", fontsize=24, weight="bold")
    fig.text(.055, .89, "Veränderung gegenüber Vorjahr, rechnerisch zerlegt in Markt- und Anteilskomponente", fontsize=12, color="#444444")
    ax.bar(x, market, .52, color=GOLD, label="Marktkomponente (BEV-Markt)")
    ax.bar(x, share, .52, bottom=np.where(market*share > 0, market, 0), color=BLUE, label="Anteilskomponente (Tesla-BEV-Anteil)")
    ax.scatter(x, total, color="black", marker="D", s=65, zorder=4, label="Veränderung insgesamt")
    for i, value in enumerate(total):
        ax.annotate(number(value, 0, True), (i, value), xytext=(12, 0), textcoords="offset points", fontsize=12, weight="bold", va="center")
    ax.axhline(0, color="black", lw=.8)
    ax.set_ylim(-41000, 40500)
    ax.set_xlim(-.5, 4.85)
    ax.set_xticks(x, ["2022", "2023", "2024", "2025", "2026\nJan–Sep"])
    ax.set_ylabel("Veränderung der Tesla-Neuzulassungen")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: number(value, 0, True)))
    ax.grid(axis="y", alpha=.25); ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, 1.19), ncol=1, frameon=False, fontsize=10)
    fig.text(.055, .09, "Quelle: Kraftfahrt-Bundesamt, FZ10; eigene Berechnung, dl-de/by-2-0. 2026: gleiche neun Vorjahresmonate.", fontsize=9, color="#555555")
    fig.text(.055, .055, "Exakte symmetrische Rechenzerlegung vor Rundung; keine kausale Ursachen- oder Förderwirkung.", fontsize=9, color="#555555")
    save(fig, "annual_market_share")

    fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharey=True)
    fig.subplots_adjust(left=.13, right=.94, top=.78, bottom=.19, wspace=.12)
    for ax, outcome, title in zip(axes, ("BEV_market", "Tesla"), ("BEV-Markt", "Tesla")):
        values = np.array([[float(data["metric"][(m, outcome, y, h)]["rmse"]) for y, h in PAIRS] for m in MODELS])
        delta = 100 * (values / values[0] - 1)
        cmap = LinearSegmentedColormap.from_list("rmse", [BLUE, "#FAFAFA", "#B25D00"])
        ax.imshow(delta, cmap=cmap, norm=TwoSlopeNorm(vmin=-60, vcenter=0, vmax=60), aspect="auto")
        for i in range(8):
            for j in range(4):
                ax.text(j, i, number(values[i,j], 0)+"\n"+number(delta[i,j], 1, True)+" %", ha="center", va="center", fontsize=10,
                        color="white" if abs(delta[i,j]) > 35 else "black")
        ax.set_title(title, fontsize=15, pad=14)
        ax.set_xticks(range(4), ["2025\nh=1", "2025\nh=3", "2026\nh=1", "2026\nh=3"])
        ax.set_yticks(range(8), [m + (" *" if m == "M2" else "") for m in MODELS])
    fig.suptitle("Alle acht Modelle: Prognosefehler und Änderung gegenüber M0", fontsize=19, y=.95)
    fig.text(.13, .87, "Je Zelle: RMSE in Zulassungen / relative Änderung. Weniger Fehler: Blau; mehr Fehler: Orange.", fontsize=10)
    fig.text(.13, .09, "Quelle: gespeicherte KBA-FZ10-Backtests. * Primärmodell. 2026: Januar–September; identische Zielmonate.", fontsize=9)
    fig.text(.13, .055, "Farbskala bei ±60 % gesättigt; Zahlen unverändert. Retrospektiv, keine Kausal- oder Signifikanzbewertung.", fontsize=9)
    save(fig, "rmse_comparison")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    fig.subplots_adjust(left=.15, right=.97, top=.77, bottom=.2, wspace=.25)
    contrasts = {r["model"]: r for r in data["contrasts.csv"] if r["group"] == "Tesla"}
    for ax, title, getter in ((axes[0], "Tesla-Quartalsende", lambda m: data["coef"][(m, "Tesla:quarter_end")]),
                              (axes[1], "Latentes Tesla-Niveau: 2025 minus 2024", lambda m: contrasts[m])):
        for i, m in enumerate(MODELS):
            row = getter(m); med, lo, hi = (float(row[k]) for k in ("median", "lower95", "upper95"))
            ax.errorbar(med, i, xerr=[[med-lo], [hi-med]], fmt="D" if m == "M2" else "o", color=BLUE if excludes_zero(row) else "#777777", capsize=3, ms=6)
        ax.axvline(0, color="black", lw=.8)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Log-Verhältniseinheiten Tesla/Rest")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, pos: number(value, 1)))
        ax.set_yticks(range(8), MODELS); ax.grid(axis="x", alpha=.2)
    axes[0].invert_yaxis()
    fig.suptitle("Robuster Kalenderzusammenhang, modellabhängiger Niveaukontrast", fontsize=18, y=.95)
    fig.text(.15, .86, "Median und punktweises bedingtes 95-%-Posteriorintervall; Raute = Primärmodell M2.", fontsize=10)
    fig.text(.08, .09, "Quelle: gespeicherte KBA-FZ10-Auswertung. Blau: Intervall ohne null; Grau: enthält null. Keine Kausalwirkung.", fontsize=9)
    fig.text(.08, .055, "M0 rechts: Nullkontrast konstruktionsbedingt festgesetzt. Die primäre Niveau-SD 0,03 wird nicht nachträglich geändert.", fontsize=9)
    save(fig, "tesla_robustness")
    return files


def run(check=False):
    data = load()
    readme = ROOT / "README.md"
    text = readme.read_text()
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Expected exactly one presentation section")
    before, tail = text.split(BEGIN)
    _, after = tail.split(END)
    computed = BEGIN + "\n\n" + tables(data).strip() + "\n\n" + END
    expected_readme = before + computed + after
    outputs = {"DETAILS.md": details(data).encode(), **figures(data)}
    source_paths = [SOURCE / name for name in ("manifest.json", "coefficients.csv", "metrics.csv", "decomposition.csv", "contrasts.csv", "predictions.csv", "diagnostics.json")]
    source_paths += [ROOT / "data/task04_regimes/data_audit.json", Path(__file__)]
    manifest = {
        "scope": "German presentation only; no model fits, changed protocols, new observations or new significance tests",
        "original_execution_commit": data["manifest"]["execution_commit"],
        "protocol": data["manifest"]["protocol"]["version"],
        "source_sha256": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in source_paths},
        "computed_readme_section_sha256": sha(computed.encode()),
        "matplotlib": matplotlib.__version__, "numpy": np.__version__,
        "files": {name: sha(content) for name, content in outputs.items()},
    }
    outputs["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if check:
        if text != expected_readme:
            raise ValueError("README tables/narrative differ from saved-output presentation")
        for name, content in outputs.items():
            if not (OUTPUT / name).exists() or (OUTPUT / name).read_bytes() != content:
                raise ValueError("Presentation differs: " + name)
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        readme.write_text(expected_readme)
        for name, content in outputs.items():
            (OUTPUT / name).write_bytes(content)
    nonzero = sum(excludes_zero(r) for r in data["coefficients.csv"])
    print("Verified" if check else "Presented", f"132 coefficients, all {nonzero} intervals excluding zero, 128 RMSE rows recomputed from 1280 saved predictions; no fits.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
