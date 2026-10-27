#!/usr/bin/env bash
# Invoked as root through Azure Run Command; config and commit contain no secrets.
set -euo pipefail
umask 077
test "$(id -u)" -eq 0
exec 9>/run/aas-bootstrap.lock
flock -n 9
config=/etc/aas/deploy.json
readarray -t settings < <(python3 - "$config" <<'PY'
import json,re,sys
d=json.load(open(sys.argv[1]))
assert re.fullmatch(r'[0-9a-f]{40}',d['source_commit'])
print(d['source_commit'])
PY
)
commit=${settings[0]:-}
[[ "$commit" =~ ^[0-9a-f]{40}$ ]]
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install --yes --no-install-recommends ca-certificates curl docker.io docker-buildx docker-compose-v2 python3-bcrypt
systemctl enable --now docker
install -d -m 0755 /opt/aas /opt/aas/releases
install -d -m 0700 /srv/aas
install -d -m 0700 -o 10001 -g 10001 /srv/aas/workspace
install -d -m 0700 -o 10002 -g 10002 /srv/aas/caddy-data /srv/aas/caddy-config
archive=$(mktemp /tmp/aas-source.XXXXXX.tar.gz)
stage=''
trap 'rm -f "$archive"; if [[ -n "$stage" ]]; then rm -rf "$stage"; fi' EXIT
url="https://github.com/sayac007/Agentic-Analytics-Studio/archive/${commit}.tar.gz"
curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 --retry 3 "$url" --output "$archive"
release="/opt/aas/releases/${commit}"
if [[ ! -d "$release" ]]; then
  stage=$(mktemp -d /opt/aas/releases/.stage.XXXXXX)
  tar -xzf "$archive" --strip-components=1 --no-same-owner -C "$stage"
  test -f "$stage/Dockerfile"
  test -f "$stage/deploy/azure/agentic-studio.service"
  mv "$stage" "$release"
  stage=''
fi
test -f "$release/Dockerfile"
for filename in Caddyfile compose.yaml refresh-secrets.py; do
  install -m 0644 "$release/deploy/azure/$filename" "/opt/aas/$filename"
done
install -m 0644 "$release/deploy/azure/agentic-studio.service" /etc/systemd/system/agentic-studio.service
python3 - "$archive" "$commit" "$url" <<'PY'
import datetime,hashlib,json,sys
from pathlib import Path
archive,commit,url=sys.argv[1:]
document={'source_commit':commit,'archive_url':url,'archive_sha256':hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
          'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
Path('/opt/aas/source-provenance.json').write_text(json.dumps(document,indent=2)+'\n')
PY
DOCKER_BUILDKIT=1 docker build --pull --tag "aas-studio:${commit}" "$release"
printf 'AAS_APP_IMAGE=aas-studio:%s\n' "$commit" > /opt/aas/image.env
chmod 0600 /opt/aas/image.env
systemctl daemon-reload
systemctl enable agentic-studio.service
systemctl restart agentic-studio.service
echo 'Studio service started. HTTPS certificate issuance may still take a few minutes.'
echo "AAS_BOOTSTRAP_OK:${commit}"
