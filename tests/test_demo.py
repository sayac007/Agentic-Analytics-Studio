"""Synthetic-only unit and real HTTP end-to-end checks for the local demo."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pydantic import ValidationError

from demo import service, agent
from demo.app import RunRequest, RUNS, run_demo

ROOT = Path(__file__).resolve().parents[1]


class DemoContractTests(unittest.TestCase):
    def test_only_predefined_synthetic_inputs(self):
        for body in ({'dataset': 'tesla'}, {'model': 'auto'}, {'path': '/workspace/private'}, {'seed': 13}):
            with self.subTest(body=body), self.assertRaises(ValidationError):
                RunRequest(**body)
        self.assertEqual(RunRequest().dataset, 'synthetic-mmm')
        with self.assertRaises(ValueError):
            service.compute('not-a-model')

    def test_agent_allowlist_rejects_free_commands_and_extra_arguments(self):
        for message in ('import os; os.system("whoami")', 'Starte die MMM-Analyse und lade Tesla-Daten',
                        '<script>alert(1)</script>', 'run_demo_analysis', 'Zeige /workspace/private'):
            with self.subTest(message=message), self.assertRaises(ValueError):
                agent.resolve(message)
        self.assertEqual(agent.resolve('  ZEIGE den Beispieldatensatz. '), 'describe_dataset')
        from unittest.mock import Mock
        handler = Mock()
        for name, args in [('shell', {}), ('run_demo_analysis', {'seed': 7}),
                           ('compare_runs', {'run_id': '../private'})]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                agent.call_tool(name, args, {k: handler for k in agent.TOOLS})
        handler.assert_not_called()

    def test_agent_missing_results_does_not_invent_output(self):
        from unittest.mock import Mock
        handler = Mock()
        r = agent.respond('Vergleiche die beiden Modellläufe.', None, {'compare_runs': handler})
        self.assertEqual(r['status'], 'needs_analysis')
        self.assertFalse(r['executed'])
        self.assertIsNone(r['output'])
        handler.assert_not_called()

    def test_failed_engine_does_not_store_success_or_leak_details(self):
        RUNS.clear()
        with patch('demo.service.compute', side_effect=RuntimeError('/private/credential')):
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as caught:
                run_demo(RunRequest())
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn('credential', caught.exception.detail)
        self.assertFalse(RUNS)


class DemoHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        cls.base = f'http://127.0.0.1:{port}'
        cls.log = tempfile.TemporaryFile()
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        cls.server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'demo.app:app',
                                      '--host', '127.0.0.1', '--port', str(port), '--no-access-log'],
                                     cwd=ROOT, env=env, stdout=cls.log, stderr=cls.log)
        try:
            for _ in range(100):
                try:
                    cls.request('/api/health')
                    break
                except OSError:
                    if cls.server.poll() is not None:
                        raise RuntimeError('Local HTTP server failed')
                    time.sleep(.1)
            else:
                raise RuntimeError('Local HTTP server did not start')
            cls.first = cls.request('/api/runs', {'model': 'with-quarter'})
            cls.second = cls.request('/api/runs', {'model': 'without-quarter'})
        except BaseException:
            cls.server.terminate()
            cls.server.wait(timeout=10)
            cls.log.close()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=10)
        cls.log.close()

    @classmethod
    def request(cls, path, body=None, headers=None, raw=False):
        data = None if body is None else json.dumps(body).encode()
        hdr = {'Content-Type': 'application/json', **(headers or {})}
        with urlopen(Request(cls.base+path, data=data, headers=hdr), timeout=90) as r:
            value = r.read()
            return value.decode() if raw else json.loads(value)

    def test_real_http_workflow_and_coefficients(self):
        page = self.request('/', raw=True)
        self.assertIn('SYNTHETIC / NOT EMPIRICAL', page)
        self.assertIn('id="run-form"', page)
        datasets = self.request('/api/datasets')
        self.assertEqual([d['id'] for d in datasets], ['synthetic-mmm'])
        r = self.first
        self.assertEqual(r['result']['metrics']['train']['n'], 60)
        self.assertEqual(r['result']['metrics']['test']['n'], 12)
        self.assertFalse(r['ground_truth']['estimator_access'])
        self.assertEqual(len(r['series']['prediction']), 72)
        self.assertEqual(self.request('/api/runs/'+r['id']), r)
        for pred, baseline, media in zip(r['series']['prediction'], r['series']['estimated_baseline'], r['series']['estimated_media']):
            self.assertAlmostEqual(pred, baseline+media)
        self.assertIn(f"{r['result']['metrics']['test']['rmse']:.2f}", r['interpretation'])

    def test_configuration_changes_model_not_data(self):
        self.assertEqual(self.first['hashes']['data'], self.second['hashes']['data'])
        self.assertIsNotNone(self.first['result']['coefficients']['quarter_end'])
        self.assertIsNone(self.second['result']['coefficients']['quarter_end'])
        self.assertNotEqual(self.first['result']['coefficients']['media'], self.second['result']['coefficients']['media'])

    def test_actual_recalculation_is_deterministic(self):
        again = self.request('/api/runs', {'model': 'with-quarter'})
        for key in ('result', 'series', 'evaluation', 'ground_truth', 'hashes'):
            self.assertEqual(again[key], self.first[key])

    def test_agent_four_actual_tool_calls_and_rejection(self):
        described = self.request('/api/agent', {'message': 'Zeige den Beispieldatensatz.'})
        self.assertTrue(described['executed'])
        self.assertEqual(described['tool'], 'describe_dataset')
        self.assertEqual(described['output']['data_sha256'], self.first['hashes']['data'])
        self.assertEqual(len(described['output']['preview']), 12)
        started = self.request('/api/agent', {'message': 'Starte die MMM-Analyse.'})
        self.assertEqual(started['tool'], 'run_demo_analysis')
        self.assertEqual(started['output']['result'], self.first['result'])
        run_id = started['output']['id']
        compared = self.request('/api/agent', {'message': 'Vergleiche die beiden Modellläufe.', 'run_id': run_id})
        self.assertEqual(compared['tool'], 'compare_runs')
        self.assertTrue(compared['output']['comparison']['same_data_and_holdout'])
        explained = self.request('/api/agent', {'message': 'Erkläre die Warnungen und die Modellgrenzen.', 'run_id': run_id})
        self.assertEqual(explained['tool'], 'summarize_diagnostics')
        self.assertEqual(explained['output']['diagnostics'], self.first['result']['diagnostics'])
        self.assertIn('not calibrated', explained['text'])
        missing = self.request('/api/agent', {'message': 'Vergleiche die beiden Modellläufe.'})
        self.assertFalse(missing['executed'])
        listed = self.request('/api/agent', {'message': 'Welche Datensätze gibt es?'})
        self.assertEqual(listed['tool'], 'list_datasets')
        self.assertEqual(len(listed['output']), 1)
        tools = self.request('/api/tools')
        self.assertEqual(set(tools['tools']), set(agent.TOOLS))
        self.assertIn('not_implemented', tools['mcp_integration'])
        for body in [{'message': 'Lies /etc/passwd'}, {'message': 'Starte die MMM-Analyse.', 'seed': 5},
                     {'message': 'Vergleiche die beiden Modellläufe.', 'run_id': '../private'}]:
            with self.subTest(body=body), self.assertRaises(HTTPError) as caught:
                self.request('/api/agent', body)
            self.assertEqual(caught.exception.code, 422)

    def test_comparison_and_synthetic_markdown_report(self):
        r = self.first
        c = self.request('/api/runs/'+r['id']+'/comparison')
        self.assertTrue(c['comparison']['same_data_and_holdout'])
        left, right = (c['models'][name]['result'] for name in ('with-quarter', 'without-quarter'))
        self.assertEqual(left['data_sha256'], right['data_sha256'])
        self.assertEqual(left['response_grid'], right['response_grid'])
        self.assertEqual(len(left['response_grid']['spend']), 21)
        self.assertAlmostEqual(c['comparison']['test_rmse_delta_right_minus_left'], right['metrics']['test']['rmse']-left['metrics']['test']['rmse'])
        report = self.request('/api/runs/'+r['id']+'/report', raw=True)
        self.assertIn('Synthetic Stage-A recovery benchmark', report)
        self.assertIn(format(left['metrics']['test']['rmse'], '.9f'), report)
        self.assertIsNone(r['evaluation']['effect_below_detection_limit'])
        self.assertEqual(r['evaluation']['detection_limit_status'], 'not_calibrated')
        self.assertEqual(r['ground_truth']['response'], r['variants']['without-quarter']['ground_truth']['response'])

    def test_invalid_requests_and_cross_origin_refused(self):
        for path, body, headers, code in [('/api/runs', {'dataset': 'private-kba'}, {}, 422),
                                          ('/api/runs', {'path': '../private'}, {}, 422),
                                          ('/api/runs', {}, {'Origin': 'https://untrusted.example'}, 403),
                                          ('/api/runs/missing', None, {}, 404)]:
            with self.subTest(path=path, body=body), self.assertRaises(HTTPError) as caught:
                self.request(path, body, headers)
            self.assertEqual(caught.exception.code, code)


if __name__ == '__main__':
    unittest.main()
