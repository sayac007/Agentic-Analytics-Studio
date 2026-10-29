"""Extract reviewed FZ10 annual/model and 2026 monthly brand columns, retaining cells."""
import csv
import datetime as dt
import math
import hashlib
import json
import re
from pathlib import Path

from kba.extract import clean, MONTHS, publication
from . import source_path

ROOT = Path(__file__).resolve().parents[1]


def count(value, dash_zero=False):
    if value == '-' and dash_zero: return 0
    if value in (None, '', '-', '/', '.', '...', 'X'): return None
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or value != int(value):
        raise ValueError('Unreviewed count cell')
    return int(value)


def parse(path, record):
    import openpyxl
    from openpyxl.utils import get_column_letter
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['sha256']: raise ValueError('Raw hash mismatch')
    period = record['period']
    if not re.fullmatch(r'20[0-9]{2}-(0[1-9]|1[0-2])', period): raise ValueError('Invalid period')
    book = openpyxl.load_workbook(path, read_only=True, data_only=False)
    names = [n for n in book.sheetnames if n.replace(' ', '') == 'FZ10.1']
    if len(names) != 1: raise ValueError('Unknown table sheet')
    name=names[0]; rows=list(book[name].values)
    headers=[i for i,row in enumerate(rows[:12]) if any(clean(v)=='Insgesamt' for v in row) and any('Elektroantrieb' in clean(v) for v in row)]
    if len(headers)!=1:raise ValueError('Ambiguous drivetrain header')
    h=headers[0]; header=rows[h]; bev=next(i for i,v in enumerate(header) if 'Elektroantrieb' in clean(v))
    definition=clean(header[bev]); explicit=definition=='mit Elektroantrieb (BEV)'
    if definition not in ('mit Elektroantrieb','mit Elektroantrieb (BEV)'):raise ValueError('Unreviewed electric definition')
    label=MONTHS[int(period[5:])-1]+' '+period[:4]
    if clean(rows[h+1][3])!=label or clean(rows[h+1][bev])!=label:
        raise ValueError('Monthly column/reporting period mismatch')
    if 'Jan' not in clean(rows[h+1][4]) or period[:4] not in clean(rows[h+1][4]):raise ValueError('Wrong YTD column')
    if 'Marke' not in ' '.join(clean(v) for row in rows[h:h+2] for v in row[:3]):raise ValueError('Missing brand header')
    dash_evidence=None; license_cell=None; published=publication(None)
    for sheet in book:
        for ri,row in enumerate(sheet.values,1):
            for ci,value in enumerate(row):
                if value=='-' and ci+1<len(row) and 'nichts vorhanden' in clean(row[ci+1]).lower():
                    dash_evidence=f'{sheet.title}!{get_column_letter(ci+1)}{ri}:{get_column_letter(ci+2)}{ri}'
                if 'Datenlizenz Deutschland' in clean(value) and '2.0' in clean(value):license_cell=f'{sheet.title}!{get_column_letter(ci+1)}{ri}'
                if 'Veröffentlichung' in clean(value) and ci+1<len(row) and row[ci+1]:
                    v=row[ci+1]
                    published=({'value':v.date().isoformat(),'precision':'day','raw':str(v)}
                               if isinstance(v,dt.datetime) else publication(v))
    dash_zero=bool(dash_evidence)  # Missing legend preserves '-' as unknown, never guessed zero.
    brands=[];models=[]; active=None; market=None
    for ri,row in enumerate(rows[h+2:],h+3):
        brand,model=clean(row[1]),clean(row[2])
        if brand=='NEUZULASSUNGEN INSGESAMT':
            market={'all':count(row[4],dash_zero),'electric':count(row[bev+1],dash_zero),
                    'monthly_all':count(row[3],dash_zero),'monthly_electric':count(row[bev],dash_zero)};break
        standalone=bool(brand and not model and (type(row[3]) in (int,float) or type(row[4]) in (int,float)))
        if brand.endswith(' ZUSAMMEN') or brand=='SONSTIGE' or standalone:
            if model:raise ValueError('Ambiguous brand total row')
            b=brand.removesuffix(' ZUSAMMEN')
            if brand=='SONSTIGE ZUSAMMEN':b='SONSTIGE'
            for kind,col in [('all',3),('BEV' if explicit else 'electric_legacy_unverified_bev',bev)]:
                brands.append({'period':period,'brand':b,'powertrain':kind,
                               'monthly':count(row[col],dash_zero),'ytd':count(row[col+1],dash_zero),
                               'source_id':record['id'],'monthly_cell':f'{name}!{get_column_letter(col+1)}{ri}',
                               'ytd_cell':f'{name}!{get_column_letter(col+2)}{ri}'})
            continue
        if brand and model:active=brand
        if not model:continue
        if not active:raise ValueError('Model without known brand')
        models.append({'year':int(period[:4]),'reporting_period':period,'kba_brand':active,'model_family':model,
                       'electric_registrations_ytd':count(row[bev+1],dash_zero),'all_registrations_ytd':count(row[4],dash_zero),
                       'definition':'BEV' if explicit else 'electric_legacy_unverified_bev',
                       'source_id':record['id'],'count_cell':f'{name}!{get_column_letter(bev+2)}{ri}',
                       'selection_unit':'KBA_model_family_not_individual_variant'})
    if not market:raise ValueError('Missing market total')
    keys=[(r['brand'],r['powertrain']) for r in brands]
    if len(keys)!=len(set(keys)):raise ValueError('Duplicate brand total')
    reconciliation=[]
    for scope,kind,expected in [
        ('ytd','all',market['all']),
        ('ytd','BEV' if explicit else 'electric_legacy_unverified_bev',market['electric']),
        ('monthly','all',market['monthly_all']),
        ('monthly','BEV' if explicit else 'electric_legacy_unverified_bev',market['monthly_electric'])]:
        values=[r[scope] for r in brands if r['powertrain']==kind]
        known=sum(v for v in values if v is not None);missing=sum(v is None for v in values)
        if expected is None:
            reconciliation.append({'scope':scope,'powertrain':kind,'known_sum':known,'market_total':None,'suppressed_brand_cells':missing,'status':'total_not_published_no_imputation'})
            continue
        if (not missing and known!=expected) or known>expected:
            raise ValueError(f'Brand YTD reconciliation failed: {period} {kind}; known sum {sum(v for v in values if v is not None)}, expected {expected}, missing {sum(v is None for v in values)}')
        reconciliation.append({'scope':scope,'powertrain':kind,'known_sum':known,'market_total':expected,'suppressed_brand_cells':missing,'status':'passed' if not missing else 'incomplete_source_suppression_no_imputation'})
    positive=[m for m in models if m['model_family']!='SONSTIGE' and m['electric_registrations_ytd'] is not None and m['electric_registrations_ytd']>0]
    top=sorted(positive,key=lambda m:(-m['electric_registrations_ytd'],m['kba_brand'],m['model_family']))[:10]
    top=[{**row,'rank':i} for i,row in enumerate(top,1)]
    if len(top)!=10 and period.endswith('-12'):raise ValueError('Cannot identify ten positive model families')
    # No unknown or residual model can be silently excluded if it might enter the top 10.
    threshold=top[-1]['electric_registrations_ytd'] if top else float('inf')
    upper={r['brand']:r['ytd'] for r in brands if r['powertrain']=='all'}
    electric_upper={r['brand']:r['ytd'] for r in brands if r['powertrain']!='all'}
    known_by_brand={}
    for m in models:
        if m['electric_registrations_ytd'] is not None:known_by_brand[m['kba_brand']]=known_by_brand.get(m['kba_brand'],0)+m['electric_registrations_ytd']
    global_residual=market['electric']-sum(known_by_brand.values()) if market['electric'] is not None else None
    if global_residual is not None and global_residual < 0:
        raise ValueError('Known model counts exceed published electric market total')
    ambiguous=[]
    for m in models:
        if m['electric_registrations_ytd'] is not None and m['model_family']!='SONSTIGE':continue
        bound=m['electric_registrations_ytd'] if m['electric_registrations_ytd'] is not None else m['all_registrations_ytd']
        if bound is None:bound=upper.get(m['kba_brand'])
        brand_electric=electric_upper.get(m['kba_brand'])
        if m['electric_registrations_ytd'] is None and brand_electric is not None:
            residual=brand_electric-known_by_brand.get(m['kba_brand'],0)
            if residual>=0:bound=min(bound,residual) if bound is not None else residual
        if m['electric_registrations_ytd'] is None and global_residual is not None and global_residual>=0:
            bound=min(bound,global_residual) if bound is not None else global_residual
        if bound is None or bound>=threshold:ambiguous.append(m)
    return {'brands':brands,'models':models,'top10':top,
            'checks':{'source_id':record['id'],'period':period,'sheet':name,'header_row':h+1,
                      'electric_header':definition,'dash_zero_evidence':dash_evidence,'license_cell':license_cell,
                      'publication':published,'market_total':market,'brand_reconciliation':reconciliation,
                      'top10_ambiguous_rows':ambiguous if period.endswith('-12') else [],
                      'top10_status':('ambiguous' if ambiguous else 'passed') if period.endswith('-12') else 'not_ranked_monthly_release'}}


def write_csv(path, rows):
    if not rows:raise ValueError('Empty output')
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)


def run(catalog, raw_dir, output):
    records=json.loads(Path(catalog).read_text())['sources']; out=Path(output);out.mkdir(parents=True,exist_ok=True)
    brands=[];models=[];top=[];checks=[]
    for record in records:
        try:
            result=parse(source_path(raw_dir,record['file']),record)
        except ValueError as exc:
            raise ValueError(record['id']+': '+str(exc)) from exc
        brands.extend(result['brands']);checks.append(result['checks'])
        if record['period'].endswith('-12'):
            models.extend(result['models']);top.extend(result['top10'])
    write_csv(out/'brand_release_observations.csv',brands)
    write_csv(out/'model_annual_electric.csv',models)
    write_csv(out/'model_year_top10.csv',top)
    (out/'kba_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    return len(brands),len(models),len(top)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--catalog',required=True);p.add_argument('--raw-dir',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(run(a.catalog,a.raw_dir,a.output))
