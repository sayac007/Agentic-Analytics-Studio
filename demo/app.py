"""Private observed-data Studio, separate synthetic archive and bounded opt-in AI."""
from contextlib import asynccontextmanager
import hashlib
import json
import os
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import agent, service
from .workspace import Workspace, WorkspaceError, MissingRecord
from . import conversation
from .openai_provider import Config, ConversationError
from .hosting import HostingConfig

DEFAULT_PROJECT = 'synthetic-quarter'
RUN_LOCK = Lock()
AI_LOCK = Lock()
STATIC = Path(__file__).with_name('static')
HOSTING = HostingConfig.from_env()


@asynccontextmanager
async def lifespan(application):
    workspace = Workspace(Path(os.environ.get('AAS_WORKSPACE_DIR', '.aas-workspace')))
    application.state.workspace = workspace
    application.state.ai_config = Config.from_env()
    try:
        yield
    finally:
        workspace.close()


app = FastAPI(title='Agentic Analytics Studio — Observed Data', version='0.3.0', lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=HOSTING.trusted_hosts, www_redirect=False)
app.mount('/static', StaticFiles(directory=STATIC), name='static')


def get_workspace():
    return app.state.workspace


def get_ai_config():
    return app.state.ai_config


@app.exception_handler(ConversationError)
async def conversation_error(request, exc):
    return JSONResponse({'detail': exc.message, 'code': exc.code, 'mode': 'openai'}, status_code=exc.status)


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Framework error payloads otherwise echo invalid input, including pasted secrets.
    return JSONResponse({'detail': 'Ungültige Anfrage oder nicht freigegebene Felder.'}, status_code=422)


@app.exception_handler(MissingRecord)
async def not_found(request, exc):
    return JSONResponse({'detail': 'Record not found in the selected project.'}, status_code=404)


@app.exception_handler(WorkspaceError)
async def storage_error(request, exc):
    return JSONResponse({'detail': 'Workspace integrity or storage check failed. No successful result is being presented.'}, status_code=503)


@app.middleware('http')
async def local_origin(request: Request, call_next):
    if len(request.headers.getlist('host')) != 1:
        return JSONResponse({'detail': 'Exactly one Host header is required.'}, status_code=400)
    error = HOSTING.request_error(request.method, request.url.scheme, request.headers.get('host'),
                                  request.headers.get('origin'), request.headers.get('sec-fetch-site'),
                                  request.headers.get('content-type'),
                                  fetch_mode=request.headers.get('sec-fetch-mode'),
                                  fetch_dest=request.headers.get('sec-fetch-dest'),
                                  path=request.url.path)
    if error:
        return JSONResponse({'detail': error[1]}, status_code=error[0])
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'"
    return response


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class RunRequest(StrictRequest):
    dataset: Literal['synthetic-mmm'] = 'synthetic-mmm'
    model: Literal['with-quarter', 'without-quarter'] | None = None


class AgentRequest(StrictRequest):
    message: str = Field(min_length=1, max_length=200)
    run_id: str | None = Field(default=None, pattern=r'^[0-9a-f]{32}$')


class MessageRequest(StrictRequest):
    message: str = Field(min_length=1, max_length=4000, pattern=r'\S')
    conversation_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    run_id: str | None = Field(default=None, pattern=r'^[0-9a-f]{32}$')
    approved_decision_ids: list[str] = Field(default_factory=list, max_length=3)
    mode: Literal['local', 'openai'] = 'local'
    consent: bool = False
    context_sha256: str | None = Field(default=None, pattern=r'^[0-9a-f]{64}$')


class ContextRequest(StrictRequest):
    message: str = Field(min_length=1, max_length=2000, pattern=r'\S')
    conversation_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    run_id: str | None = Field(default=None, pattern=r'^[0-9a-f]{32}$')
    approved_decision_ids: list[str] = Field(default_factory=list, max_length=3)


class DecisionRequest(StrictRequest):
    text: str = Field(min_length=1, max_length=4000, pattern=r'\S')
    kind: Literal['decision', 'development_workorder'] = 'decision'


@app.get('/')
def index():
    return FileResponse(STATIC / 'empirical.html')


@app.get('/archive/synthetic')
def synthetic_archive():
    return FileResponse(STATIC / 'index.html')


@app.get('/api/health')
def health():
    return {'status': 'ready', 'classification': 'OBSERVED_PRIVATE_WORKSPACE',
            'archive_classification': 'SYNTHETIC / NOT EMPIRICAL',
            'storage': 'sqlite', 'workspace_schema': 2, 'llm': 'optional_openai_opt_in'}


@app.get('/api/ai/status')
def ai_status():
    return get_ai_config().status()


@app.get('/api/datasets')
def datasets():
    return [service.DATASET]


def load_run(project_id, run_id):
    record = get_workspace().get_run(project_id, run_id)
    try:
        value = service.load_result(record['bundle_path'], record['model'])
    except Exception as exc:
        raise WorkspaceError('Stored result failed verification') from exc
    value.update(id=run_id, project_id=project_id)
    return value


def comparison(project_id, run_id):
    value = load_run(project_id, run_id)
    return {'classification': service.DATASET['classification'],
            'comparison': value['comparison'],
            'models': {name: {'result': v['result'], 'evaluation': v['evaluation']}
                       for name, v in value['variants'].items()}}


def diagnostics(project_id, run_id):
    value = load_run(project_id, run_id)
    return {'classification': service.DATASET['classification'], 'run_id': run_id,
            'diagnostics': value['result']['diagnostics'],
            'coefficients': value['result']['coefficients'], 'metrics': value['result']['metrics'],
            'evaluation': value['evaluation'], 'warnings': value['warnings']}


def resume(project_id):
    context = get_workspace().context(project_id)
    latest = load_run(project_id, context['runs'][0]['id']) if context['runs'] else None
    text = f"Projekt {context['project']['name']}. "
    if latest:
        text += (f"Letzter erneut geprüfter Lauf: {latest['id']} ({latest['model']}). "
                 + latest['interpretation'] + ' ' + ' '.join(latest['warnings']))
    else:
        text += 'Noch kein validierter Modelllauf in diesem Projekt. '
    pending = sum(d['status'] == 'proposed' for d in context['decisions'])
    interrupted = sum(e['status'] in ('failed', 'interrupted') for e in context['executions'])
    text += (f" In den angezeigten Einträgen: {pending} offene Vorschläge, "
             f"{interrupted} fehlgeschlagene oder unterbrochene Tool-Aufrufe. "
             'Gespeicherte Aussagen sind keine verifizierten Analyseergebnisse. Kein LLM beteiligt.')
    return {'summary': text, 'context': context,
            'latest_run_id': latest['id'] if latest else None, 'verified': latest is not None}


def execution_reference(name, arguments, output):
    """Small factual snapshots; no recursive transcript/context copies."""
    raw = json.dumps(output, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    reference = {'tool': name, 'run_id': arguments.get('run_id'),
                 'structured_output_sha256': hashlib.sha256(raw).hexdigest()}
    if name in ('list_datasets', 'describe_dataset', 'summarize_diagnostics'):
        reference['snapshot'] = output
    elif name == 'compare_runs':
        reference['snapshot'] = output['comparison']
    else:
        reference.update(latest_run_id=output['latest_run_id'], verified=output['verified'],
                         summary=output['summary'], counts=output['context']['counts'])
    return reference


def execute_tool(project_id, conversation_id, name, arguments, model=None):
    """Server-owned scope and permissions; never a path, expression or remote agent."""
    ws = get_workspace()
    project = ws.project(project_id)
    if project['dataset_id'] != 'synthetic-mmm':
        raise HTTPException(422, 'Synthetic archive tools cannot run in an empirical project.')
    if name not in agent.TOOLS:
        raise ValueError('Tool is not allowlisted')
    compute = name == 'run_demo_analysis'
    if compute and not RUN_LOCK.acquire(blocking=False):
        raise HTTPException(409, 'An analysis is already running. Please wait.')
    execution = None
    try:
        selected_model = model or project['default_model']
        logged_args = {'model': selected_model} if compute else arguments
        execution = ws.start_execution(project_id, conversation_id, name, logged_args)
        if compute:
            run_id = uuid4().hex
            output = service.compute(selected_model, output=ws.bundle_path(run_id))
            ws.complete_run(project_id, execution['id'], run_id, selected_model)
            output.update(id=run_id, project_id=project_id)
        else:
            handlers = {'list_datasets': datasets, 'describe_dataset': service.describe_dataset,
                        'compare_runs': lambda run_id: comparison(project_id, run_id),
                        'summarize_diagnostics': lambda run_id: diagnostics(project_id, run_id),
                        'resume_workspace': lambda: resume(project_id)}
            output = agent.call_tool(name, arguments, handlers)
            ws.finish_execution(project_id, execution['id'], 'succeeded',
                                output_ref=execution_reference(name, arguments, output))
        return output, execution['id']
    except Exception as exc:
        if execution:
            ws.finish_execution(project_id, execution['id'], 'failed', error_code='tool_failed')
        if isinstance(exc, (HTTPException, MissingRecord, WorkspaceError)):
            exc.tool_execution_id = execution['id'] if execution else None
            raise
        failure = HTTPException(503, 'Analysis/tool failed validation or runtime checks. No successful result was stored.')
        failure.tool_execution_id = execution['id'] if execution else None
        raise failure from exc
    finally:
        if compute:
            RUN_LOCK.release()


def run_demo(request: RunRequest, project_id=DEFAULT_PROJECT):
    project = get_workspace().project(project_id)
    output, _ = execute_tool(project_id, project['conversation_id'], 'run_demo_analysis', {}, request.model)
    return output


def respond(project_id, message, run_id, conversation_id):
    executed = []

    def handler(name):
        def call(**arguments):
            value, execution_id = execute_tool(project_id, conversation_id, name, arguments)
            executed.append(execution_id)
            return value
        return call

    answer = agent.respond(message, run_id, {name: handler(name) for name in agent.TOOLS})
    answer['execution_id'] = executed[0] if executed else None
    return answer


# Compatibility endpoints: the old demo API belongs only to the first project.
@app.post('/api/runs')
def create_run(request: RunRequest):
    return run_demo(request)


@app.get('/api/runs/{run_id}')
def get_run(run_id: str):
    return load_run(DEFAULT_PROJECT, run_id)


@app.get('/api/runs/{run_id}/comparison')
def compare_run(run_id: str):
    return comparison(DEFAULT_PROJECT, run_id)


def report_response(project_id, run_id):
    value = load_run(project_id, run_id)
    return PlainTextResponse(value['markdown_report'], media_type='text/markdown',
                             headers={'Content-Disposition': 'attachment; filename="synthetic-mmm-report.md"'})


@app.get('/api/runs/{run_id}/report', response_class=PlainTextResponse)
def markdown_report(run_id: str):
    return report_response(DEFAULT_PROJECT, run_id)


@app.get('/api/tools')
def list_tools():
    return {'tools': agent.TOOLS, 'permissions': agent.PERMISSIONS,
            'mcp_integration': 'not_implemented_adapter_seam_only',
            'language_mode': 'deterministic_exact_phrase_router_no_llm'}


@app.post('/api/agent')
def agent_request(request: AgentRequest):
    project = get_workspace().project(DEFAULT_PROJECT)
    try:
        return respond(DEFAULT_PROJECT, request.message, request.run_id, project['conversation_id'])
    except ValueError as exc:
        raise HTTPException(422, 'Unsupported request or arguments.') from exc


@app.get('/api/projects')
def projects():
    return [p for p in get_workspace().projects() if p['dataset_id'] == 'synthetic-mmm']


@app.get('/api/projects/{project_id}/workspace')
def project_workspace(project_id: str):
    state = get_workspace().context(project_id)
    state['ai'] = get_workspace().ai_state(project_id)
    return state


@app.post('/api/projects/{project_id}/agent-context')
def agent_context(project_id: str, request: ContextRequest):
    return conversation.preview(get_workspace(), project_id, request, get_ai_config(), load_run)


@app.post('/api/projects/{project_id}/runs')
def project_create_run(project_id: str, request: RunRequest):
    return run_demo(request, project_id)


@app.get('/api/projects/{project_id}/runs/{run_id}')
def project_get_run(project_id: str, run_id: str):
    return load_run(project_id, run_id)


@app.get('/api/projects/{project_id}/runs/{run_id}/comparison')
def project_compare_run(project_id: str, run_id: str):
    return comparison(project_id, run_id)


@app.get('/api/projects/{project_id}/runs/{run_id}/report', response_class=PlainTextResponse)
def project_report(project_id: str, run_id: str):
    return report_response(project_id, run_id)


@app.post('/api/projects/{project_id}/messages')
def project_message(project_id: str, request: MessageRequest):
    ws = get_workspace()
    if request.mode == 'openai':
        if not AI_LOCK.acquire(blocking=False):
            raise HTTPException(409, 'Ein externer Dialog läuft bereits. Bitte warten.')
        try:
            return conversation.respond(ws, project_id, request, get_ai_config(), load_run, execute_tool)
        finally:
            AI_LOCK.release()
    project = ws.project(project_id)
    if project['dataset_id'] != 'synthetic-mmm':
        raise HTTPException(422, 'Use the separate empirical conversation and consent.')
    if request.conversation_id != project['conversation_id']:
        raise MissingRecord('Conversation does not belong to project')
    if request.run_id:
        ws.get_run(project_id, request.run_id)
    ws.add_message(project_id, request.conversation_id, 'user', 'user_statement', request.message)
    try:
        agent.resolve(request.message)
    except ValueError:
        answer = dict(status='note_saved', tool=None, executed=False, execution_id=None,
                      text='Als Aussage gespeichert, nicht als verifiziertes Ergebnis oder freigegebene Entscheidung. Kein Tool ausgeführt. Nutze die angebotenen Tool-Anfragen; kein LLM integriert.', output=None)
    else:
        try:
            answer = respond(project_id, request.message, request.run_id, request.conversation_id)
        except Exception:
            ws.add_message(project_id, request.conversation_id, 'assistant', 'error',
                           'Tool fehlgeschlagen oder nicht zugänglich. Kein erfolgreiches Ergebnis behauptet.')
            raise
    ws.add_message(project_id, request.conversation_id, 'assistant',
                   'tool_result' if answer['executed'] else 'acknowledgement', answer['text'],
                   execution_id=answer['execution_id'])
    return answer


@app.post('/api/projects/{project_id}/decisions')
def propose_decision(project_id: str, request: DecisionRequest):
    return get_workspace().propose(project_id, request.text, request.kind)


@app.post('/api/projects/{project_id}/decisions/{decision_id}/approve')
def approve_decision(project_id: str, decision_id: str, request: StrictRequest):
    return get_workspace().approve(project_id, decision_id)


class EmpiricalQuestion(StrictRequest):
    message: str = Field(min_length=1, max_length=2000, pattern=r'\S')
    model: Literal['calendar', 'dynamic', 'macro', 'macro_diesel', 'macro_lag2', 'macro_diesel_lag2', 'macro_lag3', 'macro_diesel_lag3'] = 'macro'
    consent: bool = False
    context_sha256: str | None = Field(default=None, pattern=r'^[0-9a-f]{64}$')


class ResearchBrief(StrictRequest):
    question: str = Field(min_length=1, max_length=1200, pattern=r'\S')
    audience: str = Field(min_length=1, max_length=300, pattern=r'\S')
    decision: str = Field(min_length=1, max_length=1200, pattern=r'\S')
    interface_notes: str = Field(max_length=2000)
    required_drivers: list[str] = Field(min_length=2, max_length=11)


@app.get('/api/empirical/workflow')
def empirical_workflow():
    from empirical import service as observed
    from .research_workflow import overview
    try:
        bundle = observed.read()
    except FileNotFoundError:
        bundle = None
    except (ValueError, OSError, KeyError):
        raise HTTPException(503, 'Empirische Daten- oder Hashprüfung fehlgeschlagen.') from None
    record = get_workspace().research_brief()
    return {**record, 'review': overview(record['brief'], bundle)}


@app.post('/api/empirical/workflow')
def save_empirical_workflow(request: ResearchBrief):
    value = request.model_dump()
    get_ai_config().reject_secrets(value)
    try:
        return get_workspace().research_brief(value)
    except ValueError:
        raise HTTPException(422, 'Muss-Treiber ungültig; Kalender und Dynamik sind die feste Mindestbasis.') from None


@app.get('/api/empirical/presentation', response_class=PlainTextResponse)
def empirical_presentation(model: Literal['calendar', 'dynamic', 'macro', 'macro_diesel', 'macro_lag2', 'macro_diesel_lag2', 'macro_lag3', 'macro_diesel_lag3'] = 'macro'):
    from empirical import service as observed
    from .research_workflow import handoff
    try:
        bundle = observed.read()
        brief = get_workspace().research_brief()['brief']
        get_ai_config().reject_secrets(brief)
        return handoff(brief, bundle, model)
    except (FileNotFoundError, ValueError, OSError, KeyError):
        raise HTTPException(503, 'Verifiziertes Ergebnis oder Präsentationsanleitung fehlt; keine Übergabe erzeugt.') from None


@app.get('/api/empirical/copilot-instructions', response_class=PlainTextResponse)
def empirical_copilot_instructions():
    from .research_workflow import copilot_instructions
    return copilot_instructions()


@app.get('/api/empirical')
def empirical_result():
    from empirical import service as observed
    try:
        result = observed.read()
    except FileNotFoundError:
        return {'status': 'missing_data', 'classification': 'OBSERVED_PRIVATE',
                'message': 'Die realen Quellsnapshots sind auf diesem Server noch nicht eingerichtet.'}
    except (ValueError, OSError, KeyError):
        raise HTTPException(503, 'Empirische Daten- oder Hashprüfung fehlgeschlagen.') from None
    project = get_workspace().empirical_project()
    result.update(status='ready', ai=get_ai_config().status(),
                  history=get_workspace().context(project['id'])['messages'],
                  ai_budget=get_workspace().ai_state(project['id'])['budget'])
    return result


@app.post('/api/empirical/prepare')
def empirical_prepare(request: StrictRequest):
    from empirical import service as observed
    from empirical.restore import restore
    if not RUN_LOCK.acquire(blocking=False): raise HTTPException(409, 'Eine Berechnung läuft bereits.')
    try:
        if (observed.destination()/'manifest.json').exists(): return empirical_result()
        source = observed.source_directory()
        if not (source/'manifest.json').exists():
            status = restore(source)
            if status['status'] != 'ready': return status
        observed.build(source, observed.destination())
        return empirical_result()
    except (ValueError, OSError, KeyError):
        raise HTTPException(503, 'Quellprüfung oder feste Berechnung fehlgeschlagen. Keine synthetischen Ersatzdaten verwendet.') from None
    finally:
        RUN_LOCK.release()


@app.post('/api/empirical/agent-context')
def empirical_context(request: EmpiricalQuestion):
    from .empirical_chat import preview
    try:
        return preview(get_workspace(), request.message, request.model, get_ai_config())
    except (FileNotFoundError, ValueError, OSError, KeyError):
        raise HTTPException(503, 'Verifiziertes empirisches Ergebnis fehlt.') from None


@app.post('/api/empirical/messages')
def empirical_message(request: EmpiricalQuestion):
    from .empirical_chat import respond as explain
    if not AI_LOCK.acquire(blocking=False): raise HTTPException(409, 'Ein externer Dialog läuft bereits.')
    try:
        return explain(get_workspace(), request.message, request.model, request.consent,
                       request.context_sha256, get_ai_config())
    except (FileNotFoundError, ValueError, OSError, KeyError):
        raise HTTPException(503, 'Verifiziertes empirisches Ergebnis fehlt.') from None
    finally:
        AI_LOCK.release()


class OriginalObservationFile(StrictRequest):
    name: str = Field(min_length=1, max_length=120)
    content_base64: str = Field(min_length=1, max_length=8_000_000)


@app.post('/api/empirical/original-file')
def empirical_original_file(request: OriginalObservationFile):
    import base64
    from empirical.restore import install_original
    from empirical.service import source_directory
    if not RUN_LOCK.acquire(blocking=False): raise HTTPException(409, 'Eine Berechnung läuft bereits.')
    try:
        source = source_directory()
        raw = base64.b64decode(request.content_base64, validate=True)
        return install_original(source, request.name, raw)
    except (ValueError, OSError):
        raise HTTPException(422, 'Die Datei entspricht nicht dem geprüften Original-Snapshot; nichts ersetzt.') from None
    finally:
        RUN_LOCK.release()
