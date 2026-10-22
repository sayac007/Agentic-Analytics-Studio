"""One fixed, predeclared synthetic experiment; no search, tuning or scenario grid."""
import json
from pathlib import Path
from .files import artifact, store, write_once
from .runtime import versions

SOURCE = Path(__file__).resolve().parents[1]


def report(root, truth, results, evaluations, comparison):
    lines = ['# Synthetic Stage-A recovery benchmark', '',
             'All reference, media and outcomes are synthetic. Not observed Tesla data or real causal marketing ROI.', '',
             'One seed, 60 training months and 12 holdout months. Fixed oracle transforms; deliberately incomplete baseline.',
             'Conditional HAC intervals do not establish actual 95% coverage, empirical power or a validated MDE.', '',
             f"Planted media coefficient: {truth['media_coefficient']:.9f}; noise SD: {truth['noise_sd']:.9f}.", '',
             '| Run | beta | conditional 95% interval | Holdout RMSE | holdout contribution | beta error | curve RMSE | interval contains truth (one run) |',
             '|---|---:|---|---:|---:|---:|---:|---|']
    for result, evaluation in zip(results,evaluations):
        b=result['coefficients']['media']
        lines.append(f"| {result['run_id']} | {b['estimate']:.9f} | [{b['lower']:.9f}, {b['upper']:.9f}] | "
                     f"{result['metrics']['test']['rmse']:.9f} | {result['contribution']['total']['estimate']:.9f} | "
                     f"{evaluation['media_coefficient_error']:.9f} | {evaluation['response_curve_rmse']:.9f} | "
                     f"{evaluation['media_interval_covers_truth']} |")
    lines += ['', 'Contributions and response errors use count-equivalent units; spend is synthetic currency per month.',
              f"Relative response change: {comparison['relative_curve_change']:.9f}; declared sensitivity flags: {comparison['flags']}.",
              'The comparison limit is a predeclared engineering sensitivity rule, not a scientific detection threshold.',
              '`detection_limit_status=not_calibrated`; `effect_below_detection_limit=null`.', '',
              '## Artifact identity', '']
    for name in ['private/reference.csv','private/generator.json','safe/data.csv','private/truth.json',
                 'safe/with-quarter.manifest.json','safe/with-quarter.result.json',
                 'safe/without-quarter.manifest.json','safe/without-quarter.result.json','comparison.json']:
        lines.append(f"- `{name}`: `{artifact(root,name)['sha256']}`")
    lines += ['', 'Every artifact, including prediction CSVs and access records, is hashed in inventory.json.',
              'Reference/truth are evaluator-only. The estimator processes ran in separate workspaces without those files.',
              'Known transforms do not remove bias from omitted baseline disturbances. No recovery tuning was performed.', '']
    write_once(root/'report.md', '\n'.join(lines).encode())


def run(output):
    from .generate import generate
    from .isolation import isolated_fit
    from .evaluate import evaluate, compare, verify_bundle
    environment = versions()
    root = Path(output).resolve()
    root.mkdir(parents=True,exist_ok=False)
    protocol_raw=(SOURCE/'config/task-01a.json').read_bytes()
    protocol=json.loads(protocol_raw)
    write_once(root/'protocol.json',protocol_raw)  # frozen BEFORE generating or fitting
    store(root/'environment.json',environment)
    source_files = sorted([*SOURCE.glob('studio/*.py'),*SOURCE.glob('contracts/*.schema.json'),
                           SOURCE/'contracts/validate.py',SOURCE/'config/task-01a.json',SOURCE/'requirements.lock'])
    store(root/'implementation.json',{'files': {p.relative_to(SOURCE).as_posix():artifact(SOURCE,p.relative_to(SOURCE).as_posix())['sha256'] for p in source_files}})
    truth=generate(root,protocol)
    results=[]
    for name in ['with-quarter','without-quarter']:
        isolated_fit(root,f'safe/{name}.manifest.json')
        results.append(json.loads((root/f'safe/{name}.result.json').read_text()))
    evaluations=[evaluate(root,f"safe/{result['run_id']}.result.json") for result in results]
    comparison=compare(root,protocol['stability_rule'])
    report(root,truth,results,evaluations,comparison)
    files=sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())
    store(root/'inventory.json',{'protocol_sha256':artifact(root,'protocol.json')['sha256'],
                               'artifacts':{name:artifact(root,name)['sha256'] for name in files}})
    verify_bundle(root)
    return root
