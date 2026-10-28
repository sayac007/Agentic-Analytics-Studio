"""Read the already audited observations without changing their source snapshots."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERIODS = [f'{year:04d}-{month:02d}' for year in range(2018, 2026) for month in range(1, 13)]
ATTRIBUTION = {
    'cpi': 'Datenquelle: Statistisches Bundesamt (Destatis), nationaler Verbraucherpreisindex 2020=100; Datenlizenz Deutschland – Namensnennung – Version 2.0.',
    'consumer_credit': 'Source: ECB statistics, MIR consumption-credit AAR/NDER. Preserve native statistics/metadata and ESCB third-party exceptions.',
    'eurusd': 'Source: ECB statistics, EXR.M.USD.EUR.SP00.A, monthly USD per EUR; native source and metadata preserved separately.',
    'diesel_de': 'Source: European Commission, Directorate-General for Energy, Weekly Oil Bulletin, Germany automotive gas oil, prices including taxes. EUR/litre conversion and calendar-overlap monthly estimates calculated by Agentic Analytics Studio; not official monthly means. Source acknowledged under embedded reproduction notice.',
    'tesla_count': 'Datenquelle: Kraftfahrt-Bundesamt, Flensburg; dl-de/by-2-0. Tesla brand all-powertrain new registrations, not orders.'}
UNITS = {'cpi': 'index_2020_100', 'consumer_credit': 'percent_per_annum',
         'eurusd': 'USD_per_EUR', 'diesel_de': 'EUR_per_litre'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def read_bound(root, name, expected):
    path = root / name
    if path.is_symlink() or path.parent.resolve() != root.resolve():
        raise ValueError('Unsafe source path')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('Source hash mismatch: ' + name)
    return raw


def load(archive):
    root = Path(archive).resolve()
    if root.is_relative_to(ROOT):
        raise ValueError('Empirical source archive must remain outside Git')
    frozen = json.loads((ROOT / 'data/verified_sources/manifest.json').read_text())
    metadata = json.loads((root / 'manifest.json').read_text())
    if metadata.get('normalized_files') != frozen['normalized_files']:
        raise ValueError('Unreviewed normalized source snapshot')
    # Bind all four actual native source inputs and CPI dimension/unit evidence.
    required = {('consumer_credit', 'native_csv'), ('eurusd', 'native_csv'),
                ('cpi', 'verified_base_data'), ('cpi', 'verified_table_structure'),
                ('cpi', 'verified_quality_signs'), ('diesel_de', 'original_weekly_workbook')}
    for identity in required:
        old = [r for r in frozen['requests'] if (r['source'], r['role']) == identity and r.get('raw_path')]
        current = [r for r in metadata['requests'] if (r['source'], r['role']) == identity and r.get('raw_path')]
        if len(old) != 1 or len(current) != 1 or any(current[0].get(k) != old[0].get(k) for k in ('sha256', 'url', 'raw_path', 'status')):
            raise ValueError('Source identity changed')
        read_bound(root, old[0]['raw_path'], old[0]['sha256'])
    # Historical policy reviews remain bound records. Restoring the identical data
    # does not claim a fresh policy-page access or blanket redistribution rights.
    policy_evidence = []
    for name in ('ecb--reuse_policy.bin', 'commission--reuse_policy.bin', 'destatis--genesis_specific_license.bin'):
        row = next(r for r in frozen['requests'] if r.get('raw_path') == name)
        actual = [r for r in metadata['requests'] if r.get('raw_path') == name]
        if len(actual) != 1 or any(actual[0].get(k) != row.get(k) for k in ('source', 'role', 'url', 'sha256', 'status', 'accessed_at_utc')):
            raise ValueError('Historical source-policy review changed')
        policy_evidence.append({k: row[k] for k in ('source', 'url', 'sha256', 'accessed_at_utc')})
    values, provenance = {}, {}
    for source, unit in UNITS.items():
        name = source + '.normalized.csv'
        raw = read_bound(root, name, frozen['normalized_files'][name])
        rows = list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
        if len(rows) != 96 or [r['period'] for r in rows] != PERIODS:
            raise ValueError('Duplicate, missing or unordered source months')
        result = []
        for row in rows:
            if row['unit'] != unit:
                raise ValueError('Source unit mismatch: ' + source)
            value = None if row['value'] == '' else float(row['value'])
            if value is not None and (not math.isfinite(value) or (source != 'consumer_credit' and value <= 0)):
                raise ValueError('Invalid observed value')
            result.append(value)
        missing = [p for p, v in zip(PERIODS, result) if v is None]
        if missing != frozen['coverage'][source]['missing']:
            raise ValueError('Source missingness drift')
        values[source] = result
        urls = [r['url'] for r in frozen['requests'] if r['source'] == source and r.get('raw_path') and r['role'] in ('native_csv', 'verified_base_data', 'original_weekly_workbook')]
        provenance[source] = {'unit': unit, 'classification': 'observed' if source != 'diesel_de' else 'derived_observed_weekly_overlap_approximation',
                              'attribution': ATTRIBUTION[source], 'reuse_scope': 'private_retrospective_exploratory_only_no_public_approval',
                              'sha256': sha(raw), 'observed_months': 96-len(missing), 'missing_months': missing, 'urls': urls}
    raw = (ROOT / 'data/kba/derived/observations.csv').read_bytes()
    inventory = json.loads((ROOT / 'data/kba/derived/inventory.json').read_text())
    # The existing KBA audit validates complete provenance, reconciliation and hashes.
    from kba.pipeline import audit
    if sha(raw) != inventory['observations.csv']:
        raise ValueError('KBA observations hash mismatch')
    audit(ROOT / 'data/kba/sources.json', ROOT / 'data/kba/acquisition-plan.json', ROOT / 'data/kba/derived')
    rows = [r for r in csv.DictReader(raw.decode().splitlines()) if r['series'] == 'brand:TESLA' and r['period'] in PERIODS]
    by = {r['period']: r for r in rows}
    if len(rows) != 96 or set(by) != set(PERIODS) or any(r['powertrain'] != 'all' or not r['value'].isdigit() for r in rows):
        raise ValueError('Invalid KBA Tesla definition/calendar')
    values['tesla_count'] = [int(by[p]['value']) for p in PERIODS]
    provenance['tesla_count'] = {'unit': 'new_registrations_all_powertrains', 'classification': 'observed',
                                 'attribution': ATTRIBUTION['tesla_count'], 'reuse_scope': 'dl-de/by-2-0_retrospective_no_historical_asof_claim',
                                 'sha256': sha(raw), 'observed_months': 96, 'missing_months': [],
                                 'urls': ['https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz10_n_uebersicht.html']}
    ledger = json.loads((ROOT / 'data/tesla_product_events/evidence.json').read_text())
    sources = {r['source_id']: r for r in ledger['sources']}
    events = []
    for event in ledger['events']:
        date = event['date']['value']
        if date and date[:7] in PERIODS and event['status'] in ('verified', 'partial'):
            events.append({'id': event['event_id'], 'title': event['title'], 'date': date,
                           'precision': event['date']['precision'], 'status': event['status'],
                           'type': event['event_type'], 'sources': [{'url': sources[s]['url'], 'publisher': sources[s]['publisher']} for s in event['source_ids']]})
    return {'classification': 'OBSERVED_PRIVATE', 'periods': PERIODS, 'series': values,
            'sources': provenance, 'events': events, 'historical_policy_review': policy_evidence,
            'warnings': ['Retrospective observations; historical point-in-time availability is not established.',
                         'Registrations are not orders or a direct measure of demand; delivery timing remains a possible driver.',
                         'Diesel is a calendar-overlap approximation with 13 unfilled months.',
                         'Event ledger coverage is incomplete. Missing evidence is not an absent launch/promotion.',
                         'Unresolved EC third-party/member-state scope limitations remain; qualified private acceptance is not a legal guarantee.',
                         'Private analytical use only; no public raw/derived redistribution approval.']}
