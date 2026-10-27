"""VM startup only: managed identity → Key Vault → private, ephemeral Compose env files."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_BODY = 131072


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_json(url, headers):
    # IMDS is link-local: never send its token request through environment proxies.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(Request(url, headers=headers), timeout=10) as response:
        if response.status != 200:
            raise RuntimeError('Secret service request failed')
        body = response.read(MAX_BODY + 1)
    if len(body) > MAX_BODY:
        raise RuntimeError('Secret service response exceeds the limit')
    return json.loads(body)


def private_env(path, values):
    # Compose single-quoted env values preserve bcrypt '$' without interpolation.
    # No arbitrary quotes/newlines are allowed, even for future secret formats.
    for value in values.values():
        if not isinstance(value, str) or any(char in value for char in "'\r\n\x00"):
            raise ValueError('Unsafe runtime environment value')
    if path.is_symlink():
        raise ValueError('Unsafe runtime environment path')
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.aas-env-')
    try:
        with os.fdopen(descriptor, 'w') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(''.join(f"{name}='{value}'\n" for name, value in values.items()))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def refresh(config, output_dir):
    import bcrypt  # Ubuntu python3-bcrypt, independent of application dependencies.
    vault = config.get('vault_name')
    host = config.get('hostname')
    enabled = config.get('enable_openai')
    if (not isinstance(vault, str) or not re.fullmatch(r'[a-z][a-z0-9-]{1,22}[a-z0-9]', vault)
            or not isinstance(host, str) or not re.fullmatch(r'[a-z][a-z0-9-]{1,61}[a-z0-9]\.westeurope\.cloudapp\.azure\.com', host)
            or type(enabled) is not bool):
        raise ValueError('Invalid public deployment configuration')
    output_dir = Path(output_dir)
    if any(path.is_symlink() for path in (output_dir, *output_dir.parents)):
        raise ValueError('Unsafe runtime directory')
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    output_dir.chmod(0o700)
    # Bounded retries cover initial managed-identity/RBAC propagation; no secret is logged.
    for attempt in range(6):
        try:
            token_url = 'http://169.254.169.254/metadata/identity/oauth2/token?' + urlencode(
                {'api-version': '2018-02-01', 'resource': 'https://vault.azure.net'})
            token = fetch_json(token_url, {'Metadata': 'true'})['access_token']
            if not isinstance(token, str) or not token or len(token) > 16384 or any(c in token for c in '\r\n\x00'):
                raise ValueError('Invalid managed identity token')
            def secret(name):
                value = fetch_json(f'https://{vault}.vault.azure.net/secrets/{name}?api-version=7.4',
                                   {'Authorization': 'Bearer ' + token})['value']
                if not isinstance(value, str):
                    raise ValueError('Invalid secret value')
                return value
            password = secret('studio-login-password')
            encoded = password.encode('utf-8')
            if not 16 <= len(encoded) <= 72 or any(c in password for c in '\r\n\x00'):
                raise ValueError('Login password must contain 16–72 UTF-8 bytes without control line breaks')
            password_hash = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12)).decode('ascii')
            app = {'AAS_PUBLIC_ORIGIN': 'https://' + host, 'AAS_OPENAI_ENABLED': '1' if enabled else '0'}
            if enabled:
                key = secret('openai-api-key')
                if not re.fullmatch(r'sk-[A-Za-z0-9_-]{16,512}', key):
                    raise ValueError('API key has an unsupported format')
                app['OPENAI_API_KEY'] = key
            private_env(output_dir / 'app.env', app)
            private_env(output_dir / 'caddy.env', {'STUDIO_HOST': host, 'STUDIO_PASSWORD_HASH': password_hash})
            return
        except Exception:
            if attempt == 5:
                raise RuntimeError('Managed-identity secret refresh failed; service remains stopped') from None
            time.sleep(min(2 ** (attempt + 1), 30))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('/run/aas'))
    args = parser.parse_args()
    try:
        refresh(json.loads(args.config.read_text()), args.output_dir)
    except Exception:
        # Never print urllib bodies, Authorization headers, env values or exception chains.
        print('Secret refresh failed. Check VM identity, Key Vault role and secret names.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
