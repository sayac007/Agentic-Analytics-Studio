"""Constructed CSV fixtures only; no empirical findings or external requests."""
import copy
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from test_empirical import fixture
from empirical.data import json_bytes
from empirical.intake import Store, IntakeError, inspect, parse, describe
from empirical.tesla_review import annual


def meta(**changes):
    return {'series_id': 'new_metric', 'label': 'SOFTWARE FIXTURE', 'unit': 'test_unit',
            'definition': 'Constructed fixture, not an empirical series', 'source_reference': 'Software fixture',
            'source_vintage': 'unbekannt', 'classification': 'observed', 'period_column': 'month',
            'value_column': 'value', 'decimal': 'dot', 'private_use_confirmed': True, **changes}


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.store = Store(self.root/'private')
        self.base = {'snapshot_sha256': 'a'*64, 'data': fixture()}
        self.original = copy.deepcopy(self.base)

    def test_utf8_decimal_mapping_and_missing_values(self):
        raw = b'\xef\xbb\xbfmonth;value;note\r\n2020-01;1,25;x\r\n2020-02;;y\r\n'
        self.assertEqual(inspect(raw)['period_candidates'], ['month'])
        self.assertEqual(parse(raw, meta(decimal='comma')), {'2020-01': 1.25, '2020-02': None})
        self.assertEqual(self.store.preview(self.base,raw,meta(decimal='comma'))['ignored_columns'], ['note'])

    def test_invalid_month_numbers_duplicates_and_paths_fail(self):
        for text in ['month,value\n2020-13,1\n', 'month,value\n2020-01-01,1\n',
                     'month,value\n2020-01,NaN\n', 'month,value\n2020-01,inf\n',
                     'month,value\n2020-01,1e999\n', 'month,value\n2020-01,=SUM(A1)\n',
                     'month,value\n2020-01,1\n2020-01,2\n', 'month,value\n2020-01,1,extra\n',
                     'month,month\n2020-01,1\n']:
            with self.subTest(text=text), self.assertRaises(IntakeError): parse(text.encode(),meta())
        for key in ('../private','/root','calendar_month'):
            with self.subTest(key=key), self.assertRaises(IntakeError):parse(b'month,value\n2020-01,1\n',meta(series_id=key))
        self.assertEqual(list((self.root/'private').iterdir()), [])

    def test_missing_rights_definition_and_url_credentials_fail(self):
        for change in ({'private_use_confirmed': False}, {'unit': ''}, {'definition': ''},
                       {'source_reference': 'https://user:pass@example.org/data'},
                       {'source_reference': 'https://example.org/data?sig=private'}, {'decimal': 'guess'}):
            with self.subTest(change=change), self.assertRaises(IntakeError):parse(b'month,value\n2020-01,1\n',meta(**change))

    def test_unit_class_and_count_domains_preserved(self):
        self.base['data']['sources']['tesla_count']['classification'] = 'observed'
        for text, changes in [('1', {'unit':'wrong'}), ('1', {'classification':'proxy'}),
                              ('-1',{}), ('1.5',{}), ('9007199254740993',{})]:
            with self.subTest(text=text,changes=changes), self.assertRaises(IntakeError):
                self.store.preview(self.base, f'month,value\n2020-01,{text}\n'.encode(),
                    meta(series_id='tesla_count',unit='SOFTWARE_TEST_FIXTURE',**changes) if 'unit' not in changes else meta(series_id='tesla_count',**changes))

    def test_native_geography_and_unit_contradictions_are_blocked(self):
        for raw in (b'month,value,geo\n2020-01,1,AT\n', b'month,value,region\n2020-01,1,Bayern\n',
                    b'month,value,unit\n2020-01,1,wrong_unit\n'):
            with self.subTest(raw=raw),self.assertRaises(IntakeError):parse(raw,meta())
        self.assertEqual(parse(b'month,value,geo,unit\n2020-01,1,DE,test_unit\n',meta()),{'2020-01':1})

    def test_revisions_deletions_and_extremes_are_reviewed_without_imputation(self):
        raw=b'month,value\n2018-01,99999\n2018-02,\n2026-01,123\n'
        m=meta(series_id='tesla_count',unit='SOFTWARE_TEST_FIXTURE')
        review=self.store.preview(self.base,raw,m)
        self.assertEqual(len(review['revisions']),2)
        self.assertIn('2018-01',review['outside_historical_range'])
        self.assertIn('2026-01',review['new_months'])
        self.assertIsNone(review['revisions'][1]['new'])
        accepted=self.store.assemble(self.base,raw,m,review['preview_sha256'])
        d=accepted['data']
        self.assertEqual(d['series']['tesla_count'][0],99999)
        self.assertIsNone(d['series']['tesla_count'][1])
        self.assertEqual(d['series']['tesla_count'][2],self.original['data']['series']['tesla_count'][2])
        self.assertIsNone(d['series']['cpi'][-1])
        self.assertEqual(d['series']['calendar_month'][-1],1)
        self.assertEqual(self.base,self.original)

    def test_stale_preview_changed_bytes_and_changed_meta_do_not_commit(self):
        raw=b'month,value\n2020-01,2\n'; m=meta()
        p=self.store.preview(self.base,raw,m)
        for new_raw,new_meta in [(raw+b'2020-02,3\n',m),(raw,meta(unit='other'))]:
            with self.assertRaises(IntakeError):self.store.assemble(self.base,new_raw,new_meta,p['preview_sha256'])
        self.store.assemble(self.base)
        with self.assertRaises(IntakeError):self.store.assemble(self.base,raw,m,p['preview_sha256'])
        self.assertNotIn('new_metric', self.store.current(self.base)['data']['series'])

    def test_multiple_uploads_form_one_versioned_dataset_preserve_raw_and_restart(self):
        first=b'month,value\n2020-01,2\n2020-03,3\n'
        p=self.store.preview(self.base,first,meta()); a=self.store.assemble(self.base,first,meta(),p['preview_sha256'])
        first_hashes={f.name:f.read_bytes() for f in a['folder'].iterdir()}
        second=b'month,value\n2020-02,-1\n'
        m=meta(series_id='other_metric');p=self.store.preview(self.base,second,m)
        b=self.store.assemble(self.base,second,m,p['preview_sha256'])
        again=Store(self.root/'private').current(self.base)
        self.assertEqual(again['id'],b['id'])
        self.assertIn('new_metric',again['data']['series']);self.assertIn('other_metric',again['data']['series'])
        self.assertEqual(first_hashes,{f.name:f.read_bytes() for f in a['folder'].iterdir()})
        self.assertEqual((a['folder']/'source.csv').read_bytes(),first)
        rows=list(csv.DictReader(io.StringIO((b['folder']/'panel.csv').read_text())))
        self.assertEqual(next(r for r in rows if r['period']=='2020-02')['new_metric'],'')
        self.assertEqual(self.store.assemble(self.base)['id'],b['id'])
        self.assertEqual(describe(again['data'],again['id'])['analysis_status'],'candidate_dataset_not_fitted')

    def test_corrupt_files_pointer_and_changed_original_base_are_rejected(self):
        current=self.store.assemble(self.base)
        (current['folder']/'panel.csv').write_bytes(b'corrupt')
        with self.assertRaises(IntakeError):self.store.current(self.base)
        (self.root/'private/current.json').write_bytes(json_bytes({'id':'../../outside'}))
        with self.assertRaises(IntakeError):self.store.current(self.base)
        (self.root/'private/current.json').write_bytes(json_bytes({'id':current['id']}))
        altered=copy.deepcopy(self.base);altered['snapshot_sha256']='b'*64
        with self.assertRaises(IntakeError):self.store.current(altered)

    def test_annual_review_requires_twelve_months_and_keeps_absence_unknown(self):
        periods=[f'{y}-{m:02d}' for y in (2024,2025) for m in range(1,13)]
        result=annual({'tesla_count':[1]*12+[2]*12,'market_bev':[None]+[1]*23},periods)
        self.assertEqual(result[1]['series']['tesla_count']['yoy_fraction'],1)
        self.assertAlmostEqual(result[0]['series']['tesla_count']['quarter_end_fraction'],1/3)
        self.assertIsNone(result[0]['series']['market_bev']['total'])
        self.assertIsNone(result[1]['series']['market_bev']['yoy_fraction'])

    def test_dataset_change_invalidates_ai_preview_without_provider_call(self):
        from unittest.mock import patch, Mock
        from test_empirical import bundle
        from demo.workspace import Workspace
        from demo.openai_provider import Config, ConversationError
        from demo.empirical_chat import preview, respond
        b=bundle();ws=Workspace(self.root/'state');self.addCleanup(ws.close)
        with patch('empirical.service.read',return_value=b),patch('empirical.service.storage_root',return_value=self.root):
            config=Config(True,'sk-INTAKE_FIXTURE_NOT_A_REAL_KEY_123456')
            p=preview(ws,'Prüfe die Datenqualität.','macro',config)
            Store(self.root/'observed-intake').assemble(b)
            client=Mock()
            with self.assertRaises(ConversationError) as caught:
                respond(ws,'Prüfe die Datenqualität.','macro',True,p['context_sha256'],config,client)
            self.assertEqual(caught.exception.code,'context_changed');client.request.assert_not_called()


if __name__=='__main__':unittest.main()
