"""Offline validation and transparent views of manually researched offer snapshots.

No price interpolation, annual averaging, regression, or causal attribution.
"""
import argparse
import csv
import datetime as dt
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

from .kba import write_csv
from . import source_path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'competition'


def positive(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a number')
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Invalid number') from exc
    if not number.is_finite() or number <= 0:
        raise ValueError('Expected positive finite number')
    return number


def validate(observations, sources):
    ids = [s['id'] for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate source ID')
    for s in sources:
        if not re.fullmatch(r'[0-9a-f]{64}', s['sha256']):
            raise ValueError('Invalid source hash')
        if not s['url'].startswith('https://') or '@' in s['url'].split('/')[2]:
            raise ValueError('Expected public HTTPS source')
    seen = set()
    kinds = {'list', 'derived_battery_inclusive_list', 'promotion_after_manufacturer',
             'promotion_after_manufacturer_and_state',
             'displayed_price_manufacturer_bonus_already_deducted'}
    for r in observations:
        if r['id'] in seen:
            raise ValueError('Duplicate offer ID')
        seen.add(r['id'])
        date = r['price_date']
        if r['date_precision'] not in {'day', 'month'}:
            raise ValueError('Unknown date precision')
        pattern = r'\d{4}-\d{2}-\d{2}' if r['date_precision'] == 'day' else r'\d{4}-\d{2}'
        if not re.fullmatch(pattern, date):
            raise ValueError('Invalid offer date')
        dt.date.fromisoformat(date if len(date) == 10 else date + '-01')
        if r['source_id'] not in ids or (r['range_source_id'] is not None and r['range_source_id'] not in ids):
            raise ValueError('Unbound source')
        if r['geography'] != 'DE' or r['currency'] != 'EUR' or r['annual_average'] is not False:
            raise ValueError('Offer scope mismatch')
        if r.get('quoted_price_operator', 'eq') not in {'eq', 'lt'}:
            raise ValueError('Unknown price bound')
        price, distance = r['quoted_price_eur'], r['range_km_upper_or_bound']
        if price is None and distance is None:
            raise ValueError('Empty observation')
        if price is not None:
            positive(price)
            if r['price_kind'] not in kinds:
                raise ValueError('Unknown price kind')
        if distance is not None:
            positive(distance)
            if r['range_cycle'] not in {'WLTP_combined', 'NEDC'}:
                raise ValueError('Unreviewed range cycle')
            if r['range_operator'] not in {'up_to', 'gt', 'eq'}:
                raise ValueError('Unreviewed range bound')
            if not r['range_source_id']:
                raise ValueError('Unbound range')
            if r['range_scope'] != 'same_variant_equipment_envelope':
                raise ValueError('Range is not matched to variant')
            if r['range_km_lower'] is not None and positive(r['range_km_lower']) > positive(distance):
                raise ValueError('Inverted range envelope')
        if r['offer_end'] is not None:
            if dt.date.fromisoformat(r['offer_end']) < dt.date.fromisoformat(date if len(date) == 10 else date+'-01'):
                raise ValueError('Offer ends before observation')


def ratio(row):
    """Acquisition-price/declared-range ratio, never a travel-cost metric.

Conservatively require gross battery-inclusive list price and a matched WLTP
variant. Even then this is an equipment envelope, not a configured-car quote.
"""
    reasons = []
    if row['quoted_price_eur'] is None or row['range_km_upper_or_bound'] is None:
        reasons.append('price_or_matched_range_missing')
    if row['price_kind'] not in {'list', 'derived_battery_inclusive_list'}:
        reasons.append('not_unsubsidized_list_price')
    if row.get('quoted_price_operator', 'eq') != 'eq':
        reasons.append('price_is_bound')
    if row['vat'] != 'included':
        reasons.append('VAT_not_explicit')
    if row['battery_in_price'] != 'included':
        reasons.append('battery_not_included_or_unverified')
    if row['range_cycle'] != 'WLTP_combined':
        reasons.append('no_matched_combined_WLTP')
    if row['range_operator'] not in {'up_to', 'eq'}:
        reasons.append('range_is_open_bound_or_missing')
    if row.get('quality_flags'):
        reasons.extend(row['quality_flags'])
    if reasons:
        return {'ratio_status': ';'.join(reasons), 'eur_per_100km_declared_max_range': '',
                'eur_per_100km_declared_min_range': ''}
    price = positive(row['quoted_price_eur'])
    def calculate(km):
        return str((price * 100 / positive(km)).quantize(Decimal('0.01')))
    return {'ratio_status': 'variant_envelope_not_configured_car',
            'eur_per_100km_declared_max_range': calculate(row['range_km_upper_or_bound']),
            'eur_per_100km_declared_min_range': calculate(row['range_km_lower']) if row['range_km_lower'] else ''}


def matches(offer, model):
    families = [model['model_family']]
    if model['kba_brand'] == 'VW' and model['model_family'] == 'ID.4, ID.5':
        families = ['ID.4', 'ID.5']
    return (offer['brand'] == model['kba_brand'] and offer['kba_model_family'] in families
            and offer['price_date'][:4] == str(model['year']))


def brand_views(data_dir, output):
    with (data_dir/'brand_release_observations.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    checks = json.loads((data_dir/'kba_checks.json').read_text())
    market = {r['period']: r['market_total'] for r in checks}
    monthly = [{**r, 'source_classification': 'observed',
                'row_absence_policy': 'missing_not_zero'} for r in rows if r['period'] >= '2021-01']
    write_csv(output/'brand_monthly_2021_2026.csv', monthly)
    annual = []
    for r in rows:
        if not r['period'].endswith('-12'):
            continue
        denominator = market[r['period']]['all' if r['powertrain']=='all' else 'electric']
        share = str((Decimal(r['ytd']) / denominator * 100).quantize(Decimal('0.000001'))) if r['ytd'] and denominator else ''
        annual.append({**r, 'share_in_same_powertrain_percent': share})
    write_csv(output/'brand_annual_2018_2025.csv', annual)
    comparison = []
    for powertrain in ['all', 'BEV']:
        selected = [r for r in rows if r['period'] in {'2025-09','2026-09'} and r['powertrain']==powertrain and r['brand']!='SONSTIGE']
        by_key = {(r['period'],r['brand']):r for r in selected}
        for brand in sorted({r['brand'] for r in selected}):
            previous, current = [by_key.get((p,brand)) for p in ['2025-09','2026-09']]
            old, new = [r['ytd'] if r else '' for r in [previous,current]]
            growth = str(((Decimal(new)/Decimal(old)-1)*100).quantize(Decimal('0.01'))) if old and int(old)>0 and new else ''
            comparison.append({'brand':brand,'powertrain':powertrain,'comparison':'Jan-Sep_vs_Jan-Sep',
                               'registrations_2025_ytd':old,'registrations_2026_ytd':new,'growth_percent':growth,
                               'previous_source_id':previous['source_id'] if previous else '',
                               'current_source_id':current['source_id'] if current else '',
                               'status':'observed_same_month_cutoff' if old and new else 'missing_not_imputed',
                               'brand_definition_note':'KGM renamed SSANGYONG2025-04-01; not a new entrant' if brand in {'KGM','SSANGYONG'} else 'KBA reporting brand; not ownership or production country'})
    write_csv(output/'brand_ytd_comparison.csv',comparison)


def derive(data_dir=ROOT, output=None):
    data_dir = Path(data_dir)
    output = Path(output or data_dir)
    offers = json.loads((data_dir/'price_observations.json').read_text())['observations']
    sources = json.loads((data_dir/'price_sources.json').read_text())['sources']
    validate(offers, sources)
    index = {s['id']: s for s in sources}
    view = []
    for o in offers:
        view.append({**{k: v for k, v in o.items() if k != 'quality_flags'},
                     'quality_flags': ';'.join(o.get('quality_flags', [])),
                     **ratio(o), 'source_url': index[o['source_id']]['url'],
                     'source_sha256': index[o['source_id']]['sha256']})
    # CSV columns are the union: optional price bound must not disappear.
    keys = list(dict.fromkeys(k for r in view for k in r))
    view = [{k: r.get(k) for k in keys} for r in view]
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output/'prices_and_ranges.csv', view)
    with (data_dir/'model_year_top10.csv').open(encoding='utf-8', newline='') as handle:
        top = list(csv.DictReader(handle))
    coverage = []
    for m in top:
        found = [o for o in offers if matches(o, m)]
        prices = [o for o in found if o['quoted_price_eur'] is not None
                  and o.get('quoted_price_operator','eq') == 'eq' and not o.get('quality_flags')]
        paired = [o for o in prices if o['range_km_upper_or_bound'] is not None]
        coverage.append({**m, 'offer_count_same_calendar_year': len(found),
                         'exact_price_points': len(prices), 'matched_variant_price_range_points': len(paired),
                         'gross_list_WLTP_ratio_points': sum(ratio(o)['ratio_status'] == 'variant_envelope_not_configured_car' for o in found),
                         'offer_ids': ';'.join(o['id'] for o in found),
                         'coverage_status': 'partial_dated_snapshots' if prices else 'price_missing_no_backfill',
                         'full_year_entry_and_top_coverage': False,
                         'mapping_status': 'combined_family_components_partial' if m['model_family']=='ID.4, ID.5' else 'named_family_only'})
    write_csv(output/'price_coverage_by_model_year.csv', coverage)
    brand_views(data_dir, output)
    return {'offer_observations':len(offers),'price_sources':len(sources),
            'top10_model_years':len(top),
            'model_years_with_exact_price':sum(r['exact_price_points']>0 for r in coverage),
            'model_years_with_price_range_pair':sum(r['matched_variant_price_range_points']>0 for r in coverage),
            'full_year_price_panel_complete':False}


def verify_raw(catalogs, raw_dir):
    checked = 0
    for path in catalogs:
        for s in json.loads(Path(path).read_text())['sources']:
            p = source_path(raw_dir,s['file'])
            if p.stat().st_size != s['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != s['sha256']:
                raise ValueError('Raw hash/size mismatch: ' + s['id'])
            checked += 1
    return checked


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir', type=Path, default=ROOT)
    p.add_argument('--output', type=Path)
    p.add_argument('--raw-dir', type=Path)
    a = p.parse_args()
    if a.raw_dir:
        print('Verified source snapshots:', verify_raw([a.data_dir/'kba_sources.json', a.data_dir/'price_sources.json'], a.raw_dir))
    print(json.dumps(derive(a.data_dir, a.output), sort_keys=True))
