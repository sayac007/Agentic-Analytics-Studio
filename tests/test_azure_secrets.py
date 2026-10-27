"""Startup-secret boundaries; fixtures never contact Azure or use real credentials."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('azure_refresh', ROOT / 'deploy/azure/refresh-secrets.py')
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)

CONFIG = {'vault_name': 'aas-test-vault',
          'hostname': 'aas-test.westeurope.cloudapp.azure.com', 'enable_openai': True}
PASSWORD = 'TEST-ONLY-private-login-password'
KEY = 'sk-TEST_ONLY_NOT_A_REAL_KEY_123456789'
TOKEN = 'TEST-ONLY-managed-identity-token'
HASH = '$2b$12$TEST_ONLY_HASH_NOT_A_REAL_PASSWORD_HASH'
BCRYPT = SimpleNamespace(gensalt=lambda rounds: b'TEST-ONLY-salt',
                         hashpw=lambda password, salt: HASH.encode())


class AzureSecretTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aas-secret-tests-')
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'runtime'
        self.calls = []

    def fake_fetch(self, url, headers):
        self.calls.append((url, headers))
        if url.startswith('http://169.254.169.254/'):
            return {'access_token': TOKEN}
        if '/secrets/studio-login-password?' in url:
            return {'value': PASSWORD}
        if '/secrets/openai-api-key?' in url:
            return {'value': KEY}
        raise AssertionError('Unexpected secret endpoint')

    def invoke(self, config=None, fetch=None):
        with patch.dict(sys.modules, bcrypt=BCRYPT), \
                patch.object(refresh, 'fetch_json', side_effect=fetch or self.fake_fetch), \
                patch.object(refresh.time, 'sleep'):
            refresh.refresh(CONFIG if config is None else config, self.out)

    def test_identity_scopes_and_separate_private_env_files(self):
        self.invoke()
        app = (self.out / 'app.env').read_text()
        caddy = (self.out / 'caddy.env').read_text()
        self.assertIn("AAS_OPENAI_ENABLED='1'", app)
        self.assertIn(KEY, app)
        self.assertNotIn(PASSWORD, app + caddy)
        self.assertNotIn(KEY, caddy)
        self.assertIn("STUDIO_PASSWORD_HASH='" + HASH + "'", caddy)
        self.assertNotIn(TOKEN, app + caddy)
        self.assertEqual(self.calls[0][1], {'Metadata': 'true'})
        self.assertIn('resource=https%3A%2F%2Fvault.azure.net', self.calls[0][0])
        for url, headers in self.calls[1:]:
            self.assertTrue(url.startswith('https://aas-test-vault.vault.azure.net/secrets/'))
            self.assertEqual(headers, {'Authorization': 'Bearer ' + TOKEN})
        self.assertEqual(stat.S_IMODE(self.out.stat().st_mode), 0o700)
        for name in ('app.env', 'caddy.env'):
            self.assertEqual(stat.S_IMODE((self.out / name).stat().st_mode), 0o600)

    def test_disabled_provider_never_fetches_or_writes_api_key(self):
        self.invoke({**CONFIG, 'enable_openai': False})
        app = (self.out / 'app.env').read_text()
        self.assertIn("AAS_OPENAI_ENABLED='0'", app)
        self.assertNotIn('OPENAI_API_KEY', app)
        self.assertFalse(any('/secrets/openai-api-key?' in url for url, _ in self.calls))

    def test_missing_secret_fails_without_successful_runtime_files(self):
        with self.assertRaisesRegex(RuntimeError, 'remains stopped'):
            self.invoke(fetch=lambda url, headers: (_ for _ in ()).throw(RuntimeError(KEY)))
        self.assertFalse((self.out / 'app.env').exists())
        self.assertFalse((self.out / 'caddy.env').exists())

    def test_bad_secret_cannot_inject_an_environment_variable(self):
        def malicious(url, headers):
            if '/secrets/openai-api-key?' in url:
                return {'value': KEY + '\nAAS_OPENAI_ENABLED=0'}
            return self.fake_fetch(url, headers)
        with self.assertRaises(RuntimeError):
            self.invoke(fetch=malicious)
        self.assertFalse((self.out / 'app.env').exists())
        self.assertFalse((self.out / 'caddy.env').exists())

    def test_public_config_cannot_redirect_identity_to_another_host(self):
        for bad in ({**CONFIG, 'vault_name': 'bad.example/path'},
                    {**CONFIG, 'hostname': 'aas-test.westeurope.cloudapp.azure.com.evil'},
                    {**CONFIG, 'enable_openai': 'true'}):
            with self.subTest(config=bad), self.assertRaises(ValueError):
                self.invoke(bad)
        self.assertEqual(self.calls, [])

    def test_environment_quoting_and_symlink_refusal(self):
        self.out.mkdir()
        for bad in ("unsafe'value", 'line\nbreak', 'nul\0byte', 'return\rbyte'):
            with self.subTest(value=repr(bad)), self.assertRaises(ValueError):
                refresh.private_env(self.out / 'app.env', {'X': bad})
        target = self.out / 'untouched'
        target.write_text('original')
        (self.out / 'app.env').symlink_to(target)
        with self.assertRaises(ValueError):
            refresh.private_env(self.out / 'app.env', {'X': 'safe'})
        self.assertEqual(target.read_text(), 'original')

    def test_cli_does_not_echo_provider_exception_or_secret(self):
        config = Path(self.temp.name) / 'config.json'
        config.write_text(json.dumps(CONFIG))
        args = ['refresh-secrets.py', '--config', str(config), '--output-dir', str(self.out)]
        output = io.StringIO()
        with patch.object(sys, 'argv', args), patch.object(refresh, 'refresh', side_effect=RuntimeError(KEY)), \
                contextlib.redirect_stderr(output):
            self.assertEqual(refresh.main(), 1)
        self.assertNotIn(KEY, output.getvalue())
        self.assertNotIn('Traceback', output.getvalue())
        self.assertIn('Secret refresh failed', output.getvalue())


if __name__ == '__main__':
    unittest.main()
