"""Single-owner SQLite state and original synthetic bundles, separate from the estimator."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
from uuid import uuid4

from studio.export import verify_export


class WorkspaceError(RuntimeError):
    """The workspace cannot safely serve durable state."""


class MissingRecord(KeyError):
    """The requested record does not belong to this project."""


class AIBudgetError(WorkspaceError):
    """A durable request/cost guard denied dispatch before any network call."""


DEFAULT_PROJECT = 'synthetic-quarter'
TOOLS = {'list_datasets', 'describe_dataset', 'run_demo_analysis', 'compare_runs',
         'summarize_diagnostics', 'resume_workspace'}
LIMITS = {'messages': 40, 'runs': 20, 'executions': 20, 'decisions': 20}
TABLES = {'projects', 'conversations', 'messages', 'executions', 'runs', 'decisions'}
AI_TABLES = {'ai_turns', 'ai_calls'}
AI_MODEL = 'gpt-5.4-mini-2026-03-17'
AI_WORKSPACE_BUDGET = 1_000_000_000
AI_TURN_BUDGET = 100_000_000
AI_MAX_CALLS = 3
SCHEMA = """
CREATE TABLE projects (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, dataset_id TEXT NOT NULL,
 frequency TEXT NOT NULL, target TEXT NOT NULL, default_model TEXT NOT NULL,
 provenance_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE conversations (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL UNIQUE REFERENCES projects(id),
 created_at TEXT NOT NULL, UNIQUE(id, project_id));
CREATE TABLE executions (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 conversation_id TEXT NOT NULL, tool TEXT NOT NULL, arguments_json TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('running','succeeded','failed','interrupted')),
 output_ref_json TEXT, error_code TEXT, started_at TEXT NOT NULL, completed_at TEXT,
 UNIQUE(id, project_id),
 FOREIGN KEY(conversation_id, project_id) REFERENCES conversations(id, project_id));
CREATE TABLE messages (
 id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 conversation_id TEXT NOT NULL, role TEXT NOT NULL, kind TEXT NOT NULL,
 text TEXT NOT NULL, execution_id TEXT, created_at TEXT NOT NULL,
 FOREIGN KEY(conversation_id, project_id) REFERENCES conversations(id, project_id),
 FOREIGN KEY(execution_id, project_id) REFERENCES executions(id, project_id));
CREATE TABLE runs (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 execution_id TEXT NOT NULL UNIQUE, model TEXT NOT NULL, data_sha256 TEXT NOT NULL,
 inventory_sha256 TEXT NOT NULL, software_json TEXT NOT NULL,
 configuration_json TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY(execution_id, project_id) REFERENCES executions(id, project_id));
CREATE TABLE decisions (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 text TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('decision','development_workorder')),
 status TEXT NOT NULL CHECK(status IN ('proposed','approved')),
 approval_source TEXT, created_at TEXT NOT NULL, approved_at TEXT);
CREATE INDEX messages_project ON messages(project_id, id DESC);
CREATE INDEX runs_project ON runs(project_id, created_at DESC);
CREATE INDEX executions_project ON executions(project_id, started_at DESC);
CREATE INDEX decisions_project ON decisions(project_id, created_at DESC);
PRAGMA user_version=1;
"""
AI_SCHEMA = """
CREATE TABLE ai_turns (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 conversation_id TEXT NOT NULL, model TEXT NOT NULL,
 context_json TEXT NOT NULL, context_sha256 TEXT NOT NULL,
 user_message_id INTEGER NOT NULL REFERENCES messages(id),
 assistant_message_id INTEGER REFERENCES messages(id),
 status TEXT NOT NULL CHECK(status IN ('running','completed','failed','interrupted')),
 error_code TEXT, tool_execution_ids_json TEXT NOT NULL,
 created_at TEXT NOT NULL, completed_at TEXT, UNIQUE(id,project_id),
 FOREIGN KEY(conversation_id,project_id) REFERENCES conversations(id,project_id));
CREATE TABLE ai_calls (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 turn_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 1 AND 3),
 request_sha256 TEXT NOT NULL, reserved_nano_usd INTEGER NOT NULL CHECK(reserved_nano_usd>0),
 charged_nano_usd INTEGER NOT NULL CHECK(charged_nano_usd>=0),
 estimated_cost_nano_usd INTEGER, usage_json TEXT, provider_id TEXT,
 status TEXT NOT NULL CHECK(status IN ('pending','running','completed','failed','unknown')),
 created_at TEXT NOT NULL, completed_at TEXT,
 FOREIGN KEY(turn_id,project_id) REFERENCES ai_turns(id,project_id), UNIQUE(turn_id,ordinal));
CREATE INDEX ai_turns_project ON ai_turns(project_id,created_at DESC);
CREATE INDEX ai_calls_turn ON ai_calls(turn_id,ordinal);
PRAGMA user_version=2;
"""


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{32}', value):
        raise MissingRecord('Record not found in this project')
    return value


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 12000:
        raise ValueError('Text must contain between 1 and 12000 characters')
    return value


def _no_symlink(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise WorkspaceError('Symlink workspace entries are not supported')


def _digest(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Expected a SHA-256 digest')
    return value


def _amount(value, positive=False):
    if type(value) is not int or value < (1 if positive else 0) or value > AI_WORKSPACE_BUDGET:
        raise ValueError('Expected a bounded nonnegative integer amount')
    return value


def _usage(value):
    if not isinstance(value, dict) or not {'input_tokens', 'output_tokens'} <= set(value):
        raise ValueError('Expected structured token usage')
    if set(value) - {'input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_details', 'output_tokens_details'}:
        raise ValueError('Unexpected token usage fields')
    for key in ('input_tokens', 'output_tokens', 'total_tokens'):
        if key in value and (type(value[key]) is not int or not 0 <= value[key] <= 10_000_000):
            raise ValueError('Token counts must be bounded nonnegative integers')
    if 'total_tokens' in value and value['total_tokens'] != value['input_tokens'] + value['output_tokens']:
        raise ValueError('Total token count does not match input plus output')
    for field, token, maximum in (('input_tokens_details', 'cached_tokens', value['input_tokens']),
                                   ('output_tokens_details', 'reasoning_tokens', value['output_tokens'])):
        if field in value:
            details = value[field]
            if (not isinstance(details, dict) or set(details) != {token} or type(details[token]) is not int
                    or not 0 <= details[token] <= maximum):
                raise ValueError('Invalid detailed token usage')
    return value


class Workspace:
    def __init__(self, root):
        self.root = Path(os.path.abspath(root))
        self._lock_fd = None
        self._closed = False
        try:
            _no_symlink(self.root)
            self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.root.chmod(0o700)
            self.run_root = self.root / 'runs'
            _no_symlink(self.run_root)
            self.run_root.mkdir(exist_ok=True, mode=0o700)
            self.run_root.chmod(0o700)
            self._acquire_lock()
            self.database = self.root / 'workspace.sqlite3'
            _no_symlink(self.database)
            existed = self.database.exists()
            descriptor = os.open(self.database, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise WorkspaceError('Workspace database must be a regular file')
                os.fchmod(descriptor, 0o600)
            finally:
                os.close(descriptor)
            with self._connection() as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise WorkspaceError('Workspace database integrity check failed')
                version = db.execute('PRAGMA user_version').fetchone()[0]
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if existed and db.execute('PRAGMA foreign_key_check').fetchone() is not None:
                    raise WorkspaceError('Workspace relationships failed validation')
                if not existed and version == 0 and not tables:
                    db.executescript('BEGIN IMMEDIATE;\n' + SCHEMA + AI_SCHEMA + '\nCOMMIT;')
                elif version == 1 and tables == TABLES:
                    # Additive migration: existing rows, IDs, approvals and bundles stay unchanged.
                    db.executescript('BEGIN IMMEDIATE;\n' + AI_SCHEMA + '\nCOMMIT;')
                elif version != 2 or tables != TABLES | AI_TABLES:
                    # An existing version-0 file can be an interrupted initialization.
                    # Refuse it, including an empty/partial schema, rather than reset it.
                    raise WorkspaceError('Unsupported workspace schema; no state was reset')
                if db.execute('PRAGMA foreign_key_check').fetchone() is not None:
                    raise WorkspaceError('Workspace relationships failed validation')
                self._seed(db)
                db.execute("UPDATE executions SET status='interrupted', error_code='process_interrupted', "
                           "completed_at=? WHERE status='running'", (_now(),))
                db.execute("UPDATE ai_calls SET status='unknown', completed_at=? "
                           "WHERE status IN ('pending','running')", (_now(),))
                db.execute("UPDATE ai_turns SET status='interrupted', error_code='process_interrupted', "
                           "completed_at=? WHERE status='running'", (_now(),))
        except BaseException:
            self.close()
            raise

    def _acquire_lock(self):
        path = self.root / '.lock'
        _no_symlink(path)
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise WorkspaceError('Workspace lock must be a regular file')
            os.fchmod(descriptor, 0o600)
            if os.name == 'nt':
                import msvcrt
                if not os.fstat(descriptor).st_size:
                    os.write(descriptor, b'0')
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(descriptor)
            raise WorkspaceError('Workspace is already in use; use one process and worker') from exc
        except BaseException:
            os.close(descriptor)
            raise
        self._lock_fd = descriptor

    def close(self):
        if self._lock_fd is not None:
            os.close(self._lock_fd)  # Releases the process lock, including after exceptions.
            self._lock_fd = None
        self._closed = True

    @contextmanager
    def _connection(self):
        if self._closed:
            raise WorkspaceError('Workspace is closed')
        _no_symlink(self.database)
        for suffix in ('-journal', '-wal', '-shm'):
            _no_symlink(Path(str(self.database) + suffix))
        connection = None
        try:
            connection = sqlite3.connect(self.database, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA foreign_keys=ON')
            with connection:
                yield connection
        except (sqlite3.Error, json.JSONDecodeError) as exc:
            raise WorkspaceError('Workspace database could not be read or updated') from exc
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def _seed(db):
        provenance = _json({'class': 'synthetic', 'source_or_generator': 'synthetic_development_reference_v1',
                            'seed': 42, 'months': 72, 'train_months': 60, 'holdout_months': 12,
                            'rights': 'Project-generated synthetic development data; no external observations',
                            'same_dataset_in_both_projects': True})
        for identity, name, model in (
                (DEFAULT_PROJECT, 'Synthetic MMM · mit Quartalsende', 'with-quarter'),
                ('synthetic-no-quarter', 'Synthetic MMM · ohne Quartalsende', 'without-quarter')):
            db.execute('INSERT OR IGNORE INTO projects VALUES (?,?,?,?,?,?,?,?)',
                       (identity, name, 'synthetic-mmm', 'month', 'semi_synthetic_outcome', model, provenance, _now()))
            db.execute('INSERT OR IGNORE INTO conversations VALUES (?,?,?)', (uuid4().hex, identity, _now()))

    @staticmethod
    def _project(db, project_id):
        row = db.execute('SELECT p.*, c.id AS conversation_id FROM projects p JOIN conversations c '
                         'ON c.project_id=p.id WHERE p.id=?', (project_id,)).fetchone()
        if row is None:
            raise MissingRecord('Project not found')
        value = dict(row)
        value['provenance'] = json.loads(value.pop('provenance_json'))
        return value

    @staticmethod
    def _conversation(db, project_id, conversation_id):
        if db.execute('SELECT id FROM conversations WHERE project_id=? AND id=?',
                      (project_id, conversation_id)).fetchone() is None:
            raise MissingRecord('Conversation not found in this project')

    def projects(self):
        with self._connection() as db:
            ids = [r[0] for r in db.execute('SELECT id FROM projects ORDER BY created_at,id')]
            return [self._project(db, identity) for identity in ids]

    def project(self, project_id):
        with self._connection() as db:
            return self._project(db, project_id)

    def empirical_project(self):
        """Create the separate observed-data conversation without relabeling old runs."""
        identity = 'tesla-observed'
        with self._connection() as db:
            db.execute('INSERT OR IGNORE INTO projects VALUES (?,?,?,?,?,?,?,?)',
                       (identity, 'Tesla Deutschland · beobachtete Entwicklung', 'observed-registrations',
                        'month', 'monthly_change_log1p_registrations', 'macro',
                        _json({'class': 'observed', 'scope': 'private_retrospective_exploratory',
                               'synthetic_inputs': False}), _now()))
            db.execute('INSERT OR IGNORE INTO conversations VALUES (?,?,?)', (uuid4().hex, identity, _now()))
            return self._project(db, identity)

    def research_brief(self, value=None):
        """Persist descriptive task metadata; never rewrite empirical artifacts or model config."""
        from .research_workflow import DEFAULT_BRIEF, check_brief
        project = self.empirical_project()
        with self._connection() as db:
            provenance = json.loads(db.execute('SELECT provenance_json FROM projects WHERE id=?', (project['id'],)).fetchone()[0])
            if value is not None:
                check_brief(value)
                provenance['research_brief'] = {'brief': value, 'updated_at': _now()}
                db.execute('UPDATE projects SET provenance_json=? WHERE id=?', (_json(provenance), project['id']))
            record = provenance.get('research_brief', {'brief': DEFAULT_BRIEF, 'updated_at': None})
            check_brief(record['brief'])
            return record

    @staticmethod
    def _execution_value(row):
        value = dict(row)
        value['arguments'] = json.loads(value.pop('arguments_json'))
        raw = value.pop('output_ref_json')
        value['output_ref'] = None if raw is None else json.loads(raw)
        return value

    @staticmethod
    def _run_value(row):
        value = dict(row)
        value['software'] = json.loads(value.pop('software_json'))
        value['configuration'] = json.loads(value.pop('configuration_json'))
        value['status'] = 'validated_at_creation'
        value['integrity_check'] = 'required_on_open'
        return value

    def context(self, project_id):
        with self._connection() as db:
            project = self._project(db, project_id)
            messages = [dict(r) for r in db.execute('SELECT * FROM messages WHERE project_id=? '
                        'ORDER BY id DESC LIMIT 40', (project_id,))][::-1]
            runs = [self._run_value(r) for r in db.execute('SELECT * FROM runs WHERE project_id=? '
                    'ORDER BY created_at DESC,id DESC LIMIT 20', (project_id,))]
            executions = [self._execution_value(r) for r in db.execute('SELECT * FROM executions WHERE project_id=? '
                          'ORDER BY started_at DESC,id DESC LIMIT 20', (project_id,))]
            decisions = [dict(r) for r in db.execute('SELECT * FROM decisions WHERE project_id=? '
                         'ORDER BY created_at DESC,id DESC LIMIT 20', (project_id,))]
            counts = {name: db.execute(f'SELECT COUNT(*) FROM {name} WHERE project_id=?',
                      (project_id,)).fetchone()[0] for name in LIMITS}
            return {'project': project, 'conversation_id': project['conversation_id'],
                    'messages': messages, 'runs': runs, 'executions': executions, 'decisions': decisions,
                    'limits': dict(LIMITS), 'counts': counts,
                    'truncated': {name: counts[name] > limit for name, limit in LIMITS.items()}}

    def add_message(self, project_id, conversation_id, role, kind, text, execution_id=None):
        if (role == 'user' and kind != 'user_statement') or (role == 'assistant' and kind not in
                ('acknowledgement', 'tool_result', 'error', 'context', 'llm_response')) or role not in ('user', 'assistant'):
            raise ValueError('Invalid message role or evidence kind')
        _text(text)
        with self._connection() as db:
            self._conversation(db, project_id, conversation_id)
            if execution_id is not None and db.execute('SELECT id FROM executions WHERE id=? AND project_id=? '
                    'AND conversation_id=?', (execution_id, project_id, conversation_id)).fetchone() is None:
                raise MissingRecord('Execution not found in this conversation')
            cursor = db.execute('INSERT INTO messages(project_id,conversation_id,role,kind,text,execution_id,created_at) '
                                'VALUES(?,?,?,?,?,?,?)', (project_id, conversation_id, role, kind, text, execution_id, _now()))
            return dict(db.execute('SELECT * FROM messages WHERE id=?', (cursor.lastrowid,)).fetchone())

    def start_execution(self, project_id, conversation_id, tool, arguments):
        if tool not in TOOLS or not isinstance(arguments, dict):
            raise ValueError('Tool is not allowlisted')
        identity = uuid4().hex
        with self._connection() as db:
            self._conversation(db, project_id, conversation_id)
            db.execute('INSERT INTO executions(id,project_id,conversation_id,tool,arguments_json,status,started_at) '
                       "VALUES(?,?,?,?,?,'running',?)", (identity, project_id, conversation_id, tool, _json(arguments), _now()))
            return self._execution_value(db.execute('SELECT * FROM executions WHERE id=?', (identity,)).fetchone())

    def finish_execution(self, project_id, execution_id, status, output_ref=None, error_code=None):
        if status not in ('succeeded', 'failed'):
            raise ValueError('Invalid completion status')
        if error_code is not None and (not isinstance(error_code, str) or not re.fullmatch(r'[a-z_]{1,80}', error_code)):
            raise ValueError('Use a sanitized error code')
        with self._connection() as db:
            row = db.execute('SELECT * FROM executions WHERE id=? AND project_id=?',
                             (execution_id, project_id)).fetchone()
            if row is None:
                raise MissingRecord('Execution not found in this project')
            if row['status'] != 'running':
                raise WorkspaceError('A completed execution cannot be overwritten')
            db.execute('UPDATE executions SET status=?, output_ref_json=?, error_code=?, completed_at=? WHERE id=?',
                       (status, None if output_ref is None else _json(output_ref), error_code, _now(), execution_id))
            return self._execution_value(db.execute('SELECT * FROM executions WHERE id=?', (execution_id,)).fetchone())

    def bundle_path(self, run_id):
        _identifier(run_id)
        path = self.run_root / run_id
        _no_symlink(path)
        return path

    def _verify(self, run_id, expected_inventory=None):
        path = self.bundle_path(run_id)
        try:
            if not path.is_dir() or any(p.is_symlink() for p in path.rglob('*')):
                raise WorkspaceError('Stored artifact bundle is unavailable or unsafe')
            raw = (path / 'inventory.json').read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if expected_inventory is not None and digest != expected_inventory:
                raise WorkspaceError('Stored artifact inventory no longer matches its recorded hash')
            verify_export(path)  # Full contracts, byte hashes, exact membership and synthetic provenance.
            return path, digest
        except WorkspaceError:
            raise
        except Exception as exc:
            raise WorkspaceError('Stored artifact bundle failed validation') from exc

    def complete_run(self, project_id, execution_id, run_id, model):
        if model not in ('with-quarter', 'without-quarter'):
            raise ValueError('Unknown predefined model')
        path, digest = self._verify(run_id)
        result = json.loads((path / f'safe/{model}.result.json').read_text())
        manifest = json.loads((path / f'safe/{model}.manifest.json').read_text())
        with self._connection() as db:
            row = db.execute('SELECT * FROM executions WHERE id=? AND project_id=?',
                             (execution_id, project_id)).fetchone()
            if row is None:
                raise MissingRecord('Execution not found in this project')
            if row['tool'] != 'run_demo_analysis' or row['status'] != 'running':
                raise WorkspaceError('Only a running analysis execution can publish a result')
            db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)', (run_id, project_id, execution_id, model,
                       result['data_sha256'], digest, _json(result['software']), _json(manifest['estimation']), _now()))
            db.execute("UPDATE executions SET status='succeeded', output_ref_json=?, completed_at=? WHERE id=?",
                       (_json({'run_id': run_id, 'inventory_sha256': digest}), _now(), execution_id))
            return self._run_value(db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone())

    def get_run(self, project_id, run_id):
        _identifier(run_id)
        with self._connection() as db:
            row = db.execute('SELECT * FROM runs WHERE id=? AND project_id=?', (run_id, project_id)).fetchone()
            if row is None:
                raise MissingRecord('Run not found in this project')
            value = self._run_value(row)
        path, _ = self._verify(run_id, value['inventory_sha256'])
        value['bundle_path'] = str(path)  # Internal only: never serialize this field into HTTP/context.
        return value

    def runs(self, project_id):
        with self._connection() as db:
            self._project(db, project_id)
            return [self._run_value(r) for r in db.execute('SELECT * FROM runs WHERE project_id=? '
                    'ORDER BY created_at DESC,id DESC LIMIT 20', (project_id,))]

    def propose(self, project_id, text, kind='decision'):
        _text(text)
        if kind not in ('decision', 'development_workorder'):
            raise ValueError('Unknown proposal kind')
        identity = uuid4().hex
        with self._connection() as db:
            self._project(db, project_id)
            db.execute("INSERT INTO decisions VALUES(?,?,?,?, 'proposed',NULL,?,NULL)",
                       (identity, project_id, text, kind, _now()))
            return dict(db.execute('SELECT * FROM decisions WHERE id=?', (identity,)).fetchone())

    def approve(self, project_id, decision_id):
        _identifier(decision_id)
        with self._connection() as db:
            row = db.execute('SELECT * FROM decisions WHERE id=? AND project_id=?',
                             (decision_id, project_id)).fetchone()
            if row is None:
                raise MissingRecord('Decision not found in this project')
            if row['status'] == 'proposed':
                db.execute("UPDATE decisions SET status='approved', approval_source='human_explicit_action', "
                           'approved_at=? WHERE id=?', (_now(), decision_id))
            return dict(db.execute('SELECT * FROM decisions WHERE id=?', (decision_id,)).fetchone())

    @staticmethod
    def _ai_turn(db, project_id, turn_id):
        _identifier(turn_id)
        row = db.execute('SELECT * FROM ai_turns WHERE id=? AND project_id=?', (turn_id, project_id)).fetchone()
        if row is None:
            raise MissingRecord('AI turn not found in this project')
        return row

    @staticmethod
    def _ai_call_value(row):
        value = dict(row)
        usage = value.pop('usage_json')
        value['usage'] = None if usage is None else json.loads(usage)
        return value

    def _ai_turn_value(self, db, row, include_context=False):
        value = dict(row)
        raw_context = value.pop('context_json')
        if include_context:
            value['context'] = json.loads(raw_context)
        value['tool_execution_ids'] = json.loads(value.pop('tool_execution_ids_json'))
        calls = [self._ai_call_value(r) for r in db.execute('SELECT * FROM ai_calls WHERE turn_id=? '
                 'AND project_id=? ORDER BY ordinal', (value['id'], value['project_id']))]
        value['calls'] = calls
        value['charged_nano_usd'] = sum(call['charged_nano_usd'] for call in calls)
        value['usage'] = {
            'input_tokens': sum(call['usage']['input_tokens'] for call in calls if call['usage'] is not None),
            'output_tokens': sum(call['usage']['output_tokens'] for call in calls if call['usage'] is not None),
            'reported_calls': sum(call['usage'] is not None for call in calls), 'request_count': len(calls),
        }
        return value

    @staticmethod
    def _ai_budget(db):
        row = db.execute("SELECT COALESCE(SUM(charged_nano_usd),0) AS charged, "
                         "COALESCE(SUM(CASE WHEN status!='completed' OR usage_json IS NULL "
                         "OR estimated_cost_nano_usd IS NULL THEN charged_nano_usd ELSE 0 END),0) AS unknown "
                         'FROM ai_calls').fetchone()
        return {'limit_nano_usd': AI_WORKSPACE_BUDGET, 'charged_nano_usd': row['charged'],
                'unknown_nano_usd': row['unknown'],
                'remaining_nano_usd': max(0, AI_WORKSPACE_BUDGET - row['charged'])}

    def start_ai_turn(self, project_id, conversation_id, model, context, context_sha256, message):
        if model != AI_MODEL:
            raise ValueError('Only the configured model snapshot is supported')
        if not isinstance(context, dict):
            raise ValueError('AI context must be a structured projection')
        canonical = json.dumps(context, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
        if len(canonical.encode('utf-8')) > 65536:
            raise ValueError('AI context exceeds the storage bound')
        if hashlib.sha256(canonical.encode('utf-8')).hexdigest() != _digest(context_sha256):
            raise ValueError('AI context does not match its confirmed digest')
        _text(message)
        identity, timestamp = uuid4().hex, _now()
        with self._connection() as db:
            db.execute('BEGIN IMMEDIATE')
            self._conversation(db, project_id, conversation_id)
            cursor = db.execute('INSERT INTO messages(project_id,conversation_id,role,kind,text,created_at) '
                                "VALUES(?,?,'user','user_statement',?,?)",
                                (project_id, conversation_id, message, timestamp))
            db.execute('INSERT INTO ai_turns VALUES(?,?,?,?,?,?,?,NULL,\'running\',NULL,?,?,NULL)',
                       (identity, project_id, conversation_id, model, canonical, context_sha256,
                        cursor.lastrowid, '[]', timestamp))
            return self._ai_turn_value(db, self._ai_turn(db, project_id, identity))

    def reserve_ai_call(self, project_id, turn_id, reserved_nano_usd, request_sha256):
        _amount(reserved_nano_usd, positive=True)
        _digest(request_sha256)
        identity = uuid4().hex
        with self._connection() as db:
            # Serialize the read/check/reserve operation across all request threads.
            db.execute('BEGIN IMMEDIATE')
            turn = self._ai_turn(db, project_id, turn_id)
            if turn['status'] != 'running':
                raise WorkspaceError('An inactive AI turn cannot send another request')
            used = db.execute('SELECT COUNT(*) AS count,COALESCE(SUM(charged_nano_usd),0) AS charged '
                              'FROM ai_calls WHERE turn_id=?', (turn_id,)).fetchone()
            if used['count'] >= AI_MAX_CALLS or used['charged'] + reserved_nano_usd > AI_TURN_BUDGET:
                raise AIBudgetError('AI turn request or budget limit reached')
            if self._ai_budget(db)['charged_nano_usd'] + reserved_nano_usd > AI_WORKSPACE_BUDGET:
                raise AIBudgetError('Workspace AI lifetime budget reached')
            db.execute('INSERT INTO ai_calls VALUES(?,?,?,?,?,?,?,NULL,NULL,NULL,\'pending\',?,NULL)',
                       (identity, project_id, turn_id, used['count'] + 1, request_sha256,
                        reserved_nano_usd, reserved_nano_usd, _now()))
            return self._ai_call_value(db.execute('SELECT * FROM ai_calls WHERE id=?', (identity,)).fetchone())

    def finish_ai_call(self, project_id, call_id, status, usage=None, estimated_cost_nano_usd=None, provider_id=None):
        _identifier(call_id)
        if status not in ('completed', 'failed', 'unknown'):
            raise ValueError('Invalid AI call status')
        if usage is not None:
            _usage(usage)
        if estimated_cost_nano_usd is not None:
            _amount(estimated_cost_nano_usd)
        if provider_id is not None and (not isinstance(provider_id, str) or
                not re.fullmatch(r'resp_[A-Za-z0-9_-]{1,180}', provider_id)):
            raise ValueError('Invalid provider response identifier')
        with self._connection() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM ai_calls WHERE id=? AND project_id=?', (call_id, project_id)).fetchone()
            if row is None:
                raise MissingRecord('AI call not found in this project')
            if row['status'] not in ('pending', 'running'):
                raise WorkspaceError('A completed AI request cannot be overwritten')
            if self._ai_turn(db, project_id, row['turn_id'])['status'] != 'running':
                raise WorkspaceError('An inactive AI turn cannot settle a request')
            if estimated_cost_nano_usd is not None and estimated_cost_nano_usd > row['reserved_nano_usd']:
                raise WorkspaceError('Reported AI cost exceeds its reserved guard')
            known = status == 'completed' and usage is not None and estimated_cost_nano_usd is not None
            charged = estimated_cost_nano_usd if known else row['reserved_nano_usd']
            db.execute('UPDATE ai_calls SET status=?,usage_json=?,estimated_cost_nano_usd=?,provider_id=?, '
                       'charged_nano_usd=?,completed_at=? WHERE id=?',
                       (status, None if usage is None else _json(usage), estimated_cost_nano_usd if known else None,
                        provider_id, charged, _now(), call_id))
            return self._ai_call_value(db.execute('SELECT * FROM ai_calls WHERE id=?', (call_id,)).fetchone())

    def finish_ai_turn(self, project_id, turn_id, status, text=None, error_code=None, tool_execution_ids=()):
        if status not in ('completed', 'failed'):
            raise ValueError('Invalid AI turn status')
        if error_code is not None and (not isinstance(error_code, str) or not re.fullmatch(r'[a-z_]{1,80}', error_code)):
            raise ValueError('Use a sanitized AI error code')
        if not isinstance(tool_execution_ids, (list, tuple)) or len(tool_execution_ids) > 2:
            raise ValueError('At most two tool execution references are permitted')
        if len(set(tool_execution_ids)) != len(tool_execution_ids):
            raise ValueError('Duplicate tool execution reference')
        for execution_id in tool_execution_ids:
            _identifier(execution_id)
        if status == 'completed':
            _text(text)
        elif text is None:
            text = 'Die externe Unterhaltung wurde nicht abgeschlossen. Keine erfolgreiche LLM-Antwort gespeichert.'
        _text(text)
        with self._connection() as db:
            db.execute('BEGIN IMMEDIATE')
            turn = self._ai_turn(db, project_id, turn_id)
            if turn['status'] != 'running':
                raise WorkspaceError('A completed AI turn cannot be overwritten')
            calls = db.execute('SELECT status FROM ai_calls WHERE turn_id=?', (turn_id,)).fetchall()
            if status == 'completed' and (not any(call['status'] == 'completed' for call in calls)
                    or any(call['status'] in ('pending', 'running') for call in calls)):
                raise WorkspaceError('An AI answer requires a completed provider request and no pending requests')
            for execution_id in tool_execution_ids:
                execution = db.execute('SELECT * FROM executions WHERE id=? AND project_id=? AND conversation_id=?',
                                       (execution_id, project_id, turn['conversation_id'])).fetchone()
                if execution is None:
                    raise MissingRecord('Tool execution not found in this AI project')
                if status == 'completed' and execution['status'] == 'running':
                    raise WorkspaceError('An AI answer cannot claim an unfinished tool execution')
            timestamp = _now()
            cursor = db.execute('INSERT INTO messages(project_id,conversation_id,role,kind,text,created_at) '
                                "VALUES(?,?,'assistant',?,?,?)", (project_id, turn['conversation_id'],
                                'llm_response' if status == 'completed' else 'error', text, timestamp))
            db.execute('UPDATE ai_turns SET status=?,assistant_message_id=?,error_code=?, '
                       'tool_execution_ids_json=?,completed_at=? WHERE id=?',
                       (status, cursor.lastrowid, error_code, _json(list(tool_execution_ids)), timestamp, turn_id))
            return self._ai_turn_value(db, self._ai_turn(db, project_id, turn_id))

    def ai_history(self, project_id, limit=2):
        if type(limit) is not int or not 0 <= limit <= 2:
            raise ValueError('At most two completed AI turns may be selected')
        with self._connection() as db:
            self._project(db, project_id)
            rows = db.execute('SELECT t.id,u.text AS user_text,a.text AS assistant_text FROM ai_turns t '
                              'JOIN messages u ON u.id=t.user_message_id AND u.project_id=t.project_id '
                              'JOIN messages a ON a.id=t.assistant_message_id AND a.project_id=t.project_id '
                              "WHERE t.project_id=? AND t.status='completed' "
                              'ORDER BY t.created_at DESC,t.id DESC LIMIT ?', (project_id, limit)).fetchall()
            return [dict(row) for row in reversed(rows)]

    def ai_state(self, project_id):
        with self._connection() as db:
            self._project(db, project_id)
            turns = [self._ai_turn_value(db, row) for row in db.execute('SELECT * FROM ai_turns WHERE project_id=? '
                     'ORDER BY created_at DESC,id DESC LIMIT 10', (project_id,))]
            return {'turns': turns, 'budget': self._ai_budget(db)}

    def ai_turn(self, project_id, turn_id):
        with self._connection() as db:
            return self._ai_turn_value(db, self._ai_turn(db, project_id, turn_id), include_context=True)
