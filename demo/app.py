"""Loopback-only local demo. No empirical inputs, file browsing or arbitrary tools."""
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import service

app = FastAPI(title='Agentic Analytics Studio — Synthetic Demo', version='0.1.0')
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]'])
STATIC = Path(__file__).with_name('static')
app.mount('/static', StaticFiles(directory=STATIC), name='static')
RUNS = OrderedDict()
RUN_LOCK = Lock()


@app.middleware('http')
async def local_origin(request: Request, call_next):
    origin = request.headers.get('origin')
    if origin and origin != f'{request.url.scheme}://{request.headers.get("host")}':
        return JSONResponse({'detail': 'Only same-origin local requests are allowed.'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'"
    return response


class RunRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    dataset: Literal['synthetic-mmm'] = 'synthetic-mmm'
    model: Literal['with-quarter', 'without-quarter'] = 'with-quarter'


@app.get('/')
def index():
    return FileResponse(STATIC / 'index.html')


@app.get('/api/health')
def health():
    return {'status': 'ready', 'classification': 'SYNTHETIC / NOT EMPIRICAL'}


@app.get('/api/datasets')
def datasets():
    return [service.DATASET]


def run_demo(request: RunRequest):
    if not RUN_LOCK.acquire(blocking=False):
        raise HTTPException(409, 'An analysis is already running. Please wait.')
    try:
        value = service.compute(request.model)
        run_id = uuid4().hex
        value['id'] = run_id
        RUNS[run_id] = value
        while len(RUNS) > 5:
            RUNS.popitem(last=False)
        return value
    except Exception as exc:
        # Do not return filesystem paths, subprocess stderr or environment details.
        raise HTTPException(503, 'Analysis failed validation or runtime checks. Check the pinned installation; no successful result was stored.') from exc
    finally:
        RUN_LOCK.release()


@app.post('/api/runs')
def create_run(request: RunRequest):
    return run_demo(request)


@app.get('/api/runs/{run_id}')
def get_run(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(404, 'Run not found; results are kept only for this local session.')
    return RUNS[run_id]
