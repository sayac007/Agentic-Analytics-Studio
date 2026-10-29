"""Read-only verification of complete stage-1 outputs; never invokes a fit."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from .data import ROOT,read_observed,sha
from .evaluation import decompose
from .artifacts import freeze_gate


def verify(path):
    root=Path(path)
    cfg,record=freeze_gate()
    manifest=json.loads((root/"manifest.json").read_text())
    if manifest["protocol"]!=record or manifest["config_sha256"]!=record["config_sha256"]:
        raise ValueError("Result protocol/configuration does not match frozen definition")
    if manifest["input_hashes"]!=cfg["inputs_sha256"]:
        raise ValueError("Result input identities/hashes do not match frozen inputs")
    required={"coefficients.csv","states.csv","predictions.csv","metrics.csv",
              "decomposition.csv","model_decomposition.csv","contrasts.csv",
              "diagnostics.json","rolling_inference.json","frequentist_reference.json",
              "report.md","hypotheses.csv"}
    required.update(n+e for n in ("market_share_decomposition","latent_market","brand_levels")for e in (".png",".svg"))
    if set(manifest["files"])!=required:
        raise ValueError("Missing/unexpected required Stage1 payload")
    if manifest["status"]!="estimated"or manifest["protocol"]["version"]!="task-04-regimes/1.0.0":
        raise ValueError("Not a complete frozen stage-1 result")
    for name,h in manifest["files"].items():
        if Path(name).name!=name or sha(root/name)!=h:raise ValueError("Output hash/path mismatch: "+name)
    if {p.name for p in root.iterdir()if p.is_file()}!=set(manifest["files"])|{"manifest.json"}:
        raise ValueError("Unexpected/missing output files")
    for name,h in manifest["input_hashes"].items():
        if sha(ROOT/name)!=h:raise ValueError("Input changed")
    def read(name):
        with (root/name).open(newline="")as f:return list(csv.DictReader(f))
    rows=read("predictions.csv");models=[v["id"]for v in manifest["models"]]
    coherent={}
    for r in rows:
        numbers=[float(r[k])for k in ("actual","prediction_mean","lower95","upper95","error","scaled_absolute_error")]
        if not np.isfinite(numbers).all():raise ValueError("Nonfinite prediction")
        key=(r["model"],r["origin"],r["target"],r["horizon"])
        coherent.setdefault(key,{})[r["outcome"]]=float(r["prediction_mean"])
    for group in coherent.values():
        if set(group)!={"BEV_market","Tesla","VW","Rest"}or not np.isclose(group["BEV_market"],group["Tesla"]+group["VW"]+group["Rest"],rtol=1e-10,atol=1e-6):
            raise ValueError("Forecast means are not coherent")
    assert len(models)==8 and len(rows)==8*40*4
    for model in models:
        selected=[r for r in rows if r["model"]==model]
        for outcome in ("BEV_market","Tesla","VW","Rest"):
            rs=[r for r in selected if r["outcome"]==outcome]
            assert len(rs)==40
            assert sum(r["horizon"]=="1"for r in rs)==21
            assert sum(r["horizon"]=="3"for r in rs)==19
            assert len({(r["origin"],r["horizon"])for r in rs})==40
            for r in rs:
                assert r["origin"]<r["target"] and int(r["ntrain"])>=48
                assert float(r["lower95"])<=float(r["upper95"])
    diag=json.loads((root/"diagnostics.json").read_text())
    assert set(diag)==set(models)
    assert all(x["covariance_mcmc"]["passed"]and x["joint_derived_mcmc"]["passed"]for x in diag.values())
    records,values,_=read_observed()
    observed=np.column_stack([values[:,0],values[:,1],values[:,2],values[:,0]-values[:,1]-values[:,2]])
    outcomes=["BEV_market","Tesla","VW","Rest"]
    for r in rows:
        t=next(i for i,v in enumerate(records)if v["period"]==r["target"])
        assert float(r["actual"])==observed[t,outcomes.index(r["outcome"])]
    expected=decompose(values);actual=read("decomposition.csv")
    assert len(expected)==len(actual)==5
    for a,b in zip(actual,expected):
        for k,v in b.items():assert np.isclose(float(a[k]),v,rtol=1e-12,atol=1e-9),(k,a[k],v)
    rolling=json.loads((root/"rolling_inference.json").read_text())
    assert len(rolling)==8*21
    assert {(r["model"],r["ntrain"])for r in rolling}=={(m,n)for m in models for n in range(48,69)}
    assert all(r["proposal_covariance_diagnostics"]["passed"] for r in rolling)
    assert all(r["importance_diagnostics"]["accepted"]and r["importance_diagnostics"]["weight_ess"]>=4000 and r["importance_diagnostics"]["pareto_k"]<=.5 for r in rolling)
    assert all(r["diagnostics"]["n"]==r["ntrain"] for r in rolling)
    latent=read("model_decomposition.csv")
    assert len(latent)==8*5
    for r in latent:
        assert np.isclose(float(r["market_component_mean"])+float(r["share_component_mean"]),float(r["change_mean"]),atol=1e-6)
    print("Verified Task04 stage1: 69 observed months, 8 fixed specifications, 1280 forecast rows, 5 exact annual/YTD decompositions; no refit.")


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("path");args=p.parse_args();verify(args.path)
