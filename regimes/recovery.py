"""Small predeclared synthetic check; never reads observed KBA outcomes."""
import csv
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from .data import ROOT, system
from .inference import fit, posterior_draws, convergence


def simulate(case, plan):
    n=69
    H,F,_,mean,_,names=system("M2",.03,n)
    streams=np.random.SeedSequence(case["seed"]).spawn(2)
    latent=np.random.Generator(np.random.PCG64(streams[0]))
    noise=np.random.Generator(np.random.PCG64(streams[1]))
    d=len(mean); state=np.zeros(d);state[:4]=plan["initial_dynamic_state"]
    betas={f"{group}:{name}":v for group, vals in plan["calendar_coefficients"].items()
           for name,v in zip(("sin_12","cos_12","quarter_end","national_weekdays"),vals)}
    betas[plan["target"]["name"]]=plan["target"]["coefficient_log_units"]
    state[4:]=[betas.get(n,0)for n in names]
    R=np.array(plan["observation_correlation"])*np.outer(plan["observation_sds"],plan["observation_sds"])
    L=np.linalg.cholesky(R);Qsd=np.array([case["state_level_sd"],plan["slope_sd"],
                                        case["state_level_sd"],case["state_level_sd"]])
    y=[]
    for t in range(n):
        if t:
            state=F@state;state[:4]+=Qsd*latent.normal(size=4)
        y.append(H[t]@state+L@noise.normal(size=3))
    return np.array(y)


def run(output):
    plan_path=ROOT/"data/task04_regimes/recovery_plan.json"
    plan=json.loads(plan_path.read_text())
    out=Path(output)
    out.mkdir(parents=True,exist_ok=False)
    records=[];start=time.monotonic()
    for c,case in enumerate(plan["cases"]):
        y=simulate(case,plan)
        for sd in plan["candidate_level_sds"]:
            S=system("M2",sd,69)
            cfg=plan["sampler"]
            f=fit(y,S,69,draws=cfg["draws_per_chain"],tune=cfg["warmup"],chains=cfg["chains"])
            final,R=posterior_draws(f,y,S)
            index=4+S[-1].index(plan["target"]["name"])
            draws=final[:,index]
            coefficient_diag=convergence({"effect":draws.reshape(cfg["chains"],cfg["draws_per_chain"])})
            lo,med,hi=np.quantile(draws,[.025,.5,.975])
            truth=plan["target"]["coefficient_log_units"]
            row=dict(case=c,true_level_sd=case["state_level_sd"],seed=case["seed"],
                     fitted_level_sd=sd,truth=truth,median=float(med),lower95=float(lo),
                     upper95=float(hi),absolute_error=float(abs(med-truth)),
                     truth_in_interval=bool(lo<=truth<=hi),interval_excludes_zero=bool(lo>0 or hi<0),
                     converged=bool(f["diagnostics"]["passed"]and coefficient_diag["passed"]),
                     covariance_diagnostics=f["diagnostics"],effect_diagnostics=coefficient_diag)
            records.append(row)
            (out/"fits.json").write_text(json.dumps(records,indent=2,allow_nan=False)+"\n")
            print(json.dumps({k:row[k]for k in ["case","true_level_sd","fitted_level_sd","median","lower95","upper95","converged"]}),flush=True)
    aggregates=[]
    for sd in plan["candidate_level_sds"]:
        rs=[r for r in records if r["fitted_level_sd"]==sd]
        aggregates.append(dict(sd=sd,mean_absolute_error=float(np.mean([r["absolute_error"]for r in rs])),
                               truth_in_interval=sum(r["truth_in_interval"]for r in rs),
                               excludes_zero=sum(r["interval_excludes_zero"]for r in rs),
                               converged=sum(r["converged"]for r in rs),n=len(rs)))
    qualified=[r for r in aggregates if r["converged"]==len(plan["cases"])]
    if not qualified:raise RuntimeError("No candidate passes every convergence check; no primary selection")
    best=min(r["mean_absolute_error"]for r in qualified)
    selected=max(r["sd"]for r in qualified if abs(r["mean_absolute_error"]-best)<=1e-6)
    summary=dict(plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                 aggregates=aggregates,selected_primary_sd=selected,
                 elapsed_seconds=time.monotonic()-start,
                 interpretation="Artificial four-case check only, no coverage/power/MDE validation; no observed outcomes used.")
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    with (out/"summary.csv").open("w",newline="")as fp:
        w=csv.DictWriter(fp,fieldnames=list(aggregates[0]));w.writeheader();w.writerows(aggregates)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(out.iterdir())}
    (out/"sha256.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("SELECTED",selected,flush=True)


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args();run(args.output)
