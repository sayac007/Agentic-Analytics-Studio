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
   # Simulated authentication failure; the server/provider never receives this POST.
   page.route('**/api/empirical/messages',lambda route:route.fulfill(status=503,content_type='application/json',body=json.dumps({'detail':'SOFTWARE FIXTURE HTTP 401','code':'provider_authentication'})))
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(base) else None)
   page.goto(base)
   page.locator('#driver-requirements tr').nth(10).wait_for(state='attached')
   assert page.locator('.workflow-nav a').count()==6
   assert page.locator('#driver-requirements tr').count()==11
   def step(name): page.locator('.workflow-nav a[href="#task-'+name+'"]').click()
   assert page.locator('#task-definition').is_visible()
   assert page.locator('#task-drivers').is_hidden()
   assert page.locator('[aria-current="step"]').count()==1
   page.locator('#brief-question').fill('')
   step('drivers');page.locator('#save-drivers').click()
   assert page.locator('#task-definition').is_visible()
   assert page.locator('#brief-question').evaluate('(n)=>n===document.activeElement')
   page.locator('#brief-question').fill('Welche zusätzliche Information hilft Sales und Operations?')
   # Keyboard navigation must preserve the unsaved brief.
   page.locator('#next-step').focus();page.locator('#next-step').press('Enter')
   assert page.locator('#task-drivers').is_visible()
   assert page.locator('#workflow-title').evaluate('(n)=>n===document.activeElement')
   page.locator('input[value="delivery"]').check()
   step('presentation')
   page.locator('#create-handoff').click()
   assert 'Zuerst' in page.locator('#handoff-status').inner_text()
   step('drivers')
   page.locator('#save-drivers').click()
   page.locator('#drivers-save-status').filter(has_text='privat gespeichert').wait_for()
   step('data')
   page.locator('#assemble-existing').click()
   page.locator('#intake-status').filter(has_text='zusammengeführt').wait_for()
   page.locator('#intake-file').set_input_files({'name':'SOFTWARE_fixture.csv','mimeType':'text/csv','buffer':b'month,value\n2020-01,1.5\n2020-03,2.5\n'})
   page.locator('#intake-mapping').wait_for(state='visible')
   page.locator('#intake-new-id').fill('browser_metric')
   page.locator('#intake-label').fill('SOFTWARE FIXTURE ONLY')
   page.locator('#intake-unit').fill('test_unit')
   page.locator('#intake-definition').fill('Constructed browser fixture; not a real empirical measurement')
   page.locator('#intake-source').fill('Software fixture')
   page.locator('#intake-vintage').fill('unbekannt')
   page.locator('#intake-rights').check()
   page.locator('#intake-compare').click()
   page.locator('#intake-review').wait_for(state='visible')
   assert 'Keine historische Überlappung' in page.locator('#intake-warnings').inner_text()
   assert page.locator('#intake-accept').is_disabled()
   page.locator('#intake-confirm').check();page.locator('#intake-accept').click()
   page.locator('#intake-status').filter(has_text='Neue private Datensatzversion').wait_for()
   assert 'browser_metric' in page.locator('#intake-coverage').inner_text()
   with urlopen(base+'/api/empirical/intake/panel') as response:panel=response.read().decode()
   assert 'browser_metric' in panel.splitlines()[0]
   # It did not fit a model or replace original observations/results.
   assert original=={p.name:p.read_bytes() for p in results.iterdir()}
   step('quality')
   assert 'Lieferfähigkeit' in page.locator('#workflow-quality').inner_text()
   assert 'Nicht enthalten' in page.locator('#workflow-quality').inner_text()
   assert page.locator('#workflow-quality details').evaluate('(n)=>!n.open')
   assert 'offene Prüfpunkte' in page.locator('#workflow-quality h3').inner_text()
   step('presentation')
   page.locator('#create-handoff').click()
   page.locator('#handoff-panel').wait_for(state='visible')
   text=page.locator('#handoff-text').input_value()
   assert 'SOFTWARE FIXTURE rank failure' in text and 'Schritt 3' in text
   assert 'Keine Neuberechnung' in text and 'historischer Echtzeit-Test' in text
   step('quality')
   page.locator('[data-review-question]').nth(1).click()
   page.locator('#preview').click()
   page.locator('#observed-consent-panel').wait_for(state='visible')
   preview=json.loads(page.locator('#context-preview').text_content())
   assert 'delivery' in preview['business_work_order']['required_drivers']
   assert page.locator('#send-observed').is_disabled()
   assert 'Geplanter Versand' in page.locator('#context-summary').inner_text()
   page.locator('#observed-consent').check()
   assert page.locator('#send-observed').is_enabled()
   page.locator('#send-observed').click()
   page.locator('#chat-status').filter(has_text='Studio-Betreiber').wait_for()
   assert 'bleiben nutzbar' in page.locator('#chat-status').inner_text()
   page.locator('#preview').click()
   page.locator('#observed-consent-panel').wait_for(state='visible')
   page.locator('#observed-consent').check()
   step('definition')
   page.locator('#brief-decision').fill('Neue Entscheidung, deshalb neue Freigabe.')
   assert page.locator('#observed-consent-panel').is_hidden()
   page.locator('#research-brief button').click()
   page.locator('#brief-status').filter(has_text='Privat gespeichert').wait_for()
   # Typing while a save response is pending must not be overwritten by that response.
   page.evaluate('''() => {window.originalFetch=window.fetch;window.fetch=async (...args)=>{
     const response=await window.originalFetch(...args);
     if(args[0]==='/api/empirical/workflow' && args[1]?.method==='POST') {
       await new Promise(resolve=>{window.releaseSave=resolve;});
     } return response;
   };}''')
   page.locator('#brief-audience').fill('Sales und Operations')
   page.locator('#research-brief button').click()
   page.wait_for_function('() => typeof window.releaseSave === "function"')
   page.locator('#brief-decision').fill('Entwurf während des Speicherns erhalten.')
   page.evaluate('window.releaseSave()')
   page.wait_for_function('() => !document.querySelector("#save-drivers").disabled')
   assert page.locator('#brief-decision').input_value()=='Entwurf während des Speicherns erhalten.'
   assert 'Ungespeicherte' in page.locator('#workflow-save-state').inner_text()
   page.evaluate('window.fetch=window.originalFetch')
   page.locator('#research-brief button').click()
   page.locator('#brief-status').filter(has_text='Privat gespeichert').wait_for()
   step('analysis')
   page.locator('.metric-help summary').click()
   assert 'kleiner ist besser' in page.locator('.metric-help').inner_text()
   page.locator('#selected-model').select_option('macro_diesel_lag3')
   assert page.locator('#observed-coefficients tr').count()==0
   step('quality')
   assert 'Fehlgeschlagen' in page.locator('#workflow-quality').inner_text()
   step('presentation')
   page.locator('#create-handoff').click()
   page.locator('#handoff-panel').wait_for(state='visible')
   assert 'Term (Gesamtfenster)' not in page.locator('#handoff-text').input_value()
   proc.terminate();proc.wait(timeout=10);proc=start()
   page.reload();page.locator('#workflow-save-state').filter(has_text='Auftrag gespeichert').wait_for()
   assert page.locator('#task-presentation').is_visible()
   assert page.locator('#brief-decision').input_value()=='Entwurf während des Speicherns erhalten.'
   assert page.locator('input[value="delivery"]').is_checked()
   page.set_viewport_size({'width':390,'height':844})
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
   step('drivers')
   assert page.locator('#save-drivers').is_visible()
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
   # Without a snapshot, advanced steps must explain the next action, not show old results.
   manifest=results/'manifest.json'; backup=results/'manifest.hold';manifest.rename(backup)
   try:
    page.reload();step('analysis')
    page.locator('#workflow-empty').wait_for(state='visible')
    assert page.locator('#task-analysis').is_hidden()
    step('presentation');page.locator('#show-copilot').click()
    page.locator('#handoff-panel').wait_for(state='visible')
    assert 'Schritt 3' in page.locator('#handoff-text').input_value()
   finally:backup.rename(manifest)
   assert original=={p.name:p.read_bytes() for p in results.iterdir()}
   with urlopen(base+'/api/empirical') as r:state=json.load(r)
   assert state['ai_budget']['charged_nano_usd']==0
   assert not errors,errors
   assert not external,external
   browser.close()
  print('PASS: CSV upload/mapping/comparison/confirmed version/panel export; guided desktop/mobile flow; keyboard/focus/hash navigation; drafts preserved; local driver save; open QA points; missing-data guidance; durable brief; failed fits; evidence/Copilot handoff; consent invalidation; restart; unchanged snapshot bytes; zero external/provider requests. SOFTWARE FIXTURE ONLY.')
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=10)
  log.close()
