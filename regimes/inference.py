"""PyMC priors + exact Kalman marginal likelihood, NumPyro NUTS, Gaussian conditional draws.

Only six covariance coordinates enter NUTS. Initial states and regression
coefficients have the specified Normal priors and are integrated out exactly,
not replaced by MLE point estimates. Conditional Gaussian draws restore their
joint posterior and all state/market/share dependence.
"""
from functools import lru_cache
import os
os.environ.setdefault("JAX_ENABLE_X64", "true")
os.environ.setdefault("XLA_FLAGS", "--xla_force_host_platform_device_count=4")
os.environ.setdefault("PYTENSOR_FLAGS", "compiledir=/tmp/aas-regimes-pytensor")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/aas-regimes-mpl")
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/aas-regimes-numba")
import numpy as np
import jax
jax.config.update("jax_enable_x64", True)
from .kalman import filter_jax
SEEDS = (20261029, 20261030, 20261031, 20261032)


@lru_cache
def prior_graph():
    import pymc as pm
    from pymc.sampling.jax import get_jaxified_graph
    import jax
    with pm.Model() as model:
        L, _, _ = pm.LKJCholeskyCov("R_chol", n=3, eta=4,
                                   sd_dist=pm.HalfNormal.dist(sigma=np.array([.25, .5, .5])))
        R = model.replace_rvs_by_values([L @ L.T])[0]
        function = get_jaxified_graph(inputs=model.value_vars, outputs=[model.logp(), R])
    return jax.jit(function)


def numpyro_model(y, H, mask, F, Q, mean, P):
    import jax.numpy as j
    import numpyro
    import numpyro.distributions as dist
    proposal = dist.Normal(0, 1).expand([6]).to_event(1)
    packed = numpyro.sample("packed", proposal)
    lp, R = prior_graph()(packed)
    _, _, ll = filter_jax(y, H, mask, F, Q, mean, P, R)
    # Cancel the auxiliary Normal density exactly; it is not an extra prior.
    numpyro.factor("pymc_prior_and_kalman", lp + ll - proposal.log_prob(packed))


@lru_cache
def sampler(draws, tune, chains):
    from numpyro.infer import MCMC, NUTS
    return MCMC(NUTS(numpyro_model, target_accept_prob=.95, max_tree_depth=10, dense_mass=True),
                num_warmup=tune, num_samples=draws, num_chains=chains,
                chain_method="parallel", progress_bar=False, jit_model_args=True)


def fit(y, system, ntrain, *, draws=2000, tune=2000, chains=4, seeds=SEEDS):
    import jax
    import jax.numpy as j
    y = np.asarray(y, dtype=float)
    H, F, Q, mean, P, names = system
    if not np.isfinite(y).all() or y.shape != (len(H), 3):
        raise ValueError("Invalid coordinates")
    if np.any(y[ntrain:] != 0):
        raise ValueError("Estimator training input must not contain held-out outcomes")
    if not 1 <= ntrain <= len(y) or chains > len(seeds):
        raise ValueError("Invalid training prefix/seeds")
    args = tuple(map(j.asarray, (y, H, np.arange(len(y)) < ntrain, F, Q, mean, P)))
    initial = np.array([np.log(.25), 0., np.log(.5), 0., 0., np.log(.5)])
    init = np.stack([initial+np.random.default_rng(s).normal(0, .1, 6) for s in seeds[:chains]])
    keys = j.stack([jax.random.PRNGKey(s) for s in seeds[:chains]])
    mcmc = sampler(draws, tune, chains)
    mcmc.run(keys if chains > 1 else keys[0], *args,
             init_params={"packed": j.asarray(init if chains > 1 else init[0])},
             extra_fields=("diverging", "num_steps"))
    packed = np.asarray(mcmc.get_samples(group_by_chain=True)["packed"])
    extra = {k: np.asarray(v) for k, v in mcmc.get_extra_fields(group_by_chain=True).items()}
    diag = convergence({"packed": packed})
    diag["divergences"] = int(extra["diverging"].sum())
    diag["mean_num_steps"] = float(extra["num_steps"].mean())
    diag["max_tree_depth_hits"] = int((extra["num_steps"] >= 1023).sum())
    diag["passed"] = bool(diag["passed"] and diag["divergences"] == 0)
    return {"packed": packed, "diagnostics": diag, "ntrain": ntrain,
            "draws": draws, "chains": chains, "names": names}


def convergence(samples):
    import arviz as az
    data = az.from_dict(posterior=samples)
    if next(iter(samples.values())).shape[0] < 2:
        return {"passed": False, "reason": "smoke_only_less_than_two_chains"}
    rhat = az.rhat(data, method="rank").to_array().values
    bulk = az.ess(data, method="bulk").to_array().values
    tail = az.ess(data, method="tail").to_array().values
    finite = np.isfinite(rhat).all() and np.isfinite(bulk).all() and np.isfinite(tail).all()
    return {"rhat_max": float(np.max(rhat)), "ess_bulk_min": float(np.min(bulk)),
            "ess_tail_min": float(np.min(tail)),
            "passed": bool(finite and np.max(rhat) <= 1.01 and min(np.min(bulk), np.min(tail)) >= 400)}


@lru_cache
def draw_function(history):
    import jax
    import jax.numpy as j
    from jax import random
    prior = prior_graph()

    def one(packed, key, y, H, mask, F, Q, mean, P):
        _, R = prior(packed)
        m, C, _ = filter_jax(y, H, mask, F, Q, mean, P, R)
        key1, key2 = random.split(key)
        final = m + j.linalg.cholesky((C+C.T)/2) @ random.normal(key1, m.shape)
        if not history:
            return final, R
        # Given beta and R, dynamic states are only four dimensional.
        beta = final[4:]
        residual = y - j.einsum("tij,j->ti", H[:, :, 4:], beta)
        h = H[:, :, :4]; f = F[:4, :4]; q = Q[:4, :4]
        def forward(carry, args):
            t, obs, design = args
            a, V = carry
            a = j.where(t == 0, a, f@a)
            V = j.where(t == 0, V, f@V@f.T+q)
            S = design@V@design.T+R
            K = j.linalg.solve(S, design@V).T
            a = a+K@(obs-design@a); V=V-K@design@V
            return (a,(V+V.T)/2),(a,(V+V.T)/2)
        _, (ms, ps) = jax.lax.scan(forward, (mean[:4], P[:4, :4]),
                                  (j.arange(len(y)), residual, h))
        keys = random.split(key2, len(y)-1)
        def backward(last, args):
            a, V, k = args
            def dynamic(_):
                pred = f@V@f.T+q
                gain = j.linalg.solve(pred, f@V).T
                loc = a+gain@(last-f@a)
                W=V-gain@pred@gain.T; W=(W+W.T)/2
                return loc+j.linalg.cholesky(W)@random.normal(k, (4,))
            previous = jax.lax.cond(j.any(q), dynamic, lambda _: j.linalg.solve(f,last), operand=None)
            return previous,previous
        _, previous = jax.lax.scan(backward, final[:4], (ms[:-1][::-1], ps[:-1][::-1], keys))
        path = j.concatenate([previous[::-1], final[None, :4]], axis=0)
        return final, R, path
    return jax.jit(jax.vmap(one, in_axes=(0, 0, None, None, None, None, None, None, None)))


def posterior_draws(fit_result, y, system, *, history=False, seed=20261101):
    import jax
    import jax.numpy as j
    H,F,Q,mean,P,_=system
    n=fit_result["ntrain"]
    if history and n != len(y):
        raise ValueError("Full state paths only for the complete fitted window")
    args=tuple(map(j.asarray,(y,H,np.arange(len(y))<n,F,Q,mean,P)))
    packed=fit_result["packed"].reshape(-1,6)
    keys=jax.random.split(jax.random.PRNGKey(seed),len(packed))
    chunks=[]
    fn=draw_function(history)
    for i in range(0,len(packed),128):
        chunks.append(tuple(np.asarray(a)for a in fn(j.asarray(packed[i:i+128]),keys[i:i+128],*args)))
    merged=tuple(np.concatenate([x[k]for x in chunks])for k in range(len(chunks[0])))
    return merged

@lru_cache
def likelihood_particles():
    import jax
    import jax.numpy as j
    prior = prior_graph()
    def one(packed, y, H, mask, F, Q, mean, P):
        _,R=prior(packed)
        return filter_jax(y,H,mask,F,Q,mean,P,R)[2]
    return jax.jit(jax.vmap(one,in_axes=(0,None,None,None,None,None,None,None)))


def loglikelihoods(packed,y,system,ntrain):
    import jax.numpy as j
    H,F,Q,mean,P,_=system
    args=tuple(map(j.asarray,(y,H,np.arange(len(y))<ntrain,F,Q,mean,P)))
    values=[];flat=packed.reshape(-1,6)
    fn=likelihood_particles()
    for i in range(0,len(flat),128):
        values.append(np.asarray(fn(j.asarray(flat[i:i+128]),*args)))
    return np.concatenate(values)


def importance_update(previous,y,system,ntrain):
    """Exact unsmoothed likelihood-ratio weights; refresh NUTS on poor overlap."""
    from scipy.special import logsumexp
    import arviz as az
    ll=loglikelihoods(previous["packed"],y,system,ntrain)
    old=previous["loglikelihood"]
    logw=previous["logweights"]+ll-old
    logw-=logsumexp(logw);w=np.exp(logw)
    ess=float(1/np.sum(w*w))
    k=0. if np.ptp(logw)<1e-8 else float(az.psislw(logw)[1])
    accepted=bool(np.isfinite(ll).all() and ess>=len(w)/2 and np.isfinite(k)and k<=.5)
    if not accepted:return None,dict(weight_ess=ess,pareto_k=k,accepted=False)
    result=dict(previous)
    result.update(ntrain=ntrain,loglikelihood=ll,logweights=logw,
                  method="importance_update",names=system[-1])
    result["importance_diagnostics"]=dict(weight_ess=ess,pareto_k=k,accepted=True)
    return result,result["importance_diagnostics"]


def initialise_particles(result,y,system):
    """Store training-only likelihoods alongside a converged NUTS proposal."""
    result=dict(result);n=result["packed"].shape[0]*result["packed"].shape[1]
    result.update(loglikelihood=loglikelihoods(result["packed"],y,system,result["ntrain"]),
                  logweights=np.full(n,-np.log(n)),method="nuts_refresh",
                  importance_diagnostics={"weight_ess":n,"pareto_k":0.,"accepted":True})
    return result


def resampled_posterior(result,seed):
    if result.get("method")!="importance_update":return result
    rng=np.random.default_rng(seed)
    flat=result["packed"].reshape(-1,6)
    # Systematic resampling is solely integration of the weighted covariance
    # posterior; carried particles/weights are not overwritten or duplicated.
    u=(np.arange(len(flat))+rng.uniform())/len(flat)
    index=np.searchsorted(np.cumsum(np.exp(result["logweights"])),u,side="right")
    packed=flat[np.minimum(index,len(flat)-1)].reshape(result["packed"].shape)
    return {**result,"packed":packed}
