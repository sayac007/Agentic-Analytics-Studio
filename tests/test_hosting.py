"""Explicit deployment configuration and real HTTP behind a TLS-terminating proxy."""
import http.client
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

from demo.hosting import HostingConfig, HostingError


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = 'https://studio.example.test'
HOST = 'studio.example.test'


class HostingConfigurationTests(unittest.TestCase):
    def test_loopback_default_and_explicit_container_bind(self):
        local = HostingConfig.from_env({})
        self.assertEqual(local.bind_host, '127.0.0.1')
        self.assertIsNone(local.public_origin)
        self.assertEqual(local.health_host, '127.0.0.1')
        self.assertIn('localhost', local.trusted_hosts)
        self.assertIsNone(local.request_error('POST', 'http', '127.0.0.1:8000', None, None, 'application/json'))
        public = HostingConfig.from_env({'AAS_PUBLIC_ORIGIN': PUBLIC + ':443', 'AAS_BIND_HOST': '0.0.0.0'})
        self.assertEqual(public.public_origin, PUBLIC)
        self.assertEqual(public.trusted_hosts, [HOST])
        self.assertEqual(public.health_host, HOST)
        self.assertEqual(public.bind_host, '0.0.0.0')

    def test_ambiguous_origins_and_unprotected_bind_fail_closed(self):
        invalid = ('', 'http://studio.example.test', 'HTTPS://studio.example.test',
                   PUBLIC + '/', PUBLIC + '/app', PUBLIC + '?', PUBLIC + '?x=y', PUBLIC + '#',
                   PUBLIC + '#fragment', PUBLIC + ':8443', PUBLIC + ':',
                   'https://user:password@studio.example.test', 'https://*.example.test',
                   'https://studio.example.test.evil/', 'https://bad_host.test',
                   'https://studio.example.test.', 'https://-studio.example.test',
                   'https://studio..example.test', 'https://例え.test',
                   'https://studio%2eexample.test', 'https://studio.example.test\\evil',
                   'https://studio.example.test\n')
        for value in invalid:
            with self.subTest(origin=value), self.assertRaises(HostingError):
                HostingConfig.from_env({'AAS_PUBLIC_ORIGIN': value})
        for value in ('0.0.0.0', '::', 'localhost', '192.168.0.1'):
            with self.subTest(bind=value), self.assertRaises(HostingError):
                HostingConfig.from_env({'AAS_BIND_HOST': value})

    def test_launcher_uses_one_worker_and_ignores_forwarded_headers(self):
        from demo.__main__ import main
        config = HostingConfig.from_env({'AAS_PUBLIC_ORIGIN': PUBLIC, 'AAS_BIND_HOST': '0.0.0.0'})
        with patch('demo.__main__.HostingConfig.from_env', return_value=config), patch('uvicorn.run') as launch:
            main()
        launch.assert_called_once_with('demo.app:app', host='0.0.0.0', port=8000,
                                       workers=1, access_log=False, proxy_headers=False)


class HostedHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aas-hosting-http-')
        cls.log = tempfile.TemporaryFile()
        cls.process = None
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.base = f'http://127.0.0.1:{cls.port}'
        env = dict(os.environ, AAS_PUBLIC_ORIGIN=PUBLIC, AAS_BIND_HOST='127.0.0.1',
                   AAS_WORKSPACE_DIR=str(Path(cls.temp.name) / 'state'), AAS_OPENAI_ENABLED='0',
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        try:
            cls.process = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', 'demo.app:app', '--host', '127.0.0.1',
                 '--port', str(cls.port), '--no-proxy-headers', '--no-access-log'],
                cwd=ROOT, env=env, stdout=cls.log, stderr=cls.log)
            for _ in range(150):
                try:
                    cls.request('/api/health')
                    break
                except OSError:
                    if cls.process.poll() is not None:
                        raise RuntimeError('Hosted-policy test server failed')
                    time.sleep(.05)
            else:
                raise RuntimeError('Hosted-policy test server did not become ready')
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls.process is not None and cls.process.poll() is None:
            cls.process.terminate()
            cls.process.wait(timeout=10)
        cls.log.close()
        cls.temp.cleanup()

    @classmethod
    def request(cls, path, body=None, headers=None):
        encoded = None if body is None else json.dumps(body).encode()
        request = Request(cls.base + path, data=encoded,
                          headers={'Host': HOST, 'Content-Type': 'application/json', **(headers or {})})
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read()), response.headers

    def assert_http(self, status, path, body=None, headers=None):
        with self.assertRaises(HTTPError) as caught:
            self.request(path, body, headers)
        self.assertEqual(caught.exception.code, status)
        self.assertNotIn(self.temp.name, caught.exception.read().decode())

    def test_configured_https_origin_works_over_internal_http(self):
        value, headers = self.request('/api/health')
        self.assertEqual(value['status'], 'ready')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        proposed, _ = self.request('/api/projects/synthetic-quarter/decisions',
                                   {'text': 'Hosted synthetic-only test proposal'}, {'Origin': PUBLIC})
        self.assertEqual(proposed['status'], 'proposed')
        value, _ = self.request('/api/health', headers={'Host': HOST + ':443'})
        self.assertEqual(value['status'], 'ready')

    def test_host_and_origin_are_exact_not_proxy_header_claims(self):
        for host in ('evil.example', HOST + '.evil', HOST + ':8000', '127.0.0.1'):
            with self.subTest(host=host):
                self.assert_http(400, '/api/health', headers={'Host': host, 'X-Forwarded-Host': HOST})
        for origin in ('http://' + HOST, PUBLIC + '.evil', 'https://other.example.test', 'null', PUBLIC + '/'):
            with self.subTest(origin=origin):
                self.assert_http(403, '/api/projects/synthetic-quarter/decisions', {'text': 'Rejected'},
                                 {'Origin': origin, 'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': HOST})

    def test_hosted_mutations_require_origin_json_and_no_cross_site(self):
        path = '/api/projects/synthetic-quarter/decisions'
        self.assert_http(403, path, {'text': 'Rejected'})
        self.assert_http(403, path, {'text': 'Rejected'}, {'Origin': PUBLIC, 'Sec-Fetch-Site': 'cross-site'})
        self.assert_http(415, path, {'text': 'Rejected'}, {'Origin': PUBLIC, 'Content-Type': 'text/plain'})
        self.assert_http(415, path, {'text': 'Rejected'}, {'Origin': PUBLIC, 'Content-Type': 'application/x-www-form-urlencoded'})
        accepted, _ = self.request(path, {'text': 'Explicit same-origin JSON'},
                                  {'Origin': PUBLIC, 'Sec-Fetch-Site': 'same-origin',
                                   'Content-Type': 'application/json; charset=utf-8'})
        self.assertEqual(accepted['status'], 'proposed')

    def test_duplicate_host_headers_are_rejected(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        try:
            connection.putrequest('GET', '/api/health', skip_host=True)
            connection.putheader('Host', HOST)
            connection.putheader('Host', 'evil.example')
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            connection.close()


if __name__ == '__main__':
    unittest.main()
