"""Check the actual Caddy auth/origin boundary against a temporary real Studio.

Install the pinned application runtime first. Supply an existing Caddy 2.11.7
executable with ``--caddy /path/to/caddy`` or ``AAS_CADDY_BINARY``. This script
downloads nothing, creates no Azure resources and disables OpenAI. It uses a
temporary internal TLS CA with hostname verification; public ACME is not tested.
Only the proxy listener, backend and TLS issuer are replaced for the local test;
the repository's auth and upstream-header rules are retained.
"""
import argparse
import base64
import http.client
import json
import os
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOST='studio.example.test'
ORIGIN='https://'+HOST
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--caddy', default=os.environ.get('AAS_CADDY_BINARY', 'caddy'),
                    help='Existing Caddy2.11.7 executable; no automatic download')
BINARY=parser.parse_args().caddy
version=subprocess.check_output([BINARY, 'version'], text=True).split()[0]
if version != 'v2.11.7':
    parser.error('Caddy2.11.7 is required to match the pinned deployment')
PYTHON=sys.executable

def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        return sock.getsockname()[1]

with tempfile.TemporaryDirectory(prefix='aas-proxy-smoke-') as directory:
    temp=Path(directory)
    app_port,tls_port=free_port(),free_port()
    env=dict(os.environ,AAS_PUBLIC_ORIGIN=ORIGIN,AAS_WORKSPACE_DIR=str(temp/'workspace'),AAS_OPENAI_ENABLED='0',
             XDG_DATA_HOME=str(temp/'caddy-data'),XDG_CONFIG_HOME=str(temp/'caddy-config'))
    env.pop('OPENAI_API_KEY',None)
    password=base64.urlsafe_b64encode(os.urandom(24)).decode()
    password_hash=subprocess.check_output([BINARY,'hash-password'],input=(password+'\n').encode(),env=env).decode().strip()
    env.update(STUDIO_HOST=HOST,STUDIO_PASSWORD_HASH=password_hash)
    original=(ROOT/'deploy/azure/Caddyfile').read_text()
    config=('{\n admin off\n skip_install_trust\n auto_https disable_redirects\n}\n'+original
            .replace('{$STUDIO_HOST} {','https://{$STUDIO_HOST}:'+str(tls_port)+' {\n tls internal')
            .replace('app:8000','127.0.0.1:'+str(app_port)))
    (temp/'Caddyfile').write_text(config)
    # Test wrapper forwards all lifespan/HTTP behavior to the real unchanged app,
    # refusing upstream credentials before they can reach it. No header values stored.
    (temp/'review_entry.py').write_text('''from demo.app import app as inner
async def app(scope, receive, send):
    if scope['type']=='http':
        assert not any(name.lower() in (b'authorization',b'proxy-authorization') for name,value in scope['headers']), 'Proxy leaked authentication header'
    await inner(scope, receive, send)
''')
    processes=[]
    log=(temp/'services.log').open('wb')
    try:
        processes.append(subprocess.Popen([PYTHON,'-c',"import sys; sys.path.insert(0,sys.argv[1]); import uvicorn; uvicorn.run('review_entry:app',host='127.0.0.1',port=int(sys.argv[2]),proxy_headers=False,access_log=False)",str(temp),str(app_port)],cwd=ROOT,env=env,stdout=log,stderr=log))
        for _ in range(100):
            try:
                c=http.client.HTTPConnection('127.0.0.1',app_port,timeout=1)
                c.request('GET','/api/health',headers={'Host':HOST}); r=c.getresponse(); r.read(); c.close()
                if r.status==200: break
            except OSError: time.sleep(.05)
        else: raise RuntimeError('Application did not start')
        subprocess.run([BINARY,'validate','--config',str(temp/'Caddyfile'),'--adapter','caddyfile'],env=env,stdout=log,stderr=log,check=True)
        processes.append(subprocess.Popen([BINARY,'run','--config',str(temp/'Caddyfile'),'--adapter','caddyfile'],env=env,stdout=log,stderr=log))
        authority=temp/'caddy-data/caddy/pki/authorities/local/root.crt'
        for _ in range(100):
            if authority.exists():
                try:
                    with socket.create_connection(('127.0.0.1',tls_port),timeout=.2): break
                except OSError: pass
            time.sleep(.05)
        else: raise RuntimeError('Local TLS proxy did not start')
        context=ssl.create_default_context(cafile=str(authority))
        class LocalTLS(http.client.HTTPSConnection):
            def connect(self):
                raw=socket.create_connection(('127.0.0.1',tls_port),timeout=10)
                self.sock=context.wrap_socket(raw,server_hostname=HOST)
        credential='Basic '+base64.b64encode(('studio:'+password).encode()).decode()
        def request(method,path,authenticated=False,headers=None,body=None):
            c=LocalTLS(HOST,tls_port,context=context,timeout=10)
            h={'Host':HOST,**(headers or {})}
            if authenticated: h['Authorization']=credential
            payload=None if body is None else json.dumps(body)
            if payload is not None: h.setdefault('Content-Type','application/json')
            c.request(method,path,payload,h); response=c.getresponse(); raw=response.read(); status=response.status; c.close()
            return status,raw
        paths=['/','/static/app.js','/api/health','/api/projects','/api/ai/status','/docs','/openapi.json','/not-a-route','/api/projects/synthetic-quarter/workspace']
        for path in paths:
            status,_=request('GET',path)
            assert status==401,(path,status)
        mutation='/api/projects/synthetic-quarter/decisions'
        assert request('POST',mutation,body={'text':'Unauthenticated rejection'},headers={'Origin':ORIGIN})[0]==401
        assert request('GET','/api/health',headers={'Authorization':'Basic '+base64.b64encode(b'studio:wrong-password').decode()})[0]==401
        status,raw=request('GET','/api/health',True,headers={'Proxy-Authorization':'test-only-proxy-header'})
        assert status==200, ('Authenticated request failed', status)
        assert json.loads(raw)['status']=='ready'
        assert request('POST',mutation,True,body={'text':'Missing origin rejected'})[0]==403
        assert request('POST',mutation,True,body={'text':'Foreign origin rejected'},headers={'Origin':'https://evil.test','X-Forwarded-Proto':'https','X-Forwarded-Host':HOST})[0]==403
        status,raw=request('POST',mutation,True,body={'text':'Local TLS review synthetic-only proposal'},headers={'Origin':ORIGIN})
        assert status==200, ('Authenticated request failed', status)
        assert json.loads(raw)['status']=='proposed'
        print('PASS: Caddy2.11.7 local verified TLS; nine protected GET paths + POST; wrong-password rejection; authenticated app; stripped upstream credentials; exact-origin mutation. Azure/public ACME/live OpenAI: NOT VERIFIED.')
    finally:
        for process in reversed(processes):
            process.terminate()
        for process in reversed(processes):
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
        log.close()
