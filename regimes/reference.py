"""Marginal-ML covariance reference with the identical proper Gaussian system."""
import numpy as np
from statsmodels.tsa.statespace.mlemodel import MLEModel
from .kalman import filter_numpy


def covariance(packed):
    L=np.zeros((3,3));L[np.tril_indices(3)]=packed
    for i,k in enumerate((0,2,5)):L[i,i]=np.exp(packed[k])
    return L@L.T


class Reference(MLEModel):
    def __init__(self,y,system):
        H,F,Q,m,P,_=system
        super().__init__(np.asarray(y),k_states=len(m),k_posdef=len(m),
                         initialization="known",initial_state=m,initial_state_cov=P)
        self.ssm["design"]=H.transpose(1,2,0)
        self.ssm["transition"]=F
        self.ssm["selection"]=np.eye(len(m))
        self.ssm["state_cov"]=Q

    @property
    def start_params(self):
        return np.array([np.log(.25),0,np.log(.5),0,0,np.log(.5)])

    def update(self,params,**kwargs):
        params=super().update(params,**kwargs)
        self.ssm["obs_cov"]=covariance(params)


def fit_reference(y,system):
    model=Reference(y,system)
    result=model.fit(method="lbfgs",maxiter=500,disp=False,optim_complex_step=False,
                     cov_type="none")
    if not result.mle_retvals["converged"]or not np.isfinite(result.llf):
        return {"status":"failed","optimizer":str(result.mle_retvals)}
    R=covariance(result.params)
    ll,ms,ps,err,z=filter_numpy(y,*system[:5],R)
    if not np.isclose(ll,result.llf,atol=1e-6):
        raise ValueError("statsmodels and independent Kalman likelihood disagree")
    return {"status":"estimated","log_likelihood":float(ll),"packed":result.params.tolist(),
            "R":R.tolist(),"final_coefficients":ms[-1,4:].tolist(),
            "note":"Marginal ML of covariance with same proper initial/regression distribution; not unpenalized classical OLS or causal effects."}
