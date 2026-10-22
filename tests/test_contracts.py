"""Validate contracts and rejection behavior; these are not MMM tests."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from contracts.validate import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class Contracts(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'contracts/examples/manifest.json').read_text())

    def reject(self, mutate):
        mutate(self.manifest)
        with self.assertRaises((ValidationError, ValueError)):
            validate_manifest(self.manifest)

    def test_all_schemas_are_valid(self):
        paths = list((ROOT / 'contracts').glob('*.schema.json'))
        self.assertEqual(len(paths), 4)
        for path in paths:
            with self.subTest(schema=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_example_and_csv_validate(self):
        self.assertEqual(validate_manifest(self.manifest), 6)
        self.manifest['columns'] = dict(reversed(list(self.manifest['columns'].items())))
        self.assertEqual(validate_manifest(self.manifest), 6)

    def test_cannot_call_fixture_observed(self):
        self.reject(lambda m: m['columns']['observed_registrations'].update({'class': 'observed'}))

    def test_synthetic_media_cannot_be_observed(self):
        self.reject(lambda m: m['columns']['synthetic_media'].update({'class': 'observed'}))

    def test_truth_cannot_enter_estimation_manifest(self):
        self.reject(lambda m: m.update({'truth': 'private/truth.json'}))

    def test_original_reference_cannot_be_fit_target(self):
        self.reject(lambda m: m['estimation'].update({'target': 'observed_registrations'}))

    def test_parameter_bounds(self):
        self.reject(lambda m: m['estimation']['parameters'].update({'alpha': 1}))

    def test_overlap_rejected(self):
        self.reject(lambda m: m['split'].update({'test_start': '2024-04'}))

    def test_checksum_mismatch_rejected(self):
        self.reject(lambda m: m['data'].update({'sha256': '0' * 64}))

    def test_provenance_required(self):
        self.reject(lambda m: m['columns']['observed_registrations'].pop('rights'))

    def test_invalid_access_date(self):
        self.reject(lambda m: m['columns']['period'].update({'access_date': '2026-02-30'}))

    def test_bad_csv_rejected_even_with_matching_hash(self):
        original = (ROOT / self.manifest['data']['path']).read_text()
        variants = [original.replace('2024-02', '2024-01'), original.replace('2024-02', '2024-07'),
                    original.replace(',12,2,13', ',12,NaN,13'),
                    original.replace(',12,2,13', ',12,,13'),
                    original.replace(',12,2,13', ',12,-2,13'),
                    original.replace(',12,2,13', ',12.5,2,13'),
                    original.replace(',12,2,13', ',12,2,13,extra')]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for text in variants:
                with self.subTest(csv=text):
                    (root / 'input.csv').write_text(text)
                    m = copy.deepcopy(self.manifest)
                    m['data'] = {'path': 'input.csv', 'sha256': hashlib.sha256(text.encode()).hexdigest()}
                    with self.assertRaises(ValueError):
                        validate_manifest(m, root)

    def test_output_and_truth_contract_shapes(self):
        # Deliberately fabricated in-memory schema examples, never saved as model evidence.
        parameters = self.manifest['estimation']['parameters']
        truth = {'schema_version': '0.1.0', 'run_id': 'shape-only', 'data': self.manifest['data'],
                 'estimator_access': False,
                 'generator': {'id': 'shape-only', 'version': '0', 'seed': 42, 'rng': 'PCG64',
                               'noise_distribution': 'normal', 'noise_sd': 1},
                 'parameters': parameters,
                 'coefficients': {'intercept': 0, 'observed_reference': 1, 'media': 2},
                 'equation': 'y = intercept + observed_reference * observed_registrations + media * hill(adstock(synthetic_media)) + noise',
                 'claim': 'injected_effect_only_not_real_tesla_roi'}
        result = {'schema_version': '0.1.0', 'run_id': 'shape-only', 'manifest_sha256': '0'*64,
                  'data_sha256': '0'*64, 'status': 'success', 'target': 'semi_synthetic_outcome',
                  'coefficients': truth['coefficients'],
                  'metrics': {part: {'n': 2, 'mae': 1, 'rmse': 1} for part in ['train', 'test']},
                  'diagnostics': {'rank': 3, 'condition_number': 2, 'flags': []},
                  'software': {'python': 'shape-only', 'numpy': 'shape-only', 'hypoforge_commit': '0'*40},
                  'claim': self.manifest['claim']}
        comparison = {'schema_version': '0.1.0', 'comparison_id': 'shape-only',
                      'left': {'run_id': 'a', 'result': self.manifest['data']},
                      'right': {'run_id': 'b', 'result': self.manifest['data']},
                      'compatibility': {'same_data_sha256': True, 'same_holdout': True, 'same_target': True},
                      'test_rmse_delta_right_minus_left': 0, 'media_coefficient_delta_right_minus_left': 0,
                      'interpretation': 'benchmark_stability_not_causal_marketing_effect'}
        for name, example, field, invalid in [('truth', truth, 'estimator_access', True),
                                              ('result', result, 'target', 'observed_registrations'),
                                              ('comparison', comparison, 'interpretation', 'real_tesla_roi')]:
            with self.subTest(schema=name):
                validator = Draft202012Validator(json.loads((ROOT / f'contracts/{name}.schema.json').read_text()), format_checker=FormatChecker())
                validator.validate(example)
                example[field] = invalid
                with self.assertRaises(ValidationError):
                    validator.validate(example)


if __name__ == '__main__':
    unittest.main()
