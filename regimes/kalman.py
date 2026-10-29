"""Proper Gaussian marginalisation; no target observations beyond the training prefix."""
import numpy as np
from scipy.linalg import cho_factor, cho_solve


def filter_numpy(y, H, F, Q, mean, P, R):
    n = len(y); ms=[]; ps=[]; errors=[]; standardized=[]; logp=0.
    mean, P = mean.copy(), P.copy()
    for t in range(n):
        if t:
            mean = F @ mean; P = F @ P @ F.T + Q
        err = y[t]-H[t] @ mean
        S = H[t] @ P @ H[t].T + R
        cf = cho_factor(S, lower=True)
        z = np.linalg.solve(np.tril(cf[0]), err)
        K = cho_solve(cf, H[t] @ P).T
        mean = mean + K @ err
        P = P - K @ H[t] @ P; P=(P+P.T)/2
        logp += -.5*(len(err)*np.log(2*np.pi)+2*np.log(np.diag(cf[0])).sum()+z@z)
        ms.append(mean.copy()); ps.append(P.copy()); errors.append(err); standardized.append(z)
    return logp, np.array(ms), np.array(ps), np.array(errors), np.array(standardized)


def filter_jax(y, H, mask, F, Q, mean, P, R):
    import jax
    import jax.numpy as j
    def step(carry, args):
        a, C, ll = carry
        t, obs, h, active = args
        def update(_):
            pred = j.where(t == 0, a, F @ a)
            V = j.where(t == 0, C, F @ C @ F.T + Q)
            err = obs-h@pred
            S = h@V@h.T+R
            L = j.linalg.cholesky(S)
            z = j.linalg.solve(L, err)
            K = j.linalg.solve(S, h@V).T
            post = pred+K@err
            W = V-K@h@V
            ll2 = ll-.5*(3*j.log(2*j.pi)+2*j.log(j.diag(L)).sum()+z@z)
            return post,(W+W.T)/2,ll2
        return jax.lax.cond(active, update, lambda _: carry, operand=None), None
    state, _ = jax.lax.scan(step, (mean, P, j.array(0.)), (j.arange(len(y)), y, H, mask))
    return state


def smoothing_mean(ms, ps, F, Q):
    a=ms.copy(); C=ps.copy()
    for t in range(len(ms)-2, -1, -1):
        pred=F@ps[t]@F.T+Q
        J=np.linalg.solve(pred,F@ps[t]).T
        a[t]=ms[t]+J@(a[t+1]-F@ms[t])
        C[t]=ps[t]+J@(C[t+1]-pred)@J.T
    return a,C
