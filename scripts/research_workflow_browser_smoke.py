"""Local browser smoke: constructed software fixture only; no source download or provider call."""
import hashlib, json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from test_empirical import bundle
from empirical.data import json_bytes
with tempfile.TemporaryDirectory(prefix='aas-workflow-browser-fixture-') as tmp:
 root=Path(tmp); results=root/'fixture'; results.mkdir(); b=bundle();files={}
 for metadata in b['data']['sources'].values(): metadata.update(urls=[],attribution='SOFTWARE FIXTURE ONLY',missing_months=[],sha256='b'*64,classification='SOFTWARE_TEST_FIXTURE')
 # A failed fit must stay visible in the presentation and when selected.
 b['results']['models']['macro_diesel_lag3']={'status':'not_estimable','reason':'SOFTWARE FIXTURE rank failure','stationarity':{}}
 for name in ('data','results','provenance'):
  raw=json_bytes(b[name]); (results/(name+'.json')).write_bytes(raw);files[name+'.json']=hashlib.sha256(raw).hexdigest()
 (results/'manifest.json').write_bytes(json_bytes({'version':'observed-studio-v1','classification':'OBSERVED_PRIVATE','files':files}))
 original={p.name:p.read_bytes() for p in results.iterdir()}
 with socket.socket() as sock: sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 base=f'http://127.0.0.1:{port}';log=tempfile.TemporaryFile()
 env=dict(os.environ,AAS_WORKSPACE_DIR=str(root/'state'),AAS_EMPIRICAL_DIR=str(results),AAS_OPENAI_ENABLED='1',OPENAI_API_KEY='sk-WORKFLOW_BROWSER_FIXTURE_NOT_REAL_123456',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 env.pop('AAS_PUBLIC_ORIGIN',None)
 def start():
  proc=subprocess.Popen([sys.executable,'-m','uvicorn','demo.app:app','--host','127.0.0.1','--port',str(port),'--no-access-log'],cwd=ROOT,env=env,stdout=log,stderr=log)
  for _ in range(150):
   try:
    with urlopen(base+'/api/health',timeout=1):return proc
   except OSError:
    if proc.poll() is not None:raise RuntimeError('Server failed')
    time.sleep(.05)
  raise RuntimeError('Server startup timed out')
 proc=start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
   page=browser.new_page(viewport={'width':1360,'height':1000});errors=[]; external=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('**/api/empirical/messages',lambda route:route.abort())
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(base) else None)
   page.goto(base)
   page.locator('#driver-requirements tr').nth(10).wait_for()
   assert page.locator('.workflow-nav a').count()==6
   assert page.locator('#driver-requirements tr').count()==11
   page.locator('#brief-question').fill('Welche zusätzliche Information hilft Sales und Operations?')
   page.locator('input[value="delivery"]').check()
   page.locator('#create-handoff').click()
   assert 'Zuerst' in page.locator('#handoff-status').inner_text()
   page.locator('#research-brief button').click()
   page.locator('#brief-status').filter(has_text='Privat gespeichert').wait_for()
   assert 'Lieferfähigkeit' in page.locator('#workflow-quality').inner_text()
   assert 'Nicht enthalten' in page.locator('#workflow-quality').inner_text()
   page.locator('#create-handoff').click()
   page.locator('#handoff-panel').wait_for(state='visible')
   text=page.locator('#handoff-text').input_value()
   assert 'SOFTWARE FIXTURE rank failure' in text and 'Schritt 3' in text
   assert 'Keine Neuberechnung' in text and 'historischer Echtzeit-Test' in text
   page.locator('[data-review-question]').nth(1).click()
   page.locator('#preview').click()
   page.locator('#observed-consent-panel').wait_for(state='visible')
   preview=json.loads(page.locator('#context-preview').text_content())
   assert 'delivery' in preview['business_work_order']['required_drivers']
   assert page.locator('#send-observed').is_disabled()
   assert 'Geplanter Versand' in page.locator('#context-summary').inner_text()
   page.locator('#observed-consent').check()
   assert page.locator('#send-observed').is_enabled()
   page.locator('#brief-decision').fill('Neue Entscheidung, deshalb neue Freigabe.')
   assert page.locator('#observed-consent-panel').is_hidden()
   page.locator('#research-brief button').click()
   page.locator('#brief-status').filter(has_text='Privat gespeichert').wait_for()
   page.locator('#selected-model').select_option('macro_diesel_lag3')
   assert page.locator('#observed-coefficients tr').count()==0
   assert 'Fehlgeschlagen' in page.locator('#workflow-quality').inner_text()
   page.locator('#create-handoff').click()
   page.locator('#handoff-panel').wait_for(state='visible')
   assert 'Term (Gesamtfenster)' not in page.locator('#handoff-text').input_value()
   proc.terminate();proc.wait(timeout=10);proc=start()
   page.reload();page.locator('#brief-status').filter(has_text='Privat gespeichert').wait_for()
   assert page.locator('#brief-decision').input_value()=='Neue Entscheidung, deshalb neue Freigabe.'
   assert page.locator('input[value="delivery"]').is_checked()
   page.set_viewport_size({'width':390,'height':844})
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
   assert original=={p.name:p.read_bytes() for p in results.iterdir()}
   with urlopen(base+'/api/empirical') as r:state=json.load(r)
   assert state['ai_budget']['charged_nano_usd']==0
   assert not errors,errors
   assert not external,external
   browser.close()
  print('PASS: 6 blocks; durable brief/requirements; gaps; evidence+Copilot handoff; failed-fit visibility; explicit AI preview/consent invalidation; desktop/mobile; restart; unchanged snapshot bytes; zero external/provider requests. SOFTWARE FIXTURE ONLY.')
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=10)
  log.close()
