"""Primary-source metadata/rights review; private immutable responses, no models."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from fuel_oil.fetch_fuel_oil import redact, safe_url

ALLOWED_HOSTS = {
 'ecb': {'www.ecb.europa.eu'},
 'consumer_credit': {'data.ecb.europa.eu','data-api.ecb.europa.eu'},
 'eurusd': {'data.ecb.europa.eu','data-api.ecb.europa.eu'},
 'destatis': {'www.destatis.de'},
 'cpi': {'www-genesis.destatis.de','genesis.destatis.de'},
 'commission': {'commission.europa.eu'},
 'diesel_de': {'energy.ec.europa.eu'},
 'eia': {'www.eia.gov'}, 'brent': {'www.eia.gov'},
}

REQUESTS = [
    ('ecb','reuse_policy','https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html'),
    ('consumer_credit','series_metadata','https://data.ecb.europa.eu/data/datasets/MIR/MIR.M.DE.B.A2B.A.R.A.2250.EUR.N'),
    ('eurusd','series_metadata','https://data.ecb.europa.eu/data/datasets/EXR/EXR.M.USD.EUR.SP00.A'),
    ('destatis','reuse_policy','https://www.destatis.de/DE/Service/Impressum/copyright.html'),
    ('cpi','table_metadata','https://www-genesis.destatis.de/datenbank/online/statistic/61111/table/61111-0002'),
    ('commission','reuse_policy','https://commission.europa.eu/legal-notice_en'),
    ('diesel_de','dataset_metadata','https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en'),
    ('eia','reuse_policy','https://www.eia.gov/about/copyrights_reuse.php'),
    ('brent','third_party_source_notes','https://www.eia.gov/dnav/pet/TblDefs/pet_pri_spt_tbldef2.asp'),
]


def fetch_review(item):
    source,role,url=item
    row=dict(source=source,role=role,url=url,
             attempted_at_utc=datetime.now(timezone.utc).isoformat(),accessed_at_utc=None,
             status=None,sha256=None,bytes=0,error=None)
    try:
        safe_url(url)
        if urlsplit(url).hostname not in ALLOWED_HOSTS.get(source,set()):raise ValueError('Not an allowlisted primary publisher')
        request=urllib.request.Request(url,headers={'User-Agent':'AgenticAnalyticsStudio/primary-source-review'})
        with urllib.request.urlopen(request,timeout=20) as response:
            safe_url(response.geturl())
            if urlsplit(response.geturl()).hostname not in ALLOWED_HOSTS.get(source,set()):raise ValueError('Unexpected publisher redirect')
            raw=response.read(20*1024*1024+1)
            if len(raw)>20*1024*1024:raise ValueError('Review response exceeds byte limit')
            row.update(status=response.status,final_url=response.geturl())
            if response.status!=200:raise ValueError('Non-200 source response')
            row.update(accessed_at_utc=datetime.now(timezone.utc).isoformat(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
            return row,raw
    except urllib.error.HTTPError as error:
        row.update(status=error.code,error=f'HTTP {error.code}: {error.reason}')
    except (OSError,ValueError) as error:
        row['error']=redact(str(error))
    return row,None


def run(output, acquire=False):
    root=Path(output).resolve()
    repo=Path(__file__).resolve().parents[1]
    if root.exists() or root.is_relative_to(repo):raise ValueError('New PRIVATE directory outside Git required')
    results=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        acquired=list(pool.map(fetch_review,REQUESTS))
    root.mkdir(parents=True,mode=0o700)
    for row,raw in acquired:
        if raw is not None:
            name=f"{row['source']}--{row['role']}.bin"
            (root/name).write_bytes(raw);row['raw_path']=name
        results.append(row)
    manifest=dict(scope='PRIVATE_PRIMARY_SOURCE_RIGHTS_AND_METADATA_REVIEW',requests=results,
                  numerical_observations_acquired=0,
                  note='Policy/metadata responses are not observations or automatic rights clearance. Source-specific review precedes any dataset fetch.')
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    if acquire:
        verify_current_rights(root, require_destatis=False)
        append_fetches(root, ACQUISITION_REQUESTS[:1], 'rights_review')
        verify_current_rights(root, require_destatis=True)
        append_fetches(root, ACQUISITION_REQUESTS[1:], 'qualified_private_archive')
        from .normalize import run as normalize
        normalize(root)
    print(json.dumps(results,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--acquire-reviewed',action='store_true',help='Private data archive/QA only, no model/public admission')
    args=p.parse_args();run(args.output,args.acquire_reviewed)



def append_fetches(root, items, phase='review'):
    """Append exact raw responses to the same data manifest; never replace bytes."""
    root=Path(root)
    manifest=json.loads((root/'manifest.json').read_text())
    for item in items:
        row,raw=fetch_review(item)
        row['phase']=phase
        if raw is not None:
            name=f"{row['source']}--{row['role']}.bin"
            path=root/name
            if path.exists():raise FileExistsError('Immutable response already exists')
            path.write_bytes(raw);row['raw_path']=name
        manifest['requests'].append(row)
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest


# Current documented primary endpoints, discovered from the official GENESIS
# client/environment. The retired /genesisWS route is NOT treated as observations.
ACQUISITION_REQUESTS = [
 ('destatis','genesis_specific_license','https://www.destatis.de/DE/Service/Impressum/copyright-genesis-online.html'),
 ('consumer_credit','native_csv','https://data-api.ecb.europa.eu/service/data/MIR/M.DE.B.A2B.A.R.A.2250.EUR.N?startPeriod=2018-01&endPeriod=2025-12&format=csvdata'),
 ('eurusd','native_csv','https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?startPeriod=2018-01&endPeriod=2025-12&format=csvdata'),
 ('diesel_de','original_weekly_workbook','https://energy.ec.europa.eu/document/download/906e60ca-8b6a-44e7-8589-652854d2fd3f_en?filename=Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx'),
 ('cpi','verified_base_metadata','https://genesis.destatis.de/genesis/api/rest/tables/61111-0002/information'),
 ('cpi','verified_base_data','https://genesis.destatis.de/genesis/api/rest/tables/61111-0002/data'),
 ('cpi','verified_table_structure','https://genesis.destatis.de/genesis/api/rest/tables/61111-0002/structure'),
 ('cpi','verified_quality_signs','https://genesis.destatis.de/genesis/api/rest/tables/61111-0002/qualitySigns'),
]


def verify_current_rights(root, require_destatis):
    from html.parser import HTMLParser
    class Text(HTMLParser):
        def __init__(self):super().__init__();self.parts=[]
        def handle_data(self,data):self.parts.append(data)
    m=json.loads((Path(root)/'manifest.json').read_text())
    required=[('ecb','reuse_policy',('free access and free reuse','third-party data')),
              ('commission','reuse_policy',('cc by 4.0','third-party works'))]
    if require_destatis:required.append(('destatis','genesis_specific_license',('datenlizenz deutschland','version 2.0')))
    for source,role,phrases in required:
        rows=[r for r in m['requests'] if r['source']==source and r['role']==role and r.get('raw_path')]
        if len(rows)!=1 or rows[0]['status']!=200:raise ValueError('Missing primary rights evidence: '+source)
        raw=(Path(root)/rows[0]['raw_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=rows[0]['sha256']:raise ValueError('Rights evidence hash mismatch')
        text=Text();text.feed(raw.decode('utf-8',errors='replace'));plain=' '.join(' '.join(text.parts).casefold().split())
        if any(p not in plain for p in phrases):raise ValueError('Rights policy changed; fresh review required: '+source)
    # This permits private archive/QA only. It never clears third-party/public
    # redistribution, creates an analytical permit or changes old human decisions.


if __name__=='__main__':main()
