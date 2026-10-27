"""Durable state, project ownership and original-artifact checks using temporary workspaces."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from demo.workspace import DEFAULT_PROJECT, MissingRecord, Workspace, WorkspaceError


class WorkspaceStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='aas-store-test-')
        self.root = Path(self.temporary.name) / 'workspace'
        self.store = Workspace(self.root)
        self.first, self.second = self.store.projects()

    def tearDown(self):
        self.store.close()
        self.temporary.cleanup()

    def execution(self, project=None, tool='describe_dataset'):
        project = project or self.first
        return self.store.start_execution(project['id'], project['conversation_id'], tool, {})

    def test_project_messages_decisions_and_execution_survive_restart(self):
        self.assertEqual(self.first['id'], DEFAULT_PROJECT)
        self.assertEqual(self.first['dataset_id'], self.second['dataset_id'])
        self.assertNotEqual(self.first['default_model'], self.second['default_model'])
        self.assertTrue(self.first['provenance']['same_dataset_in_both_projects'])
        message = self.store.add_message(self.first['id'], self.first['conversation_id'],
                                        'user', 'user_statement', 'Investigate weak recovery <script>not HTML</script>')
        proposal = self.store.propose(self.first['id'], 'Prepare external work order', 'development_workorder')
        self.assertEqual(proposal['status'], 'proposed')
        execution = self.execution()
        self.store.finish_execution(self.first['id'], execution['id'], 'succeeded', {'preview_months': 12})
        self.store.close()
        self.store = Workspace(self.root)
        context = self.store.context(self.first['id'])
        self.assertEqual(context['messages'], [message])
        self.assertEqual(context['decisions'][0], proposal)
        self.assertEqual(context['executions'][0]['status'], 'succeeded')
        self.assertEqual(context['executions'][0]['output_ref'], {'preview_months': 12})
        approved = self.store.approve(self.first['id'], proposal['id'])
        self.assertEqual(approved['approval_source'], 'human_explicit_action')
        self.assertEqual(approved['status'], 'approved')
        self.assertEqual(self.store.approve(self.first['id'], proposal['id']), approved)
        self.assertFalse(self.store.context(self.second['id'])['messages'])
        self.assertNotIn(str(self.root), json.dumps(context))

    def test_every_foreign_identifier_is_rejected(self):
        execution = self.execution()
        proposal = self.store.propose(self.first['id'], 'A proposed decision')
        operations = (
            lambda: self.store.add_message(self.second['id'], self.first['conversation_id'], 'user', 'user_statement', 'foreign'),
            lambda: self.store.start_execution(self.second['id'], self.first['conversation_id'], 'describe_dataset', {}),
            lambda: self.store.add_message(self.second['id'], self.second['conversation_id'], 'assistant', 'tool_result', 'foreign', execution['id']),
            lambda: self.store.finish_execution(self.second['id'], execution['id'], 'succeeded'),
            lambda: self.store.approve(self.second['id'], proposal['id']),
            lambda: self.store.get_run(self.second['id'], uuid4().hex),
            lambda: self.store.project('missing'),
        )
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(MissingRecord):
                operation()
        self.assertFalse(self.store.context(self.second['id'])['messages'])
        self.assertFalse(self.store.context(self.second['id'])['executions'])

    def test_interrupted_calls_are_not_successful_or_retried(self):
        running = self.execution(tool='run_demo_analysis')
        failed = self.execution()
        self.store.finish_execution(self.first['id'], failed['id'], 'failed', error_code='validation_failed')
        with self.assertRaises(WorkspaceError):
            self.store.finish_execution(self.first['id'], failed['id'], 'succeeded')
        self.store.close()
        self.store = Workspace(self.root)
        values = {value['id']: value for value in self.store.context(self.first['id'])['executions']}
        self.assertEqual(values[running['id']]['status'], 'interrupted')
        self.assertEqual(values[running['id']]['error_code'], 'process_interrupted')
        self.assertEqual(values[failed['id']]['status'], 'failed')
        self.assertEqual(self.store.runs(self.first['id']), [])
        with self.assertRaises(WorkspaceError):
            self.store.finish_execution(self.first['id'], running['id'], 'succeeded')

    def test_live_workspace_lock_prevents_false_restart(self):
        running = self.execution()
        with self.assertRaisesRegex(WorkspaceError, 'already in use'):
            Workspace(self.root)
        self.assertEqual(self.store.context(self.first['id'])['executions'][0]['id'], running['id'])
        self.assertEqual(self.store.context(self.first['id'])['executions'][0]['status'], 'running')

    def test_context_bound_is_explicit_without_deleting_history(self):
        for i in range(45):
            self.store.add_message(self.first['id'], self.first['conversation_id'], 'user', 'user_statement', f'Note {i}')
        context = self.store.context(self.first['id'])
        self.assertEqual(context['counts']['messages'], 45)
        self.assertEqual(context['limits']['messages'], 40)
        self.assertTrue(context['truncated']['messages'])
        self.assertEqual(context['messages'][0]['text'], 'Note 5')
        self.assertEqual(context['messages'][-1]['text'], 'Note 44')
        with sqlite3.connect(self.store.database) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 45)

    def test_unknown_schema_and_database_corruption_are_not_reset(self):
        self.store.close()
        with sqlite3.connect(self.root / 'workspace.sqlite3') as db:
            db.execute('PRAGMA user_version=999')
        before = (self.root / 'workspace.sqlite3').read_bytes()
        with self.assertRaisesRegex(WorkspaceError, 'Unsupported workspace schema'):
            Workspace(self.root)
        self.assertEqual((self.root / 'workspace.sqlite3').read_bytes(), before)
        damaged = Path(self.temporary.name) / 'damaged'
        damaged.mkdir()
        (damaged / 'workspace.sqlite3').write_bytes(b'not SQLite; preserve this exact failure')
        with self.assertRaises(WorkspaceError):
            Workspace(damaged)
        self.assertEqual((damaged / 'workspace.sqlite3').read_bytes(), b'not SQLite; preserve this exact failure')
        # Crash residue from schema initialization is never treated as a fresh DB.
        partial = Path(self.temporary.name) / 'partial-schema'
        partial.mkdir()
        with sqlite3.connect(partial / 'workspace.sqlite3') as db:
            db.execute('CREATE TABLE projects(id TEXT PRIMARY KEY)')
        partial_bytes = (partial / 'workspace.sqlite3').read_bytes()
        with self.assertRaisesRegex(WorkspaceError, 'Unsupported workspace schema'):
            Workspace(partial)
        self.assertEqual((partial / 'workspace.sqlite3').read_bytes(), partial_bytes)

    def test_permissions_symlinks_and_traversal(self):
        if os.name != 'nt':
            self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
            self.assertEqual(self.store.database.stat().st_mode & 0o777, 0o600)
        for identity in ('../private', '/tmp/foreign', 'a' * 31, 'A' * 32):
            with self.subTest(identity=identity), self.assertRaises(MissingRecord):
                self.store.bundle_path(identity)
        linked = Path(self.temporary.name) / 'linked'
        linked.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(WorkspaceError):
            Workspace(linked)
        run_id = uuid4().hex
        self.store.bundle_path(run_id).symlink_to(self.temporary.name, target_is_directory=True)
        with self.assertRaises(WorkspaceError):
            self.store.bundle_path(run_id)

    def test_invalid_stored_json_reports_storage_failure_without_reset(self):
        with sqlite3.connect(self.store.database) as db:
            db.execute('UPDATE projects SET provenance_json=? WHERE id=?', ('{invalid', self.first['id']))
        with self.assertRaises(WorkspaceError):
            self.store.context(self.first['id'])
        with sqlite3.connect(self.store.database) as db:
            self.assertEqual(db.execute('SELECT provenance_json FROM projects WHERE id=?',
                             (self.first['id'],)).fetchone()[0], '{invalid')

    def test_original_bundle_published_atomically_and_reverified_after_restart(self):
        # Copy only committed synthetic output; no new model fitting in this storage test.
        example = Path(__file__).resolve().parents[1] / 'examples/task-01a'
        original = {p.relative_to(example): p.read_bytes() for p in example.rglob('*') if p.is_file()}
        run_id = uuid4().hex
        root = self.store.bundle_path(run_id)
        shutil.copytree(example, root)
        running = self.execution(tool='run_demo_analysis')
        saved = self.store.complete_run(self.first['id'], running['id'], run_id, 'with-quarter')
        self.assertEqual(saved['inventory_sha256'], hashlib.sha256(original[Path('inventory.json')]).hexdigest())
        self.assertEqual(saved['configuration']['controls']['include_quarter_end'], True)
        self.assertEqual(self.store.context(self.first['id'])['executions'][0]['status'], 'succeeded')
        self.assertEqual(self.store.runs(self.first['id'])[0]['id'], run_id)
        with self.assertRaises(MissingRecord):
            self.store.get_run(self.second['id'], run_id)
        self.store.close()
        self.store = Workspace(self.root)
        restored = self.store.get_run(self.first['id'], run_id)
        self.assertEqual(restored['software'], saved['software'])
        self.assertEqual({p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}, original)
        # A modified file is not accepted merely because its historical DB row says validated.
        target = root / 'report.md'
        target.chmod(0o600)
        target.write_bytes(target.read_bytes() + b'\nmodified\n')
        with self.assertRaises(WorkspaceError):
            self.store.get_run(self.first['id'], run_id)
        history = self.store.context(self.first['id'])
        self.assertEqual(history['runs'][0]['status'], 'validated_at_creation')
        self.assertEqual(history['runs'][0]['integrity_check'], 'required_on_open')
        self.assertNotIn('bundle_path', history['runs'][0])
        self.assertNotIn(str(self.root), json.dumps(history))
        invalid_id = uuid4().hex
        shutil.copytree(example, self.store.bundle_path(invalid_id))
        invalid = self.store.bundle_path(invalid_id) / 'inventory.json'
        invalid.chmod(0o600)
        invalid.write_text('{}')
        failed = self.execution(tool='run_demo_analysis')
        with self.assertRaises(WorkspaceError):
            self.store.complete_run(self.first['id'], failed['id'], invalid_id, 'with-quarter')
        self.assertEqual(len(self.store.runs(self.first['id'])), 1)
        self.assertEqual(self.store.context(self.first['id'])['executions'][0]['status'], 'running')

    def test_failed_completion_transaction_rolls_back_run_and_success_status(self):
        example = Path(__file__).resolve().parents[1] / 'examples/task-01a'
        run_id = uuid4().hex
        shutil.copytree(example, self.store.bundle_path(run_id))
        execution = self.execution(tool='run_demo_analysis')
        # Fail the success update after the run INSERT has executed, proving both
        # state changes share one transaction rather than just rejecting bad input.
        with sqlite3.connect(self.store.database) as db:
            db.execute("CREATE TRIGGER reject_completion BEFORE UPDATE OF status ON executions "
                       "WHEN NEW.status='succeeded' BEGIN SELECT RAISE(ABORT,'test completion failure'); END")
        with self.assertRaises(WorkspaceError):
            self.store.complete_run(self.first['id'], execution['id'], run_id, 'with-quarter')
        context = self.store.context(self.first['id'])
        self.assertEqual(context['runs'], [])
        self.assertEqual(context['executions'][0]['status'], 'running')
        self.assertIsNone(context['executions'][0]['output_ref'])
        with sqlite3.connect(self.store.database) as db:
            db.execute('DROP TRIGGER reject_completion')
        self.store.complete_run(self.first['id'], execution['id'], run_id, 'with-quarter')
        duplicate = self.execution(tool='run_demo_analysis')
        with self.assertRaises(WorkspaceError):
            self.store.complete_run(self.first['id'], duplicate['id'], run_id, 'without-quarter')
        context = self.store.context(self.first['id'])
        self.assertEqual(len(context['runs']), 1)
        self.assertEqual(context['runs'][0]['execution_id'], execution['id'])
        self.assertEqual(context['executions'][0]['status'], 'running')


if __name__ == '__main__':
    unittest.main()
