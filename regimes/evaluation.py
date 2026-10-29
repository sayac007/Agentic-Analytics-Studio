"""Coherent predictive counts and exact accounting decomposition."""
import numpy as np
from .data import counts


def forecast(final,R,system,ntrain,values,horizons,seed,logit_market=False):
    H,F,Q,_,_,_=system
    rng=np.random.default_rng(seed)
    state=final.copy();out={}
    sd=np.sqrt(np.diag(Q))
    for h in range(1,max(horizons)+1):
        state=state@F.T+rng.normal(size=state.shape)*sd
        target=ntrain+h-1
        obs=state@H[target].T
        # Same joint draw contains market and both ALR coordinates.
        obs+=np.einsum("nij,nj->ni",np.linalg.cholesky(R),rng.normal(size=(len(state),3)))
        if h in horizons:
            cars=values[target-12,3]if logit_market else None
            sample=counts(obs,cars)
            if not np.isfinite(sample).all():raise ValueError("Nonfinite predictive count")
            out[h]=sample
    return out


def decompose(values):
    result=[]
    for year in range(2022,2027):
        a=(year-2021)*12;n=9 if year==2026 else 12
        before=values[a-12:a-12+n].sum(axis=0)
        after=values[a:a+n].sum(axis=0)
        M0,T0=before[:2];M1,T1=after[:2]
        s0=T0/M0;s1=T1/M1
        market=(s0+s1)/2*(M1-M0);share=(M0+M1)/2*(s1-s0)
        if not np.isclose(market+share,T1-T0,atol=1e-8):raise AssertionError("Accounting mismatch")
        result.append(dict(year=year,months=n,market_before=M0,market_after=M1,
                           Tesla_before=T0,Tesla_after=T1,share_before=s0,share_after=s1,
                           Tesla_change=T1-T0,market_component=market,share_component=share))
    return result


def paired_metrics(rows):
    groups={}
    for r in rows:
        key=(r["model"],r["outcome"],r["horizon"],r["year"])
        groups.setdefault(key,[]).append(r)
    out=[]
    for (model,outcome,horizon,year),rs in groups.items():
        err=np.array([r["prediction_mean"]-r["actual"]for r in rs])
        baseline=[r for r in rows if r["model"]=="M0"and r["outcome"]==outcome and
                  r["horizon"]==horizon and r["year"]==year]
        assert len(rs)==len(baseline)
        berr=np.array([r["prediction_mean"]-r["actual"]for r in baseline])
        rmse=float(np.sqrt(np.mean(err**2)));base=float(np.sqrt(np.mean(berr**2)))
        out.append(dict(model=model,outcome=outcome,horizon=horizon,year=year,n=len(rs),
                        rmse=rmse,baseline_rmse=base,rmse_difference=rmse-base,
                        mae=float(np.mean(abs(err))),mase=float(np.mean([r["scaled_absolute_error"]for r in rs])),
                        coverage95=float(np.mean([r["lower95"]<=r["actual"]<=r["upper95"]for r in rs])),
                        mean_interval_width=float(np.mean([r["upper95"]-r["lower95"]for r in rs]))))
    return out
