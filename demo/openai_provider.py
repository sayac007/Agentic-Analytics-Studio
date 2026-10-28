"""One documented Responses endpoint; bounded HTTPS, no retries or browser keys."""
from dataclasses import dataclass, field
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener
from .provider_diagnostics import safe_http_failure, safe_transport_failure

MODEL = 'gpt-5.4-mini-2026-03-17'
ENDPOINT = 'https://api.openai.com/v1/responses'
REQUEST_BYTES = 16384
MAX_OUTPUT_TOKENS = 1536
MAX_INPUT_GUARD = REQUEST_BYTES + 4096
MAX_REQUEST_NANO_USD = MAX_INPUT_GUARD * 750 + MAX_OUTPUT_TOKENS * 4500
LIMITS = dict(requests=3, tools=2, max_output_tokens=MAX_OUTPUT_TOKENS,
              request_bytes=REQUEST_BYTES, turn_usd=.10, workspace_usd=1.0)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


class ConversationError(RuntimeError):
    def __init__(self, code, message, status=503):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


@dataclass(frozen=True)
class Config:
    enabled: bool = False
    api_key: str = field(default='', repr=False)

    @classmethod
    def from_env(cls):
        return cls(os.environ.get('AAS_OPENAI_ENABLED') == '1', os.environ.get('OPENAI_API_KEY', ''))

    def status(self):
        return dict(provider='openai', enabled=self.enabled, configured=bool(self.api_key),
                    available=self.enabled and bool(self.api_key), model=MODEL, limits=LIMITS,
                    reason='configured_not_live_verified' if self.enabled and self.api_key else
                           'disabled' if not self.enabled else 'missing_server_key',
                    live_verification='not_verified_by_configuration',
                    notice='Separate API billing; store:false is not zero retention. Only explicitly previewed and consented project context; archive and observed scopes remain separate.')

    def require_available(self):
        if not self.enabled or not self.api_key:
            raise ConversationError('provider_unavailable',
                                    'OpenAI ist serverseitig nicht aktiviert oder kein API-Schlüssel konfiguriert. Lokaler Modus bleibt verfügbar.')

    def safe_text(self, text):
        if self.api_key:
            text = text.replace(self.api_key, '[REDACTED]')
        return re.sub(r'(?i)(?:sk-[a-z0-9_-]{12,}|bearer\s+[a-z0-9._-]{12,})', '[REDACTED]', text)

    def reject_secrets(self, value):
        text = canonical(value).decode()
        if self.safe_text(text) != text:
            raise ConversationError('credential_in_context', 'Zugangsdaten dürfen nicht als Kontext gesendet werden.', 422)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ConversationError('provider_redirect', 'Provider-Weiterleitung abgewiesen.')


class Client:
    def __init__(self, config):
        self.config = config

    def request(self, payload):
        self.config.require_available()
        raw = canonical(payload)
        if len(raw) > REQUEST_BYTES:
            raise ConversationError('context_limit', 'Kontextgrenze erreicht; Anfrage kürzen oder einen neuen Kontext wählen.', 422)
        request = Request(ENDPOINT, data=raw, method='POST', headers={
            'Authorization': 'Bearer ' + self.config.api_key,
            'Content-Type': 'application/json', 'User-Agent': 'AgenticAnalyticsStudio/03B'})
        try:
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                raw = response.read(256001)
            if len(raw) > 256000:
                raise ValueError('Oversized response')
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError('Invalid response')
            return value
        except ConversationError:
            raise
        except HTTPError as error:
            detail = safe_http_failure(error)
            labels = ''.join(' ' + value for value in (detail['provider_code'], detail['parameter']) if value)
            raise ConversationError(detail['category'], detail['hint'] + labels +
                                    ' Keine automatische Wiederholung; Kostenstatus gegebenenfalls ungeklärt.') from None
        except (URLError, TimeoutError, OSError) as error:
            detail = safe_transport_failure(error)
            raise ConversationError(detail['category'], detail['hint'] +
                                    ' Keine automatische Wiederholung; Kostenstatus ungeklärt.') from None
        except ValueError:
            raise ConversationError('provider_unavailable',
                                    'OpenAI-Aufruf fehlgeschlagen; keine automatische Wiederholung. Kosten können trotz fehlender Antwort entstanden sein.') from None


def usage_and_cost(response):
    if response.get('model') != MODEL or response.get('service_tier') != 'default':
        raise ConversationError('price_scope', 'Provider-Modell oder Tarifstufe entspricht nicht dem lokalen Kostenguard; Reservierung bleibt bestehen.')
    usage = response.get('usage')
    if not isinstance(usage, dict):
        raise ConversationError('missing_usage', 'Provider-Nutzung fehlt; Kostenreservierung bleibt bestehen.')
    def integer(value):
        if type(value) is not int or value < 0:
            raise ConversationError('invalid_usage', 'Ungültige Provider-Nutzungsangaben; Reservierung bleibt bestehen.')
        return value
    inputs = integer(usage.get('input_tokens'))
    outputs = integer(usage.get('output_tokens'))
    total = integer(usage.get('total_tokens'))
    details = usage.get('input_tokens_details') or {}
    cached = integer(details.get('cached_tokens', 0)) if isinstance(details, dict) else -1
    if cached < 0 or cached > inputs or total != inputs+outputs or inputs > MAX_INPUT_GUARD or outputs > MAX_OUTPUT_TOKENS:
        raise ConversationError('usage_guard', 'Provider-Nutzung überschreitet den lokalen Guard; keine weiteren Aufrufe.')
    cost = (inputs-cached)*750 + cached*75 + outputs*4500
    output_details = usage.get('output_tokens_details') or {}
    reasoning = integer(output_details.get('reasoning_tokens', 0)) if isinstance(output_details, dict) else -1
    if reasoning < 0 or reasoning > outputs:
        raise ConversationError('invalid_usage', 'Ungültige Reasoning-Nutzungsangaben.')
    record = dict(input_tokens=inputs, output_tokens=outputs, total_tokens=total)
    if isinstance(usage.get('input_tokens_details'), dict) and 'cached_tokens' in usage['input_tokens_details']:
        record['input_tokens_details'] = dict(cached_tokens=cached)
    if isinstance(usage.get('output_tokens_details'), dict) and 'reasoning_tokens' in usage['output_tokens_details']:
        record['output_tokens_details'] = dict(reasoning_tokens=reasoning)
    return record, cost
