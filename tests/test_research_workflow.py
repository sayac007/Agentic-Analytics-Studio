"""Constructed fixtures only: durable task scope, honest QA and evidence-only handoff."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from test_empirical import bundle
from demo import empirical_chat
from demo.openai_provider import Config, ConversationError, canonical, REQUEST_BYTES
from demo.research_workflow import DEFAULT_BRIEF, check_brief, overview, handoff
from demo.workspace import Workspace


class ResearchWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = bundle()  # Software fixture, never a real empirical finding.

    def setUp(self):
        self.b = copy.deepcopy(self.snapshot)
        self.brief = copy.deepcopy(DEFAULT_BRIEF)

    def test_task_persists_restart_without_mutating_models_or_other_projects(self):
        with tempfile.TemporaryDirectory() as temp:
            ws = Workspace(Path(temp)/'state')
            original = ws.project('synthetic-quarter')
            self.assertIsNone(ws.research_brief()['updated_at'])
            self.brief['required_drivers'].append('delivery')
            saved = ws.research_brief(self.brief)
            self.assertTrue(saved['updated_at'].endswith('+00:00'))
            ws.close()
            ws = Workspace(Path(temp)/'state')
            try:
                self.assertEqual(saved, ws.research_brief())
                self.assertEqual(original, ws.project('synthetic-quarter'))
                self.assertEqual(self.b, self.snapshot)
                self.assertEqual(ws.context('tesla-observed')['runs'], [])
            finally: ws.close()

    def test_mandatory_baseline_unknown_duplicate_and_configuration_injection_rejected(self):
        for drivers in (['calendar'], ['calendar', 'dynamics', 'fake'], ['calendar', 'dynamics', 'dynamics'], ['calendar', []]):
            value = copy.deepcopy(self.brief); value['required_drivers'] = drivers
            with self.subTest(drivers=drivers), self.assertRaises(ValueError): check_brief(value)
        for change in ({'model': 'search'}, {'source_path': '/private'}, {'question': ''}, {'audience': 4}):
            with self.subTest(change=change), self.assertRaises(ValueError): check_brief({**self.brief, **change})

    def test_missing_snapshot_never_claims_verified_sources(self):
        review = overview(self.brief)
        self.assertIsNone(review['snapshot_sha256'])
        self.assertEqual(review['models'], {})
        self.assertEqual(review['sources'], [])
        self.assertFalse(any(c['status'] == 'verified' for c in review['checks']))

    def test_unmodeled_required_driver_is_gap_not_automatic_model_change(self):
        self.brief['required_drivers'] += ['delivery', 'promotions']
        review = overview(self.brief, self.b)
        self.assertIn('delivery', review['models']['macro']['unmet_drivers'])
        self.assertIn('promotions', review['models']['macro']['unmet_drivers'])
        self.assertEqual(review['models']['macro']['checks'][0]['status'], 'review')
        self.assertIn('dynamics', review['models']['calendar']['unmet_drivers'])
        self.assertEqual(review['statistical_approval'], 'not_granted_by_checklist')
        self.assertEqual(self.b, self.snapshot)

    def test_real_calendar_gaps_and_metadata_drift_are_separate(self):
        self.b['data']['series']['diesel_de'][10] = None
        self.b['data']['sources']['diesel_de'].update(observed_months=95, missing_months=['2018-11'])
        checks = overview(self.brief, self.b)['checks']
        gap = next(c for c in checks if c['check'] == 'Deutscher Dieselpreis')
        self.assertEqual(gap['status'], 'review'); self.assertIn('2018-11', gap['detail'])
        self.b['data']['sources']['diesel_de']['observed_months'] = 96
        checks = overview(self.brief, self.b)['checks']
        self.assertEqual(next(c for c in checks if c['check'] == 'Deutscher Dieselpreis')['status'], 'failed')
        self.b['data']['periods'][10] = '2018-10'
        checks = overview(self.brief, self.b)['checks']
        self.assertEqual(next(c for c in checks if c['check'] == 'Monatskalender')['status'], 'failed')

    def test_comparator_rank_and_train_test_corruption_are_visible(self):
        m = self.b['results']['models']['macro']
        m['paired_comparator']['holdout_count_metrics']['n'] -= 1
        m['full']['rank'] -= 1
        m['training']['periods'].append('2025-01')
        checks = overview(self.brief, self.b)['models']['macro']['checks']
        self.assertEqual(sum(c['status'] == 'failed' for c in checks), 3)

    def test_handoff_preserves_bad_results_failed_models_precision_and_no_raw_arrays(self):
        m = self.b['results']['models']['macro']
        m['full']['metrics']['r2'] = -0.12345678901234567
        m['holdout']['count_metrics']['rmse'] = 9999.12345678901
        m['full']['coefficients']['intercept']['estimate'] = -1.2345678901234567
        self.b['results']['models']['macro_diesel_lag3'] = {'status': 'not_estimable', 'reason': 'Fixture rank failure', 'stationarity': {}}
        self.b['data']['series']['tesla_count'][0] = 987654321  # Deliberate raw-data sentinel.
        self.b['history'] = [{'text': 'PRIVATE_HISTORY_SENTINEL'}]
        self.b['data']['sources']['tesla_count']['attribution'] = 'Source <img src=x> | copied\n# forge'
        report = handoff(self.brief, self.b)
        for value in ('-0.12345678901234566', '9999.12345678901', '-1.2345678901234567', 'Fixture rank failure', 'a'*64):
            self.assertIn(value, report)
        self.assertIn('Source &lt;img src=x&gt; &#124; copied # forge', report)
        self.assertNotIn('987654321', report)
        self.assertNotIn('PRIVATE_HISTORY_SENTINEL', report)
        self.assertNotIn('holdout_predicted_counts', report)
        self.assertIn('Keine Neuberechnung', report)
        self.assertIn('Schritt 3', report)
        self.assertIn('keine feste Zwölf-Monats-Prognose', report)

    def test_not_estimable_selected_model_does_not_fabricate_coefficients(self):
        self.b['results']['models']['macro'] = {'status': 'not_estimable', 'reason': 'Fixture no rank', 'stationarity': {}}
        text = handoff(self.brief, self.b)
        self.assertIn('Fixture no rank', text)
        self.assertNotIn('Term (Gesamtfenster)', text)

    def test_work_order_change_invalidates_ai_consent_before_any_external_call(self):
        with tempfile.TemporaryDirectory() as temp, patch('empirical.service.read', return_value=self.b):
            ws = Workspace(Path(temp)/'state')
            self.addCleanup(ws.close)
            config = Config(True, 'sk-WORKFLOW_TEST_NOT_REAL_KEY_123456')
            question = 'Prüfe die Qualität.'
            preview = empirical_chat.preview(ws, question, 'macro', config)
            self.assertIn('business_work_order', preview['context'])
            self.assertIn('quality_review', preview['context'])
            self.assertLess(len(canonical(preview['context'])) + len(empirical_chat.INSTRUCTIONS.encode()) + 1000, REQUEST_BYTES)
            self.brief['required_drivers'].append('delivery')
            ws.research_brief(self.brief)
            client = Mock()
            with self.assertRaises(ConversationError) as caught:
                empirical_chat.respond(ws, question, 'macro', True, preview['context_sha256'], config, client)
            self.assertEqual(caught.exception.code, 'context_changed')
            client.request.assert_not_called()
            new_preview = empirical_chat.preview(ws, question, 'macro', config)
            self.brief['interface_notes'] = 'Andere gewünschte Datenlieferung, nicht zum Versand bestimmt.'
            ws.research_brief(self.brief)
            with self.assertRaises(ConversationError) as caught:
                empirical_chat.respond(ws, question, 'macro', True, new_preview['context_sha256'], config, client)
            self.assertEqual(caught.exception.code, 'context_changed')
            client.request.assert_not_called()
            self.assertNotIn(self.brief['interface_notes'], str(empirical_chat.preview(ws, question, 'macro', config)))


if __name__ == '__main__': unittest.main()
