"""Small reviewable outputs, immutable output directories, training-bound checkpoints."""
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import numpy as np
from .data import ROOT,sha


def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+"\n")


def write_csv(path,rows):
    if not rows:raise ValueError("Empty result table")
    with Path(path).open("w",newline="")as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def freeze_gate():
    config=json.loads((ROOT/"config/task-04-regimes.json").read_text())
    record=json.loads((ROOT/"data/task04_regimes/freeze.json").read_text())
    path=ROOT/"docs/REGIME_STATE_SPACE_PROTOCOL.md"
    if config["version"]!="task-04-regimes/1.0.0"or sha(path)!=record["protocol_sha256"]:
        raise ValueError("Protocol freeze/hash mismatch")
    if sha(ROOT/"config/task-04-regimes.json")!=record["config_sha256"]:
        raise ValueError("Frozen config changed")
    commit=record["commit"]
    subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],cwd=ROOT,check=True,capture_output=True)
    raw=subprocess.check_output(["git","show",commit+":docs/REGIME_STATE_SPACE_PROTOCOL.md"],cwd=ROOT)
    if hashlib.sha256(raw).hexdigest()!=record["protocol_sha256"]:
        raise ValueError("Protocol not committed before real estimation")
    for name,h in config["inputs_sha256"].items():
        if sha(ROOT/name)!=h:raise ValueError("Frozen input changed: "+name)
    return config,record


def fingerprint(record):
    names=["regimes/"+n for n in ["data.py","kalman.py","inference.py","evaluation.py"]]
    obj={"protocol":record,"code":{n:sha(ROOT/n)for n in names}}
    return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()


def save_checkpoint(path,result,tag):
    arrays={k:result[k]for k in ("packed","loglikelihood","logweights")if k in result}
    meta={k:v for k,v in result.items()if k not in arrays}
    meta["fingerprint"]=tag
    np.savez_compressed(path,metadata=np.array(json.dumps(meta)),**arrays)


def load_checkpoint(path,tag):
    with np.load(path,allow_pickle=False)as fp:
        obj=json.loads(str(fp["metadata"]))
        if obj.pop("fingerprint")!=tag:raise ValueError("Incompatible checkpoint")
        obj.update({k:fp[k]for k in fp.files if k!="metadata"})
    return obj


def runtime():
    names=["numpy","scipy","pandas","statsmodels","pymc","pytensor","jax","jaxlib","numpyro","arviz","hypoforge"]
    return {n:importlib.metadata.version(n)for n in names}
