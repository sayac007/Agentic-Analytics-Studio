"""Recover only the exact previously reviewed public-source bytes, privately."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlsplit

from .data import ROOT, sha, json_bytes

PAIRS = {('consumer_credit', 'native_csv'), ('eurusd', 'native_csv'),
         ('cpi', 'verified_base_data'), ('cpi', 'verified_table_structure'), ('cpi', 'verified_quality_signs'),
         ('diesel_de', 'original_weekly_workbook')}
HOSTS = {'data-api.ecb.europa.eu', 'genesis.destatis.de', 'www.ecb.europa.eu', 'commission.europa.eu',
         'www.destatis.de', 'energy.ec.europa.eu'}


def required():
    manifest = json.loads((ROOT/'data/verified_sources/manifest.json').read_text())
    return manifest, [r for r in manifest['requests'] if (r['source'], r['role']) in PAIRS and r.get('raw_path')]


def restore(directory):
    root = Path(directory).resolve()
    if root.is_relative_to(ROOT) or Path(directory).is_symlink(): raise ValueError('Private source directory required')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    manifest, rows = required()
    def one(row):
        path = root/row['raw_path']
        receipt = {'name': row['raw_path'], 'url': row['url'], 'attempted_at_utc': datetime.now(timezone.utc).isoformat()}
        try:
            if path.is_symlink(): raise ValueError('Unsafe source snapshot')
            if path.exists():
                if sha(path.read_bytes()) != row['sha256']: raise ValueError('Existing snapshot hash differs')
                return dict(receipt, status='already_verified')
            url = row['url']; u = urlsplit(url)
            if u.scheme != 'https' or u.hostname not in HOSTS or u.username or u.password:
                raise ValueError('Unapproved source endpoint')
            request = urllib.request.Request(url, headers={'User-Agent': 'AgenticAnalyticsStudio/primary-source-review'})
            with urllib.request.urlopen(request, timeout=25) as response:
                final = urlsplit(response.geturl())
                if final.scheme != 'https' or final.hostname not in HOSTS: raise ValueError('Publisher redirect changed')
                raw = response.read(6_000_001)
            if len(raw) > 6_000_000 or sha(raw) != row['sha256']: raise ValueError('Snapshot changed; original file required')
            with path.open('xb') as stream: stream.write(raw)
            path.chmod(0o600)
            return dict(receipt, status='restored_exact_bytes', retrieved_at_utc=datetime.now(timezone.utc).isoformat(), sha256=sha(raw))
        except Exception:
            return dict(receipt, status='needs_original_file', expected_sha256=row['sha256'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(one, rows))
    (root/'restoration.json').write_bytes(json_bytes(receipts))
    missing = [r for r in receipts if r['status'] == 'needs_original_file']
    if missing: return {'status': 'needs_original_files', 'missing': missing}
    # Original acquisition dates remain historical evidence. Fresh requests are in restoration.json.
    if not (root/'manifest.json').exists():
        (root/'manifest.json').write_bytes(json_bytes(manifest))
    from source_acquisition.normalize import run
    run(root)
    for name, expected in manifest['normalized_files'].items():
        if sha((root/name).read_bytes()) != expected: raise ValueError('Normalized observations changed')
    return {'status': 'ready', 'restored_files': len(rows)}


def install_original(directory, name, raw):
    """Owner-supplied original bytes, never a new vintage or arbitrary upload path."""
    root = Path(directory).resolve()
    if root.is_relative_to(ROOT) or Path(directory).is_symlink(): raise ValueError('Private source directory required')
    _, rows = required()
    allowed = {row['raw_path']: row['sha256'] for row in rows}
    if name not in allowed or len(raw) > 6_000_000 or sha(raw) != allowed[name]:
        raise ValueError('Not the reviewed original source bytes')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root/name
    if path.is_symlink(): raise ValueError('Unsafe snapshot path')
    if path.exists():
        if path.read_bytes() != raw: raise ValueError('Existing snapshot is immutable')
    else:
        with path.open('xb') as stream: stream.write(raw)
        path.chmod(0o600)
    return {'status': 'original_bytes_verified', 'name': name, 'sha256': sha(raw)}
