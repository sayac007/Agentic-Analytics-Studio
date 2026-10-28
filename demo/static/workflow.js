'use strict';
let workflowState = null;
let briefDirty = false;
const w$ = id => document.getElementById(id);

function clearHandoff() {
  w$('handoff-panel').hidden = true;
  w$('handoff-text').value = '';
  w$('handoff-status').textContent = '';
}

function markBriefDirty() {
  briefDirty = true;
  w$('brief-status').textContent = 'Ungespeicherte Änderungen: vor KI-Kontext oder Ergebnisübergabe speichern.';
  clearHandoff();
  invalidate();
}

function renderQuality() {
  const container = w$('workflow-quality');
  container.replaceChildren();
  w$('create-handoff').disabled = !bundle || bundle.status !== 'ready';
  if (!workflowState) return;
  const selected = w$('selected-model').value;
  const review = workflowState.review;
  const list = document.createElement('ul');
  container.append(list);
  const labels = {recorded: 'Erfasst', pending: 'Offen', verified: 'Technisch geprüft',
    review: 'Prüfbedarf', failed: 'Fehlgeschlagen', diagnostic: 'Diagnostischer Hinweis'};
  for (const check of [...review.checks, ...(review.models[selected]?.checks || [])]) {
    const item = document.createElement('li');
    item.textContent = `${labels[check.status] || check.status} · ${check.check}: ${check.detail}`;
    list.append(item);
  }
  if (briefDirty) {
    const note = document.createElement('p');
    note.textContent = 'Der Abgleich bezieht sich auf den zuletzt gespeicherten Auftrag.';
    container.prepend(note);
  }
}

async function loadWorkflow(fillForm = false) {
  try {
    workflowState = await api('/api/empirical/workflow');
    if (fillForm) {
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
    }
    renderQuality();
  } catch (error) {
    workflowState = null;
    w$('workflow-quality').textContent = 'Qualitätsstand nicht verfügbar: ' + error.message;
    w$('brief-status').textContent = 'Auftrag konnte nicht gelesen werden: ' + error.message;
  }
}

for (const id of ['brief-question', 'brief-audience', 'brief-decision', 'brief-interfaces']) {
  w$(id).addEventListener('input', markBriefDirty);
}
w$('research-brief').addEventListener('submit', async event => {
  event.preventDefault();
  const required = [...w$('driver-requirements').querySelectorAll('input:checked')].map(input => input.value);
  try {
    await api('/api/empirical/workflow', {question: w$('brief-question').value,
      audience: w$('brief-audience').value, decision: w$('brief-decision').value,
      interface_notes: w$('brief-interfaces').value, required_drivers: required});
    invalidate(); clearHandoff();
    await loadWorkflow(true);
  } catch (error) { w$('brief-status').textContent = error.message; }
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
