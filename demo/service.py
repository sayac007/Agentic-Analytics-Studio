"""Synthetic-only adapter over the unchanged, isolated Stage-A engine."""
import csv
import json
from pathlib import Path
import tempfile

import numpy as np

from studio.evaluate import verify_bundle
from studio.pipeline import run
from studio.statistics import design

DATASET = {
    'id': 'synthetic-mmm', 'name': 'Synthetic MMM Demo',
    'classification': 'SYNTHETIC / NOT EMPIRICAL',
    'description': '72 fictional monthly observations, 2018–2023. A synthetic baseline plus a known injected media response and seeded noise. No external data.',
    'seed': 42, 'months': 72, 'train_months': 60, 'holdout_months': 12,
    'transform': 'HypoForge geometric adstock α=0.5, L=3, unnormalized; Hill k=100, n=1.5.',
    'unit': 'count-equivalent; spend in synthetic currency per month',
}
LIMITS = [
    'All observations are synthetic. This benchmark does not estimate real marketing ROI.',
    'HAC 95% intervals are conditional on fixed oracle transforms and controls; actual coverage is not validated.',
    'The baseline deliberately contains an unmodelled break and outlier. Known transforms do not guarantee unbiased recovery.',
    'Detection limit is not calibrated; effect_below_detection_limit is null.',
]


def load_json(root, name):
    return json.loads((root / name).read_text())


def compute(model):
    if model not in ('with-quarter', 'without-quarter'):
        raise ValueError('Unknown predefined model')
    # No input paths/uploads/source selectors; generated data are synthetic by construction.
    with tempfile.TemporaryDirectory(prefix='aas-synthetic-demo-') as tmp:
        root = run(Path(tmp) / 'bundle')
        verify_bundle(root)  # Never present unvalidated result artifacts.
        return summarize(root, model)


def summarize(root, model):
    result = load_json(root, f'safe/{model}.result.json')
    manifest = load_json(root, f'safe/{model}.manifest.json')
    truth = load_json(root, 'private/truth.json')  # Evaluator-only, after estimator exit.
    evaluation = load_json(root, f'evaluation/{model}.json')
    with (root / 'safe/data.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    with (root / 'private/reference.csv').open(newline='') as f:
        reference = [float(r['observed_registrations']) for r in csv.DictReader(f)]
    periods = [r['period'] for r in rows]
    spend = np.array([float(r['synthetic_media']) for r in rows])
    outcome = np.array([float(r['semi_synthetic_outcome']) for r in rows])
    x, names = design(periods, spend, manifest['estimation'])
    beta = np.array([result['coefficients'][n]['estimate'] for n in names])
    prediction = x @ beta
    media = x[:, names.index('media')] * result['coefficients']['media']['estimate']
    formula = 'outcome ~ intercept + trend + annual_sin + annual_cos + hill(adstock(media))'
    if model == 'with-quarter':
        formula += ' + quarter_end'
    b = result['coefficients']['media']
    summary = (f"Holdout RMSE is {result['metrics']['test']['rmse']:.2f} count-equivalent across 12 months. "
               f"Estimated media coefficient {b['estimate']:.2f}, conditional 95% interval "
               f"[{b['lower']:.2f}, {b['upper']:.2f}], versus planted truth {truth['media_coefficient']:.2f}. "
               f"Coefficient error is {evaluation['media_coefficient_error']:.2f}; "
               'a single recovery run does not establish accuracy, power or causality.')
    return dict(dataset=DATASET, model=model, formula=formula, result=result,
                ground_truth=dict(media_coefficient=truth['media_coefficient'],
                                  noise_sd=truth['noise_sd'], estimator_access=False),
                evaluation=evaluation, interpretation=summary, warnings=LIMITS + result['diagnostics']['flags'],
                series=dict(periods=periods, outcome=outcome.tolist(),
                            synthetic_reference=reference, simulated_media=truth['true_contribution_monthly'],
                            estimated_baseline=(prediction-media).tolist(), estimated_media=media.tolist(),
                            prediction=prediction.tolist(), residual=(outcome-prediction).tolist(), spend=spend.tolist()),
                hashes=dict(data=result['data_sha256'], inventory=__import__('hashlib').sha256((root/'inventory.json').read_bytes()).hexdigest()),
                software=result['software'])
