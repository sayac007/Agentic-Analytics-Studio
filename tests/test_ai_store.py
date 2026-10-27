"""Versioned AI state and conservative lifetime budgets; no provider calls or fitting."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from demo.workspace import AI_MODEL, AI_WORKSPACE_BUDGET, MissingRecord, SCHEMA, Workspace, WorkspaceError


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class AIStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='aas-ai-store-')
        self.root = Path(self.temporary.name) / 'workspace'
        self.store = Workspace(self.root)
        self.first, self.second = self.store.projects()

    def tearDown(self):
        self.store.close()
        self.temporary.cleanup()

    def turn(self, project=None, question='Explain the synthetic model limitations.'):
        project = project or self.first
        context = {'project_id': project['id'], 'classification': 'SYNTHETIC / NOT EMPIRICAL'}
        return self.store.start_ai_turn(project['id'], project['conversation_id'], AI_MODEL,
                                        context, digest(context), question)

    def call(self, turn, reserve=22_272_000):
        return self.store.reserve_ai_call(turn['project_id'], turn['id'], reserve, 'a' * 64)

    def complete(self, turn, text='Model interpretation, not verified measurements.'):
        call = self.call(turn)
        self.store.finish_ai_call(turn['project_id'], call['id'], 'completed',
                                  {'input_tokens': 1, 'output_tokens': 0}, 750, 'resp_fixture')
        return self.store.finish_ai_turn(turn['project_id'], turn['id'], 'completed', text)

    def test_v1_migration_preserves_all_original_records_and_bundle_bytes(self):
        self.store.close()
        legacy = Path(self.temporary.name) / 'legacy'
        legacy.mkdir()
        dbpath = legacy / 'workspace.sqlite3'
        run_id, execution_id = uuid4().hex, uuid4().hex
        example = Path(__file__).resolve().parents[1] / 'examples/task-01a'
        shutil.copytree(example, legacy / 'runs' / run_id)
        expected_bytes = {p.relative_to(example): p.read_bytes() for p in example.rglob('*') if p.is_file()}
        result = json.loads(expected_bytes[Path('safe/with-quarter.result.json')])
        manifest = json.loads(expected_bytes[Path('safe/with-quarter.manifest.json')])
        with sqlite3.connect(dbpath) as db:
            db.executescript(SCHEMA)
            Workspace._seed(db)
            project, conversation = db.execute('SELECT project_id,id FROM conversations ORDER BY rowid').fetchone()
            db.execute("INSERT INTO messages(project_id,conversation_id,role,kind,text,created_at) "
                       "VALUES(?,?,'user','user_statement','Preserve this private local note','2026-10-26')",
                       (project, conversation))
            db.execute("INSERT INTO decisions VALUES(?,?,?,'decision','approved','human_explicit_action',?,?)",
                       (uuid4().hex, project, 'Preserve this approval', '2026-10-26', '2026-10-26'))
            db.execute("INSERT INTO executions VALUES(?,?,?,'run_demo_analysis','{}','succeeded',NULL,NULL,?,?)",
                       (execution_id, project, conversation, '2026-10-26', '2026-10-26'))
            db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)', (run_id, project, execution_id,
                       'with-quarter', result['data_sha256'], hashlib.sha256(expected_bytes[Path('inventory.json')]).hexdigest(),
                       json.dumps(result['software']), json.dumps(manifest['estimation']), '2026-10-26'))
            tables = ('projects', 'conversations', 'messages', 'executions', 'runs', 'decisions')
            before = {table: db.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall() for table in tables}
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 1)
        migrated = Workspace(legacy)
        try:
            with sqlite3.connect(dbpath) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 2)
                self.assertEqual({table: db.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall()
                                  for table in tables}, before)
            migrated.get_run(project, run_id)
            self.assertEqual({p.relative_to(legacy / 'runs' / run_id): p.read_bytes()
                              for p in (legacy / 'runs' / run_id).rglob('*') if p.is_file()}, expected_bytes)
            self.assertEqual(migrated.ai_state(project)['budget']['charged_nano_usd'], 0)
        finally:
            migrated.close()

    def test_failed_migration_rolls_back_all_schema_changes(self):
        legacy = Path(self.temporary.name) / 'failed-migration'
        legacy.mkdir()
        dbpath = legacy / 'workspace.sqlite3'
        with sqlite3.connect(dbpath) as db:
            db.executescript(SCHEMA)
            Workspace._seed(db)
        from demo.workspace import AI_SCHEMA
        with patch('demo.workspace.AI_SCHEMA', AI_SCHEMA + '\nINSERT INTO missing_table VALUES(1);'):
            with self.assertRaises(WorkspaceError):
                Workspace(legacy)
        with sqlite3.connect(dbpath) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name LIKE 'ai_%'").fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM projects').fetchone()[0], 2)

    def test_context_digest_and_user_turn_are_atomic_and_inspectable(self):
        context = {'project': self.first['id'], 'note': 'Synthetische Größen, keine privaten Notizen'}
        with self.assertRaises(ValueError):
            self.store.start_ai_turn(self.first['id'], self.first['conversation_id'], AI_MODEL,
                                     context, '0' * 64, 'Question')
        with sqlite3.connect(self.store.database) as db:
            db.execute("CREATE TRIGGER reject_turn BEFORE INSERT ON ai_turns "
                       "BEGIN SELECT RAISE(ABORT,'test rollback'); END")
        with self.assertRaises(WorkspaceError):
            self.store.start_ai_turn(self.first['id'], self.first['conversation_id'], AI_MODEL,
                                     context, digest(context), 'Question')
        self.assertEqual(self.store.context(self.first['id'])['messages'], [])
        with sqlite3.connect(self.store.database) as db:
            db.execute('DROP TRIGGER reject_turn')
        turn = self.store.start_ai_turn(self.first['id'], self.first['conversation_id'], AI_MODEL,
                                        context, digest(context), 'Question')
        inspected = self.store.ai_turn(self.first['id'], turn['id'])
        self.assertEqual(inspected['context'], context)
        self.assertEqual(inspected['context_sha256'], digest(context))
        self.assertEqual(turn['user_message_id'], self.store.context(self.first['id'])['messages'][0]['id'])
        self.assertNotIn('context', self.store.ai_state(self.first['id'])['turns'][0])

    def test_known_usage_settles_charge_and_missing_or_failed_usage_keeps_reservation(self):
        turn = self.turn()
        first = self.call(turn)
        usage = {'input_tokens': 100, 'output_tokens': 20, 'total_tokens': 120,
                 'input_tokens_details': {'cached_tokens': 40}, 'output_tokens_details': {'reasoning_tokens': 0}}
        settled = self.store.finish_ai_call(self.first['id'], first['id'], 'completed', usage, 138_000, 'resp_usage')
        self.assertEqual(settled['charged_nano_usd'], 138_000)
        self.assertEqual(settled['usage'], usage)
        self.assertEqual(self.store.ai_state(self.first['id'])['budget']['unknown_nano_usd'], 0)
        missing = self.call(turn)
        missing = self.store.finish_ai_call(self.first['id'], missing['id'], 'completed', None, 0)
        self.assertEqual(missing['charged_nano_usd'], 22_272_000)
        self.assertIsNone(missing['estimated_cost_nano_usd'])
        failed = self.call(turn)
        failed = self.store.finish_ai_call(self.first['id'], failed['id'], 'failed', usage, 138_000)
        self.assertEqual(failed['charged_nano_usd'], 22_272_000)
        budget = self.store.ai_state(self.first['id'])['budget']
        self.assertEqual(budget['charged_nano_usd'], 138_000 + 2 * 22_272_000)
        self.assertEqual(budget['unknown_nano_usd'], 2 * 22_272_000)
        with self.assertRaises(WorkspaceError):
            self.store.finish_ai_call(self.first['id'], first['id'], 'completed', usage, 0)
        self.store.close()
        self.store = Workspace(self.root)
        self.assertEqual(self.store.ai_state(self.first['id'])['budget'], budget)
        self.assertEqual(self.store.ai_turn(self.first['id'], turn['id'])['status'], 'interrupted')

    def test_budget_reservation_is_atomic_across_threads_and_projects_and_survives_restart(self):
        turns = [self.turn(self.first if i % 2 else self.second) for i in range(12)]
        def reserve(turn):
            try:
                return self.call(turn, 100_000_000)
            except WorkspaceError:
                return None
        with ThreadPoolExecutor(max_workers=12) as pool:
            calls = list(pool.map(reserve, turns))
        self.assertEqual(sum(call is not None for call in calls), 10)
        budget = self.store.ai_state(self.first['id'])['budget']
        self.assertEqual(budget['charged_nano_usd'], AI_WORKSPACE_BUDGET)
        self.assertEqual(budget['unknown_nano_usd'], AI_WORKSPACE_BUDGET)
        self.assertEqual(budget['remaining_nano_usd'], 0)
        self.store.close()
        self.store = Workspace(self.root)
        self.assertEqual(self.store.ai_state(self.first['id'])['budget'], budget)
        for turn, call in zip(turns, calls):
            restored = self.store.ai_turn(turn['project_id'], turn['id'])
            self.assertEqual(restored['status'], 'interrupted')
            if call is not None:
                self.assertEqual(restored['calls'][0]['status'], 'unknown')
                self.assertEqual(restored['calls'][0]['charged_nano_usd'], 100_000_000)
        with self.assertRaises(WorkspaceError):
            self.call(self.turn(), 1)

    def test_per_turn_call_count_and_amount_guards_cannot_race(self):
        turn = self.turn()
        def reserve(_):
            try:
                return self.call(turn, 10_000_000)
            except WorkspaceError:
                return None
        with ThreadPoolExecutor(max_workers=8) as pool:
            calls = list(pool.map(reserve, range(8)))
        self.assertEqual(sum(call is not None for call in calls), 3)
        self.assertEqual(self.store.ai_turn(self.first['id'], turn['id'])['charged_nano_usd'], 30_000_000)
        another = self.turn()
        self.call(another, 90_000_000)
        with self.assertRaises(WorkspaceError):
            self.call(another, 20_000_000)
        for amount in (0, -1, True, 1.5, 1_000_000_001):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.call(self.turn(), amount)

    def test_foreign_ai_and_tool_identifiers_are_rejected(self):
        turn = self.turn()
        call = self.call(turn)
        foreign = self.store.start_execution(self.second['id'], self.second['conversation_id'], 'describe_dataset', {})
        self.store.finish_execution(self.second['id'], foreign['id'], 'succeeded')
        self.store.finish_ai_call(self.first['id'], call['id'], 'completed', {'input_tokens': 1, 'output_tokens': 0}, 750)
        operations = (
            lambda: self.store.start_ai_turn(self.second['id'], self.first['conversation_id'], AI_MODEL, {}, digest({}), 'Question'),
            lambda: self.store.reserve_ai_call(self.second['id'], turn['id'], 1, 'a' * 64),
            lambda: self.store.finish_ai_call(self.second['id'], call['id'], 'unknown'),
            lambda: self.store.finish_ai_turn(self.second['id'], turn['id'], 'failed'),
            lambda: self.store.ai_turn(self.second['id'], turn['id']),
            lambda: self.store.finish_ai_turn(self.first['id'], turn['id'], 'completed', 'Not verified',
                                             tool_execution_ids=[foreign['id']]),
        )
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(MissingRecord):
                operation()
        self.assertEqual(self.store.ai_history(self.second['id']), [])
        self.assertEqual(self.store.ai_state(self.second['id'])['turns'], [])

    def test_invalid_usage_and_terminal_transitions_cannot_refund_unknown_cost(self):
        turn = self.turn()
        call = self.call(turn)
        invalid_usage = (
            {'input_tokens': True, 'output_tokens': 0}, {'input_tokens': -1, 'output_tokens': 0},
            {'input_tokens': 1, 'output_tokens': 0, 'total_tokens': 0},
            {'input_tokens': 1, 'output_tokens': 0, 'input_tokens_details': {'cached_tokens': 2}},
            {'input_tokens': 1, 'output_tokens': 0, 'secret': 'must not be stored'},
        )
        for usage in invalid_usage:
            with self.subTest(usage=usage), self.assertRaises(ValueError):
                self.store.finish_ai_call(self.first['id'], call['id'], 'completed', usage, 0)
        with self.assertRaises(WorkspaceError):
            self.store.finish_ai_call(self.first['id'], call['id'], 'completed',
                                      {'input_tokens': 1, 'output_tokens': 0}, 22_272_001)
        with self.assertRaises(ValueError):
            self.store.finish_ai_call(self.first['id'], call['id'], 'unknown', provider_id='sk-not-a-response-id')
        with self.assertRaises(WorkspaceError):
            self.store.finish_ai_turn(self.first['id'], turn['id'], 'completed', 'Premature model text')
        self.assertEqual(self.store.ai_state(self.first['id'])['budget']['charged_nano_usd'], 22_272_000)
        failed = self.store.finish_ai_turn(self.first['id'], turn['id'], 'failed', error_code='provider_failed')
        self.assertEqual(failed['status'], 'failed')
        self.assertEqual(self.store.context(self.first['id'])['messages'][-1]['kind'], 'error')
        for operation in (lambda: self.call(turn),
                          lambda: self.store.finish_ai_turn(self.first['id'], turn['id'], 'completed', 'overwrite'),
                          lambda: self.store.finish_ai_call(self.first['id'], call['id'], 'completed',
                                                           {'input_tokens': 1, 'output_tokens': 0}, 750)):
            with self.assertRaises(WorkspaceError):
                operation()

    def test_completed_history_is_project_scoped_bounded_and_unverified_kind(self):
        completed = [self.complete(self.turn(question=f'Question {i}'), f'Interpretation {i}') for i in range(4)]
        self.complete(self.turn(self.second, question='Other project'), 'Other interpretation')
        self.store.finish_ai_turn(self.first['id'], self.turn()['id'], 'failed', error_code='provider_failed')
        history = self.store.ai_history(self.first['id'])
        self.assertEqual([turn['id'] for turn in history], [turn['id'] for turn in completed[-2:]])
        self.assertEqual(history[-1]['assistant_text'], 'Interpretation 3')
        self.assertEqual(self.store.ai_history(self.first['id'], limit=0), [])
        with self.assertRaises(ValueError):
            self.store.ai_history(self.first['id'], limit=3)
        messages = self.store.context(self.first['id'])['messages']
        self.assertEqual(sum(message['kind'] == 'llm_response' for message in messages), 4)
        self.assertFalse(any(message['kind'] == 'tool_result' for message in messages))
        safe = json.dumps(self.store.ai_state(self.first['id']))
        self.assertNotIn('Interpretation 3', safe)
        self.assertNotIn('Question 3', safe)
        self.assertNotIn('context_json', safe)

    def test_provider_failure_does_not_undo_actual_successful_tool_result(self):
        turn = self.turn()
        with self.assertRaises(WorkspaceError):
            self.store.finish_ai_turn(self.first['id'], turn['id'], 'completed', 'No provider call occurred')
        execution = self.store.start_execution(self.first['id'], self.first['conversation_id'],
                                               'run_demo_analysis', {})
        run_id = uuid4().hex
        shutil.copytree(Path(__file__).resolve().parents[1] / 'examples/task-01a', self.store.bundle_path(run_id))
        self.store.complete_run(self.first['id'], execution['id'], run_id, 'with-quarter')
        call = self.call(turn)
        self.store.finish_ai_call(self.first['id'], call['id'], 'unknown')
        failed = self.store.finish_ai_turn(self.first['id'], turn['id'], 'failed', error_code='provider_timeout',
                                           tool_execution_ids=[execution['id']])
        self.assertEqual(failed['tool_execution_ids'], [execution['id']])
        self.assertEqual(self.store.context(self.first['id'])['executions'][0]['status'], 'succeeded')
        self.assertEqual(self.store.get_run(self.first['id'], run_id)['id'], run_id)
        self.assertEqual(self.store.ai_state(self.first['id'])['budget']['charged_nano_usd'], 22_272_000)
        self.assertEqual(self.store.ai_history(self.first['id']), [])


if __name__ == '__main__':
    unittest.main()
