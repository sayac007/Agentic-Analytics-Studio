'use strict';
let intakeRaw = null, intakePreview = null, intakeDataset = null, intakeRevision = 0;
const i$ = id => document.getElementById(id);
function invalidateIntake() {
  intakeRevision += 1; intakePreview = null;
  i$('intake-review').hidden = true; i$('intake-confirm').checked = false; i$('intake-accept').disabled = true;
}
function showDataset(data) {
  intakeDataset = data;
  i$('intake-dataset').hidden = false;
  i$('intake-dataset-summary').textContent = `${data.start} bis ${data.end} · ${data.months} Kalendermonate · ${data.series.length} Reihen · Datenhash ${data.dataset_sha256.slice(0,12)}. Ein gemeinsamer Kalender ist keine Behauptung lückenloser Beobachtungen.`;
  i$('intake-coverage').replaceChildren();
  for (const source of data.series) {
    const row = document.createElement('tr');
    for (const text of [source.id, source.unit, `${source.observed_months}/${data.months}`, source.missing_months.join(', ') || 'keine']) {
      const cell = document.createElement('td'); cell.textContent = text; row.append(cell);
    }
    i$('intake-coverage').append(row);
  }
  i$('intake-download').hidden = data.stored === false;
  const previous = i$('intake-series').value;
  i$('intake-series').replaceChildren(new Option('Neue Reihe', 'new'));
  data.series.filter(s => !s.id.startsWith('calendar_')).forEach(s => i$('intake-series').add(new Option(s.id + ' · ' + s.unit, s.id)));
  if ([...i$('intake-series').options].some(o => o.value === previous)) i$('intake-series').value = previous;
}
async function loadIntake() {
  try {showDataset(await api('/api/empirical/intake'));}
  catch {i$('intake-status').textContent = 'Für den historischen Vergleich zuerst die vorhandenen Quellen und Ergebnisse prüfen. Eine CSV kannst du bereits auswählen.';}
}
async function selectIntakeFile(file) {
  invalidateIntake(); intakeRaw = null; i$('intake-mapping').hidden = true;
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.csv') || file.size > 2000000) {
    i$('intake-status').textContent = 'Bitte eine UTF-8-CSV bis 2 MB auswählen. Excel-, Tages- und Wochenformate brauchen einen passenden Adapter.'; return;
  }
  const revision = intakeRevision;
  try {
    const bytes = new Uint8Array(await file.arrayBuffer()); let binary = '';
    for (let i=0; i<bytes.length; i+=32768) binary += String.fromCharCode(...bytes.subarray(i,i+32768));
    const encoded = btoa(binary);
    const inspected = await api('/api/empirical/intake/inspect', {content_base64: encoded});
    if (revision !== intakeRevision) return;
    intakeRaw = encoded;
    for (const id of ['intake-period', 'intake-value']) {
      i$(id).replaceChildren(); inspected.columns.forEach(name => i$(id).add(new Option(name,name)));
    }
    if (inspected.period_candidates.length === 1) i$('intake-period').value = inspected.period_candidates[0];
    const value = inspected.columns.find(h => h.toLowerCase() === 'value') || inspected.columns.find(h => h !== i$('intake-period').value);
    if (value) i$('intake-value').value = value;
    i$('intake-mapping').hidden = false;
    i$('intake-status').textContent = `${file.name}: ${inspected.rows} Zeilen, ${inspected.columns.length} Spalten erkannt. Bedeutung, Einheit und Datenstand bitte bestätigen; noch nichts übernommen.`;
  } catch (error) {i$('intake-status').textContent = error.message;}
}
i$('intake-file').addEventListener('change', () => selectIntakeFile(i$('intake-file').files[0]));
const zone = document.querySelector('.upload-zone');
zone.addEventListener('dragover', event => {event.preventDefault(); zone.classList.add('drag-active');});
zone.addEventListener('dragleave', () => zone.classList.remove('drag-active'));
zone.addEventListener('drop', event => {
  event.preventDefault(); zone.classList.remove('drag-active');
  if (event.dataTransfer.files.length !== 1) {i$('intake-status').textContent = 'Bitte jeweils eine eindeutig definierte Reihe prüfen.'; return;}
  selectIntakeFile(event.dataTransfer.files[0]);
});
for (const field of i$('intake-mapping').querySelectorAll('input,select')) field.addEventListener('input', invalidateIntake);
i$('intake-series').addEventListener('change', () => {
  const source = intakeDataset?.series.find(s => s.id === i$('intake-series').value);
  i$('intake-new-id-label').hidden = Boolean(source);
  i$('intake-new-id').required = !source;
  if (source) {i$('intake-unit').value = source.unit; i$('intake-label').value = source.id;}
  else {i$('intake-unit').value=''; i$('intake-label').value='';}
  invalidateIntake();
});
i$('intake-new-id').required = true;
function intakeMetadata() {
  return {series_id: i$('intake-series').value === 'new' ? i$('intake-new-id').value : i$('intake-series').value,
    label: i$('intake-label').value, unit: i$('intake-unit').value, definition: i$('intake-definition').value,
    source_reference: i$('intake-source').value, source_vintage: i$('intake-vintage').value,
    classification: i$('intake-class').value, period_column: i$('intake-period').value,
    value_column: i$('intake-value').value, decimal: i$('intake-decimal').value,
    private_use_confirmed: i$('intake-rights').checked};
}
i$('intake-mapping').addEventListener('submit', async event => {
  event.preventDefault(); invalidateIntake();
  if (!intakeRaw) return;
  const revision = intakeRevision;
  const payload = {content_base64: intakeRaw, metadata: intakeMetadata()};
  try {
    const report = await api('/api/empirical/intake/preview', payload);
    if (revision !== intakeRevision) return;
    intakePreview = {...payload, preview_sha256: report.preview_sha256};
    i$('intake-comparison').textContent = `${report.incoming_months} eingelesene Monate · ${report.overlap_months} Monate mit historischem Bezug · ${report.unchanged_overlap} unverändert · ${report.revisions.length} Revisionen · ${report.new_months.length} zusätzliche Monate.`;
    i$('intake-warnings').replaceChildren();
    for (const warning of [...report.warnings, report.boundary]) {
      const li = document.createElement('li'); li.textContent = warning; i$('intake-warnings').append(li);
    }
    i$('intake-revisions').replaceChildren();
    for (const change of report.revisions) {
      const row = document.createElement('tr');
      for (const value of [change.period, change.old, change.new]) {
        const cell = document.createElement('td'); cell.textContent = value === null ? 'fehlend' : String(value); row.append(cell);
      }
      i$('intake-revisions').append(row);
    }
    i$('intake-details').textContent = JSON.stringify(report,null,2);
    i$('intake-review').hidden = false;
    i$('intake-status').textContent = 'Abgleich berechnet. Änderungen und Grenzen prüfen; der Bestand ist noch unverändert.';
  } catch (error) {i$('intake-status').textContent = error.message;}
});
i$('intake-confirm').addEventListener('change', () => {i$('intake-accept').disabled = !intakePreview || !i$('intake-confirm').checked;});
i$('intake-accept').addEventListener('click', async () => {
  if (!intakePreview || !i$('intake-confirm').checked) return;
  const request = {...intakePreview, confirm: true}; invalidateIntake();
  try {
    showDataset(await api('/api/empirical/intake/accept', request));
    i$('intake-status').textContent = 'Neue private Datensatzversion erstellt. Originale erhalten; bestehende Fits unverändert. Nächster fachlicher Schritt: die neue Datenversion als Grundlage eines festgelegten Analyseauftrags prüfen.';
  } catch (error) {i$('intake-status').textContent = error.message;}
});
i$('assemble-existing').addEventListener('click', async () => {
  i$('assemble-existing').disabled = true;
  try {showDataset(await api('/api/empirical/intake/assemble', {})); i$('intake-status').textContent = 'Vorhandene geprüfte Reihen und Kalender auf einem Monatsraster zusammengeführt. Lücken und Ereignisbelege erhalten.';}
  catch (error) {i$('intake-status').textContent = error.message;}
  finally {i$('assemble-existing').disabled = false;}
});

async function loadBusinessEvidence() {
  try {
    const result = await api('/api/empirical/evidence-review');
    const panel = i$('business-evidence'); panel.replaceChildren();
    if (result.status !== 'verified_existing_evidence') return;
    const h = document.createElement('h3'); h.textContent = 'Tesla und Markt: was die vorhandenen Daten zeigen'; panel.append(h);
    for (const row of result.annual_last_three_years) {
      const tesla = row.series.tesla_count, market = row.series.market_bev;
      const p = document.createElement('p');
      const percent = v => v === null ? 'nicht berechenbar' : (100*v).toLocaleString('de-DE',{maximumFractionDigits:1})+' %';
      p.textContent = `${row.year}: Tesla ${tesla.total.toLocaleString('de-DE')} Zulassungen (${percent(tesla.yoy_fraction)} zum Vorjahr), BEV-Markt ${market.total?.toLocaleString('de-DE') || 'nicht vollständig'} (${percent(market.yoy_fraction)}).`;
      panel.append(p);
    }
    const note = document.createElement('p'); note.textContent = 'Marken: alle Antriebe; Markt: BEV. Gegenläufige Entwicklungen zeigen Grenzen einer reinen Markterklärung, aber noch keine kausalen Einzelursachen. Alle Modellvergleiche und negativen Befunde folgen unten.'; panel.append(note);
  } catch {i$('business-evidence').textContent = 'Marktvergleich derzeit nicht verifiziert verfügbar.';}
}
