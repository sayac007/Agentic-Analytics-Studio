"""Render the portfolio from a verified full synthetic run; never fit or tune models."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research_benchmark.verify import verify


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def percent(value):return f'{float(value)*100:.1f}%'


def threshold(value):return f'{float(value)*100:.0f}%' if value else 'not reached (3/8/15%)'


def render(source,output,readme):
    source,output,readme=Path(source),Path(output),Path(readme)
    verify(source)
    original=json.loads((source/'manifest.json').read_text())
    if original['smoke_only'] or original['seeds_per_cell']!=1000:
        raise ValueError('Portfolio requires the full preregistered run, never smoke power')
    summary=rows(source/'summary.csv');mde=rows(source/'mde.csv')
    def cell(family,design,confound,effect,model='with-quarter'):
        return next(r for r in summary if r['cell']==f'{family}-{design}-{confound}-{effect:g}' and r['model']==model)
    selected=[('Legacy always-on, fixed k=100','legacy','always_on','independent'),
              ('Always-on, train-relative k','grid','always_on','independent'),
              ('Flighting, independent','grid','flighting','independent'),
              ('Flighting, calendar-aligned','grid','flighting','calendar_aligned')]
    table=['| Design at 8% mean effect | Median SNR | Positive detection | Null false positives | 95% interval coverage |',
           '|---|---:|---:|---:|---:|']
    for label,family,design,confound in selected:
        r=cell(family,design,confound,.08);null=cell(family,design,confound,0)
        table.append(f"| {label} | {float(r['snr_median']):.3f} | {percent(r['positive_detection_rate'])} | {percent(null['rejection_rate'])} | {percent(r['coverage_rate'])} |")
    thresholds=['| Spend design | Confounding | Calendar model | Smallest tested effect reaching 80% rejection | Null false positives |',
                '|---|---|---|---|---:|']
    for r in mde:
        thresholds.append(f"| {r['design']} | {r['confounding']} | {r['model']} | {threshold(r['rejection_grid_mde'])} | {percent(r['null_rejection_rate'])} |")
    legacy=cell('legacy','always_on','independent',.08);null=cell('legacy','always_on','independent',0)
    flight=cell('grid','flighting','independent',.08)
    findings=[
        f"**Always-on can miss the planted effect.** In the legacy 8% design, correct positive detection is {percent(legacy['positive_detection_rate'])}; nominal two-sided rejection is {percent(legacy['rejection_rate'])} (Monte Carlo SE {100*float(legacy['rejection_mcse']):.2f} percentage points). Its null false-positive rate is {percent(null['rejection_rate'])}, so the anticipated near-5% two-sided operating characteristic is not reproduced.",
        f"**Flighting improves recovery in this benchmark.** At 8%, independent flighting reaches {percent(flight['positive_detection_rate'])} positive detection (MCSE {100*float(flight['positive_detection_mcse']):.2f} pp); median estimated/planted beta is {float(flight['beta_ratio_median']):.3f}. Yet interval coverage is only {percent(flight['coverage_rate'])}, not 95%.",
        "**Significance is not identification.** Calendar-aligned media without the quarter-end control produces 53.2% / 48.0% null false positives (always-on / flighting). A small engineering condition number and agreement between two bad estimates do not establish recovery.",
        "**The original negative estimates now trigger warnings.** Both Task01a seed42 fits receive not_identified, sign_uncertain and extrapolated_counterfactual in the new-stage evaluation. Their original files remain unchanged. SNR for that original seed is 0.124840.",
    ]
    # The last two statements are derived from the corresponding stored rows too.
    wrong_a=cell('grid','always_on','calendar_aligned',0,'without-quarter')
    wrong_f=cell('grid','flighting','calendar_aligned',0,'without-quarter')
    findings[2]=findings[2].replace('53.2% / 48.0%',percent(wrong_a['rejection_rate'])+' / '+percent(wrong_f['rejection_rate']))
    flags=rows(source/'legacy_flags.csv')
    if len(flags)!=2 or not all(float(r['beta'])<0 for r in flags) or not all(r[k]=='True' for r in flags for k in ('not_identified','sign_uncertain','extrapolated_counterfactual')):
        raise ValueError('Stored legacy flags do not support the portfolio statement')
    findings[3]=findings[3].replace('0.124840',f"{float(flags[0]['snr']):.6f}")
    title='# When does an MMM reliably recover a media effect?'
    introduction='A reproducible synthetic benchmark with known ground truth: 1,000 seeds per cell, 18 cells, two fixed models and 36,000 fits. No real campaign data, causal ROI or outcome-based tuning.'
    caveat='These are exploratory **tested-grid crossings, not validated MDEs**. The grid is 3%, 8%, 15%; no interpolation. Every design has inflated null rejection and/or undercoverage. An apparently low threshold under confounding can be a false-positive problem. Positive-detection thresholds and Monte Carlo Wilson bounds are retained in the CSVs.'
    limits='All findings are conditional on this synthetic baseline, spend/noise design, oracle transforms and finite-sample HAC intervals. They do not establish causal effects of real marketing, general power or reliable real-data inference.'
    lines=[title,'',introduction,'','![Nominal rejection rates and Monte Carlo intervals](examples/research-task02/power.png)',
           '', '## Detection thresholds by design — not validated MDE', '', '\n'.join(thresholds), '', caveat,
           '', '## What the experiment shows', '', *[f'- {v}' for v in findings], '', '\n'.join(table),
           '', 'Primary table uses the with-quarter model. “Positive detection” means lower interval bound >0; null false positives use two-sided rejection. These are different quantities.',
           '', '## Reproduce', '', 'Python 3.12, Git and the pinned runtime:', '', '```sh',
           'python3.12 -m venv .venv','.venv/bin/python -m pip install -r requirements-attention.lock',
           'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m research_benchmark.run --output artifacts/research-task02',
           '.venv/bin/python -m research_benchmark.verify artifacts/research-task02','```',
           '', 'Read the [full results report](examples/research-task02/report.md), [summary CSV](examples/research-task02/summary.csv), [grid thresholds](examples/research-task02/mde.csv) and [preregistered protocol](benchmarks/task02/PROTOCOL.md).',
           'Successful **Synthetic identifiability research** Actions runs export complete seed-level truth/evaluations for 30 days. The committed presentation subset is derived from a verified full run; it is not the full 36,000-row data bundle.',
           '', '## Limits', '', limits,
           '', '## Appendix and earlier work', '',
           '- [Scientific implementation and isolation](docs/IDENTIFIABILITY_RESEARCH.md)',
           '- [Data sources and private acquisition limits](DATA_SOURCES.md)',
           '- [Architecture](docs/ARCHITECTURE.md), [data policy](docs/DATA_POLICY.md), [statistical contracts](docs/STATISTICAL_CONTRACTS.md)',
           '- [Earlier project milestones and commands](docs/PROJECT_HISTORY.md)',
           '- [Local synthetic demo](docs/LOCAL_DEMO.md) is optional infrastructure; the scientific benchmark needs no UI, cloud account or model key.',
           '', 'One focused PR per package; no automatic merge. Real-data models, Bayesian extensions and additional integrations are outside these results.', '']
    root_readme='\n'.join(lines)
    # Result report: findings first, complete negative/null tables next, identity last.
    detailed=(source/'report.md').read_text()
    report='\n'.join([title,'',introduction,'',*findings,'','\n'.join(table),'',
                       '## Tested-grid thresholds','','\n'.join(thresholds),'',caveat,'',
                       '## Complete prespecified results','',detailed,
                       '## Limits','',limits,'','## Artifact identity','',
                       'Source and presentation hashes are recorded in manifest.json. No additional QA inventory.',''])
    if output.exists():raise FileExistsError('New presentation directory required')
    output.mkdir(parents=True)
    for name in ['power.png','summary.csv','mde.csv','legacy_flags.csv','protocol.json']:
        shutil.copyfile(source/name,output/name)
    (output/'report.md').write_text(report)
    manifest=dict(kind='synthetic_presentation_subset_not_full_seed_data',scope='SYNTHETIC_ONLY',seeds_per_cell=1000,
        source_data_manifest_sha256=hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),
        source_code_commit=original['code_commit'],protocol_sha256=original['protocol_sha256'],
        files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())})
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    readme.parent.mkdir(parents=True,exist_ok=True);readme.write_text(root_readme)
    print('Rendered results-first portfolio from verified stored outputs; no model fitting')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--readme',type=Path,required=True)
    a=p.parse_args();render(a.source,a.output,a.readme)


if __name__=='__main__':main()
