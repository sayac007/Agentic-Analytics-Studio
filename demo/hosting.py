"""Explicit reverse-proxy origin policy; loopback remains the default."""
from dataclasses import dataclass
import os
import re
from urllib.parse import urlsplit


class HostingError(ValueError):
    """Hosting configuration is unsafe or ambiguous."""


def _public_origin(raw):
    error = ('AAS_PUBLIC_ORIGIN must be an exact HTTPS origin with an ASCII hostname, '
             'optionally port 443, and no path, query, fragment or credentials')
    if (not isinstance(raw, str) or not raw.startswith('https://')
            or any(character.isspace() for character in raw)
            or any(character in raw for character in ('\\', '%', '*', '?', '#'))):
        raise HostingError(error)
    try:
        parsed = urlsplit(raw)
        host = parsed.hostname
        port = parsed.port
        if (parsed.scheme != 'https' or not host or parsed.username is not None
                or parsed.password is not None or parsed.path or parsed.query or parsed.fragment
                or port not in (None, 443) or not host.isascii() or len(host) > 253
                or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
                           for label in host.split('.'))
                or parsed.netloc.lower() not in (host, host + ':443')):
            raise HostingError(error)
    except ValueError:
        raise HostingError(error) from None
    # Browsers omit the default HTTPS port from their serialized Origin header.
    return 'https://' + host, host


@dataclass(frozen=True)
class HostingConfig:
    public_origin: str | None = None
    hostname: str | None = None
    bind_host: str = '127.0.0.1'

    @classmethod
    def from_env(cls, environment=None):
        env = os.environ if environment is None else environment
        raw = env.get('AAS_PUBLIC_ORIGIN')
        origin, hostname = (None, None) if raw is None else _public_origin(raw)
        bind = env.get('AAS_BIND_HOST', '127.0.0.1')
        if bind not in ('127.0.0.1', '0.0.0.0'):
            raise HostingError('AAS_BIND_HOST must be 127.0.0.1 or explicitly 0.0.0.0')
        if bind == '0.0.0.0' and origin is None:
            raise HostingError('AAS_BIND_HOST=0.0.0.0 requires a valid AAS_PUBLIC_ORIGIN')
        return cls(origin, hostname, bind)

    @property
    def trusted_hosts(self):
        return [self.hostname] if self.hostname else ['127.0.0.1', 'localhost', '[::1]']

    @property
    def health_host(self):
        return self.hostname or '127.0.0.1'

    def request_error(self, method, scheme, host, origin, fetch_site, content_type):
        """Return (status, safe message), or None. Forwarded headers are irrelevant."""
        if self.public_origin and host not in (self.hostname, self.hostname + ':443'):
            return 400, 'Unexpected Host for the configured public origin.'
        expected = self.public_origin or f'{scheme}://{host}'
        if (origin is not None and origin != expected) or fetch_site == 'cross-site':
            return 403, 'Only requests from the configured same origin are allowed.'
        if self.public_origin and method not in ('GET', 'HEAD', 'OPTIONS'):
            if origin != self.public_origin:
                return 403, 'State-changing hosted requests require the exact public Origin.'
            if (content_type or '').split(';', 1)[0].strip().lower() != 'application/json':
                return 415, 'State-changing hosted requests require application/json.'
        return None
