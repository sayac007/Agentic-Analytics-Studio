"""Existing contract guarantees migrated to the separated v0.2.0 interfaces."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, ValidationError
from contracts.validate import SCHEMAS, validate_document, validate_generator, validate_manifest
from support import template, graph

ROOT = Path(__file__).resolve().parents[1]


class Contracts(unittest.TestCase):
    def setUp(self):
        self.manifest = template()

    def reject(self, mutate):
        mutate(self.manifest)
        with self.assertRaises((ValidationError, ValueError)):
            validate_manifest(self.manifest)

    def test_all_schemas_are_valid(self):
        self.assertEqual(set(SCHEMAS), {'common','manifest','generator','release','truth','result','comparison','evaluation'})
        for name,schema in SCHEMAS.items():
            with self.subTest(schema=name):
                Draft202012Validator.check_schema(schema)

    def test_example_and_csv_validate(self):
        self.assertEqual(validate_manifest(self.manifest), 6)
        self.manifest['columns'] = dict(reversed(list(self.manifest['columns'].items())))
        self.assertEqual(validate_manifest(self.manifest), 6)

    def test_cannot_call_fixture_observed(self):
        generator = template('generator')
        generator['reference_columns']['observed_registrations']['class'] = 'observed'
        with self.assertRaises(ValidationError):
            validate_generator(generator)

    def test_synthetic_media_cannot_be_observed(self):
        self.reject(lambda m: m['columns']['synthetic_media'].update({'class':'observed'}))

    def test_truth_cannot_enter_estimation_manifest(self):
        self.reject(lambda m: m.update({'truth':'private/truth.json'}))

    def test_original_reference_cannot_be_fit_target(self):
        self.reject(lambda m: m['estimation'].update({'target':'observed_registrations'}))

    def test_parameter_bounds(self):
        self.reject(lambda m: m['estimation']['parameters'].update({'alpha':1}))

    def test_overlap_rejected(self):
        self.reject(lambda m: m['split'].update({'test_start':'2024-04'}))

    def test_checksum_mismatch_rejected(self):
        self.reject(lambda m: m['data'].update({'sha256':'0'*64}))

    def test_provenance_required(self):
        self.reject(lambda m: m['columns']['synthetic_media'].pop('rights'))

    def test_invalid_access_date(self):
        self.reject(lambda m: m['columns']['period'].update({'access_date':'2026-02-30'}))

    def test_bad_csv_rejected_even_with_matching_hash(self):
        original=(ROOT/self.manifest['data']['path']).read_text()
        variants=[original.replace('2024-02','2024-01'), original.replace('2024-02','2024-07'),
                  original.replace(',2,13',',NaN,13'),original.replace(',2,13',',,13'),
                  original.replace(',2,13',',-2,13'),original.replace(',2,13',',2,13,extra')]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for text in variants:
                with self.subTest(csv=text):
                    (root/'input.csv').write_text(text)
                    m=copy.deepcopy(self.manifest)
                    m['data']={'path':'input.csv','sha256':hashlib.sha256(text.encode()).hexdigest()}
                    with self.assertRaises(ValueError):validate_manifest(m,root)

    def test_output_and_truth_contract_shapes(self):
        with tempfile.TemporaryDirectory() as directory:
            examples=graph(Path(directory))
            for kind,field,invalid in [('truth','estimator_access',True),
                                       ('result','target','observed_registrations'),
                                       ('comparison','claim','real_tesla_roi')]:
                with self.subTest(schema=kind):
                    example=examples[kind]
                    validate_document(kind,example)
                    example[field]=invalid
                    with self.assertRaises(ValidationError):validate_document(kind,example)


if __name__=='__main__':unittest.main()
