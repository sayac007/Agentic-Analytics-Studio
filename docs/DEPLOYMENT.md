# Local and private Azure operation

The existing browser pilot and the Task 04 research CLI are separate.
The cleanup does not deploy a new server, expose private data or enable a paid AI call.
Read the preserved results without starting the app:
[Task 04](../results/task04/README.md), [Task 02](../results/task02/report.md).

## Local browser pilot

Tested configuration: Python 3.12 on Linux. Windows-specific execution of the
Task 04 JAX environment is not verified. The existing app has a smaller lock:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-empirical.lock
AAS_OPENAI_ENABLED=0 .venv/bin/python -m demo
```

Open http://127.0.0.1:8000. Health is `/api/health`.
The process uses loopback by default. A new environment has no automatically
restored private observations; synthetic history remains a labelled archive,
not replacement empirical data. Stop with Ctrl+C.

Persistent project storage and private import requirements:
[empirical pilot](EMPIRICAL_STUDIO.md) and [research workflow](RESEARCH_WORKFLOW.md).
Do not copy private files into Git or public CI to make an empty workspace appear
complete. Installing a provider key alone does not enable provider calls.
The optional provider path previews its selected context and requires explicit
user approval; invalid provider credentials remain a separate operational failure.

## Existing private Azure deployment

The existing PowerShell script and pinned-image/container restrictions remain
unchanged: [operator guide](AZURE_PRIVATE_STUDIO.md). Authentication is required;
no live instance address, login identity or credential value is repeated here.
TLS/origin settings, Managed Identity, Key Vault and least-privilege roles are
operational prerequisites, not evidence of a successful OpenAI response.
No Azure changes or paid model calls are part of this documentation cleanup.

Authoritative secret values belong in Key Vault. Preserve metadata (purpose,
reference, owner, actual date/precision, consumers and rotation procedure),
never values/hashes/tokens, under [the existing inventory rule](../AGENTS.md).
[SECRET_INVENTORY.md](SECRET_INVENTORY.md) remains unchanged until a complete
private metadata backup and responsible access are explicitly confirmed.
Do not fabricate a private backup location or creation timestamp.

Existing Docker build remains the existing Dockerfile; documentation changes
do not add Task 04 packages or private datasets to the image.
