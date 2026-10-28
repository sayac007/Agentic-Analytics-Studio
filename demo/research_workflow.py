"""Business work order, evidence checklist and presentation handoff; never fits models."""
import math
from pathlib import Path

from empirical.data import PERIODS

DRIVERS = {
    'calendar': {'label': 'Monatssaisonalität', 'role': 'Kalenderbasis', 'source': None,
                 'terms': ['month_02'], 'definition': 'Intercept + elf Monatsindikatoren; Januar ist Referenz.'},
    'dynamics': {'label': 'Vorherige Absatzveränderung', 'role': 'Dynamische Basis', 'source': 'tesla_count',
                 'terms': ['target_change_lag1'], 'definition': 'Vorherige tatsächliche Veränderung von log(1 + Zulassungen), Lag 1.'},
    'cpi': {'label': 'Inflation / Preisniveau', 'role': 'Makrokontrolle', 'source': 'cpi',
            'terms': ['cpi_change_lag'], 'definition': 'Monatliche Log-Veränderung des CPI, gemeinsame feste Lags 1/2/3.'},
    'consumer_credit': {'label': 'Konsumentenkreditzinsen', 'role': 'Finanzierung', 'source': 'consumer_credit',
                        'terms': ['consumer_credit_change_lag'], 'definition': 'Zinsänderung in Prozentpunkten; kein Logarithmus.'},
    'eurusd': {'label': 'EUR/USD', 'role': 'Makrokontrolle', 'source': 'eurusd',
               'terms': ['eurusd_change_lag'], 'definition': 'Log-Veränderung von USD je EUR; kein umgekehrter Wechselkurs.'},
    'diesel_de': {'label': 'Deutsche Dieselpreise', 'role': 'Energiekosten', 'source': 'diesel_de',
                  'terms': ['diesel_de_change_lag'], 'definition': 'Log-Veränderung der EUR/Liter-Monatsapproximation; Lücken bleiben erhalten.'},
    'delivery': {'label': 'Lieferfähigkeit / Quartalsende', 'role': 'Operations', 'source': None,
                 'terms': [], 'definition': 'Lieferfähigkeit ist nicht direkt gemessen; kein separater Quartalsende-Term im Pilot.'},
    'launches': {'label': 'Modellstarts / Verfügbarkeit', 'role': 'Produkt / Operations', 'source': None,
                'terms': [], 'definition': 'Unvollständiges Ereignis-Ledger nur zur Recherche; keine Expositionsreihe.'},
    'promotions': {'label': 'Preise / Promotions', 'role': 'Sales', 'source': None,
                   'terms': [], 'definition': 'Keine vollständige monatliche Preis-/Promotion-Reihe im Modell.'},
    'market': {'label': 'Gesamtmarkt / Wettbewerb', 'role': 'Marktumfeld', 'source': None,
               'terms': [], 'definition': 'Weitere KBA-Reihen sind noch nicht mit diesem Pilotmodell verbunden.'},
    'breaks': {'label': 'Subventionen / Strukturbrüche', 'role': 'Rahmenbedingungen', 'source': None,
               'terms': [], 'definition': 'Ereigniskandidaten ersetzen keine vorab begründete Bruchvariable.'},
}
DEFAULT_BRIEF = {
    'question': 'Welche verfügbaren Treiber helfen, die monatliche Absatzentwicklung zu erklären und bedingt vorherzusagen?',
    'audience': 'Business, Sales und Operations',
    'decision': 'Zusatzinformation gegenüber der Kalender-/Dynamikbasis prüfen; unerklärte Monate untersuchen.',
    'interface_notes': '',
    'required_drivers': ['calendar', 'dynamics'],
}
MODEL_NAMES = {
    'calendar': 'Kalender', 'dynamic': 'Kalender + Dynamik', 'macro': 'Dynamik + Makro · Lag 1',
    'macro_diesel': 'Dynamik + Makro + Diesel · Lag 1', 'macro_lag2': 'Dynamik + Makro · Lag 2',
    'macro_diesel_lag2': 'Dynamik + Makro + Diesel · Lag 2', 'macro_lag3': 'Dynamik + Makro · Lag 3',
    'macro_diesel_lag3': 'Dynamik + Makro + Diesel · Lag 3',
}
SOURCE_NAMES = {'tesla_count': 'Tesla-Neuzulassungen', 'cpi': 'Verbraucherpreisindex',
                'consumer_credit': 'Konsumentenkreditzinsen', 'eurusd': 'USD je EUR', 'diesel_de': 'Deutscher Dieselpreis'}


def check_brief(value):
    """Strict even when called without HTTP/Pydantic; no paths or model config accepted."""
    if not isinstance(value, dict) or set(value) != set(DEFAULT_BRIEF):
        raise ValueError('Invalid analysis work order')
    for key, limit in [('question', 1200), ('audience', 300), ('decision', 1200), ('interface_notes', 2000)]:
        text = value[key]
        if not isinstance(text, str) or len(text) > limit or (key != 'interface_notes' and not text.strip()):
            raise ValueError('Invalid analysis work order text')
    required = value['required_drivers']
    if (not isinstance(required, list) or not all(isinstance(x, str) and x in DRIVERS for x in required)
            or len(required) != len(set(required)) or not {'calendar', 'dynamics'} <= set(required)):
        raise ValueError('Invalid mandatory drivers')
    return value


def overview(brief, bundle=None):
    """Inspect existing evidence, not a statistical acceptance score or fresh data audit."""
    check_brief(brief)
    data = bundle['data'] if bundle else None
    checks = []
    def add(name, status, detail):
        checks.append({'check': name, 'status': status, 'detail': detail})
    add('Auftrag', 'recorded', 'Fachlicher Soll-Auftrag; ändert keine vorhandene Modellspezifikation.')
    if data is None:
        add('Datenstand', 'pending', 'Noch kein verifizierter Ergebnissnapshot; keine Datenvollständigkeit behauptet.')
        return {'checks': checks, 'drivers': driver_status(brief, None), 'sources': [], 'models': {},
                'snapshot_sha256': None, 'statistical_approval': 'not_granted_by_checklist'}
    add('Snapshot', 'verified', 'Bestehende Ergebnisdateien wurden vor Anzeige durch service.read auf Hash und Protokoll geprüft.')
    calendar_ok = data['periods'] == PERIODS
    add('Monatskalender', 'verified' if calendar_ok else 'failed',
        'Erwartet: genau 96 eindeutige, geordnete Monate 2018-01 bis 2025-12; kein Auffüllen.')
    sources = []
    for key, metadata in data['sources'].items():
        values = data['series'][key]
        finite = len(values) == len(PERIODS) and all(v is None or (type(v) in (int, float) and math.isfinite(v)) for v in values)
        missing = [p for p, v in zip(data['periods'], values) if v is None]
        consistent = (finite and len(values)-len(missing) == metadata['observed_months']
                      and missing == metadata.get('missing_months', []))
        add(SOURCE_NAMES[key], 'review' if consistent and missing else 'verified' if consistent else 'failed',
            f"{len(missing)} fehlende Quellmonate: {', '.join(missing) or 'keine'}. Differenzen/Lags können weitere Modellmonate ausschließen.")
        sources.append({'id': key, 'name': SOURCE_NAMES[key], **metadata,
                        'period_start': data['periods'][0], 'period_end': data['periods'][-1],
                        'computed_missing_months': missing})
    models = {}
    for key, model in bundle['results']['models'].items():
        if model['status'] != 'estimated':
            models[key] = {'status': 'not_estimable', 'checks': [{'check': 'Fit', 'status': 'failed', 'detail': model['reason']}]}
            continue
        full, train, test, paired = model['full'], model['training'], model['holdout'], model['paired_comparator']
        terms = full['terms']
        unmet = [d for d in brief['required_drivers'] if not included(d, terms)]
        finite_fit = all(type(v) in (float, int) and math.isfinite(v) for c in full['coefficients'].values() for v in c.values())
        paired_n = (full['n'] == paired['full_metrics']['n'] and train['n'] == paired['training_metrics']['n']
                    and len(test['periods']) == paired['holdout_count_metrics']['n'])
        boundaries = (bool(train['periods']) and all(p < '2025-01' for p in train['periods'])
                      and bool(test['periods']) and all('2025-01' <= p <= '2025-12' for p in test['periods'])
                      and not set(train['periods']) & set(test['periods']))
        models[key] = {'status': 'estimated', 'unmet_drivers': unmet, 'checks': [
            {'check': 'Muss-Treiber', 'status': 'review' if unmet else 'verified',
             'detail': 'Nicht enthalten: ' + ', '.join(DRIVERS[d]['label'] for d in unmet) if unmet else 'Alle benannten Muss-Treiber enthalten; kein Nachweis ihrer kausalen Identifikation.'},
            {'check': 'Rang / endliche Koeffizienten und HAC-Intervalle', 'status': 'verified' if finite_fit and full['rank'] == len(terms) else 'failed',
             'detail': f"Rang {full['rank']} / {len(terms)}; Residual-Freiheitsgrade {full['residual_df']}."},
            {'check': 'Vergleichsbasis', 'status': 'verified' if paired_n else 'failed',
             'detail': 'Stichprobenzahlen gegen den vom festen Rechenweg erzeugten Vergleich geprüft; Monatsmengen siehe Ergebnisnachweis. Keine unabhängige Neuschätzung.'},
            {'check': 'Training / 2025', 'status': 'verified' if boundaries else 'failed',
             'detail': 'Training bis 2024-12, retrospektiver bedingter Ein-Monats-Vergleich 2025; kein historischer Echtzeit-Test.'},
            {'check': 'Stationarität Ziel und Residuen', 'status': 'diagnostic' if model['model_assessment'] == 'diagnostic_support_only' else 'review',
             'detail': 'Ziel: ' + bundle['results']['outcome_stationarity']['modeled_log1p_change']['training_only']['verdict']
                       + '; Residuen: ' + model['stationarity']['training_residuals']['verdict'] + '. Explorativ; keine automatische Abnahme.'},
            {'check': 'Negative Count-Vorhersagen', 'status': 'review' if test['negative_predictions'] else 'verified',
             'detail': str(test['negative_predictions']) + '; keine nachträgliche Begrenzung auf null.'},
        ]}
    return {'checks': checks, 'drivers': driver_status(brief, bundle), 'sources': sources, 'models': models,
            'snapshot_sha256': bundle['snapshot_sha256'], 'statistical_approval': 'not_granted_by_checklist'}


def included(driver, terms):
    return bool(DRIVERS[driver]['terms']) and all(any(t.startswith(prefix) for t in terms) for prefix in DRIVERS[driver]['terms'])


def driver_status(brief, bundle):
    output = []
    for key, value in DRIVERS.items():
        model_ids = [k for k, m in bundle['results']['models'].items() if m['status'] == 'estimated' and included(key, m['full']['terms'])] if bundle else []
        output.append({'id': key, **value, 'required': key in brief['required_drivers'], 'included_in_models': model_ids,
                       'availability': 'modeled' if model_ids else 'not_modeled' if bundle else 'not_checked'})
    return output


def copilot_instructions():
    return (Path(__file__).resolve().parents[1]/'docs/COPILOT_RESULT_PRESENTATION.md').read_text(encoding='utf-8')


def cell(value):
    # Preserve float precision and prevent user/source text from forging Markdown rows/headings.
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\r', ' ').replace('\n', ' ')


def handoff(brief, bundle, selected='macro'):
    """Private text projection of a checked snapshot. No raw rows, prompts or saved AI replies."""
    qa = overview(brief, bundle)
    result = bundle['results']['models'][selected]
    lines = ['# Private Ergebnisübergabe – Agentic Analytics Studio',
             'Nur im für diese Daten freigegebenen Microsoft-365-Copilot-Tenant verwenden. Kein automatischer Versand.',
             'Beobachteter Pilot: Tesla Deutschland. Dies ist ein Anwendungsfall, keine Festlegung der Zielgruppe auf Tesla.',
             'Keine Neuberechnung; ausschließlich Projektion des gespeicherten, vor Ausgabe geprüften Snapshots.',
             f"Snapshot SHA-256: `{bundle['snapshot_sha256']}`", '', '## Fachlicher Auftrag']
    for key, label in [('question', 'Frage'), ('audience', 'Empfänger'), ('decision', 'Entscheidungsbezug'), ('interface_notes', 'Gewünschte Schnittstellen / Aktualisierung / Verantwortliche')]:
        lines.append(f'- {label}: {cell(brief[key]) or "nicht angegeben"}')
    lines += ['', '## Daten und Datenschnittstellen',
              'Schlüssel: YYYY-MM; Monatsfrequenz, Deutschland; 2018-01 bis 2025-12. Zulassungen sind keine Bestellungen.',
              'Aktuell nur fest gebundene Quellen-Snapshots; keine frei konfigurierbare API oder allgemeine CSV-Aufnahme.',
              '| Reihe | Einheit | Vorhandene Monate | Fehlende Monate | Herkunft / Hash / Bearbeitung |',
              '|---|---|---|---|---|']
    for s in qa['sources']:
        lines.append('| ' + ' | '.join(cell(x) for x in [s['name'], s['unit'], s['observed_months'],
                     ', '.join(s['computed_missing_months']) or 'keine',
                     f"{s.get('classification', 'nicht dokumentiert')}; {s.get('attribution', 'nicht dokumentiert')}; SHA-256 {s.get('sha256', 'nicht dokumentiert')}; {'; '.join(s.get('urls', []))}; Nutzung {s.get('reuse_scope', 'nicht dokumentiert')}"]) + ' |')
    lines += ['', '## Muss-Treiber: Soll und Ist', '| Treiber | Erforderlich | Enthaltene Modelle | Definition / Lücke |', '|---|---|---|---|']
    for d in qa['drivers']:
        lines.append('| ' + ' | '.join(cell(x) for x in [d['label'], 'ja' if d['required'] else 'nein', ', '.join(d['included_in_models']) or 'nicht modelliert', d['definition']]) + ' |')
    lines += ['', '## Alle vorab festgelegten Modellvergleiche',
              'Ziel: Δlog(1 + Zulassungen). R² beschreibt Veränderungen, nicht das erklärte Absatzniveau.',
              'RMSE-Differenz = Modell minus gepaarte Basis auf denselben Monaten; negativ bedeutet geringeren Fehler.',
              '| Modell | Status | n gesamt / Training / 2025 | R² / adj. R² Veränderungen | 2025 RMSE / MAE Zulassungen | Gepaarte Basis RMSE | RMSE-Differenz |',
              '|---|---|---|---|---|---|---|']
    for key, m in bundle['results']['models'].items():
        if m['status'] != 'estimated':
            lines.append(f"| {cell(MODEL_NAMES[key])} | nicht schätzbar: {cell(m['reason'])} | – | – | – | – | – |")
            continue
        rmse = m['holdout']['count_metrics']['rmse']; base = m['paired_comparator']['holdout_count_metrics']['rmse']
        row = [MODEL_NAMES[key], m['status'], f"{m['full']['n']} / {m['training']['n']} / {len(m['holdout']['periods'])}",
               f"{m['full']['metrics']['r2']} / {m['full']['metrics']['adjusted_r2']}",
               f"{rmse} / {m['holdout']['count_metrics']['mae']}", base, rmse-base]
        lines.append('| ' + ' | '.join(cell(v) for v in row) + ' |')
    lines += ['', '## Pflichtdiagnostik aller Modelle', '| Modell | Trainingsresiduen | Gesamtfenster-Residuen | Muss-Treiber fehlen |', '|---|---|---|---|']
    for key, m in bundle['results']['models'].items():
        row = [MODEL_NAMES[key], m['stationarity'].get('training_residuals', {}).get('verdict', 'nicht schätzbar'),
               m['stationarity'].get('full_residuals', {}).get('verdict', 'nicht schätzbar'), ', '.join(qa['models'][key].get('unmet_drivers', [])) or 'keine / bei fehlendem Fit nicht geprüft']
        lines.append('| ' + ' | '.join(cell(v) for v in row) + ' |')
    lines += ['', f'## Detail: {MODEL_NAMES[selected]}']
    for check in qa['checks'] + qa['models'][selected]['checks']:
        lines.append(f"- [{check['status']}] {cell(check['check'])}: {cell(check['detail'])}")
    if result['status'] == 'estimated':
        lines += ['', '| Term (Gesamtfenster) | Koeffizient | HAC-SE | 95-% unten | 95-% oben |', '|---|---|---|---|---|']
        for term, values in result['full']['coefficients'].items():
            lines.append('| ' + ' | '.join(cell(v) for v in [term, values['estimate'], values['standard_error'], values['lower'], values['upper']]) + ' |')
        lines += ['', 'Training: ' + ', '.join(result['training']['periods']),
                  '2025-Vergleich: ' + ', '.join(result['holdout']['periods']),
                  'Ausgeschlossene Modellmonate: ' + (', '.join(result['excluded_periods']) or 'keine'),
                  'HAC: drei tatsächliche Kalendermonate, bedingte asymptotische Intervalle; keine validierte empirische Abdeckung.']
        diagnostics = [(key, window, value) for key, profile in bundle['results']['outcome_stationarity'].items() for window, value in profile.items()]
        diagnostics += [('selected_model_residuals', window, value) for window, value in result['stationarity'].items()]
        lines += ['', '| Diagnostikreihe | Fenster | n / Segment | ADF p | KPSS p (Grenze) | Einordnung | Warnungen |', '|---|---|---|---|---|---|---|']
        for key, window, value in diagnostics:
            segment = value.get('segment_periods', [])
            row = [key, window, f"{value['n']} / {segment[0] + ' bis ' + segment[-1] if segment else 'kein Segment'}",
                   value.get('adf', {}).get('pvalue', 'nicht schätzbar'),
                   str(value.get('kpss', {}).get('pvalue_bound') or '') + str(value.get('kpss', {}).get('pvalue', 'nicht schätzbar')), value['verdict'], '; '.join(value.get('warnings', [])) or 'keine']
            lines.append('| ' + ' | '.join(cell(v) for v in row) + ' |')
    lines += ['', '## Ungeklärte Monate / Recherchekandidaten',
              'Festes Makromodell Lag 1, Trainingsfenster; keine kausale Erklärung und keine Vollständigkeit des Ledgers.']
    for peak in bundle['results']['residual_research']:
        lines.append(f"- {peak['period']}: Restfehler Δlog1p = {peak['residual_change']}; Recherchefenster {', '.join(peak['search_months'])}.")
        for event in peak['documented_candidates']:
            lines.append(f"  - Kandidat: {cell(event['date'])}, {cell(event.get('precision', 'unbekannt'))}, {cell(event['status'])}: {cell(event['title'])}; " + '; '.join(cell(s['url']) for s in event['sources']))
    lines += ['', '## Grenzen und Rechenstand']
    lines.extend('- ' + cell(v) for v in bundle['results']['limits'])
    lines += ['- ADF: Nullhypothese Einheitswurzel; KPSS: Nullhypothese Stationarität. Feste drei Lags; Residuentests explorativ, kein Kointegrationsnachweis.',
              '- Kein automatischer Gewinner, keine kausale Treiberzerlegung, keine ROI-Aussage. Unvollständige Pflicht-Treiber bleiben Forschungsbedarf.',
              '- Neue Daten, Modelländerungen und externe Recherche benötigen einen getrennten fachlichen Schritt.',
              '- Keine Rohdaten, Monatsbeobachtungsarrays, Zugangsdaten, privaten Source-Permits oder gespeicherten Gespräche enthalten.',
              '- Protokoll SHA-256: ' + str(bundle['provenance'].get('protocol_sha256', 'nicht dokumentiert')),
              '- Software: ' + cell(str({k: bundle['provenance'].get(k, 'nicht dokumentiert') for k in ('python', 'packages', 'feature_library', 'implementation')})),
              '', '---', '', copilot_instructions()]
    return '\n'.join(lines) + '\n'
