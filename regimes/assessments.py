"""Read-only Gaussian diagnostics and joint-draw accounting, without refitting."""
import numpy as np
from .data import PERIODS,counts
from .kalman import filter_numpy
from .diagnostics import stationarity,innovations


def rolling_diagnostics(y,system,result):
    H,F,Q,m,P,_=system
    if result["ntrain"] != len(y):
        raise ValueError("Diagnostic covariance must use the same training prefix")
    p=result["packed"].reshape(-1,6)
    L=np.zeros((len(p),3,3));L[:,np.tril_indices(3)[0],np.tril_indices(3)[1]]=p
    for i,k in enumerate((0,2,5)):L[:,i,i]=np.exp(p[:,k])
    R=L@L.transpose(0,2,1)
    w=np.exp(result["logweights"]);w/=w.sum()
    Rmean=np.einsum("n,nij->ij",w,R)
    _,_,_,_,z=filter_numpy(y,H[:len(y)],F,Q,m,P,Rmean)
    return {"n":len(y),"source":"training-prefix only; posterior mean R",
            "targets":{str(j):stationarity(y[:,j],True)for j in range(3)},
            "innovations":{str(j):innovations(z[:,j])for j in range(3)}}


def latent_decomposition(name,coordinates,car_total=None):
    """Mean components add exactly; marginal interval endpoints need not add."""
    value=counts(coordinates,car_total)
    if not np.isfinite(value).all():raise ValueError("Nonfinite latent intensity")
    out=[]
    for year in range(2022,2027):
        start=(year-2021)*12;n=9 if year==2026 else 12
        before=value[:,start-12:start-12+n,:].sum(axis=1)
        after=value[:,start:start+n,:].sum(axis=1)
        M0,T0=before[:,0],before[:,1];M1,T1=after[:,0],after[:,1]
        s0=T0/M0;s1=T1/M1
        a=(s0+s1)/2*(M1-M0);b=(M0+M1)/2*(s1-s0);delta=T1-T0
        if not np.allclose(a+b,delta,atol=1e-7,rtol=1e-10):raise ValueError("Joint-draw accounting mismatch")
        row=dict(model=name,year=year,months=n,units="latent registration intensity; calendar and policy included, observation noise excluded")
        for term,d in [("change",delta),("market_component",a),("share_component",b)]:
            row[term+"_mean"]=float(d.mean())
            row[term+"_lower95"]=float(np.quantile(d,.025))
            row[term+"_upper95"]=float(np.quantile(d,.975))
        out.append(row)
    return out
