"""Reviewed private monthly CSV intake. No fits, interpolation, URL fetches or old-file writes."""
import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
import io
import json
import math
from pathlib import Path
import re
import shutil
import tempfile

from .data import ROOT, sha, json_bytes

MAX_BYTES = 2_000_000
MONTH = re.compile(r'^(19|20)[0-9]{2}-(0[1-9]|1[0-2])$')
IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]{1,40}$')
NUMBER = re.compile(r'^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$')
FIELDS = {'series_id', 'label', 'unit', 'definition', 'source_reference', 'source_vintage',
          'classification', 'period_column', 'value_column', 'decimal', 'private_use_confirmed'}
CALENDAR = {'calendar_year': 'Kalenderjahr', 'calendar_month': 'Kalendermonat',
            'calendar_quarter': 'Quartal', 'calendar_quarter_end': 'Quartalsendmonat'}


class IntakeError(ValueError):
    pass


def table(raw):
    if not raw or len(raw) > MAX_BYTES:
        raise IntakeError('Eine nicht leere UTF-8-CSV mit höchstens 2 MB auswählen.')
    try:
        text = raw.decode('utf-8-sig')
        if '\x00' in text: raise ValueError()
        first = text.splitlines()[0]
        delimiter = ';' if first.count(';') > first.count(',') else ','
        parsed = list(csv.reader(io.StringIO(text, newline=''), delimiter=delimiter, strict=True))
    except (UnicodeError, ValueError, csv.Error, IndexError):
        raise IntakeError('CSV nicht lesbar. Unterstützt sind UTF-8 und Komma oder Semikolon als Trennzeichen.') from None
    headers, rows = parsed[0], parsed[1:]
    if (not 2 <= len(headers) <= 30 or len(set(headers)) != len(headers)
            or any(not h.strip() or len(h) > 100 for h in headers)
            or not 1 <= len(rows) <= 2400 or any(len(r) != len(headers) for r in rows)):
        raise IntakeError('CSV benötigt eindeutige Spaltennamen und 1–2400 vollständige Zeilen; keine leeren Zusatzzeilen oder doppelten Header.')
    return headers, [dict(zip(headers, row)) for row in rows]


def inspect(raw):
    headers, rows = table(raw)
    return {'columns': headers, 'rows': len(rows), 'sha256': sha(raw),
            'period_candidates': [h for h in headers if all(MONTH.fullmatch(r[h].strip()) for r in rows)],
            'notice': 'Spalten erkannt, noch keine inhaltliche Freigabe. Keine Daten an KI gesendet.'}


def metadata(value):
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise IntakeError('Quellenbeschreibung oder Spaltenzuordnung unvollständig.')
    for key in FIELDS - {'private_use_confirmed'}:
        if not isinstance(value[key], str) or not value[key].strip() or len(value[key]) > 600:
            raise IntakeError('Definition, Einheit, Quelle und Datenstand müssen benannt sein; Unbekanntes ausdrücklich als unbekannt kennzeichnen.')
    if (not IDENTIFIER.fullmatch(value['series_id']) or value['series_id'] in CALENDAR
            or value['classification'] not in ('observed', 'proxy', 'derived_observed')
            or value['decimal'] not in ('dot', 'comma') or value['private_use_confirmed'] is not True):
        raise IntakeError('Reihenkennung, Klasse oder Dezimalformat ungültig; private Nutzungsbefugnis muss bestätigt sein. Kalenderfelder sind reserviert.')
    # References are descriptions, never endpoints to call or credential-bearing URLs.
    from urllib.parse import urlsplit
    ref = value['source_reference']
    if '://' in ref:
        u = urlsplit(ref)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment:
            raise IntakeError('Quellen-URL ohne Zugangsdaten, Token, Query oder Fragment angeben; sie wird nicht automatisch aufgerufen.')
    return value


def parse(raw, meta):
    metadata(meta)
    headers, rows = table(raw)
    pc, vc = meta['period_column'], meta['value_column']
    if pc == vc or pc not in headers or vc not in headers:
        raise IntakeError('Unterschiedliche vorhandene Monats- und Wertespalten auswählen.')
    result = {}
    for index, row in enumerate(rows, 2):
        for name, source_value in row.items():
            if name.lower() in ('geo', 'geography', 'country', 'region', 'land') and source_value.strip():
                if source_value.strip().casefold() not in ('de', 'deu', 'deutschland', 'germany'):
                    raise IntakeError(f'Zeile {index}: ausgewiesene Geographie passt nicht zum nationalen Deutschland-Datensatz.')
            if name.lower() in ('unit', 'einheit') and source_value.strip() and source_value.strip() != meta['unit']:
                raise IntakeError(f'Zeile {index}: Einheit in der Datei widerspricht der Quellenbeschreibung.')
        period, text = row[pc].strip(), row[vc].strip()
        if not MONTH.fullmatch(period):
            raise IntakeError(f'Zeile {index}: Monat muss YYYY-MM sein; Tages-, Wochen- und Quartalsdaten benötigen eine eigene Aggregationsregel.')
        if period in result:
            raise IntakeError(f'Zeile {index}: doppelter Monat; keine automatische Summierung oder Auswahl einer Zeile.')
        normalized = text.replace(',', '.') if meta['decimal'] == 'comma' else text
        if text == '': value = None
        elif not NUMBER.fullmatch(normalized):
            raise IntakeError(f'Zeile {index}: ungültiger Zahlenwert. Leer bedeutet fehlend; keine Tausendertrennzeichen oder automatischen Ersetzungen.')
        else:
            value = float(normalized)
            if not math.isfinite(value): raise IntakeError(f'Zeile {index}: Zahl ist nicht endlich.')
            try: exact = Decimal(normalized)
            except InvalidOperation: raise IntakeError(f'Zeile {index}: Zahl nicht verarbeitbar.') from None
            if value == 0 and exact != 0: raise IntakeError(f'Zeile {index}: Zahl würde im Zahlenformat unbemerkt zu null werden.')
        key = meta['series_id']
        if value is not None and ((key in ('cpi', 'eurusd', 'diesel_de') and value <= 0)
                                  or (key in ('tesla_count', 'vw_count', 'toyota_count', 'market_bev') and (exact < 0 or exact != exact.to_integral_value() or exact > 2**53))):
            raise IntakeError(f'Zeile {index}: Wert verletzt die Definition der bestehenden Reihe.')
        result[period] = value
    return result


def months(start, end):
    first = int(start[:4])*12 + int(start[5:])-1
    last = int(end[:4])*12 + int(end[5:])-1
    if last-first >= 600: raise IntakeError('Der gemeinsame Monatskalender darf höchstens 600 Monate umfassen.')
    return [f'{i//12:04d}-{i%12+1:02d}' for i in range(first, last+1)]


def with_calendar(data):
    result = json.loads(json.dumps(data, allow_nan=False))
    for key in CALENDAR:
        result['series'][key] = []
        result['sources'][key] = {'unit': 'year' if key == 'calendar_year' else 'month' if key == 'calendar_month' else 'quarter' if key == 'calendar_quarter' else 'indicator',
                                 'classification': 'derived_calendar', 'definition': CALENDAR[key],
                                 'source_reference': 'Deterministic YYYY-MM calendar; not an observed demand driver',
                                 'observed_months': len(result['periods']), 'missing_months': []}
    for period in result['periods']:
        year, month = map(int, period.split('-'))
        for key, value in zip(CALENDAR, [year, month, (month-1)//3+1, int(month in (3, 6, 9, 12))]):
            result['series'][key].append(value)
    return result


def reviewed_base(base):
    """Enrich only if the analyzed Tesla series is bound to this audited KBA catalog."""
    path = ROOT/'data/kba/derived/observations.csv'
    if base['data']['sources']['tesla_count'].get('sha256') == sha(path.read_bytes()):
        from .tesla_review import joint_data
        return {**base, 'data': joint_data(base)}
    return base


def describe(data, identity):
    return {'dataset_sha256': sha(json_bytes(data)), 'version_id': identity, 'months': len(data['periods']), 'start': data['periods'][0], 'end': data['periods'][-1],
            'series': [{'id': key, 'unit': data['sources'][key]['unit'],
                        'classification': data['sources'][key].get('classification', 'not_documented'),
                        'observed_months': sum(v is not None for v in values),
                        'missing_months': [p for p, v in zip(data['periods'], values) if v is None]}
                       for key, values in data['series'].items()],
            'analysis_status': 'candidate_dataset_not_fitted',
            'limits': ['Lücken sind keine Nullen; es wird nicht interpoliert.',
                       'Quellenbestätigung ist keine allgemeine Rechtefreigabe oder historische Point-in-time-Freigabe.',
                       'Ereignis-Ledger bleiben Annotationen; fehlende Ereignisse sind unbekannt.',
                       'Bestehende Modelle bleiben an ihren ursprünglichen Datensatz gebunden. Keine automatische Neuinterpretation als Analyse des Uploads.']}


def context_summary(base):
    """Bound QA facts only; no raw uploaded rows or source files enter a provider prompt."""
    from .service import storage_root
    root = storage_root()/'observed-intake'
    pointer = root/'current.json'
    if not pointer.exists() and not pointer.is_symlink(): return {'status': 'no_new_dataset'}
    current = Store(root).current(base)
    review = json.loads((current['folder']/'review.json').read_bytes())
    meta = review.get('metadata', {})
    return {'status': 'private_candidate_not_fitted', 'version_id': current['id'],
            'months': len(current['data']['periods']), 'series_count': len(current['data']['series']),
            'latest_series_id': meta.get('series_id'), 'unit': meta.get('unit'), 'definition': meta.get('definition'),
            'revision_count': len(review.get('revisions', [])), 'new_month_count': len(review.get('new_months', [])),
            'outside_historical_range_count': len(review.get('outside_historical_range', [])),
            'source_vintage': meta.get('source_vintage'),
            'source_identity_and_rights_not_independently_certified': True,
            'existing_model_results_are_not_fits_of_this_candidate': True}


class Store:
    def __init__(self, root):
        self.root = Path(root)
        if self.root.resolve().is_relative_to(ROOT) or any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise IntakeError('Privater Datenspeicher außerhalb des Repositorys erforderlich.')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def read(self, identity, base_sha):
        if not re.fullmatch(r'[a-f0-9]{64}', identity): raise IntakeError('Ungültige Datensatzkennung.')
        folder = self.root/identity
        if folder.is_symlink(): raise IntakeError('Unsicherer Datensatzpfad.')
        manifest_path = folder/'manifest.json'
        if manifest_path.is_symlink(): raise IntakeError('Unsicherer Manifestpfad.')
        manifest = json.loads(manifest_path.read_bytes())
        expected = {'data.json', 'panel.csv', 'source.csv', 'review.json', 'provenance.json'}
        if manifest.get('id') != identity or set(manifest.get('files', {})) != expected:
            raise IntakeError('Ungültiges Datensatzmanifest.')
        for name, digest in manifest['files'].items():
            file = folder/name
            if file.is_symlink() or sha(file.read_bytes()) != digest:
                raise IntakeError('Gespeicherte Datensatzdatei verändert; keine erfolgreiche Prüfung.')
        provenance = json.loads((folder/'provenance.json').read_bytes())
        if sha((folder/'review.json').read_bytes()) != identity:
            raise IntakeError('Versionskennung und Review stimmen nicht überein.')
        if provenance['base_snapshot_sha256'] != base_sha:
            raise IntakeError('Der ursprüngliche Datenstand hat sich geändert; Abgleich muss neu erfolgen.')
        return {'id': identity, 'data': json.loads((folder/'data.json').read_bytes()), 'folder': folder}

    def current(self, base):
        pointer = self.root/'current.json'
        if pointer.is_symlink(): raise IntakeError('Unsicherer Datensatzzeiger.')
        if pointer.exists(): return self.read(json.loads(pointer.read_bytes())['id'], base['snapshot_sha256'])
        data = with_calendar(reviewed_base(base)['data'])
        return {'id': sha(json_bytes(data)), 'data': data, 'folder': None}

    def preview(self, base, raw, meta):
        incoming = parse(raw, meta)
        current = self.current(base)
        data = current['data']; key = meta['series_id']
        if key not in data['series'] and len(data['series']) >= 40:
            raise IntakeError('Höchstens 40 Reihen in dieser Datenaufnahme; weitere Aufteilung benötigt einen eigenen Auftrag.')
        if key in data['sources'] and meta['unit'] != data['sources'][key]['unit']:
            raise IntakeError('Einheit passt nicht zur bestehenden Reihe. Umrechnung oder geänderte Definition separat prüfen; kein stiller Wechsel.')
        if key in data['sources']:
            old_class = data['sources'][key].get('classification')
            expected_class = 'derived_observed' if old_class == 'derived_observed_weekly_overlap_approximation' else old_class
            if expected_class in ('observed', 'proxy', 'derived_observed') and meta['classification'] != expected_class:
                raise IntakeError('Datenart geändert. Eine direkte Messung nicht still durch einen Proxy ersetzen; getrennte Reihenkennung verwenden.')
        old = dict(zip(data['periods'], data['series'].get(key, [None]*len(data['periods']))))
        existing = key in data['series']
        revisions = [{'period': p, 'old': old[p], 'new': value} for p, value in incoming.items()
                     if existing and p in old and old[p] != value]
        overlap = [p for p in incoming if existing and p in old]
        values = [v for v in old.values() if v is not None] if existing else []
        extremes = [p for p, v in incoming.items() if v is not None and values and (v < min(values) or v > max(values))]
        calendar = months(min(data['periods'][0], min(incoming)), max(data['periods'][-1], max(incoming)))
        warnings = []
        ignored = [c for c in table(raw)[0] if c not in (meta['period_column'], meta['value_column'])]
        if ignored: warnings.append('Weitere Spalten werden nicht übernommen oder als Filter interpretiert: ' + ', '.join(ignored))
        if revisions: warnings.append(f'{len(revisions)} historische Werte ändern sich, einschließlich expliziter Leerwerte. Originalbestand bleibt erhalten.')
        if not overlap: warnings.append('Keine historische Überlappung für diese Reihe; numerische Vergleichbarkeit nicht nachgewiesen.')
        if extremes: warnings.append(f'{len(extremes)} Werte außerhalb der historischen Spannweite; Prüfanlass, kein Fehlernachweis.')
        if any(v is None for v in incoming.values()): warnings.append('Explizite Leerwerte bleiben fehlend; sie können in dieser neuen Version auch vorhandene Werte ersetzen.')
        if meta['source_vintage'].lower() in ('unbekannt', 'unknown'): warnings.append('Quell-Vintage unbekannt; Uploadzeit ist kein Veröffentlichungsdatum.')
        if meta['classification'] == 'proxy': warnings.append('Proxy ist keine direkte Messung des behaupteten Treibers.')
        review = {'parent_dataset_sha256': current['id'], 'base_snapshot_sha256': base['snapshot_sha256'],
                  'raw_sha256': sha(raw), 'metadata': meta, 'incoming_months': len(incoming),
                  'new_months': sorted(p for p in incoming if p not in data['periods']),
                  'overlap_months': len(overlap), 'unchanged_overlap': len(overlap)-len(revisions),
                  'revisions': revisions, 'outside_historical_range': extremes,
                  'ignored_columns': ignored,
                  'common_calendar_months': len(calendar), 'warnings': warnings,
                  'implementation_sha256': sha(Path(__file__).read_bytes()),
                  'boundary': 'Monatlich, Deutschland. Einheit und Definition sind menschliche Quellenangaben; keine unabhängige Inhalts-/Rechtezertifizierung.'}
        review['preview_sha256'] = sha(json_bytes(review))
        return review

    def assemble(self, base, raw=b'', meta=None, expected=None):
        current = self.current(base)
        if meta is None:
            if current['folder'] is not None: return current
            review = {'base_snapshot_sha256': base['snapshot_sha256'], 'parent_dataset_sha256': current['id'], 'operation': 'assemble_verified_existing'}
        else:
            review = self.preview(base, raw, meta)
            if expected != review['preview_sha256']:
                raise IntakeError('Datei, Metadaten oder historischer Stand geändert; Abgleich erneut prüfen.')
        identity = sha(json_bytes(review))
        folder = self.root/identity
        if folder.exists(): return self.read(identity, base['snapshot_sha256'])
        data = json.loads(json.dumps(current['data'], allow_nan=False))
        if meta is not None:
            incoming = parse(raw, meta); key = meta['series_id']
            periods = months(min(data['periods'][0], min(incoming)), max(data['periods'][-1], max(incoming)))
            for name, values in data['series'].items():
                old = dict(zip(data['periods'], values))
                data['series'][name] = [old.get(p) for p in periods]
            old = dict(zip(periods, data['series'].get(key, [None]*len(periods))))
            old.update(incoming)
            data['series'][key] = [old.get(p) for p in periods]
            data['periods'] = periods
            data['sources'][key] = {**meta, 'sha256': sha(raw),
                                    'reuse_scope': 'owner_confirmed_private_candidate_only_not_general_admission',
                                    'parent_dataset_sha256': current['id'],
                                    'origin_source': (current['data']['sources'].get(key) or {}).get('origin_source', current['data']['sources'].get(key))}
        data = with_calendar(data)
        for key, values in data['series'].items():
            data['sources'][key]['observed_months'] = sum(v is not None for v in values)
            data['sources'][key]['missing_months'] = [p for p, v in zip(data['periods'], values) if v is None]
        stream = io.StringIO(newline=''); writer = csv.writer(stream, lineterminator='\n')
        columns = sorted(data['series']); writer.writerow(['period', *columns])
        for i, period in enumerate(data['periods']):
            writer.writerow([period, *['' if data['series'][key][i] is None else data['series'][key][i] for key in columns]])
        provenance = {'base_snapshot_sha256': base['snapshot_sha256'], 'parent_dataset_sha256': current['id'],
                      'created_at_utc': datetime.now(timezone.utc).isoformat(), 'public_redistribution_allowed': False,
                      'analysis_status': 'candidate_dataset_not_fitted', 'definition_changes_not_independently_verified': True,
                      'originals_unchanged': True, 'source_review': 'original source-specific exceptions retained; upload is not an unconditional admission permit'}
        files = {'data.json': json_bytes(data), 'panel.csv': stream.getvalue().encode(), 'source.csv': raw,
                 'review.json': json_bytes(review), 'provenance.json': json_bytes(provenance)}
        stage = Path(tempfile.mkdtemp(prefix='.stage-', dir=self.root))
        try:
            for name, content in files.items(): (stage/name).write_bytes(content); (stage/name).chmod(0o600)
            (stage/'manifest.json').write_bytes(json_bytes({'id': identity, 'files': {n: sha(v) for n,v in files.items()}}))
            (stage/'manifest.json').chmod(0o600);stage.rename(folder)
            temp = self.root/'current.tmp'
            if temp.is_symlink(): raise IntakeError('Unsicherer Datensatzzeiger.')
            temp.write_bytes(json_bytes({'id': identity}));temp.chmod(0o600);temp.replace(self.root/'current.json')
        finally:
            if stage.exists(): shutil.rmtree(stage)
        return self.read(identity, base['snapshot_sha256'])
