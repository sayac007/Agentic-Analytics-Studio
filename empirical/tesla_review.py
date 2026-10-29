"""Descriptive review of actual existing evidence. No new fits or driver selection."""
import csv
import json
from .data import ROOT, sha, json_bytes
from .service import read

COMPARATORS = {'tesla_count': 'brand:TESLA', 'market_bev': 'market:BEV',
               'vw_count': 'brand:VW', 'toyota_count': 'brand:TOYOTA'}


def market_data(base):
    from kba.pipeline import audit
    root = ROOT/'data/kba'
    audit(root/'sources.json', root/'acquisition-plan.json', root/'derived')
    raw = (root/'derived/observations.csv').read_bytes()
    rows = list(csv.DictReader(raw.decode().splitlines()))
    result = {}
    for key, series_id in COMPARATORS.items():
        chosen = [r for r in rows if r['series'] == series_id and r['period'] in base['data']['periods']]
        expected_powertrain = 'BEV_only' if key == 'market_bev' else 'all'
        if len({r['period'] for r in chosen}) != len(chosen) or any(r['powertrain'] != expected_powertrain or not r['value'].isdigit() for r in chosen):
            raise ValueError('Invalid KBA comparator definition/calendar')
        by = {r['period']: int(r['value']) for r in chosen}
        result[key] = [by.get(p) for p in base['data']['periods']]
    if result['tesla_count'] != base['data']['series']['tesla_count']:
        raise ValueError('Tesla reference differs from the already analyzed snapshot')
    return result, sha(raw)


def annual(data, periods):
    output = []
    for year in sorted({p[:4] for p in periods}):
        indices = [i for i,p in enumerate(periods) if p[:4] == year]
        row = {'year': year, 'series': {}}
        for key, values in data.items():
            observed = [values[i] for i in indices if values[i] is not None]
            total = sum(observed) if len(observed) == 12 and len(indices) == 12 else None
            ends = sum(values[i] for i in indices if periods[i][5:] in ('03','06','09','12')) if total is not None else None
            previous = output[-1]['series'][key]['total'] if output else None
            row['series'][key] = {'observed_months': len(observed), 'total': total,
                                  'yoy_fraction': total/previous-1 if total is not None and previous else None,
                                  'quarter_end_fraction': ends/total if total else None}
        output.append(row)
    return output


def review(directory):
    return review_bundle(read(directory))


def review_bundle(base):
    comparators, kba_hash = market_data(base)
    models = {}
    for key,m in base['results']['models'].items():
        if m['status'] != 'estimated':
            models[key] = {'status': m['status'], 'reason': m['reason']}; continue
        models[key] = {'status': 'estimated', 'n_full': m['full']['n'], 'n_training': m['training']['n'],
                       'n_2025': len(m['holdout']['periods']), 'r2_changes': m['full']['metrics']['r2'],
                       'paired_r2_changes': m['paired_comparator']['full_metrics']['r2'],
                       'rmse_2025': m['holdout']['count_metrics']['rmse'],
                       'mae_2025': m['holdout']['count_metrics']['mae'],
                       'paired_rmse_2025': m['paired_comparator']['holdout_count_metrics']['rmse'],
                       'rmse_difference': m['holdout']['count_metrics']['rmse']-m['paired_comparator']['holdout_count_metrics']['rmse'],
                       'training_residual_stationarity': m['stationarity']['training_residuals']['verdict'],
                       'full_residual_stationarity': m['stationarity']['full_residuals']['verdict']}
    return {'snapshot_sha256': base['snapshot_sha256'], 'kba_observations_sha256': kba_hash,
            'protocol_sha256': base['provenance']['protocol_sha256'],
            'annual': annual(comparators, base['data']['periods']), 'models': models,
            'calendar_coefficients': base['results']['models']['calendar']['full']['coefficients'],
            'stationarity': base['results']['outcome_stationarity'],
            'event_candidates': base['data']['events'], 'limits': base['results']['limits']}


def evidence_context(base):
    path = ROOT/'data/kba/derived/observations.csv'
    if base['data']['sources']['tesla_count'].get('sha256') != sha(path.read_bytes()):
        return {'status': 'not_bound_to_kba_catalogue'}
    result = review_bundle(base)
    return {'status': 'verified_existing_evidence', 'snapshot_sha256': result['snapshot_sha256'],
            'scope': 'Tesla/VW/Toyota: all powertrains; market_bev: BEV only. No exact matched-segment share or causal decomposition.',
            'annual_last_three_years': [{'year': row['year'], 'series': {key: {k:v for k,v in values.items() if k in ('total','yoy_fraction','quarter_end_fraction')}
                                        for key,values in row['series'].items() if key in ('tesla_count','market_bev')}} for row in result['annual'][-3:]],
            'fixed_model_comparison': {key: {k:v for k,v in m.items() if k in ('n_full','n_2025','r2_changes','rmse_difference','training_residual_stationarity','status')}
                                       for key,m in result['models'].items()},
            'not_estimated': ['transaction prices/promotions', 'product-specific supply and orders',
                              'causal subsidy, launch or brand effects']}


def joint_data(base):
    """One explicit calendar; no fabricated pre-2021 BEV values or event zeros."""
    data = json.loads(json.dumps(base['data'], allow_nan=False))
    comparators, digest = market_data(base)
    for key in ('market_bev', 'vw_count', 'toyota_count'):
        data['series'][key] = comparators[key]
        data['sources'][key] = {'unit': 'new_registrations_BEV_only' if key == 'market_bev' else 'new_registrations_all_powertrains',
                                'classification': 'observed', 'definition': COMPARATORS[key],
                                'sha256': digest, 'source_reference': 'Audited KBA FZ10 observations.csv',
                                'attribution': 'Kraftfahrt-Bundesamt, Flensburg; dl-de/by-2-0',
                                'reuse_scope': 'retrospective_comparator_no_historical_asof_claim',
                                'observed_months': sum(x is not None for x in comparators[key]),
                                'missing_months': [p for p,v in zip(data['periods'],comparators[key]) if v is None]}
    return data


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--existing-results', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args()
    if a.output.resolve().is_relative_to(ROOT):p.error('Output must stay private outside Git')
    payload=review(a.existing_results)
    a.output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with a.output.open('xb') as f:f.write(json_bytes(payload))
    a.output.chmod(0o600)
    print('Reviewed existing evidence; no fits. Private output SHA-256:',sha(a.output.read_bytes()))
