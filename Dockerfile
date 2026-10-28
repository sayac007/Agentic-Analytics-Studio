# Official Python image index inspected 2026-10-27; digest fixes the base bytes.
FROM python:3.12.16-slim-bookworm@sha256:6dd8b6dab6b3adc7812bab69eca5dbdc1a5cc690ad28306d234ffb4ef8ac9753

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    AAS_WORKSPACE_DIR=/data/workspace \
    AAS_BIND_HOST=0.0.0.0 \
    AAS_OPENAI_ENABLED=0

WORKDIR /app
COPY requirements.lock requirements-demo.lock requirements-kba.lock requirements-empirical.lock ./
# Optional build-only CA bundle supports managed TLS proxies; never copied to layers.
RUN --mount=type=secret,id=build_ca,mode=0444 \
    aas_ca_file=/etc/ssl/certs/ca-certificates.crt \
    && if [ -f /run/secrets/build_ca ]; then aas_ca_file=/run/secrets/build_ca; fi \
    && export SSL_CERT_FILE="$aas_ca_file" PIP_CERT="$aas_ca_file" GIT_SSL_CAINFO="$aas_ca_file" \
    && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::https::CaInfo="$aas_ca_file" update -o APT::Update::Error-Mode=any \
    && apt-get -o Acquire::https::CaInfo="$aas_ca_file" install -y --no-install-recommends git ca-certificates \
    && python -m pip install --no-cache-dir -r requirements-empirical.lock \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 studio \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin studio \
    && mkdir -p /data/workspace \
    && chown 10001:10001 /data/workspace \
    && chmod 700 /data/workspace

# Public code/catalogs only. Private source snapshots and results are installed at runtime.
COPY demo/ ./demo/
COPY studio/ ./studio/
COPY contracts/ ./contracts/
COPY config/ ./config/
COPY empirical/ ./empirical/
COPY source_acquisition/ ./source_acquisition/
COPY fuel_oil/ ./fuel_oil/
COPY kba/ ./kba/
COPY data/kba/ ./data/kba/
COPY data/fuel_oil/ ./data/fuel_oil/
COPY data/verified_sources/ ./data/verified_sources/
COPY data/tesla_product_events/ ./data/tesla_product_events/
COPY workorders/03c-empirical-live.md ./workorders/03c-empirical-live.md
COPY docs/COPILOT_RESULT_PRESENTATION.md ./docs/COPILOT_RESULT_PRESENTATION.md
RUN find /app -type d -exec chmod 0755 {} + \
    && find /app -type f -exec chmod 0644 {} +

USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "from urllib.request import Request,urlopen; from demo.hosting import HostingConfig; config=HostingConfig.from_env(); urlopen(Request('http://127.0.0.1:8000/api/health',headers={'Host':config.health_host}),timeout=3).read()"]
CMD ["python", "-m", "demo"]
