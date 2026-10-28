"""Browser consent/error tests with explicitly simulated provider HTTP responses.

The local app, SQLite project and one synthetic fit are real. Playwright routes
fake the external-mode API contract so this script needs no API key, makes no
provider request and is NOT live OpenAI integration evidence. Backend provider,
budget and persistence behavior require their separate HTTP/unit tests.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from playwright.sync_api import expect, sync_playwright

from workspace_browser_smoke import FIRST, SECOND, LocalServer, fit, message, ready


def main():
    with tempfile.TemporaryDirectory(prefix='aas-conversation-browser-') as directory:
        server = LocalServer(Path(directory) / 'workspace')
        try:
            with patch.dict(os.environ, {'AAS_OPENAI_ENABLED': '0'}):
                server.start()
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=os.environ.get('DEMO_CHROMIUM', '/usr/bin/chromium'),
                    headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1365, 'height': 1100})
                errors, previews, sends = [], [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                status = dict(provider='openai', configured=False, enabled=False, available=False,
                              model='TEST FAKE PROVIDER', reason='test_fake_not_configured',
                              limits=dict(requests=3, tools=2, max_output_tokens=1536,
                                          request_bytes=16384, turn_usd=.1, workspace_usd=1),
                              live_verification='not_verified')
                ledger = dict(limit_nano_usd=1_000_000_000, charged_nano_usd=0,
                              remaining_nano_usd=1_000_000_000, unknown_nano_usd=0)
                latest = {}
                fail_send = False
                approved_decision = None
                approved_text = 'SYNTHETIC TEST: Konditionale Unsicherheit ausdrücklich kennzeichnen.'

                page.route('**/api/ai/status', lambda route: route.fulfill(json=status))

                def workspace(route):
                    response = route.fetch()
                    state = response.json()
                    state['ai'] = dict(turns=[], budget=ledger)
                    route.fulfill(response=response, json=state)

                page.route('**/api/projects/*/workspace', workspace)

                def preview(route):
                    body = route.request.post_data_json
                    assert set(body['approved_decision_ids']).issubset({approved_decision})
                    assert set(body) == {'message', 'conversation_id', 'run_id', 'approved_decision_ids'}
                    context = dict(classification='SYNTHETIC / NOT EMPIRICAL',
                                   question=body['message'], run_id=body['run_id'],
                                   notice='TEST FAKE context, not real provider execution',
                                   prior_external_turns=[],
                                   selected_decisions=[dict(id=identity, text=approved_text)
                                                       for identity in body['approved_decision_ids']])
                    digest = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()
                    latest.update(body=body, digest=digest)
                    previews.append(body)
                    route.fulfill(json=dict(context_sha256=digest, context=context,
                                            limits=status['limits'], notice='TEST FAKE preview only'))

                page.route('**/api/projects/*/agent-context', preview)

                def send(route):
                    nonlocal fail_send
                    body = route.request.post_data_json
                    if body.get('mode') != 'openai':
                        route.continue_()
                        return
                    assert body['consent'] is True
                    assert body['context_sha256'] == latest['digest']
                    assert body['message'] == latest['body']['message']
                    assert body['run_id'] == latest['body']['run_id']
                    assert body['approved_decision_ids'] == latest['body']['approved_decision_ids']
                    sends.append(body)
                    if fail_send:
                        ledger.update(charged_nano_usd=100_000_000,
                                      remaining_nano_usd=900_000_000, unknown_nano_usd=100_000_000)
                        route.fulfill(status=503, json={'detail': 'TEST FAKE provider timeout; reservation retained'})
                        return
                    ledger.update(charged_nano_usd=12345, remaining_nano_usd=999_987_655)
                    route.fulfill(json=dict(
                        status='completed', mode='openai', tool=None, executed=True,
                        text='TEST FAKE model interpretation <script>window.responseInjected=true</script>',
                        output=None, execution_id=None, ai_turn_id='test-fake-turn',
                        tool_executions=[dict(id='test-fake-execution', tool='describe_dataset')],
                        evidence=[dict(tool='describe_dataset', execution_id='test-fake-execution',
                                       output=dict(classification='SYNTHETIC / NOT EMPIRICAL',
                                                   notice='TEST FAKE evidence projection; not a real tool execution'))],
                        usage=dict(input_tokens=12, output_tokens=4), cost_estimate_nano_usd=12345))

                page.route('**/api/projects/*/messages', send)
                page.goto(server.base + '/archive/synthetic')
                ready(page, FIRST)
                assert page.locator('#agent-panel').evaluate(
                    '(e)=>Boolean(e.compareDocumentPosition(document.querySelector("#run-form")) & Node.DOCUMENT_POSITION_FOLLOWING)')
                expect(page.locator('#agent-mode')).to_have_value('local')
                message(page, 'Lokale synthetische Prüfnotiz; nicht automatisch nach extern senden.')
                saved_run = fit(page)

                def proposal(text, kind='decision', approve=False):
                    response = page.request.post(server.base + f'/api/projects/{FIRST}/decisions',
                                                 data=dict(text=text, kind=kind))
                    assert response.ok, response.status
                    identity = response.json()['id']
                    if approve:
                        response = page.request.post(
                            server.base + f'/api/projects/{FIRST}/decisions/{identity}/approve', data={})
                        assert response.ok, response.status
                    return identity

                approved_decision = proposal(approved_text, approve=True)
                excluded_proposal = 'SYNTHETIC TEST: Noch nicht freigegebener Vorschlag.'
                excluded_workorder = 'SYNTHETIC TEST: Entwicklungsauftrag nicht automatisch übertragen.'
                proposal(excluded_proposal)
                proposal(excluded_workorder, kind='development_workorder', approve=True)
                page.reload()
                ready(page, FIRST)

                page.locator('#agent-mode').select_option('openai')
                choice = page.locator(f'.ai-decision-choice[value="{approved_decision}"]')
                expect(choice).not_to_be_checked()
                assert page.locator('.ai-decision-choice').count() == 1
                expect(page.locator('#ai-decision-options')).not_to_contain_text(excluded_proposal)
                expect(page.locator('#ai-decision-options')).not_to_contain_text(excluded_workorder)
                page.locator('#agent-input').fill('SYNTHETIC TEST: Welche Grenzen hat dieses Modell?')
                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                expect(page.locator('#ai-context-preview')).to_contain_text(saved_run)
                assert len(previews) == 1 and not sends
                assert previews[0]['approved_decision_ids'] == []
                page.locator('#ai-consent').check()
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                expect(page.locator('#ai-status')).to_contain_text('prüft keinen Live-Zugang')

                # Test the configured UI contract, still with a disabled real server.
                status.update(configured=True, enabled=True, available=True, reason=None)
                page.reload()
                ready(page, FIRST)
                page.locator('#agent-mode').select_option('openai')
                question = 'SYNTHETIC TEST: Erkläre die Unsicherheit.'
                page.locator('#agent-input').fill(question)
                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                page.locator('#ai-consent').check()
                expect(page.locator('#ai-confirm-send')).to_be_enabled()
                choice.check()
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                expect(page.locator('#ai-consent')).not_to_be_checked()
                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                expect(page.locator('#ai-context-preview')).to_contain_text(approved_text)
                page.locator('#ai-consent').check()
                page.locator('#agent-input').fill(question + ' Frage geändert.')
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                expect(page.locator('#ai-consent')).not_to_be_checked()
                assert not sends

                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                page.locator('#ai-consent').check()
                page.locator('#run-history').select_option('')
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                expect(page.locator('#ai-consent')).not_to_be_checked()
                page.locator('#run-history').select_option(saved_run)
                expect(page.locator('#run-history')).to_be_enabled()

                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                page.locator('#ai-consent').check()
                page.locator('#ai-confirm-send').click()
                expect(page.locator('#agent-status')).to_contain_text('modellgenerierte Interpretation')
                expect(page.locator('#ai-response-label')).to_be_visible()
                expect(page.locator('#agent-answer')).to_contain_text('<script>')
                assert page.locator('#agent-answer script').count() == 0
                assert page.evaluate('window.responseInjected') is None
                expect(page.locator('#ai-evidence')).to_contain_text('TEST FAKE evidence projection')
                expect(page.locator('#ai-usage')).to_contain_text('12345')
                expect(page.locator('#ai-confirm-send')).to_be_disabled()
                assert len(sends) == 1
                assert sends[0]['approved_decision_ids'] == [approved_decision]
                expect(page.locator('#agent-send')).to_be_enabled()
                expect(choice).to_be_checked()  # Context refresh preserves explicit selection.

                fail_send = True
                page.locator('#agent-input').fill('SYNTHETIC TEST: Simulierter Providerfehler.')
                page.locator('#agent-send').click()
                expect(page.locator('#agent-status')).to_contain_text('Kontextvorschau bereit')
                page.locator('#ai-consent').check()
                page.locator('#ai-confirm-send').click()
                expect(page.locator('#agent-status')).to_contain_text('OpenAI-Aufruf fehlgeschlagen')
                expect(page.locator('#agent-send')).to_be_enabled()
                expect(page.locator('#ai-response-label')).to_be_hidden()
                expect(page.locator('#agent-answer')).to_be_empty()
                expect(page.locator('#ai-budget')).to_contain_text('unbekannte Nutzung USD 0,1000')
                assert len(sends) == 2  # No retry or automatic local fallback.

                page.locator('#project').select_option(SECOND)
                ready(page, SECOND)
                expect(page.locator('#agent-mode')).to_have_value('local')
                expect(page.locator('#ai-preview-panel')).to_be_hidden()
                expect(page.locator('#agent-answer')).to_be_empty()
                expect(page.locator('#ai-context-preview')).to_be_empty()
                assert page.locator('.ai-decision-choice').count() == 0
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.locator('body').evaluate('(e)=>e.scrollWidth <= window.innerWidth')
                assert not errors, errors
                browser.close()
                print('PASS: conversation-first Chromium UI, real local note/fit, '
                      'TEST-FAKE provider preview/consent/hash binding, unavailable state, '
                      'optional approved-decision selection, question/run/selection invalidation, '
                      'escaped interpretation/evidence/usage, '
                      'simulated timeout with unknown reservation, no retry/fallback, '
                      'project reset and mobile layout. NO LIVE OPENAI REQUEST.')
        finally:
            server.close()


if __name__ == '__main__':
    main()
