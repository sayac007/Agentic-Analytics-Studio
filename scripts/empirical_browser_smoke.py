"""Private local real-data UI check; never uploads data or calls OpenAI.

--source-archive must name an existing reviewed private source archive. Actual
observations remain in temporary local state; no screenshot or public artifact
is written. A clearly fake server key enables preview UI only; paid POSTs are
blocked by the test browser and never clicked. This is not live API evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-archive',type=Path,required=True)
a=p.parse_args()
with tempfile.TemporaryDirectory(prefix='aas-observed-browser-') as tmp:
    root=Path(tmp);log=tempfile.TemporaryFile();process=None
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    env=dict(os.environ,AAS_WORKSPACE_DIR=str(root/'state'),AAS_EMPIRICAL_SOURCE_DIR=str(a.source_archive.resolve()),
             AAS_OPENAI_ENABLED='1',OPENAI_API_KEY='sk-SOFTWARE_BROWSER_TEST_NOT_A_REAL_KEY_123456',
             OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env.pop('AAS_EMPIRICAL_DIR',None);env.pop('AAS_PUBLIC_ORIGIN',None)
    def start():
        process=subprocess.Popen([sys.executable,'-m','uvicorn','demo.app:app','--host','127.0.0.1','--port',str(port),'--no-access-log'],
                                 cwd=ROOT,env=env,stdout=log,stderr=log)
        for _ in range(180):
            try:
                with urlopen(base+'/api/health',timeout=1):return process
            except OSError:
                if process.poll() is not None:raise RuntimeError('Local empirical server failed')
                time.sleep(.05)
        raise RuntimeError('Local empirical server unavailable')
    try:
        process=start()
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1360,'height':1000});errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            # Safety: this test never sends a provider request, even accidentally.
            page.route('**/api/empirical/messages',lambda route:route.abort())
            page.goto(base)
            page.locator('.workflow-nav a[href="#task-data"]').click()
            page.locator('#status').filter(has_text='noch nicht').wait_for()
            page.locator('#prepare').click()
            page.locator('#observed-results').wait_for(state='visible',timeout=90000)
            assert page.locator('#coverage tr').count()==5
            assert page.locator('#models tr').count()==8
            assert page.locator('#peaks tr').count()==8
            page.locator('#series').select_option('diesel_de')
            path=page.locator('#observed-chart path').get_attribute('d')
            assert path.count('M')>1,'Missing diesel months were connected'
            page.locator('.workflow-nav a[href="#task-analysis"]').click()
            page.locator('#selected-model').select_option('macro_diesel_lag3')
            assert page.locator('#stationarity tr').count()==8
            assert page.locator('#stationarity-assessment').inner_text()
            assert page.locator('#observed-coefficients tr').count()==17
            page.locator('.workflow-nav a[href="#task-quality"]').click()
            page.locator('#question').fill('Welche Unsicherheit bleibt bei den Residuen?')
            page.locator('#preview').click()
            page.locator('#observed-consent-panel').wait_for(state='visible')
            context=json.loads(page.locator('#context-preview').text_content())
            assert context['classification']=='OBSERVED_PRIVATE'
            assert context['selected_model']=='macro_diesel_lag3'
            assert 'series' not in context and 'history' not in context
            assert not page.locator('#observed-consent').is_checked()
            assert page.locator('#send-observed').is_disabled()
            page.locator('#observed-consent').check()
            assert page.locator('#send-observed').is_enabled()
            page.locator('#question').fill('Andere Frage, neue Freigabe erforderlich.')
            assert page.locator('#observed-consent-panel').is_hidden()
            assert page.locator('#send-observed').is_disabled()
            with urlopen(base+'/api/empirical') as r:before=json.load(r)
            assert before['ai_budget']['charged_nano_usd']==0
            hashes={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (root/'state/empirical').rglob('*.json')}
            process.terminate();process.wait(timeout=10);process=start()
            page.goto(base);page.locator('#observed-results').wait_for(state='visible')
            with urlopen(base+'/api/empirical') as r:after=json.load(r)
            assert before['snapshot_sha256']==after['snapshot_sha256']
            assert before['results']==after['results']
            assert hashes=={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (root/'state/empirical').rglob('*.json')}
            assert not errors,errors
            browser.close()
        print('PASS: real private source archive -> actual HTTP fit -> 8 models/5 observed series/stationarity/residual research; gaps retained; private-context preview/consent invalidation; process restart preserves original result bytes; no OpenAI call or public upload.')
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        log.close()
