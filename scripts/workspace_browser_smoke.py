"""Actual Chromium workflow, two isolated synthetic projects and a server restart.

Run with the pinned requirements-demo-browser.lock environment. The script starts
its own loopback server and temporary workspace; it does not use existing local
history, import empirical data or leave generated results in the repository.
"""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
FIRST = 'synthetic-quarter'
SECOND = 'synthetic-no-quarter'


class LocalServer:
    def __init__(self, workspace):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        self.base = f'http://127.0.0.1:{self.port}'
        self.workspace = workspace
        self.process = None
        self.log = tempfile.TemporaryFile()

    def start(self):
        env = dict(os.environ, AAS_WORKSPACE_DIR=str(self.workspace),
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        self.process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'demo.app:app', '--host', '127.0.0.1',
             '--port', str(self.port), '--no-access-log'], cwd=ROOT, env=env,
            stdout=self.log, stderr=self.log)
        for _ in range(150):
            try:
                with urlopen(self.base + '/api/health', timeout=1) as response:
                    if response.status == 200:
                        return
            except OSError:
                if self.process.poll() is not None:
                    raise RuntimeError('Temporary workspace server failed to start')
                time.sleep(.1)
        raise RuntimeError('Temporary workspace server did not become ready')

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process = None

    def close(self):
        self.stop()
        self.log.close()


def get_json(page, base, project_id, suffix='/workspace'):
    response = page.request.get(f'{base}/api/projects/{project_id}{suffix}')
    assert response.ok, response.status
    return response.json()


def ready(page, project_id):
    expect(page.locator('#project')).to_have_value(project_id)
    expect(page.locator('#project')).to_be_enabled(timeout=90000)
    expect(page.locator('#dataset-description')).not_to_contain_text('geladen')


def message(page, text, tool=None):
    page.locator('#agent-input').fill(text)
    page.get_by_role('button', name='Anfrage ausführen', exact=True).click()
    if tool:
        expect(page.locator('#agent-status')).to_have_text('Tool ausgeführt: ' + tool, timeout=90000)
    else:
        expect(page.locator('#agent-status')).to_contain_text('als Notiz gespeichert', timeout=90000)
    expect(page.locator('#agent-send')).to_be_enabled(timeout=90000)


def fit(page):
    page.get_by_role('button', name='Run analysis', exact=True).click()
    expect(page.locator('#status')).to_contain_text('abgeschlossen', timeout=90000)
    expect(page.locator('#run')).to_be_enabled(timeout=90000)
    return page.locator('#run-history').input_value()


def main():
    with tempfile.TemporaryDirectory(prefix='aas-workspace-browser-') as directory:
        server = LocalServer(Path(directory) / 'workspace')
        try:
            server.start()
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=os.environ.get('DEMO_CHROMIUM', '/usr/bin/chromium'),
                    headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1365, 'height': 1000})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(server.base)
                ready(page, FIRST)
                assert page.locator('#project option').count() == 2

                note = 'Prüfnotiz <script>window.workspaceInjected=true</script> bleibt eine Aussage.'
                message(page, note)
                expect(page.locator('#conversation')).to_contain_text(note)
                assert page.locator('#conversation script').count() == 0
                assert page.evaluate('window.workspaceInjected') is None
                assert not get_json(page, server.base, FIRST)['executions']

                proposal = 'Die unvollständig modellierte Baseline bei der Interpretation berücksichtigen.'
                page.locator('#decision-text').fill(proposal)
                page.get_by_role('button', name='Vorschlag speichern', exact=True).click()
                proposed = page.locator('#decisions li[data-status="proposed"]')
                expect(proposed).to_contain_text(proposal)
                proposed.get_by_role('button', name='Ausdrücklich freigeben', exact=True).click()
                expect(page.locator('#decisions li[data-status="approved"]')).to_contain_text(proposal)
                expect(page.locator('#decision-save')).to_be_enabled()

                first_run = fit(page)
                assert first_run
                assert page.locator('#coefficients tr').count() == 6
                assert page.locator('#timeseries svg polyline').count() == 6
                assert page.locator('#residuals svg polyline').count() == 1
                for phrase, tool in (
                        ('Zeige den Beispieldatensatz.', 'describe_dataset'),
                        ('Starte die MMM-Analyse.', 'run_demo_analysis'),
                        ('Vergleiche die beiden Modellläufe.', 'compare_runs'),
                        ('Erkläre die Warnungen und die Modellgrenzen.', 'summarize_diagnostics')):
                    message(page, phrase, tool)
                saved_first = page.locator('#run-history').input_value()
                assert saved_first and saved_first != first_run
                assert page.locator('#comparison-rows tr').count() == 2
                assert page.locator('#response-curves svg polyline').count() == 3
                first_result = get_json(page, server.base, FIRST, '/runs/' + saved_first)
                with page.expect_download() as download:
                    page.locator('#report-export').click()
                assert download.value.suggested_filename == 'synthetic-mmm-report.md'
                assert Path(download.value.path()).read_text() == first_result['markdown_report']

                page.locator('#project').select_option(SECOND)
                ready(page, SECOND)
                expect(page.locator('#model')).to_have_value('without-quarter')
                expect(page.locator('#results')).to_be_hidden()
                expect(page.locator('#conversation')).not_to_contain_text(note)
                expect(page.locator('#decisions')).not_to_contain_text(proposal)
                assert not get_json(page, server.base, SECOND)['runs']
                second_note = 'Nur im zweiten Projekt: Sensitivität ohne Quartalsende.'
                message(page, second_note)
                saved_second = fit(page)
                assert saved_second not in (first_run, saved_first)
                assert page.locator('#coefficients tr').count() == 5
                second_result = get_json(page, server.base, SECOND, '/runs/' + saved_second)
                assert second_result['hashes']['data'] == first_result['hashes']['data']

                page.reload()
                ready(page, SECOND)
                expect(page.locator('#run-history')).to_have_value(saved_second)
                expect(page.locator('#conversation')).to_contain_text(second_note)
                expect(page.locator('#conversation')).not_to_contain_text(note)
                expect(page.locator('#history-status')).to_contain_text('erneut validiert')
                before = {identity: get_json(page, server.base, identity) for identity in (FIRST, SECOND)}
                assert [len(before[identity]['runs']) for identity in (FIRST, SECOND)] == [2, 1]

                # A real application process restart, not merely a page reload.
                server.stop()
                server.start()
                page.reload()
                ready(page, SECOND)
                expect(page.locator('#run-history')).to_have_value(saved_second)
                expect(page.locator('#conversation')).to_contain_text(second_note)
                assert get_json(page, server.base, SECOND, '/runs/' + saved_second) == second_result
                for identity in (FIRST, SECOND):
                    after = get_json(page, server.base, identity)
                    assert after['runs'] == before[identity]['runs']
                    assert after['executions'] == before[identity]['executions']
                    assert after['messages'] == before[identity]['messages']
                    assert after['decisions'] == before[identity]['decisions']

                message(page, 'Wo haben wir aufgehört?', 'resume_workspace')
                expect(page.locator('#agent-answer')).to_contain_text(saved_second)
                assert get_json(page, server.base, SECOND)['runs'] == before[SECOND]['runs']
                page.locator('#project').select_option(FIRST)
                ready(page, FIRST)
                expect(page.locator('#run-history')).to_have_value(saved_first)
                expect(page.locator('#conversation')).to_contain_text(note)
                expect(page.locator('#conversation')).not_to_contain_text(second_note)
                expect(page.locator('#decisions li[data-status="approved"]')).to_contain_text(proposal)
                assert get_json(page, server.base, FIRST, '/runs/' + saved_first) == first_result
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.locator('body').evaluate('(e)=>e.scrollWidth <= window.innerWidth')
                assert not errors, errors
                browser.close()
                print('PASS: actual Chromium notes as text, explicit approval, three real synthetic fits, '
                      'four tools/comparison/report, two-project separation, reload and real process restart, '
                      'unchanged run IDs/hashes/execution counts on restore, resume tool and mobile layout; '
                      'no JavaScript page errors')
        finally:
            server.close()


if __name__ == '__main__':
    main()
