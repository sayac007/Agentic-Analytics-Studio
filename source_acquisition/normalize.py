"""Source-specific data QA, private only; never joins outcomes or admits models."""
import argparse
import csv
from datetime import date, datetime
import hashlib
import io
import json
import math
from pathlib import Path

from fuel_oil.fetch_fuel_oil import month_range, parse_fx, weekly_monthly
from fuel_oil.import_energy import parse_diesel

ROOT=Path(__file__).resolve().parents[1]
START,END='2018-01','2025-12'


def credit(raw):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    checks={'KEY':'MIR.M.DE.B.A2B.A.R.A.2250.EUR.N','FREQ':'M','REF_AREA':'DE','BS_ITEM':'A2B',
            'MATURITY_NOT_IRATE':'A','DATA_TYPE_MIR':'R','IR_BUS_COV':'N','BS_COUNT_SECTOR':'2250',
            'CURRENCY_TRANS':'EUR','UNIT':'PCPA','UNIT_MULT':'0'}
    if not reader.fieldnames or not set(checks)|{'TIME_PERIOD','OBS_VALUE','OBS_STATUS'}<=set(reader.fieldnames):
        raise ValueError('Expected native MIR CSV, not an HTML page or alternative rate')
    if len(reader.fieldnames)!=len(set(reader.fieldnames)):raise ValueError('Duplicate headers')
    rows=[]
    for r in reader:
        if None in r or None in r.values() or any(r[k]!=v for k,v in checks.items()):raise ValueError('MIR identity/unit/AAR drift; APRC is not accepted')
        p=r['TIME_PERIOD'];date.fromisoformat(p+'-01')
        if r['OBS_STATUS'] not in ('A','P','E','M'):raise ValueError('Unrecognized MIR status')
        if not r['OBS_VALUE']:
            if r['OBS_STATUS']!='M':raise ValueError('Missing value without missing status')
            v=None
        else:
            v=float(r['OBS_VALUE'])
            if not math.isfinite(v) or r['OBS_STATUS']=='M':raise ValueError('Invalid native rate/status')
        rows.append(dict(period=p,value=v,source_status=r['OBS_STATUS'],unit='percent_per_annum',quality='source_native_monthly_AAR_NDER'))
    if len({r['period'] for r in rows})!=len(rows):raise ValueError('Duplicate/revised MIR periods')
    return rows


def cpi(data_raw,structure_raw,signs_raw):
    payload=json.loads(data_raw);structure=json.loads(structure_raw);signs=json.loads(signs_raw)
    if structure['table']['code']!='61111-0002' or structure['contents']['PREIS1']['functions']['QMU']['label']['de']!='2020=100':
        raise ValueError('Not national CPI 61111-0002, base 2020=100')
    if len(payload['data'])!=1:raise ValueError('Unexpected multiple datasets')
    ds=payload['data'][0];ids=ds['id'];sizes=ds['size']
    if set(ids)!={'statistic','DINSG','content','MONAT','JAHR'} or len(set(ids))!=5 or len(sizes)!=5:
        raise ValueError('Unreviewed CPI dimensions')
    maps={k:ds['dimension'][k]['category']['index'] for k in ids}
    for k,size in zip(ids,sizes):
        if sorted(maps[k].values())!=list(range(size)):raise ValueError('Non-bijective CPI dimension')
    if len(ds['value'])!=math.prod(sizes) or len(ds['status'])!=math.prod(sizes):raise ValueError('CPI payload length mismatch')
    if set(maps['statistic'])!={'61111'} or set(maps['DINSG'])!={'DG'} or 'PREIS1$QMU' not in maps['content']:
        raise ValueError('Wrong CPI concept/country/statistic')
    rows=[]
    for year in maps['JAHR']:
        for month in maps['MONAT']:
            if not year.isdigit() or not month.startswith('MONAT'):raise ValueError('Invalid CPI date dimensions')
            p=f'{int(year):04d}-{int(month[5:]):02d}';date.fromisoformat(p+'-01')
            selected={'statistic':'61111','DINSG':'DG','content':'PREIS1$QMU','MONAT':month,'JAHR':year}
            index=0
            for dim,size in zip(ids,sizes):index=index*size+maps[dim][selected[dim]]
            status=ds['status'][index];v=ds['value'][index]
            if status in signs['signsReplacingValue']:
                v=None  # e.g. source placeholder zero with '-' is missing, never an index of zero.
            elif status not in signs['signsWithValue'] or isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0:
                raise ValueError('Invalid CPI value/status; no conversion from change percentages')
            rows.append(dict(period=p,value=v,source_status=status,unit='index_2020_100',quality='source_native_national_CPI'))
    return sorted(rows,key=lambda r:r['period'])


def coverage(rows):
    expected=month_range(START,END);by={r['period']:r for r in rows}
    if len(by)!=len(rows):raise ValueError('Duplicate periods')
    missing=[p for p in expected if p not in by or by[p]['value'] is None]
    return dict(start=START,end=END,expected=len(expected),present=len(expected)-len(missing),missing=missing,
                interpolation='none',forward_fill='none',historical_point_in_time='not_established')


def save_csv(path,rows):
    selected=[r for r in rows if START<=r['period']<=END]
    text=io.StringIO(newline='')
    writer=csv.DictWriter(text,fieldnames=list(selected[0]));writer.writeheader();writer.writerows(selected)
    raw=text.getvalue().encode()
    if path.exists():
        if path.is_symlink() or path.read_bytes()!=raw:raise ValueError('Existing normalized snapshot changed')
    else:
        with path.open('xb') as f:f.write(raw)


def run(archive):
    root=Path(archive).resolve()
    if root.is_relative_to(ROOT):raise ValueError('Numerical QA must remain outside Git')
    m=json.loads((root/'manifest.json').read_text())
    sources={}
    def source_raw(source,role):
        found=[r for r in m['requests'] if r['source']==source and r['role']==role and r.get('raw_path')]
        if len(found)!=1:raise ValueError('Missing/duplicate source '+source+'/'+role)
        path=(root/found[0]['raw_path']).resolve()
        if not path.is_relative_to(root) or (root/found[0]['raw_path']).is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=found[0]['sha256']:raise ValueError('Source hash mismatch')
        return path.read_bytes()
    sources['consumer_credit']=credit(source_raw('consumer_credit','native_csv'))
    sources['eurusd']=parse_fx(source_raw('eurusd','native_csv'))
    sources['cpi']=cpi(source_raw('cpi','verified_base_data'),source_raw('cpi','verified_table_structure'),source_raw('cpi','verified_quality_signs'))
    old=json.loads((ROOT/'data/fuel_oil/real_sources.json').read_text())['files']['diesel_de']
    diesel_raw=source_raw('diesel_de','original_weekly_workbook')
    if hashlib.sha256(diesel_raw).hexdigest()!=old['sha256']:raise ValueError('New diesel vintage requires review; old rights/unit proof not silently transferred')
    weekly=parse_diesel(diesel_raw,old['unit_evidence'])
    retrieved=next(r['accessed_at_utc'] for r in m['requests'] if r['source']=='diesel_de' and r['role']=='original_weekly_workbook')
    sources['diesel_de']=weekly_monthly(weekly,START,END,datetime.fromisoformat(retrieved).date())
    expected_missing=json.loads((ROOT/'data/fuel_oil/rights_admission.json').read_text())['diesel_missingness']['missing_months']
    if coverage(sources['diesel_de'])['missing']!=expected_missing:raise ValueError('Diesel missingness drift')
    outputs={};reports={}
    for key,rows in sources.items():
        name=key+'.normalized.csv';save_csv(root/name,rows)
        outputs[name]=hashlib.sha256((root/name).read_bytes()).hexdigest();reports[key]=coverage(rows)
    reports['brent']=dict(start=START,end=END,expected=96,present=0,missing=month_range(START,END),
        status='blocked_third_party_rights_Refinitiv_LSEG',api_request='not_attempted_rights_gate',model_admission=False)
    m.update(scope='PRIVATE_PRIMARY_SOURCE_ARCHIVE_AND_QA_NO_MODEL_ADMISSION',normalized_files=outputs,coverage=reports,
             numerical_observations_acquired=sum(reports[key]['present'] for key in sources),
             observation_count_scope='Nonmissing normalized monthly values, 2018-01..2025-12; diesel is derived, not native monthly',
             native_rows_acquired={'consumer_credit':len(sources['consumer_credit']),'eurusd':len(sources['eurusd']),'cpi':len(sources['cpi']),'diesel_weekly':len(weekly)},
             model_admission=False,public_raw_or_derived_redistribution_approved=False,
             note='Raw source bytes unchanged. Native observations/derived weekly-overlap approximations remain private. Prior source-specific rights/approval limitations are preserved.')
    (root/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    print(json.dumps(reports,indent=2))
    return m


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path);run(p.parse_args().archive)


if __name__=='__main__':main()
