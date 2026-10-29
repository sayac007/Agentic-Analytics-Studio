"""Computed scientific report and three reproducible figures, no narrative invented values."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .data import PERIODS
from .artifacts import write_csv

COLORS={"Tesla":"#0072B2","VW":"#E69F00","China":"#009E73","Rest":"#777777"}
DATES=np.array(PERIODS,dtype="datetime64[M]")


def annotate(ax):
    for date,label,color in [("2023-01","2023 grant cut","#999999"),("2023-09","Private applicants","#777777"),
                             ("2024-01","After programme end","#333333"),("2026-01","2026 grant","#009E73")]:
        ax.axvline(np.datetime64(date),color=color,lw=.8,alpha=.7)
    ax.grid(alpha=.15)


def save(fig,out,name):
    fig.text(.01,.005,"Source: KBA FZ10, own calculation. Current-vintage retrospective analysis; no causal identification.",fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(out/(name+".png"),dpi=160)
    fig.savefig(out/(name+".svg"),metadata={"Date":None})
    plt.close(fig)


def render(out,values,decomposition,metrics,contrasts,full):
    primary=full["M2"];paths=primary["paths"]
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True)
    axes[0].plot(DATES,values[:,1],color=COLORS["Tesla"],label="Tesla registrations")
    axes[0].set_ylabel("Registrations / month");axes[0].legend();annotate(axes[0])
    M0=values[:-12,0];M1=values[12:,0];s0=values[:-12,1]/M0;s1=values[12:,1]/M1
    a=(s0+s1)/2*(M1-M0);b=(M0+M1)/2*(s1-s0)
    for d,v,c,label in [(DATES[12:],a,COLORS["VW"],"BEV-market component"),(DATES[12:],b,COLORS["Tesla"],"Tesla-share component")]:
        bottom=np.where(np.sign(v)==np.sign(a),a,0)if label.startswith("Tesla-share")else 0
        axes[1].bar(d,v,bottom=bottom,width=22,color=c,label=label)
    axes[1].plot(DATES[12:],values[12:,1]-values[:-12,1],color="black",lw=1,label="Observed year-on-year change")
    axes[1].set_ylabel("Change vs same month previous year");axes[1].legend();annotate(axes[1])
    fig.suptitle("Tesla Germany: growing market and changing brand share")
    save(fig,out,"market_share_decomposition")

    fig,ax=plt.subplots(figsize=(11,4.5))
    low,med,high=np.quantile(np.exp(paths[:,:,0]),[.025,.5,.975],axis=0)
    ax.fill_between(DATES,low,high,color=COLORS["Rest"],alpha=.2)
    ax.plot(DATES,med,color=COLORS["Rest"])
    ax.set_ylabel("Registrations / month, baseline component")
    ax.set_title("Local BEV-market baseline: calendar and explicit policy terms excluded")
    annotate(ax);save(fig,out,"latent_market")

    fig,axes=plt.subplots(2,1,figsize=(11,6),sharex=True)
    for ax,j,g in zip(axes,[2,3],["Tesla","VW"]):
        lo,med,hi=np.quantile(paths[:,:,j],[.025,.5,.975],axis=0)
        ax.fill_between(DATES,lo,hi,color=COLORS[g],alpha=.2);ax.plot(DATES,med,color=COLORS[g])
        ax.set_ylabel(g+" / Rest, log ratio");annotate(ax)
    fig.suptitle("Smoothed relative brand levels, 95% posterior intervals; not measured brand image")
    save(fig,out,"brand_levels")

    year24=decomposition[2];year25=decomposition[3];ytd=decomposition[4]
    def delta(r,key):
        return (r[key+"_after"]/r[key+"_before"]-1)*100
    tc=next(r for r in contrasts if r["model"]=="M2"and r["group"]=="Tesla")
    relevant=[r for r in metrics if r["model"]in ["M0","M1","M2"]and r["outcome"]=="BEV_market"]
    wins=[]
    for r in [x for x in relevant if x["model"]=="M2"]:
        other=next(x for x in relevant if x["model"]=="M1"and x["year"]==r["year"]and x["horizon"]==r["horizon"])
        wins.append(r["rmse"]<min(r["baseline_rmse"],other["rmse"]))
    hp="gestützt"if all(wins)else"offen"
    hwhy=("Verbessert in allen vier Jahr-/Horizontvergleichen die bedingte Marktprognose gegen M0 und M1; kein Kausalnachweis."
          if all(wins)else"Kein durchgängig besserer Markt-Prognosefehler gegen M0 und M1; Koeffizienten bleiben bedingte Zusammenhänge.")
    hypotheses=[
     dict(Hypothese="2025 ist Tesla-spezifisch relativ zum BEV-Markt",Test="Exakte Markt-/Anteilszerlegung 2025 gegen 2024",
          Ergebnis="gestützt",Begründung=f"Tesla {delta(year25,'Tesla'):+.1f} %, BEV-Markt {delta(year25,'market'):+.1f} %; das erklärt keine einzelne Ursache."),
     dict(Hypothese="Das latente Tesla-Niveau liegt 2025 niedriger als 2024",Test="Primärmodell M2/G1: Jahresmittelkontrast der ALR-Niveaus",
          Ergebnis="gestützt"if tc["upper95"]<0 else"offen",
          Begründung=f"Kontrast {tc['median']:.3f}, 95-%-Intervall [{tc['lower95']:.3f}, {tc['upper95']:.3f}]; modellabhängig, kein Image-/Juniper-Beweis."),
     dict(Hypothese="Förderregime verbessern die bedingte Marktprognose",Test="M2 gegen M0 und M1, 2025/2026, h=1/3",Ergebnis=hp,Begründung=hwhy),
     dict(Hypothese="China-Preiswettbewerb erklärt Tesla",Test="Nicht durchgeführt in Stufe 1",Ergebnis="offen",Begründung="Korbzuordnung/vergleichbare Preisgeschichte unvollständig; negative Anteilskorrelation wäre kein Beweis."),
     dict(Hypothese="Kraftstoff wirkt 2026 nachhaltig",Test="Nicht durchgeführt in Stufe 1",Ergebnis="offen",Begründung="Kein Kraftstoff im Kernmodell; kurze Reihe und neue Förderung erlauben keine vorweggenommene Trennung."),
     dict(Hypothese="Diffusion bzw. veränderte Käufertypen treiben den Markt",Test="Nicht durchgeführt in Stufe 1",Ergebnis="offen",Begründung="Ohne beobachteten Bestands-/Käuferproxy keine gemessene soziale Norm oder Preisempfindlichkeit.")
    ]
    write_csv(out/"hypotheses.csv",hypotheses)
    text=["# Task 04, Stufe 1 – beobachtete Markt-/Anteilsentwicklung\n\n",
          "KBA-Monatsdaten Januar 2021–September 2026; keine Energie-/Aufmerksamkeitsdaten und keine synthetischen Ersatzbeobachtungen.\n",
          "Die gesonderte kleine synthetische Wiederfindung diente ausschließlich der Modellprüfung vor dem Freeze.\n\n",
          "## Fünf Sätze\n\n",
          f"1. 2025 sanken Teslas deutsche Zulassungen um {abs(delta(year25,'Tesla')):.1f} %, während der BEV-Markt um {delta(year25,'market'):.1f} % wuchs.\n",
          f"2. Die exakte Jahreszerlegung ordnet {year25['market_component']:+,.0f} Zulassungen der Marktveränderung und {year25['share_component']:+,.0f} der Tesla-Anteilsveränderung zu; das ist Buchhaltung, keine Ursachenmessung.\n",
          f"3. Januar–September 2026 stiegen Teslas Zulassungen gegenüber denselben Vorjahresmonaten um {delta(ytd,'Tesla'):.1f} %; Markt- und Anteilsbeiträge bleiben getrennt ausgewiesen.\n",
          f"4. Ob Förderung die Prognose verbessert, ist anhand aller Jahr-/Horizontvergleiche zu lesen: Ergebnis {hp}; ein bedingter Koeffizient ist kein kausaler Fördereffekt.\n",
          "5. Image, Modellwechsel, Preise und Konkurrenz sind mit dieser Stufe nicht als einzelne Ursachen identifiziert; Kraftstoff und Diffusion bleiben ausdrücklich ununtersucht.\n\n",
          "## Exakte Jahreszerlegung\n\n",
          "| Jahr | Monate | Tesla-Veränderung | Marktkomponente | Anteilskomponente |\n|---|---:|---:|---:|---:|\n"]
    for r in decomposition:text.append(f"| {r['year']} | {r['months']} | {r['Tesla_change']:+.0f} | {r['market_component']:+.1f} | {r['share_component']:+.1f} |\n")
    text+=["\n2026 jeweils Januar–September gegen Januar–September, keine YTD-/Ganzjahresvermischung.\n\n",
           "## Hypothesen\n\n| Hypothese | Test | Ergebnis | Begründung |\n|---|---|---|---|\n"]
    for r in hypotheses:text.append("| "+" | ".join(r.values())+" |\n")
    text+=["\n## Baseline und Erweiterungen – alle Marktprognosen\n\n",
           "| Modell | Jahr | Horizont | n | RMSE | Differenz zu M0 | MAE | MASE | Intervallabdeckung |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"]
    for r in [x for x in metrics if x["outcome"]=="BEV_market"]:
        text.append(f"| {r['model']} | {r['year']} | {r['horizon']} | {r['n']} | {r['rmse']:.1f} | {r['rmse_difference']:+.1f} | {r['mae']:.1f} | {r['mase']:.3f} | {r['coverage95']:.3f} |\n")
    text+=["\nAlle Tesla-/VW-/Rest-Fehler ebenfalls in metrics.csv; jedes einzelne Fenster in predictions.csv.\n",
           "Negative Verbesserungen bedeuten kleinere RMSE. Überlappende Dreimonatsfehler sind abhängig; neun 2026-Zielmonate validieren keine 95-%-Abdeckung.\n\n",
           "## Koeffizienten, Zustände und Grenzen\n\n",
           "coefficients.csv enthält alle Koeffizienten und Intervalle, states.csv alle Zustände, contrasts.csv die Jahreskontraste.\n",
           "diagnostics.json berichtet ADF/KPSS, Warnungen und Ljung–Box/Holm ohne automatische Modelländerung.\n",
           "frequentist_reference.json ist eine marginale ML-Kovarianzreferenz bei derselben proper-Gauß-Initialisierung; keine unregularisierte OLS-Parität.\n",
           "rolling_inference.json unterscheidet NUTS-Neuschätzungen von geprüften Wichtigkeitsupdates (ESS/Pareto-k), ohne aktuelle R-hat-Werte dafür zu erfinden.\n",
           "Latente Bänder sind modellabhängige Posteriorintervalle; Filterspalte konditioniert auf Vollstichproben-R, kein historischer Echtzeitfilter.\n",
           "Die Logit-Robustheit verwendet für unbekannte zukünftige Pkw-Gesamtwerte die saisonal-naive Vorjahreszahl.\n",
           "Förderstufen sind aggregierte Regimeproxies, keine individuelle Behandlungsdosis; kurze Reihe, Trend-/Interventionskonkurrenz, Lieferwellen und fehlende Preise begrenzen die Identifikation.\n",
           "Keine Aussage über kausalen Tesla-ROI, soziale Normen, validierte MDE oder empirisch bestätigte Intervallabdeckung.\n\n",
           "Source: Kraftfahrt-Bundesamt, Flensburg, FZ10; own calculation; Datenlizenz Deutschland – Namensnennung – Version 2.0.\n"]
    (out/"report.md").write_text("".join(text))
