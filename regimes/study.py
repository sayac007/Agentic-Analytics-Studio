"""Frozen Task04 stage1 runner: no energy, no private source data, no tuning."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from .data import PERIODS,ROOT,read_observed,observed_coordinates,system,sha
from .inference import (fit,posterior_draws,convergence,initialise_particles,
                        importance_update,resampled_posterior,prior_graph)
from .kalman import filter_numpy
from .artifacts import (write_json,write_csv,freeze_gate,fingerprint,
                        save_checkpoint,load_checkpoint,runtime)
from .evaluation import decompose,forecast,paired_metrics
from .diagnostics import stationarity,innovations
from .reference import fit_reference
from .assessments import rolling_diagnostics,latent_decomposition


def variants(primary):
    out=[dict(id="M0",model="M0",sd=primary,portal=False,logit=False),
         dict(id="M1",model="M1",sd=primary,portal=False,logit=False),
         dict(id="M2",model="M2",sd=primary,portal=False,logit=False)]
    for sd in (.03,.05,.10,.20):
        if sd!=primary:out.append(dict(id=f"M2_sd{sd:.2f}",model="M2",sd=sd,portal=False,logit=False))
    out.append(dict(id="M2_portal",model="M2",sd=primary,portal=True,logit=False))
    out.append(dict(id="M2_logit",model="M2",sd=primary,portal=False,logit=True))
    return out


def get_system(v,n):
    return system(v["model"],v["sd"],n,portal=v["portal"],logit_market=v["logit"])


def padded(y,n):
    data=np.zeros_like(y);data[:n]=y[:n]
    return data


def fitted(v,n,y,S,checkpoint,tag,previous=None,shared=None,draws=2000,tune=2000):
    name=f'{v["id"]}_{n}'
    tag=hashlib.sha256((tag+json.dumps(v,sort_keys=True)+str(n)).encode()).hexdigest()
    path=checkpoint/(name+".npz")
    if path.exists():
        result=load_checkpoint(path,tag)
        print("CHECKPOINT",name,flush=True);return result
    training=padded(y,n)
    result=None
    if previous is not None:
        result,overlap=importance_update(previous,training,S,n)
        if result is None:print("NUTS_REFRESH_REQUIRED",name,overlap,flush=True)
    if result is None and shared is not None:
        result,overlap=importance_update(shared,training,S,n,same_prefix=True)
        if result is None:print("SHARED_PROPOSAL_REJECTED",name,overlap,flush=True)
    if result is None:
        start=time.monotonic()
        result=fit(training,S,n,draws=draws,tune=tune)
        print("NUTS",name,round(time.monotonic()-start,2),result["diagnostics"],flush=True)
        attempts=[result["diagnostics"]]
        if not result["diagnostics"]["passed"]:
            write_json(checkpoint/(name+".failed.json"),result["diagnostics"])
            print("NUMERICAL_BUDGET_DOUBLING",name,flush=True)
            result=fit(training,S,n,draws=draws*2,tune=tune*2)
            attempts.append(result["diagnostics"])
        if not result["diagnostics"]["passed"]:
            write_json(checkpoint/(name+".retry_failed.json"),result["diagnostics"])
            raise RuntimeError("No successful fit after fixed numerical retry: "+name)
        result["numerical_attempts"]=attempts
        result=initialise_particles(result,training,S)
    save_checkpoint(path,result,tag)
    return result


def run(output,checkpoint):
    cfg,record=freeze_gate()
    execution_commit=__import__("subprocess").check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    implementation={str(p.relative_to(ROOT)):sha(p)for p in sorted((ROOT/"regimes").glob("*.py"))}
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    checkpoint=Path(checkpoint)
    if checkpoint.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Raw sampling checkpoints must remain outside Git")
    checkpoint.mkdir(parents=True,exist_ok=True)
    tag=fingerprint(record)
    records,values,_=read_observed()
    vs=variants(cfg["primary_level_sd"])
    full={};coefficients=[];state_rows=[];diagnostics={};references={};model_decomposition=[]
    # First all complete-window fits; rolling never borrows these samples.
    for i,v in enumerate(vs):
        y=observed_coordinates(values,v["logit"]);S=get_system(v,69)
        f=fitted(v,69,y,S,checkpoint,tag)
        final,R,paths=posterior_draws(f,y,S,history=True,seed=20261101+i)
        if not all(np.isfinite(x).all()for x in (final,R,paths)):
            raise ValueError("Nonfinite posterior")
        post_diag=convergence({"coefficients":final[:,4:].reshape(f["chains"],f["draws"],-1),
                              "levels":paths.reshape(f["chains"],f["draws"],69,4)})
        if not post_diag["passed"]:
            write_json(checkpoint/(v["id"]+".derived_failed.json"),post_diag)
            raise RuntimeError("No successful posterior: "+v["id"])
        full[v["id"]]={"variant":v,"final":final,"R":R,"paths":paths,"fit":f}
        coordinates=np.einsum("tkd,ntd->ntk",S[0][:,:,:4],paths)+np.einsum("tkd,nd->ntk",S[0][:,:,4:],final[:,4:])
        model_decomposition.extend(latent_decomposition(v["id"],coordinates,values[:,3]if v["logit"]else None))

        ref=fit_reference(y,S);references[v["id"]]=ref
        for j,name in enumerate(S[-1]):
            d=final[:,4+j];lo,med,hi=np.quantile(d,[.025,.5,.975])
            observed_nonzero=int(np.any(S[0][:69,:,4+j]!=0,axis=1).sum())
            coefficients.append(dict(model=v["id"],term=name,mean=float(d.mean()),median=float(med),
                                     posterior_sd=float(d.std(ddof=1)),lower95=float(lo),upper95=float(hi),
                                     observed_nonzero_months=observed_nonzero,
                                     prior_sd=float(np.sqrt(S[4][4+j,4+j])),
                                     posterior_prior_sd_ratio=float(d.std(ddof=1)/np.sqrt(S[4][4+j,4+j])),
                                     identification="prior_only"if not observed_nonzero else
                                     "interval_includes_zero"if lo<=0<=hi else"conditional_interval_excludes_zero",
                                     interpretation="conditional log/logit/ALR coefficient, not causal"))
        ll,ms,ps,err,z=filter_numpy(y,*S[:5],R.mean(axis=0))
        for j,label in enumerate(("market_level","market_slope","Tesla_ALR_level","VW_ALR_level")):
            lo,med,hi=np.quantile(paths[:,:,j],[.025,.5,.975],axis=0)
            for t,p in enumerate(PERIODS):
                state_rows.append(dict(model=v["id"],period=p,state=label,
                                       smoothed_mean=float(paths[:,t,j].mean()),smoothed_median=float(med[t]),
                                       lower95=float(lo[t]),upper95=float(hi[t]),conditional_filtered_mean=float(ms[t,j]),
                                       units="logit"if v["logit"]and j==0 else"log"if j==0 else"ALR"if j>1 else"log change/month"))
        designs=[]
        for j in range(3):
            active=S[0][:,:,4:][:,j,:]
            active=active[:,np.any(abs(active)>1e-12,axis=0)]
            x=np.column_stack([np.ones(69),np.arange(69)])if j==0 else np.ones((69,1))
            x=np.column_stack([x,active])
            designs.append({"group":j,"rank":int(np.linalg.matrix_rank(x)),
                            "columns":x.shape[1],
                            "unit_norm_condition_number":float(np.linalg.cond(x/np.linalg.norm(x,axis=0))),
                            "note":"fixed calendar/policy design check, not proof of latent-state identification"})
        diagnostics[v["id"]]={"covariance_mcmc":f["diagnostics"],
                               "fixed_design":designs,
                               "observation_covariance_posterior_mean":R.mean(axis=0).tolist(),
                               "numerical_attempts":f.get("numerical_attempts",[]),"joint_derived_mcmc":post_diag,
                               "levels":{str(j):stationarity(y[:,j],True)for j in range(3)},
                               "innovations":{str(j):innovations(z[:,j])for j in range(3)},
                               "filter_note":"One-step innovations at full-training posterior mean R; no smoothed residuals, not a historical live filter."}
        print("FULL_COMPLETE",v["id"],flush=True)
    predictions=[];rolling_records=[];shared_primary={}
    ordered=sorted(enumerate(vs),key=lambda pair:pair[1]["id"]!="M2")
    for i,v in ordered:
        y=observed_coordinates(values,v["logit"]);previous=None
        for n in range(48,69):
            S=get_system(v,n)
            f=fitted(v,n,y,S,checkpoint,tag,previous,shared_primary.get(n))
            if v["id"]=="M2":shared_primary[n]=f
            previous=f
            sample_fit=resampled_posterior(f,20262000+n+i*100)
            final,R=posterior_draws(sample_fit,padded(y,n),S,seed=20263000+n+i*100)
            hs=[h for h in (1,3)if n+h<=69]
            samples=forecast(final,R,S,n,values,hs,20264000+n+i*100,v["logit"])
            rolling_records.append(dict(model=v["id"],training_end=PERIODS[n-1],ntrain=n,method=f["method"],
                                        proposal_covariance_diagnostics=f["diagnostics"],
                                        proposal_type=f.get("proposal_type","direct_nuts"),
                                        importance_diagnostics=f["importance_diagnostics"],
                                        source="strict_training_prefix; independent of complete-window posterior",
                                        diagnostics=rolling_diagnostics(y[:n],S,f)))
            raw=np.column_stack([values[:,0],values[:,1],values[:,2],values[:,0]-values[:,1]-values[:,2]])
            scales=np.abs(raw[12:n]-raw[:n-12]).mean(axis=0)
            for h,d in samples.items():
                target=n+h-1
                for j,name in enumerate(("BEV_market","Tesla","VW","Rest")):
                    lo,hi=np.quantile(d[:,j],[.025,.975]);mean=float(d[:,j].mean());actual=float(raw[target,j])
                    predictions.append(dict(model=v["id"],origin=PERIODS[n-1],ntrain=n,target=PERIODS[target],
                                            year=int(PERIODS[target][:4]),horizon=h,outcome=name,actual=actual,
                                            prediction_mean=mean,lower95=float(lo),upper95=float(hi),
                                            error=mean-actual,scaled_absolute_error=abs(mean-actual)/scales[j],
                                            scenario="calendar + policy known by origin; logit uses seasonal-naive Pkw denominator",
                                            inference=f["method"]))
            print("ROLL_COMPLETE",v["id"],PERIODS[n-1],f["method"],flush=True)
    metrics=paired_metrics(predictions)
    decomposition=decompose(values)
    contrasts=[]
    for name,info in full.items():
        path=info["paths"]
        a=np.array([p.startswith("2024-")for p in PERIODS])
        b=np.array([p.startswith("2025-")for p in PERIODS])
        for j,g in [(2,"Tesla"),(3,"VW")]:
            d=path[:,b,j].mean(axis=1)-path[:,a,j].mean(axis=1)
            lo,med,hi=np.quantile(d,[.025,.5,.975])
            contrasts.append(dict(model=name,group=g,contrast="mean2025_minus_mean2024_ALR_level",
                                  median=float(med),lower95=float(lo),upper95=float(hi),
                                  causal_interpretation=False))
    write_csv(out/"coefficients.csv",coefficients)
    write_csv(out/"states.csv",state_rows)
    write_csv(out/"predictions.csv",predictions)
    write_csv(out/"metrics.csv",metrics)
    write_csv(out/"decomposition.csv",decomposition)
    write_csv(out/"model_decomposition.csv",model_decomposition)
    write_csv(out/"contrasts.csv",contrasts)
    write_json(out/"diagnostics.json",diagnostics)
    write_json(out/"rolling_inference.json",rolling_records)
    write_json(out/"frequentist_reference.json",references)
    from .reporting import render
    render(out,values,decomposition,metrics,contrasts,full)
    if any(sha(ROOT/name)!=h for name,h in implementation.items()):
        raise ValueError("Implementation changed during execution; no successful manifest")
    manifest=dict(status="estimated",protocol=record,execution_commit=execution_commit,
                  implementation_sha256=implementation,
                  config_sha256=sha(ROOT/"config/task-04-regimes.json"),
                  input_hashes=cfg["inputs_sha256"],runtime=runtime(),models=vs,
                  source="Kraftfahrt-Bundesamt FZ10, own calculations, dl-de/by-2-0",
                  source_vintage="2026-10-29, retrospective current-vintage reference-month backtest",
                  periods=69,training_minimum=48,
                  forecast_targets_per_model={"h1":21,"h3":19},
                  method="Joint Gaussian state-space; PyMC priors, exact Kalman marginalisation, NumPyro NUTS; guarded unsmoothed importance updates for rolling prefixes.",
                  fingerprint=tag,
                  files={p.name:sha(p)for p in sorted(out.iterdir())if p.is_file()})
    write_json(out/"manifest.json",manifest)
    print("STAGE1_COMPLETE",str(out),flush=True)


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--checkpoint",required=True)
    args=parser.parse_args()
    run(args.output,args.checkpoint)
