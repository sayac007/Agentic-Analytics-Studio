"""Safe provider failures and a read-only model-access check; no inference/retries."""
import json
import os
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


SAFE_CODES = {'invalid_api_key', 'insufficient_quota', 'rate_limit_exceeded',
              'model_not_found', 'permission_denied', 'unsupported_value',
              'unsupported_parameter', 'invalid_request_error'}
SAFE_PARAMS = {'model', 'reasoning', 'reasoning.effort', 'service_tier', 'max_output_tokens'}


def safe_http_failure(error):
    """Never expose provider messages, URLs, auth headers or arbitrary error fields."""
    status = error.code if type(error.code) is int and 100 <= error.code <= 599 else None
    code = param = None
    try:
        raw = error.read(8193)
        if len(raw) <= 8192:
            data = json.loads(raw)
            detail = data.get('error') if isinstance(data, dict) else None
            if isinstance(detail, dict):
                if isinstance(detail.get('code'), str) and detail['code'] in SAFE_CODES:
                    code = detail['code']
                if isinstance(detail.get('param'), str) and detail['param'] in SAFE_PARAMS:
                    param = detail['param']
    except Exception:
        pass
    finally:
        try:
            error.close()
        except Exception:
            pass
    if status == 401:
        category, hint = 'provider_authentication', 'OpenAI hat den API-Schlüssel abgelehnt (HTTP 401). Schlüsselstatus beim Anbieter und Vault-Eintrag prüfen.'
    elif code == 'insufficient_quota':
        category, hint = 'provider_quota', 'OpenAI meldet insufficient_quota. API-Guthaben, Abrechnung und Projektlimit beim Anbieter prüfen.'
    elif status == 403:
        category, hint = 'provider_permission', 'OpenAI verweigert die Berechtigung (HTTP 403). API-Projekt und Modellberechtigungen prüfen.'
    elif status == 404 or code == 'model_not_found':
        category, hint = 'provider_model_access', 'Das konfigurierte OpenAI-Modell ist für diese Anfrage nicht verfügbar. Modellkennung und Projektzugriff prüfen.'
    elif status == 429:
        category, hint = 'provider_rate_limit', 'OpenAI hat die Anfrage begrenzt (HTTP 429). Ohne Fehlercode ist die genaue Ursache nicht geklärt.'
    elif status in (400, 422):
        category, hint = 'provider_request_rejected', f'OpenAI hat das Anfrageformat abgelehnt (HTTP {status}).'
    else:
        category, hint = 'provider_http_error', 'OpenAI hat einen HTTP-Fehler zurückgegeben.'
    return {'category': category, 'http_status': status, 'provider_code': code,
            'parameter': param, 'hint': hint}


def safe_transport_failure(error):
    reason = error.reason if isinstance(error, URLError) else error
    if isinstance(reason, ssl.SSLCertVerificationError):
        return {'category': 'provider_tls', 'hint': 'TLS-Zertifikatsprüfung zur OpenAI-API fehlgeschlagen.'}
    if isinstance(reason, TimeoutError):
        return {'category': 'provider_timeout', 'hint': 'Zeitüberschreitung beim OpenAI-Aufruf.'}
    return {'category': 'provider_transport', 'hint': 'Netzwerkverbindung zur OpenAI-API fehlgeschlagen.'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise OSError('Provider redirect refused')


def check_model_access(api_key, model, enabled=True, opener=None):
    result = {'model': model, 'server_enabled': bool(enabled),
              'server_key_present': bool(api_key),
              'scope': 'model_metadata_only; no inference, no project context, no retry'}
    if not enabled or not api_key:
        return {**result, 'category': 'provider_not_configured'}
    request = Request('https://api.openai.com/v1/models/' + model,
                      headers={'Authorization': 'Bearer ' + api_key,
                               'User-Agent': 'AgenticAnalyticsStudio/ReadOnlyDiagnosis'})
    try:
        with (opener or build_opener(NoRedirect())).open(request, timeout=20) as response:
            status = response.status
            raw = response.read(16385)
        if len(raw) > 16384:
            raise ValueError('Oversized model metadata')
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get('id') != model or status != 200:
            raise ValueError('Unexpected model metadata')
        return {**result, 'category': 'model_access_ok', 'http_status': 200,
                'hint': 'Schlüssel und Modell-Metadaten erreichbar. Responses-Aufruf, Abrechnung und Parameter damit noch nicht geprüft.'}
    except HTTPError as error:
        return {**result, **safe_http_failure(error)}
    except (URLError, OSError, TimeoutError) as error:
        return {**result, **safe_transport_failure(error)}
    except ValueError:
        return {**result, 'category': 'provider_invalid_metadata'}
    except Exception:
        return {**result, 'category': 'provider_diagnostic_failed'}


if __name__ == '__main__':
    from demo.openai_provider import MODEL
    print(json.dumps(check_model_access(os.environ.get('OPENAI_API_KEY', ''),
                                       MODEL, os.environ.get('AAS_OPENAI_ENABLED') == '1'),
                     ensure_ascii=False))
