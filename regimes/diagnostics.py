"""Fixed stationarity/innovation diagnostics; warnings and boundary p-values retained."""
import warnings
import numpy as np
from statsmodels.tsa.stattools import adfuller,kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.multitest import multipletests


def stationarity(values,trend):
    x=np.asarray(values,dtype=float)
    if len(x)<24 or not np.isfinite(x).all() or np.ptp(x)==0:
        return {"status":"not_computed","n":len(x),"reason":"short/nonfinite/constant segment"}
    with warnings.catch_warnings(record=True)as caught:
        warnings.simplefilter("always")
        a=adfuller(x,maxlag=3,regression="ct"if trend else"c",autolag=None)
        k=kpss(x,regression="ct"if trend else"c",nlags=3)
    return {"status":"computed","n":len(x),
            "adf":{"statistic":float(a[0]),"p":float(a[1]),"lags":int(a[2]),"effective_n":int(a[3]),"null":"unit root"},
            "kpss":{"statistic":float(k[0]),"p":float(k[1]),"lags":int(k[2]),"null":"trend stationarity"if trend else"level stationarity"},
            "warnings":[str(w.message)for w in caught]}


def innovations(values):
    x=np.asarray(values,dtype=float)[12:]
    result=stationarity(x,False)
    if result["status"]!="computed":return result
    lb=acorr_ljungbox(x,lags=[3,6,12],model_df=0,return_df=True)
    raw=lb["lb_pvalue"].to_numpy()
    adjusted=multipletests(raw,method="holm")[1]
    result["ljung_box"]=[{"lag":int(l),"statistic":float(s),"p":float(p),"p_holm":float(h)}
                         for l,s,p,h in zip([3,6,12],lb["lb_stat"],raw,adjusted)]
    result["limitation"]="Conditional filtered innovations, fixed hyperparameter posterior mean; fitted-parameter/short-sample tests are diagnostic, not calibrated specification tests."
    return result
