'use strict';
let workflowState = null;
let briefDirty = false;
let briefRevision = 0;
let savingBrief = false;
const w$ = id => document.getElementById(id);
const workflowSteps = [
  {id: 'task-definition', title: 'Datenauftrag', help: 'Formuliere die Geschäftsfrage, die Empfänger und die Entscheidung. Speichere deinen Auftrag.'},
  {id: 'task-drivers', title: 'Muss-Treiber', help: 'Welche Treiber braucht deine Fragestellung? Markiere sie und speichere. Ein Häkchen ergänzt keine Modellvariable.'},
  {id: 'task-data', title: 'Daten zusammenstellen', help: 'Prüfe die vorhandenen Quellen, Einheiten und Lücken. Die Schaltfläche bereitet auch die festen Analysen vor.'},
  {id: 'task-analysis', title: 'Analyse verstehen', help: 'Vergleiche die festen Varianten mit ihrer gepaarten Basis. Wähle anschließend ein Modell für die Detailansicht.'},
  {id: 'task-quality', title: 'Qualität und KI-Kommentare', help: 'Beginne mit offenen Prüfpunkten. Optional kannst du eine Erklärung durch KI vorbereiten; gesendet wird erst nach deiner Freigabe.'},
  {id: 'task-presentation', title: 'Präsentation vorbereiten', help: 'Prüfe die Ergebnisübergabe und nutze die Copilot-Anleitung. Die Anleitung funktioniert auch ohne Ergebnisdaten oder API-Schlüssel.'},
];
let activeStep = 'task-definition';

function syncWorkflowNavigation() {
  const index = workflowSteps.findIndex(step => step.id === activeStep);
  const step = workflowSteps[index];
  for (const panel of document.querySelectorAll('[data-workflow-step]')) {
    panel.hidden = panel.dataset.workflowStep !== activeStep;
  }
  for (const link of document.querySelectorAll('.workflow-nav a')) {
    if (link.hash === '#' + activeStep) link.setAttribute('aria-current', 'step');
    else link.removeAttribute('aria-current');
  }
  w$('workflow-position').textContent = `Schritt ${index + 1} von ${workflowSteps.length}`;
  w$('workflow-title').textContent = step.title;
  w$('workflow-help').textContent = step.help;
  w$('previous-step').disabled = index === 0;
  w$('next-step').hidden = index === workflowSteps.length - 1;
  w$('next-step').textContent = index < workflowSteps.length - 1 ? 'Weiter: ' + workflowSteps[index + 1].title : 'Weiter';
  w$('workflow-empty').hidden = !(['task-analysis', 'task-quality'].includes(activeStep) && bundle?.status !== 'ready');
  w$('workflow-save-state').textContent = briefDirty
    ? 'Ungespeicherte Änderungen – sie bleiben beim Schrittwechsel erhalten. Vor einer KI-Anfrage oder Ergebnisübergabe speichern.'
    : workflowState?.updated_at ? 'Auftrag gespeichert. Die Schrittnavigation ist keine fachliche Freigabe.'
      : 'Auftrag noch nicht bestätigt. Du kannst alle Schritte ansehen.';
}

function showWorkflowStep(id, focus = true) {
  if (!workflowSteps.some(step => step.id === id)) return;
  activeStep = id;
  syncWorkflowNavigation();
  history.replaceState(null, '', '#' + id);
  if (focus) {
    w$('workflow-title').focus({preventScroll: true});
    w$('workflow-title').scrollIntoView({block: 'start', behavior: 'auto'});
  }
}

function initWorkflowNavigation() {
  const fromHash = location.hash.slice(1);
  if (workflowSteps.some(step => step.id === fromHash)) activeStep = fromHash;
  document.body.classList.add('guided-workflow');
  for (const link of document.querySelectorAll('.workflow-nav a')) {
    link.addEventListener('click', event => {event.preventDefault(); showWorkflowStep(link.hash.slice(1));});
  }
  for (const button of document.querySelectorAll('[data-go-step]')) {
    button.addEventListener('click', () => showWorkflowStep(button.dataset.goStep));
  }
  w$('previous-step').addEventListener('click', () => showWorkflowStep(workflowSteps[workflowSteps.findIndex(s => s.id === activeStep) - 1]?.id));
  w$('next-step').addEventListener('click', () => showWorkflowStep(workflowSteps[workflowSteps.findIndex(s => s.id === activeStep) + 1]?.id));
  window.addEventListener('hashchange', () => showWorkflowStep(location.hash.slice(1), false));
  window.addEventListener('beforeunload', event => {
    if (briefDirty) {event.preventDefault(); event.returnValue = '';}
  });
  syncWorkflowNavigation();
}

function clearHandoff() {
  w$('handoff-panel').hidden = true;
  w$('handoff-text').value = '';
  w$('handoff-status').textContent = '';
}

function markBriefDirty() {
  briefRevision += 1;
  briefDirty = true;
  w$('brief-status').textContent = 'Ungespeicherte Änderungen: vor KI-Kontext oder Ergebnisübergabe speichern.';
  clearHandoff();
  invalidate();
  w$('drivers-save-status').textContent = 'Ungespeicherte Änderungen.';
  syncWorkflowNavigation();
}

function renderQuality() {
  const container = w$('workflow-quality');
  container.replaceChildren();
  w$('create-handoff').disabled = !bundle || bundle.status !== 'ready';
  w$('quality-model').textContent = 'Ausgewähltes Detailmodell: ' + modelNames[w$('selected-model').value];
  syncWorkflowNavigation();
  if (!workflowState) return;
  const selected = w$('selected-model').value;
  const review = workflowState.review;
  const allChecks = [...review.checks, ...(review.models[selected]?.checks || [])];
  const openChecks = allChecks.filter(check => ['review', 'failed', 'pending'].includes(check.status));
  const heading = document.createElement('h3');
  heading.textContent = openChecks.length ? `${openChecks.length} offene Prüfpunkte` : 'Keine offenen Punkte in dieser technischen Checkliste';
  container.append(heading);
  const reminder = document.createElement('p');
  reminder.textContent = 'Dies ist keine fachliche Modellfreigabe. Diagnostische Hinweise und wissenschaftliche Grenzen bleiben bestehen.';
  container.append(reminder);
  const list = document.createElement('ul'); container.append(list);
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = `Alle ${allChecks.length} Prüfungen und ihre Belege`;
  details.append(summary);
  const complete = document.createElement('ul'); details.append(complete); container.append(details);
  const labels = {recorded: 'Erfasst', pending: 'Offen', verified: 'Technisch geprüft',
    review: 'Prüfbedarf', failed: 'Fehlgeschlagen', diagnostic: 'Diagnostischer Hinweis'};
  for (const check of allChecks) {
    const item = document.createElement('li');
    item.className = 'quality-item'; item.dataset.status = check.status;
    item.textContent = `${labels[check.status] || check.status} · ${check.check}: ${check.detail}`;
    complete.append(item);
    if (openChecks.includes(check)) list.append(item.cloneNode(true));
  }
  if (briefDirty) {
    const note = document.createElement('p');
    note.textContent = 'Der Abgleich bezieht sich auf den zuletzt gespeicherten Auftrag.';
    container.prepend(note);
  }
}

async function loadWorkflow(fillForm = false, expectedRevision = briefRevision) {
  try {
    workflowState = await api('/api/empirical/workflow');
    if (fillForm && expectedRevision === briefRevision) {
      const b = workflowState.brief;
      for (const [id, key] of [['brief-question','question'], ['brief-audience','audience'],
        ['brief-decision','decision'], ['brief-interfaces','interface_notes']]) w$(id).value = b[key];
      w$('driver-requirements').replaceChildren();
      for (const driver of workflowState.review.drivers) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        const input = document.createElement('input');
        input.type = 'checkbox'; input.value = driver.id;
        input.checked = driver.required;
        input.disabled = ['calendar', 'dynamics'].includes(driver.id);
        input.setAttribute('aria-label', 'Muss-Treiber: ' + driver.label);
        input.addEventListener('change', markBriefDirty);
        cell.append(input); row.append(cell);
        for (const value of [driver.label + ' · ' + driver.role, driver.definition,
          driver.included_in_models.length ? driver.included_in_models.map(k => modelNames[k]).join(', ')
            : driver.availability === 'not_checked' ? 'Noch nicht geprüft' : 'Nicht als Modellterm verfügbar']) {
          const td = document.createElement('td'); td.textContent = value; row.append(td);
        }
        w$('driver-requirements').append(row);
      }
      briefDirty = false;
      w$('brief-status').textContent = workflowState.updated_at
        ? 'Privat gespeichert · ' + new Date(workflowState.updated_at).toLocaleString('de-DE')
        : 'Vorbelegter Pilotauftrag; prüfen und für deinen Anwendungsfall speichern.';
      w$('drivers-save-status').textContent = workflowState.updated_at ? 'Muss-Treiber privat gespeichert.' : 'Anforderungen prüfen und speichern.';
    }
    renderQuality();
  } catch (error) {
    workflowState = null;
    w$('workflow-quality').textContent = 'Qualitätsstand nicht verfügbar: ' + error.message;
    w$('brief-status').textContent = 'Auftrag konnte nicht gelesen werden: ' + error.message;
    w$('drivers-save-status').textContent = 'Speicherstand nicht verfügbar. Bitte erneut laden.';
  }
}

for (const id of ['brief-question', 'brief-audience', 'brief-decision', 'brief-interfaces']) {
  w$(id).addEventListener('input', markBriefDirty);
}
w$('research-brief').addEventListener('submit', async event => {
  event.preventDefault();
  if (savingBrief) return;
  savingBrief = true;
  const submittedRevision = briefRevision;
  const buttons = [w$('research-brief').querySelector('button'), w$('save-drivers')];
  for (const button of buttons) {button.disabled = true; button.setAttribute('aria-busy', 'true');}
  const required = [...w$('driver-requirements').querySelectorAll('input:checked')].map(input => input.value);
  try {
    await api('/api/empirical/workflow', {question: w$('brief-question').value,
      audience: w$('brief-audience').value, decision: w$('brief-decision').value,
      interface_notes: w$('brief-interfaces').value, required_drivers: required});
    invalidate(); clearHandoff();
    await loadWorkflow(true, submittedRevision);
  } catch (error) {
    w$('brief-status').textContent = error.message;
    w$('drivers-save-status').textContent = error.message;
  } finally {
    savingBrief = false;
    for (const button of buttons) {button.disabled = false; button.removeAttribute('aria-busy');}
  }
});
w$('save-drivers').addEventListener('click', () => {
  const form = w$('research-brief');
  if (!form.checkValidity()) {showWorkflowStep('task-definition'); form.reportValidity(); return;}
  form.requestSubmit();
});

for (const button of document.querySelectorAll('[data-review-question]')) {
  button.addEventListener('click', () => {
    w$('question').value = button.dataset.reviewQuestion;
    invalidate(); w$('question').focus();
    w$('chat-status').textContent = 'Prüffrage vorbereitet. Erst Kontext prüfen; noch kein externer Aufruf.';
  });
}

async function showHandoff(instructionsOnly) {
  clearHandoff();
  if (!instructionsOnly && briefDirty) {
    w$('handoff-status').textContent = 'Zuerst Auftrag und Muss-Treiber speichern.';
    return;
  }
  try {
    const path = instructionsOnly ? '/api/empirical/copilot-instructions'
      : '/api/empirical/presentation?model=' + encodeURIComponent(w$('selected-model').value);
    const response = await fetch(path);
    if (!response.ok) throw Error('Verifizierte Übergabe derzeit nicht verfügbar. Daten- und Qualitätsstand prüfen.');
    w$('handoff-text').value = await response.text();
    w$('handoff-panel').hidden = false;
    w$('handoff-status').textContent = 'Text lokal erstellt. Vor einer bewussten Weitergabe vollständig prüfen.';
  } catch (error) { w$('handoff-status').textContent = error.message; }
}
w$('create-handoff').addEventListener('click', () => showHandoff(false));
w$('show-copilot').addEventListener('click', () => showHandoff(true));
w$('copy-handoff').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(w$('handoff-text').value);
    w$('handoff-status').textContent = 'In deine Zwischenablage kopiert; kein Versand an einen Anbieter.';
  } catch {
    w$('handoff-text').focus(); w$('handoff-text').select();
    w$('handoff-status').textContent = 'Text ausgewählt. Mit Strg+C kopieren.';
  }
});
