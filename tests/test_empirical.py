"""Software fixtures and numerical boundaries; fixtures are never empirical evidence."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from empirical.data import PERIODS, json_bytes
from empirical.model import matrices, analyze
from empirical import service
from empirical.restore import install_original
from demo import empirical_chat
from demo.openai_provider import Config, ConversationError, MODEL, MAX_REQUEST_NANO_USD
from demo.workspace import Workspace


def fixture():
    # Constructed software-only fixture, not acquired observations or a product fallback.
    t=np.arange(96); rng=np.random.default_rng(91)
    return {'classification':'OBSERVED_PRIVATE','periods':PERIODS,
            'series':{'tesla_count':np.round(np.exp(5+.01*t+.2*np.sin(2*np.pi*t/12)+rng.normal(0,.1,96))).astype(int).tolist(),
                      'cpi':(100+np.cumsum(rng.normal(.2,.1,96))).tolist(),
                      'consumer_credit':(5+rng.normal(0,.3,96)).tolist(),
                      'eurusd':(1.1+rng.normal(0,.03,96)).tolist(),
                      'diesel_de':(1.3+rng.normal(0,.04,96)).tolist()},
            'sources':{k:{'observed_months':96,'unit':'SOFTWARE_TEST_FIXTURE'} for k in ('tesla_count','cpi','consumer_credit','eurusd','diesel_de')},
            'events':[],'warnings':['SOFTWARE TEST FIXTURE, NOT REAL EMPIRICAL EVIDENCE']}


def bundle():
    data=fixture()
    return {'data':data,'results':analyze(data),'provenance':{'synthetic_inputs':False,
             'protocol_sha256':hashlib.sha256(service.PROTOCOL.read_bytes()).hexdigest()},'snapshot_sha256':'a'*64}


class EmpiricalNumericsTests(unittest.TestCase):
    def test_hypoforge_lag_diff_parity_and_causal_boundaries(self):
        from empirical.features import feature, verify_library, COMMIT
        x=np.array([1.,2.,np.nan,4.,9.,10.])
        np.testing.assert_allclose(feature(x,'lag',1),[np.nan,1,2,np.nan,4,9],equal_nan=True)
        np.testing.assert_allclose(feature(x,'diff',1),[np.nan,1,np.nan,np.nan,5,1],equal_nan=True)
        np.testing.assert_allclose(feature(x,'lag',3),[np.nan,np.nan,np.nan,1,2,np.nan],equal_nan=True)
        changed=x.copy();changed[-1]=999
        for lag in (1,2,3):
            np.testing.assert_allclose(feature(x,'lag',lag),feature(changed,'lag',lag),equal_nan=True)
        for lag in (-1,0,4):
            with self.assertRaises(ValueError):feature(x,'lag',lag)
        self.assertEqual(verify_library()['commit'],COMMIT)

    def test_stationarity_is_mandatory_and_training_diagnostics_exclude_holdout(self):
        result=analyze(fixture())
        self.assertEqual(len(result['models']),8)
        self.assertEqual(set(result['outcome_stationarity']),{'registrations_count','registrations_log1p','modeled_log1p_change'})
        for profile in result['outcome_stationarity'].values():
            self.assertTrue(all(p<'2025-01' for p in profile['training_only']['segment_periods']))
            self.assertEqual(profile['training_only']['adf']['lags'],3)
            self.assertEqual(profile['training_only']['kpss']['lags'],3)
        for model in result['models'].values():
            self.assertIn('stationarity',model)
            self.assertTrue(all(p<'2025-01' for p in model['stationarity']['training_residuals']['segment_periods']))
            self.assertIn('exploratory',model['stationarity']['training_residuals']['assessment'])

    def test_residual_stationarity_never_compresses_calendar_gaps(self):
        d=fixture()
        for i in range(10,81,10):d['series']['diesel_de'][i]=None
        result=analyze(d)['models']['macro_diesel']
        self.assertEqual(result['status'],'estimated')
        check=result['stationarity']['training_residuals']
        self.assertEqual(check['status'],'not_estimable')
        self.assertLess(check['n'],27)
        self.assertEqual(result['model_assessment'],'stationarity_review_required')

    def test_calendar_lags_gaps_and_rate_units(self):
        d=fixture(); d['series']['diesel_de'][10]=None
        y, designs=matrices(d)
        self.assertTrue(np.isnan(y[0])); self.assertEqual(np.isfinite(y).sum(),95)
        x,names=designs['macro']
        self.assertTrue(np.isnan(x[:2]).any(axis=1).all())
        self.assertAlmostEqual(x[8,names.index('consumer_credit_change_lag1')],d['series']['consumer_credit'][7]-d['series']['consumer_credit'][6])
        self.assertAlmostEqual(x[8,names.index('cpi_change_lag1')],np.log(d['series']['cpi'][7])-np.log(d['series']['cpi'][6]))
        dx,_=designs['macro_diesel']
        self.assertTrue(np.isnan(dx[11,-1]));self.assertTrue(np.isnan(dx[12,-1]));self.assertTrue(np.isfinite(dx[13,-1]))

    def test_holdout_target_does_not_enter_its_prediction_or_training(self):
        d=fixture(); first=analyze(d); altered=copy.deepcopy(d); altered['series']['tesla_count'][-1]*=3
        second=analyze(altered)
        for name in first['models']:
            a,b=first['models'][name],second['models'][name]
            self.assertEqual(a['status'],'estimated'); self.assertEqual(b['status'],'estimated')
            self.assertEqual(a['training'],b['training'])
            self.assertEqual(a['holdout']['predicted_counts'],b['holdout']['predicted_counts'])
            self.assertNotEqual(a['holdout']['count_metrics'],b['holdout']['count_metrics'])
        self.assertEqual(first['residual_research'],second['residual_research'])

    def test_paired_samples_and_inverse_prediction_arithmetic(self):
        d=fixture();d['series']['diesel_de'][15]=None;result=analyze(d)
        for name,v in result['models'].items():
            self.assertEqual(v['status'],'estimated')
            self.assertEqual(v['holdout']['count_metrics']['n'],v['paired_comparator']['holdout_count_metrics']['n'])
            self.assertEqual(v['full']['n'],v['paired_comparator']['full_metrics']['n'])
            for period,change,pred in zip(v['holdout']['periods'],v['holdout']['predicted_change'],v['holdout']['predicted_counts']):
                previous=d['series']['tesla_count'][PERIODS.index(period)-1]
                self.assertAlmostEqual(pred,np.expm1(np.log1p(previous)+change))
        self.assertIn(PERIODS[16],result['models']['macro_diesel']['excluded_periods'])
        self.assertEqual(result['models']['macro']['full']['n'],94)
        self.assertTrue(all(p['period']<'2025-01' for p in result['residual_research']))

    def test_rank_failure_remains_failure(self):
        d=fixture();d['series']['consumer_credit']=[5.0]*96
        result=analyze(d)
        self.assertEqual(result['models']['macro']['status'],'not_estimable')
        self.assertNotIn('holdout',result['models']['macro'])
        self.assertEqual(result['residual_research'],[])

    def test_original_upload_rejects_unknown_paths_or_unbound_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('../../outside','eurusd--native_csv.bin','unreviewed.csv'):
                with self.subTest(name=name),self.assertRaises(ValueError):install_original(tmp,name,b'not reviewed observations')
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_corruption_scope_protocol_and_symlink_checks(self):
        b=bundle()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def save():
                files={}
                for name in ('data','results','provenance'):
                    raw=json_bytes(b[name]);(root/(name+'.json')).write_bytes(raw);files[name+'.json']=hashlib.sha256(raw).hexdigest()
                (root/'manifest.json').write_bytes(json_bytes({'version':'observed-studio-v1','classification':'OBSERVED_PRIVATE','files':files}))
            save();self.assertEqual(service.read(root)['results'],b['results'])
            (root/'results.json').write_text('{}')
            with self.assertRaises(ValueError):service.read(root)
            b['data']['classification']='SYNTHETIC';save()
            with self.assertRaises(ValueError):service.read(root)
            b['data']['classification']='OBSERVED_PRIVATE';b['provenance']['protocol_sha256']='0'*64;save()
            with self.assertRaises(ValueError):service.read(root)
            with self.assertRaises(ValueError):service.build(tmp,root)


class EmpiricalConversationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.ws=Workspace(Path(self.tmp.name)/'state');self.addCleanup(self.ws.close)
        self.config=Config(True,'sk-test-NOT_A_REAL_API_KEY_123456')
        self.b=bundle();self.reader=patch('empirical.service.read',return_value=self.b);self.reader.start();self.addCleanup(self.reader.stop)

    def test_private_preview_is_separate_and_requires_bound_consent(self):
        from unittest.mock import Mock
        fake=Mock()
        p=empirical_chat.preview(self.ws,'Welche Variablen verbessern die Prognose?','macro',self.config)
        self.assertEqual(p['context']['classification'],'OBSERVED_PRIVATE')
        self.assertNotIn('series',p['context']);self.assertNotIn('history',p['context'])
        self.assertEqual(p['context']['snapshot_sha256'],'a'*64)
        for consent,digest in ((False,p['context_sha256']),(True,'0'*64)):
            with self.assertRaises(ConversationError):empirical_chat.respond(self.ws,p['context']['question'],'macro',consent,digest,self.config,client=fake)
        fake.request.assert_not_called()
        with self.assertRaises(ConversationError):empirical_chat.preview(self.ws,self.config.api_key,'macro',self.config)
        project=self.ws.empirical_project()
        self.assertEqual(project['dataset_id'],'observed-registrations')
        from demo import conversation
        from types import SimpleNamespace
        with self.assertRaises(ConversationError):conversation.preview(self.ws,project['id'],SimpleNamespace(conversation_id=project['conversation_id']),self.config,lambda *a:None)

    def test_single_call_budget_persistence_and_no_tools(self):
        from test_conversation import FakeClient,reply
        p=empirical_chat.preview(self.ws,'Erkläre das Ergebnis.','macro',self.config)
        client=FakeClient([reply('FAKE provider interpretation, not a real API request')])
        answer=empirical_chat.respond(self.ws,p['context']['question'],'macro',True,p['context_sha256'],self.config,client)
        self.assertEqual(answer['status'],'completed');self.assertEqual(len(client.payloads),1)
        self.assertNotIn('tools',client.payloads[0]);self.assertFalse(client.payloads[0]['store'])
        state=self.ws.context('tesla-observed')
        self.assertEqual(state['messages'][-1]['kind'],'llm_response')
        self.assertEqual(len(self.ws.context('synthetic-quarter')['messages']),0)
        self.assertGreater(answer['cost_estimate_nano_usd'],0)

    def test_provider_failure_retains_reservation_and_changed_snapshot_stops(self):
        from test_conversation import FakeClient
        p=empirical_chat.preview(self.ws,'Erkläre das Ergebnis.','macro',self.config)
        client=FakeClient([RuntimeError(self.config.api_key)])
        with self.assertRaises(ConversationError) as caught:empirical_chat.respond(self.ws,p['context']['question'],'macro',True,p['context_sha256'],self.config,client)
        self.assertNotIn(self.config.api_key,str(caught.exception))
        self.assertEqual(self.ws.ai_state('tesla-observed')['budget']['unknown_nano_usd'],MAX_REQUEST_NANO_USD)
        self.b['snapshot_sha256']='b'*64
        with self.assertRaises(ConversationError) as caught:empirical_chat.respond(self.ws,p['context']['question'],'macro',True,p['context_sha256'],self.config,client)
        self.assertEqual(caught.exception.code,'context_changed')


if __name__=='__main__':unittest.main()


class EmpiricalHTTPTests(unittest.TestCase):
    """Real HTTP with an explicitly constructed software fixture, no source downloads."""
    @classmethod
    def setUpClass(cls):
        import os,socket,subprocess,sys,time
        cls.temp=tempfile.TemporaryDirectory(prefix='aas-empirical-http-fixture-')
        cls.root=Path(cls.temp.name);cls.folder=cls.root/'fixture'
        cls.folder.mkdir();b=bundle();files={}
        for name in ('data','results','provenance'):
            raw=json_bytes(b[name]);(cls.folder/(name+'.json')).write_bytes(raw);files[name+'.json']=hashlib.sha256(raw).hexdigest()
        (cls.folder/'manifest.json').write_bytes(json_bytes({'version':'observed-studio-v1','classification':'OBSERVED_PRIVATE','files':files}))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1]
        cls.base=f'http://127.0.0.1:{cls.port}';cls.log=tempfile.TemporaryFile()
        env=dict(os.environ,AAS_EMPIRICAL_DIR=str(cls.folder),AAS_EMPIRICAL_SOURCE_DIR=str(cls.root/'sources'),
                 AAS_WORKSPACE_DIR=str(cls.root/'state'),AAS_OPENAI_ENABLED='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        env.pop('AAS_PUBLIC_ORIGIN',None)
        cls.process=subprocess.Popen([sys.executable,'-m','uvicorn','demo.app:app','--host','127.0.0.1','--port',str(cls.port),'--no-access-log'],
                                     cwd=service.ROOT,env=env,stdout=cls.log,stderr=cls.log)
        cls.addClassCleanup(cls.cleanup)
        for _ in range(150):
            try:cls.request('/api/health');break
            except OSError:time.sleep(.05)
        else:raise RuntimeError('Empirical fixture HTTP server did not start')

    @classmethod
    def cleanup(cls):
        cls.process.terminate();cls.process.wait(timeout=10);cls.log.close();cls.temp.cleanup()

    @classmethod
    def request(cls,path,body=None,headers=None,raw=False):
        from urllib.request import Request,urlopen
        data=None if body is None else json.dumps(body).encode()
        with urlopen(Request(cls.base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})}),timeout=30) as r:
            value=r.read();return value.decode() if raw else json.loads(value)

    def expect_status(self,status,path,body=None,headers=None):
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as caught:self.request(path,body,headers)
        self.assertEqual(caught.exception.code,status)
        self.assertNotIn(str(self.root),caught.exception.read().decode())

    def test_homepage_and_actual_api_are_observed_with_separate_archive(self):
        page=self.request('/',raw=True)
        self.assertIn('BEOBACHTETE DATEN',page);self.assertNotIn('id="run-form"',page)
        self.assertIn('SYNTHETIC / NOT EMPIRICAL',self.request('/archive/synthetic',raw=True))
        result=self.request('/api/empirical')
        self.assertEqual(result['status'],'ready');self.assertEqual(len(result['results']['models']),8)
        self.assertFalse(result['ai']['available'])

    def test_prepare_reopens_same_snapshot_and_strict_inputs_do_not_trigger_downloads(self):
        before=self.request('/api/empirical')
        after=self.request('/api/empirical/prepare',{})
        self.assertEqual(before['snapshot_sha256'],after['snapshot_sha256'])
        self.expect_status(422,'/api/empirical/prepare',{'source_dir':'/private'})
        self.expect_status(422,'/api/empirical/original-file',{'name':'../../outside','content_base64':'YmFk'})

    def test_empirical_project_cannot_execute_synthetic_tools_or_implicit_external_calls(self):
        self.request('/api/empirical')
        self.expect_status(422,'/api/projects/tesla-observed/runs',{})
        preview=self.request('/api/empirical/agent-context',{'message':'Erkläre die Unsicherheit.','model':'macro'})
        self.assertEqual(preview['context']['classification'],'OBSERVED_PRIVATE')
        self.assertNotIn('series',preview['context'])
        self.expect_status(503,'/api/empirical/messages',{'message':'Erkläre die Unsicherheit.','model':'macro'})

    def test_http_origin_and_invalid_configuration_are_rejected(self):
        self.expect_status(403,'/api/empirical/prepare',{}, {'Origin':'https://evil.test'})
        self.expect_status(422,'/api/empirical/agent-context',{'message':'test','model':'search_best'})

    def test_workflow_is_saved_and_presentation_is_read_only_and_private(self):
        from demo.research_workflow import DEFAULT_BRIEF
        value = copy.deepcopy(DEFAULT_BRIEF)
        value['required_drivers'].append('delivery')
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        self.request('/api/empirical/workflow', value)
        state = self.request('/api/empirical/workflow')
        self.assertEqual(state['brief'], value)
        self.assertIn('delivery', state['review']['models']['macro']['unmet_drivers'])
        text = self.request('/api/empirical/presentation?model=macro', raw=True)
        self.assertIn('Lieferfähigkeit', text)
        self.assertIn(state['review']['snapshot_sha256'], text)
        self.assertIn('Microsoft Copilot', text)
        self.assertIn('Schritt 3', self.request('/api/empirical/copilot-instructions', raw=True))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})
        self.assertEqual(self.request('/api/empirical')['ai_budget']['charged_nano_usd'], 0)

    def test_workflow_rejects_secrets_model_injection_unknown_drivers_and_cross_origin(self):
        from demo.research_workflow import DEFAULT_BRIEF
        value = copy.deepcopy(DEFAULT_BRIEF)
        self.expect_status(422, '/api/empirical/workflow', {**value, 'model': 'search'})
        self.expect_status(422, '/api/empirical/workflow', {**value, 'question': 'sk-NEVER_STORE_THIS_TEST_KEY_123456789'})
        self.expect_status(422, '/api/empirical/workflow', {**value, 'required_drivers': ['calendar', 'dynamics', '../private']})
        self.expect_status(422, '/api/empirical/workflow', {**value, 'required_drivers': ['calendar', 'cpi']})
        self.expect_status(403, '/api/empirical/workflow', value, {'Origin': 'https://evil.test'})
        self.expect_status(422, '/api/empirical/presentation?model=search_best')
