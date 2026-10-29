"""Read-only verification of complete stage-1 outputs; never invokes a fit."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from .data import ROOT,read_observed,sha
from .evaluation import decompose


def verify(path):
    root=Path(path)
    manifest=json.loads((root/"manifest.json").read_text())
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
    print("Verified Task04 stage1: 69 observed months, 8 fixed specifications, 1280 forecast rows, 5 exact annual/YTD decompositions; no refit.")


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("path");args=p.parse_args();verify(args.path)
