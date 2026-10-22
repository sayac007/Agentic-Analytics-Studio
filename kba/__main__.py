import argparse
from .pipeline import fetch, run, verify, audit

p = argparse.ArgumentParser(description="KBA acquisition; no MMM fitting")
p.add_argument("command", choices=["fetch", "extract", "verify", "audit"])
p.add_argument("--catalog", default="data/kba/sources.json")
p.add_argument("--plan", default="data/kba/acquisition-plan.json")
p.add_argument("--raw-dir", default="artifacts/kba-raw")
p.add_argument("--output", default="data/kba/derived")
a = p.parse_args()
if a.command == "fetch":
    fetch(a.catalog, a.raw_dir)
elif a.command == "extract":
    run(a.catalog, a.plan, a.raw_dir, a.output)
elif a.command == "audit":
    audit(a.catalog, a.plan, a.output)
else:
    verify(a.catalog, a.plan, a.raw_dir, a.output)
print("KBA " + a.command + " completed")
