"""Read-only supplementary ACF/outlier/variance diagnostics; never fit or tune."""
import argparse
import csv
import json
import os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR","/tmp/aas-task04-review-mpl")
os.environ.setdefault("XDG_CACHE_HOME","/tmp/aas-task04-review-cache")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf
from regimes.data import PERIODS,read_observed,observed_coordinates,system,sha,ROOT
from regimes.kalman import filter_numpy
from regimes.artifacts import write_json,write_csv
from regimes.verify import verify

LABELS=("market coordinate","log Tesla/Rest","log VW/Rest")


def summarize(z):
    """Fixed twelve-month burn-in; all remaining observations retained."""
    x=np.asarray(z,dtype=float)[12:]
    if x.shape!=(57,3)or not np.isfinite(x).all()or np.any(np.ptp(x,axis=0)==0):
        raise ValueError("Expected 57 finite post-burn-in innovations per coordinate")
    correlations=[];outliers=[];variances=[]
    for j,label in enumerate(LABELS):
        a=acf(x[:,j],nlags=12,fft=False,adjusted=False)
        correlations += [dict(series=label,lag=k,acf=float(a[k]),n=57)for k in range(1,13)]
        order=np.argsort(-np.abs(x[:,j]),kind="stable")[:5]
        outliers += [dict(series=label,rank=r+1,period=PERIODS[12+i],
                          standardized_innovation=float(x[i,j]),
                          meaning="largest absolute post-burn-in innovations; descriptive, no removal")
                     for r,i in enumerate(order)]
        for year in range(2022,2027):
            selected=x[[p.startswith(str(year))for p in PERIODS[12:]],j]
            variances.append(dict(series=label,year=year,n=len(selected),
                                  mean=float(selected.mean()),sd=float(selected.std(ddof=1)),
                                  rms=float(np.sqrt(np.mean(selected**2))),
                                  meaning="descriptive unequal annual windows, not a calibrated variance-change test"))
    return correlations,outliers,variances


def run(source,output):
    source=Path(source);out=Path(output)
    verify(source)
    m=json.loads((source/"manifest.json").read_text())
    for name in ("regimes/data.py","regimes/kalman.py"):
        if sha(ROOT/name)!=m["implementation_sha256"][name]:
            raise ValueError("Diagnostic reconstruction code differs from estimated model")
    d=json.loads((source/"diagnostics.json").read_text())
    _,values,_=read_observed()
    out.mkdir(parents=True,exist_ok=False)
    all_acf=[];all_outliers=[];all_variances=[];innovations=[];covariates=[]
    with (source/"states.csv").open(newline="")as fp:
        states=list(csv.DictReader(fp))
    fig,axes=plt.subplots(3,2,figsize=(14,8),sharex="col")
    for v in m["models"]:
        y=observed_coordinates(values,v["logit"])
        S=system(v["model"],v["sd"],69,portal=v["portal"],logit_market=v["logit"])
        R=np.array(d[v["id"]]["observation_covariance_posterior_mean"])
        _,_,_,_,z=filter_numpy(y,*S[:5],R)
        a,o,var=summarize(z)
        for rows,target in ((a,all_acf),(o,all_outliers),(var,all_variances)):
            target.extend([dict(model=v["id"],**r)for r in rows])
        for t in range(12,69):
            for j,label in enumerate(LABELS):
                innovations.append(dict(model=v["id"],period=PERIODS[t],series=label,
                                        standardized_innovation=float(z[t,j])))
        # Explicit paths include intervening months, not only scored targets.
        for n in range(48,69):
            H,_,_,_,_,names=system(v["model"],v["sd"],n,portal=v["portal"],logit_market=v["logit"])
            for t in range(n,n+(3 if n+3<=69 else 1)):
                for j,term in enumerate(names):
                    coordinate=0 if term.startswith("market:")else 1 if term.startswith("Tesla:")else 2
                    covariates.append(dict(model=v["id"],origin=PERIODS[n-1],ntrain=n,
                                           target=PERIODS[t],step=t-n+1,term=term,
                                           value=float(H[t,coordinate,4+j]),
                                           interpretation="fixed design known by origin; working days centred using training only"))
        if v["id"]=="M2":
            for j in range(3):
                ax=axes[j,0]
                rows=a[j*12:(j+1)*12]
                ax.bar(range(1,13),[r["acf"]for r in rows],color="#0072B2")
                ax.axhline(0,color="black",lw=.8)
                ax.set_ylabel(LABELS[j]+"\ninnovation ACF")
                ax.set_ylim(-1,1);ax.grid(alpha=.15)
                state=("market_level","Tesla_ALR_level","VW_ALR_level")[j]
                rs=[r for r in states if r["model"]=="M2"and r["state"]==state]
                ax=axes[j,1];dates=np.array([r["period"]for r in rs],dtype="datetime64[M]")
                ax.fill_between(dates,[float(r["lower95"])for r in rs],[float(r["upper95"])for r in rs],alpha=.15)
                ax.plot(dates,[float(r["smoothed_median"])for r in rs],label="Smoothed median + 95% band")
                ax.plot(dates,[float(r["conditional_filtered_mean"])for r in rs],ls="--",label="Conditional filtered mean")
                ax.set_ylabel(state+" (log / ALR)");ax.grid(alpha=.15)
                if j==0:ax.legend(fontsize=7)
    axes[-1,0].set_xlabel("Fixed lags 1–12; n=57 after twelve-month burn-in")
    axes[-1,1].set_xlabel("Full-window R conditions filter; not a historical real-time estimate")
    fig.suptitle("Primary M2: innovation ACF and filtered versus smoothed latent states")
    fig.text(.01,.01,"Source: KBA FZ10, own calculation. Descriptive fitted-model diagnostics; not calibrated specification tests.",fontsize=8)
    fig.tight_layout(rect=(0,.035,1,.97))
    plt.rcParams["svg.hashsalt"]="task04-innovation-review"
    fig.savefig(out/"innovation_acf.png",dpi=160)
    fig.savefig(out/"innovation_acf.svg",metadata={"Date":None})
    plt.close(fig)
    write_csv(out/"acf.csv",all_acf)
    write_csv(out/"largest_innovations.csv",all_outliers)
    write_csv(out/"annual_innovation_variation.csv",all_variances)
    write_csv(out/"innovations.csv",innovations)
    write_csv(out/"forecast_covariates.csv",covariates)
    write_json(out/"manifest.json",{
        "method":"Read-only conditional innovation diagnostics, no estimation or data changes",
        "protocol":m["protocol"],"stage1_manifest_sha256":sha(source/"manifest.json"),
        "script_sha256":sha(Path(__file__)),"periods":69,"diagnostic_burn_in":12,
        "acf_lags":12,"source":"KBA FZ10, own calculations, dl-de/by-2-0",
        "files":{p.name:sha(p)for p in sorted(out.iterdir())if p.is_file()}})
    print("Verified supplementary ACF/outlier/annual-variation outputs, all eight fixed models; no refit.")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source");p.add_argument("--output",required=True)
    a=p.parse_args();run(a.source,a.output)

