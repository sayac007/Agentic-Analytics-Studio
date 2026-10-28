import io
import json
import ssl
import unittest
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError, URLError

from demo.openai_provider import Client, Config, ConversationError, MODEL
from demo.provider_diagnostics import check_model_access, safe_http_failure

SECRET = 'sk-test-NOT-A-REAL-CREDENTIAL-123456'


def failure(status, code=None, param=None):
    body = json.dumps({'error': {'message': 'PRIVATE ' + SECRET,
                                 'code': code, 'param': param}}).encode()
    return HTTPError('https://api.openai.com/PRIVATE', status, SECRET, {},
                     io.BytesIO(body))


class ProviderDiagnosticsTests(unittest.TestCase):
    def test_status_and_allowlisted_codes_without_provider_message(self):
        for status, code, expected in (
            (401, 'invalid_api_key', 'provider_authentication'),
            (403, None, 'provider_permission'), (404, 'model_not_found', 'provider_model_access'),
            (429, 'insufficient_quota', 'provider_quota'),
            (429, 'rate_limit_exceeded', 'provider_rate_limit'),
            (400, 'unsupported_value', 'provider_request_rejected'),
            (500, SECRET, 'provider_http_error')
        ):
            with self.subTest(status=status, code=code):
                safe = safe_http_failure(failure(status, code, SECRET))
                self.assertEqual(safe['category'], expected)
                self.assertEqual(safe['http_status'], status)
                self.assertNotIn(SECRET, json.dumps(safe))
                self.assertNotIn('PRIVATE', json.dumps(safe))
                self.assertIsNone(safe['parameter'])

    def test_whitelisted_parameter_and_malformed_body(self):
        self.assertEqual(safe_http_failure(failure(400, 'unsupported_value', 'reasoning.effort'))['parameter'],
                         'reasoning.effort')
        for raw in (b'not JSON', b'x' * 9000, b'{"error": {"code": [], "param": {}}}'):
            safe = safe_http_failure(HTTPError('private', 429, SECRET, {}, io.BytesIO(raw)))
            self.assertEqual(safe['category'], 'provider_rate_limit')
            self.assertIsNone(safe['provider_code'])

    def test_real_client_uses_safe_http_error_and_never_retries(self):
        opener = Mock()
        opener.open.side_effect = failure(429, 'insufficient_quota')
        with patch('demo.openai_provider.build_opener', return_value=opener):
            with self.assertRaises(ConversationError) as caught:
                Client(Config(True, SECRET)).request({'model': MODEL})
        self.assertEqual(caught.exception.code, 'provider_quota')
        self.assertIn('insufficient_quota', str(caught.exception))
        self.assertNotIn(SECRET, str(caught.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_metadata_check_is_get_without_prompt_or_inference(self):
        response = Mock(status=200)
        response.read.return_value = json.dumps({'id': MODEL}).encode()
        opener = Mock()
        opener.open.return_value = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        result = check_model_access(SECRET, MODEL, opener=opener)
        self.assertEqual(result['category'], 'model_access_ok')
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertIsNone(request.data)
        self.assertEqual(request.full_url, 'https://api.openai.com/v1/models/' + MODEL)
        self.assertEqual(opener.open.call_count, 1)
        self.assertNotIn(SECRET, json.dumps(result))

    def test_no_request_when_disabled_or_key_missing(self):
        opener = Mock()
        self.assertEqual(check_model_access('', MODEL, opener=opener)['category'], 'provider_not_configured')
        self.assertEqual(check_model_access(SECRET, MODEL, enabled=False, opener=opener)['category'],
                         'provider_not_configured')
        opener.open.assert_not_called()

    def test_metadata_errors_are_safe_and_no_automatic_retry(self):
        for error, expected in (
            (failure(401, 'invalid_api_key'), 'provider_authentication'),
            (URLError(ssl.SSLCertVerificationError(1, SECRET)), 'provider_tls'),
            (TimeoutError(SECRET), 'provider_timeout'),
            (URLError(SECRET), 'provider_transport'),
            (RuntimeError(SECRET), 'provider_diagnostic_failed')
        ):
            with self.subTest(category=expected):
                opener = Mock()
                opener.open.side_effect = error
                result = check_model_access(SECRET, MODEL, opener=opener)
                self.assertEqual(result['category'], expected)
                self.assertNotIn(SECRET, json.dumps(result))
                self.assertEqual(opener.open.call_count, 1)

    def test_wrong_model_metadata_does_not_claim_responses_work(self):
        response = Mock(status=200)
        response.read.return_value = b'{"id":"some-other-model"}'
        opener = Mock()
        opener.open.return_value = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        self.assertEqual(check_model_access(SECRET, MODEL, opener=opener)['category'],
                         'provider_invalid_metadata')


if __name__ == '__main__':
    unittest.main()
