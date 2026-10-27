"""Deterministic provider fakes and real project tools; NOT live API verification."""
import copy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch, Mock
from uuid import uuid4

from demo import app as api, conversation as c
from demo.openai_provider import (Client, Config, ConversationError, MODEL, ENDPOINT,
                                 MAX_REQUEST_NANO_USD, MAX_OUTPUT_TOKENS, NoRedirect, usage_and_cost)
from demo.workspace import Workspace, MissingRecord


def reply(text='FAKE PROVIDER TEST: interpretation only.', tool=None, arguments=None):
    output = ([dict(type='function_call', name=tool, arguments=json.dumps(arguments or {}), call_id='call_test')]
              if tool is not None else [dict(type='message', role='assistant',
                                             content=[dict(type='output_text', text=text)])])
    return dict(id='resp_test', model=MODEL, service_tier='default', status='completed', output=output,
                usage=dict(input_tokens=100, output_tokens=30, total_tokens=130,
                           input_tokens_details=dict(cached_tokens=10),
                           output_tokens_details=dict(reasoning_tokens=0)))


class FakeClient:
    """Only tests inject this object; production has no fake-provider mode."""
    def __init__(self, replies):
        self.replies, self.payloads = iter(replies), []

    def request(self, payload):
        self.payloads.append(copy.deepcopy(payload))
        result = next(self.replies)
        if isinstance(result, Exception):
            raise result
        return copy.deepcopy(result)


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aas-ai-test-')
        self.addCleanup(self.temp.cleanup)
        self.ws = Workspace(Path(self.temp.name)/'workspace')
        self.addCleanup(lambda: self.ws.close())
        self.config = Config(True, 'sk-test-NOT-A-REAL-CREDENTIAL-123456')
        self.addCleanup(patch.stopall)
        patch('demo.app.get_workspace', side_effect=lambda: self.ws).start()
        patch('demo.app.get_ai_config', return_value=self.config).start()
        self.project = self.ws.projects()[0]
        self.other = self.ws.projects()[1]
        self.run_id = self.publish_fixture(self.project)

    def publish_fixture(self, project):
        # Original committed synthetic bundle, no new fit in orchestration tests.
        identity = uuid4().hex
        execution = self.ws.start_execution(project['id'], project['conversation_id'], 'run_demo_analysis', {})
        shutil.copytree(Path(__file__).resolve().parents[1]/'examples/task-01a', self.ws.bundle_path(identity))
        self.ws.complete_run(project['id'], execution['id'], identity, project['default_model'])
        return identity

    def request(self, message='Warum ist der Mediaeffekt so unsicher?', **kwargs):
        return api.MessageRequest(message=message, conversation_id=self.project['conversation_id'],
                                  run_id=self.run_id, mode='openai', **kwargs)

    def consented(self, request=None):
        request = request or self.request()
        preview = c.preview(self.ws, self.project['id'], request, self.config, api.load_run)
        return request.model_copy(update=dict(consent=True, context_sha256=preview['context_sha256']))

    def run_dialog(self, client, request=None, execute=None):
        return c.respond(self.ws, self.project['id'], request or self.consented(), self.config,
                         api.load_run, execute or api.execute_tool, client=client)

    def test_real_diagnostic_evidence_model_labels_and_persistent_followup(self):
        client = FakeClient([reply(tool='summarize_diagnostics', arguments={'run_id': self.run_id}), reply()])
        answer = self.run_dialog(client)
        actual = api.load_run(self.project['id'], self.run_id)
        self.assertEqual(answer['evidence'][0]['output']['coefficients'], actual['result']['coefficients'])
        self.assertEqual(answer['evidence'][0]['output']['diagnostics'], actual['result']['diagnostics'])
        self.assertEqual(answer['interpretation_status'], 'model_generated_not_verified_measurement')
        self.assertEqual(self.ws.context(self.project['id'])['messages'][-1]['kind'], 'llm_response')
        self.assertEqual(len(client.payloads), 2)
        self.assertEqual(client.payloads[0]['model'], MODEL)
        self.assertFalse(client.payloads[0]['store'])
        self.assertFalse(client.payloads[0]['parallel_tool_calls'])
        self.assertEqual(client.payloads[0]['service_tier'], 'default')
        self.assertTrue(all(tool['strict'] and not tool['parameters']['additionalProperties']
                            for tool in client.payloads[0]['tools']))
        self.assertEqual(client.payloads[0]['max_output_tokens'], MAX_OUTPUT_TOKENS)
        self.assertIn('function_call_output', json.dumps(client.payloads[1]))
        root = self.ws.root
        self.ws.close()
        self.ws = Workspace(root)
        request = self.request('Compare that with the other model.')
        selected = c.preview(self.ws, self.project['id'], request, self.config, api.load_run)
        self.assertEqual(len(selected['context']['history']), 1)
        self.assertEqual(selected['context']['history'][0]['assistant_interpretation'], answer['text'])
        second = FakeClient([reply(tool='compare_runs', arguments={'run_id': self.run_id}), reply('FAKE comparison interpretation')])
        compared = self.run_dialog(second, self.consented(request))
        self.assertEqual(compared['evidence'][0]['output']['comparison']['test_rmse_delta_right_minus_left'],
                         actual['comparison']['test_rmse_delta_right_minus_left'])
        self.assertEqual(self.ws.ai_state(self.other['id'])['turns'], [])

    def test_default_context_excludes_notes_proposals_and_unselected_approved_text(self):
        secret_note = 'PRIVATE empirical note: customer123 sales 987654'
        self.ws.add_message(self.project['id'], self.project['conversation_id'], 'user', 'user_statement', secret_note)
        approved = self.ws.propose(self.project['id'], 'PRIVATE unselected approved decision')
        self.ws.approve(self.project['id'], approved['id'])
        self.ws.propose(self.project['id'], 'PRIVATE unexecuted proposal')
        other = self.ws.propose(self.other['id'], 'PRIVATE other project')
        before = c.preview(self.ws, self.project['id'], self.request(), self.config, api.load_run)
        self.assertNotIn('PRIVATE', json.dumps(before))
        client = FakeClient([reply(tool='resume_workspace'), reply()])
        self.run_dialog(client)
        self.assertNotIn('PRIVATE', json.dumps(client.payloads))
        self.assertNotIn(str(self.ws.root), json.dumps(client.payloads))
        request = self.request(approved_decision_ids=[approved['id']])
        selected = c.preview(self.ws, self.project['id'], request, self.config, api.load_run)
        self.assertIn('PRIVATE unselected approved decision', json.dumps(selected))
        with self.assertRaises(MissingRecord):
            c.preview(self.ws, self.project['id'], self.request(approved_decision_ids=[other['id']]), self.config, api.load_run)

    def test_consent_hash_bounds_and_foreign_ids_before_network(self):
        client = FakeClient([reply()])
        with self.assertRaises(ConversationError):
            self.run_dialog(client, self.request())
        self.assertEqual(client.payloads, [])
        request = self.consented()
        changed = request.model_copy(update={'message': 'different question'})
        with self.assertRaisesRegex(ConversationError, 'Kontext hat sich geändert'):
            self.run_dialog(client, changed)
        foreign = self.publish_fixture(self.other)
        with self.assertRaises(MissingRecord):
            self.consented(self.request().model_copy(update={'run_id': foreign}))
        with self.assertRaises(ConversationError):
            self.consented(self.request('a'*2001))
        with self.assertRaises(ConversationError):
            self.consented(self.request(self.config.api_key))
        self.assertEqual(self.ws.ai_state(self.project['id'])['turns'], [])

    def test_unicode_history_is_byte_bounded_without_blocking_future_questions(self):
        for i in range(2):
            context={}; turn=self.ws.start_ai_turn(self.project['id'],self.project['conversation_id'],MODEL,context,c.digest(context),'历史'*500)
            call=self.ws.reserve_ai_call(self.project['id'],turn['id'],MAX_REQUEST_NANO_USD,'a'*64)
            self.ws.finish_ai_call(self.project['id'],call['id'],'completed',usage={'input_tokens':10,'output_tokens':10},estimated_cost_nano_usd=1000)
            self.ws.finish_ai_turn(self.project['id'],turn['id'],'completed',text='解释'*1500)
        selection=c.preview(self.ws,self.project['id'],self.request(),self.config,api.load_run)
        self.assertLessEqual(len(c.canonical(selection['context'])),7000)
        self.assertGreater(selection['context']['history_selection']['omitted_for_byte_limit'],0)
        self.assertEqual(selection['context']['question'],self.request().message)

    def test_strict_tool_rejection_never_executes(self):
        for name, args in [('shell', {}), ('approve_decision', {}), ('run_demo_analysis', {'path': '/private'}),
                           ('compare_runs', {'run_id': uuid4().hex}), ('summarize_diagnostics', {'run_id': []})]:
            with self.subTest(name=name,args=args):
                execute = Mock()
                client = FakeClient([reply(tool=name, arguments=args)])
                with self.assertRaises(ConversationError):
                    self.run_dialog(client, execute=execute)
                execute.assert_not_called()
        self.assertTrue(all(t['status']=='failed' for t in self.ws.ai_state(self.project['id'])['turns']))

    def test_timeout_unknown_cost_and_budget_survive_restart(self):
        client = FakeClient([TimeoutError('PRIVATE failure '+self.config.api_key)])
        with self.assertRaises(ConversationError) as caught:
            self.run_dialog(client)
        self.assertNotIn(self.config.api_key, str(caught.exception))
        state = self.ws.ai_state(self.project['id'])
        self.assertEqual(state['budget']['unknown_nano_usd'], MAX_REQUEST_NANO_USD)
        self.assertEqual(state['turns'][0]['status'], 'failed')
        self.assertEqual(self.ws.ai_history(self.project['id']), [])
        root=self.ws.root; self.ws.close(); self.ws=Workspace(root)
        self.assertEqual(self.ws.ai_state(self.project['id'])['budget'], state['budget'])

    def test_provider_incomplete_usage_missing_and_refusal_are_not_success(self):
        bad = reply(); bad['status']='incomplete'
        missing = reply(); missing.pop('usage')
        refused = reply(); refused['output'][0]['content']=[{'type':'refusal','refusal':'PRIVATE reason'}]
        for response in (bad, missing, refused):
            with self.subTest(response=response.get('status')), self.assertRaises(ConversationError):
                self.run_dialog(FakeClient([response]))
        state=self.ws.ai_state(self.project['id'])
        self.assertTrue(all(t['status']=='failed' for t in state['turns']))
        self.assertEqual(self.ws.ai_history(self.project['id']), [])
        self.assertGreater(state['budget']['unknown_nano_usd'], 0)

    def test_model_tier_mismatch_and_projection_failure_keep_truthful_evidence(self):
        for field,value in [('model','different-model'),('service_tier','priority')]:
            response=reply(); response[field]=value
            with self.assertRaises(ConversationError):self.run_dialog(FakeClient([response]))
        self.assertEqual(self.ws.ai_state(self.project['id'])['budget']['unknown_nano_usd'],2*MAX_REQUEST_NANO_USD)
        def execute(pid,cid,name,args):
            output,eid=api.execute_tool(pid,cid,name,args)
            output.clear()  # Simulate a failed safe projection after the actual recorded tool.
            return output,eid
        with self.assertRaises(ConversationError):
            self.run_dialog(FakeClient([reply(tool='resume_workspace')]),execute=execute)
        last=self.ws.ai_state(self.project['id'])['turns'][0]
        self.assertEqual(last['status'],'failed')
        self.assertEqual(len(last['tool_execution_ids']),1)
        self.assertEqual(self.ws.context(self.project['id'])['executions'][0]['status'],'succeeded')

    def test_custom_loop_tools_requests_and_persistent_budget_are_bounded(self):
        client=FakeClient([reply(tool='list_datasets')]*3)
        with self.assertRaises(ConversationError):self.run_dialog(client)
        self.assertEqual(len(client.payloads), 3)
        self.assertEqual(client.payloads[-1]['tool_choice'], 'none')
        self.assertEqual(len([e for e in self.ws.context(self.project['id'])['executions'] if e['tool']=='list_datasets']), 2)
        # Consume the remaining workspace guard without any provider request.
        remaining=self.ws.ai_state(self.project['id'])['budget']['remaining_nano_usd']
        while remaining:
            context={}; turn=self.ws.start_ai_turn(self.project['id'],self.project['conversation_id'],MODEL,context,c.digest(context),'reserve')
            amount=min(remaining,100_000_000)
            call=self.ws.reserve_ai_call(self.project['id'],turn['id'],amount,'a'*64)
            self.ws.finish_ai_call(self.project['id'],call['id'],'unknown')
            self.ws.finish_ai_turn(self.project['id'],turn['id'],'failed',error_code='test_unknown')
            remaining-=amount
        client=FakeClient([reply()])
        with self.assertRaises(ConversationError) as caught:self.run_dialog(client)
        self.assertEqual(caught.exception.code,'budget_limit')
        self.assertEqual(client.payloads,[])

    def test_multiple_fit_requests_publish_only_one_fixed_synthetic_run(self):
        def execute(pid,cid,name,args):
            self.assertEqual(name,'run_demo_analysis')
            identity=self.publish_fixture(self.project)
            record=self.ws.get_run(pid,identity)
            return api.load_run(pid,identity),record['execution_id']
        wrapped=Mock(side_effect=execute)
        with self.assertRaises(ConversationError) as caught:
            self.run_dialog(FakeClient([reply(tool='run_demo_analysis')]*2),execute=wrapped)
        self.assertEqual(caught.exception.code,'fit_limit')
        self.assertEqual(wrapped.call_count,1)
        self.assertEqual(self.ws.context(self.project['id'])['counts']['runs'],2)
        self.assertEqual(len(self.ws.ai_state(self.project['id'])['turns'][0]['tool_execution_ids']),1)

    def test_tool_failure_and_projection_do_not_claim_successful_computation(self):
        failed=Mock(side_effect=RuntimeError('/private/source-'+self.config.api_key))
        answer=self.run_dialog(FakeClient([reply(tool='summarize_diagnostics',arguments={'run_id':self.run_id}),reply('FAKE: the tool failed')]),execute=failed)
        self.assertFalse(answer['executed'])
        self.assertEqual(answer['evidence'][0]['status'],'failed')
        self.assertNotIn('/private',json.dumps(answer))
        self.assertNotIn(self.config.api_key,json.dumps(answer))
        projected=c.projection('resume_workspace',dict(latest_run_id=self.run_id,verified=True,
            context={'counts':{'runs':1},'messages':[{'text':'PRIVATE'}]},summary='PRIVATE'))
        self.assertNotIn('PRIVATE',json.dumps(projected))
        response=reply('FAKE: '+self.config.api_key)
        response['id']='resp_'+self.config.api_key
        redacted=self.run_dialog(FakeClient([response]))
        self.assertNotIn(self.config.api_key,json.dumps(redacted))
        self.assertNotIn(self.config.api_key,json.dumps(self.ws.ai_state(self.project['id'])))
        self.assertNotIn(self.config.api_key,json.dumps(self.ws.context(self.project['id'])['messages']))


class ProviderTransportTests(unittest.TestCase):
    def test_fixed_endpoint_headers_store_false_and_secret_safety(self):
        config=Config(True,'sk-test-NOT-A-REAL-CREDENTIAL-123456')
        response=Mock(); response.__enter__=Mock(return_value=response); response.__exit__=Mock(return_value=False)
        response.read.return_value=json.dumps(reply()).encode()
        opener=Mock(); opener.open.return_value=response
        with patch('demo.openai_provider.build_opener',return_value=opener):
            result=Client(config).request({'model':MODEL,'store':False})
        sent=opener.open.call_args.args[0]
        self.assertEqual(sent.full_url,ENDPOINT)
        self.assertEqual(sent.get_header('Authorization'),'Bearer '+config.api_key)
        self.assertFalse(json.loads(sent.data)['store'])
        self.assertNotIn(config.api_key,repr(config))
        usage,cost=usage_and_cost(result)
        self.assertEqual(cost,90*750+10*75+30*4500)
        self.assertEqual(usage['total_tokens'],130)
        with self.assertRaises(ConversationError):NoRedirect().redirect_request(sent,None,302,'redirect',{},'https://evil.invalid')
        with patch('demo.openai_provider.build_opener',side_effect=RuntimeError('must not dispatch')):
            with self.assertRaises(ConversationError):Client(Config()).request({})

    def test_bad_usage_and_http_errors_are_sanitized(self):
        for usage in (None,dict(input_tokens=True,output_tokens=1,total_tokens=2),
                      dict(input_tokens=1,output_tokens=1,total_tokens=3),
                      dict(input_tokens=999999,output_tokens=1,total_tokens=1000000)):
            response=reply(); response['usage']=usage
            with self.subTest(usage=usage),self.assertRaises(ConversationError) as caught:
                usage_and_cost(response)
            self.assertIn(caught.exception.code,('missing_usage','invalid_usage','usage_guard'))
        from urllib.error import HTTPError
        secret='sk-test-NOT-A-REAL-CREDENTIAL-123456'
        opener=Mock(); opener.open.side_effect=HTTPError(ENDPOINT,401,'PRIVATE '+secret,{},io.BytesIO(secret.encode()))
        with patch('demo.openai_provider.build_opener',return_value=opener),self.assertRaises(ConversationError) as caught:
            Client(Config(True,secret)).request({})
        self.assertNotIn(secret,str(caught.exception))
        self.assertNotIn('PRIVATE',str(caught.exception))


class ConversationHTTPTests(unittest.TestCase):
    def test_actual_http_conversation_uses_real_tool_and_mocked_provider(self):
        # A real HTTP application and a fresh real synthetic fit; only OpenAI is fake.
        import os, socket, threading, time
        from urllib.request import Request, urlopen
        import uvicorn
        with tempfile.TemporaryDirectory(prefix='aas-ai-http-') as td:
            client=FakeClient([])
            config=Config(True,'sk-test-NOT-A-REAL-CREDENTIAL-123456')
            with patch.dict(os.environ,{'AAS_WORKSPACE_DIR':td}), \
                 patch('demo.app.Config.from_env',return_value=config), \
                 patch('demo.conversation.Client',return_value=client):
                sock=socket.socket();sock.bind(('127.0.0.1',0))
                base=f'http://127.0.0.1:{sock.getsockname()[1]}'
                server=uvicorn.Server(uvicorn.Config(api.app,log_level='critical',access_log=False))
                thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True)
                thread.start()
                def request(path,body=None):
                    raw=None if body is None else json.dumps(body).encode()
                    with urlopen(Request(base+path,data=raw,headers={'Content-Type':'application/json'}),timeout=90) as response:
                        return json.loads(response.read())
                try:
                    for _ in range(200):
                        if server.started:break
                        time.sleep(.02)
                    self.assertTrue(server.started)
                    self.assertTrue(request('/api/ai/status')['available'])
                    from urllib.error import HTTPError
                    with self.assertRaises(HTTPError) as caught:
                        request('/api/projects/synthetic-quarter/messages',{'api_key':config.api_key})
                    self.assertEqual(caught.exception.code,422)
                    self.assertNotIn(config.api_key,caught.exception.read().decode())
                    project=request('/api/projects')[0]
                    prefix='/api/projects/'+project['id']
                    fitted=request(prefix+'/runs',{})
                    body={'message':'Warum ist der Mediaeffekt so unsicher?',
                          'conversation_id':project['conversation_id'],'run_id':fitted['id']}
                    selected=request(prefix+'/agent-context',body)
                    client.replies=iter([reply(tool='summarize_diagnostics',arguments={'run_id':fitted['id']}),reply()])
                    result=request(prefix+'/messages',{**body,'mode':'openai','consent':True,
                                                       'context_sha256':selected['context_sha256']})
                    self.assertTrue(result['text'].startswith('FAKE PROVIDER TEST'))
                    self.assertEqual(result['evidence'][0]['output']['coefficients'],fitted['result']['coefficients'])
                    state=request(prefix+'/workspace')
                    self.assertEqual(state['messages'][-1]['kind'],'llm_response')
                    self.assertEqual(state['ai']['turns'][0]['status'],'completed')
                    self.assertEqual(len(client.payloads),2)
                finally:
                    server.should_exit=True;thread.join(timeout=15);sock.close()
                    self.assertFalse(thread.is_alive())


if __name__ == '__main__':
    unittest.main()
