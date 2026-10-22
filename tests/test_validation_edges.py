"""Boundary and traversal cases missing from the original contract checks."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, ValidationError
from contracts.validate import validate_manifest, validate_generator

ROOT = Path(__file__).resolve().parents[1]


def pattern_nodes(node, location=()):
    if isinstance(node, dict):
        if 'pattern' in node:
            yield node, location
        for key, value in node.items():
            yield from pattern_nodes(value, location + (key,))
    elif isinstance(node, list):
        for value in node:
            yield from pattern_nodes(value, location)


class SchemaPatterns(unittest.TestCase):
    def test_every_pattern_accepts_valid_and_rejects_invalid_values(self):
        cases = {
            'month': (
                ['0001-01', '2024-01', '2024-09', '2024-12', '9999-12'],
                ['', '0000-01', '2024-00', '2024-13', '2024-1', '24-01',
                 '2024-001', '2024-01-01', '2024/01', '2024-01\n', '2024-01\r\n',
                 ' 2024-01', '2024-01 ', '\u0662\u0660\u0662\u0664-01', r'\dddd-01']),
            'path': (
                ['file.csv', 'contracts/examples/fixture.csv', '.cache/run-1.json',
                 'nested_dir/a.b-c_1.csv', 'release..json'],
                ['', '.', '..', '../secret', 'a/../secret', 'a/..', 'a/../../secret',
                 './file.csv', 'a/./file.csv', '/tmp/file.csv', '//host/file',
                 'a//file.csv', 'a/', 'C:/file.csv', r'C:\file.csv', r'a\..\secret',
                 '%2e%2e/secret', 'a/%2E%2E/secret', 'a/..%2fsecret', 'a%252f..%252fsecret',
                 'file.csv\n', 'file.csv\r', 'file\x00.csv', 'file name.csv',
                 'https://example.com/file.csv']),
            'sha256': (
                ['0' * 64, 'abcdef0123456789' * 4],
                ['0' * 63, '0' * 65, 'g' * 64, 'A' * 64, '0' * 64 + '\n']),
            'commit': (
                ['0' * 40, 'abcdef0123' * 4],
                ['0' * 39, '0' * 41, 'g' * 40, 'A' * 40, '0' * 40 + '\n']),
        }
        counts = dict.fromkeys(cases, 0)
        for file in sorted((ROOT / 'contracts').glob('*.schema.json')):
            for node, location in pattern_nodes(json.loads(file.read_text())):
                field = location[-1]
                if field in ['month', 'train_start', 'train_end', 'test_start', 'test_end']:
                    domain = 'month'
                elif field == 'path' or location == ('properties', 'outputs', 'properties', 'result'):
                    domain = 'path'
                elif field in ['sha256', 'manifest_sha256', 'data_sha256']:
                    domain = 'sha256'
                elif field in ['commit', 'hypoforge_commit']:
                    domain = 'commit'
                else:
                    self.fail(f'Unreviewed regex field in {file.name}: {location}')
                counts[domain] += 1
                valid, invalid = cases[domain]
                validator = Draft202012Validator(node)
                for value, expected in [(v, True) for v in valid] + [(v, False) for v in invalid]:
                    with self.subTest(schema=file.name, field=location, value=value):
                        self.assertEqual(validator.is_valid(value), expected)
        self.assertEqual(counts, {'month': 1, 'path': 1, 'sha256': 1, 'commit': 1})


class CsvEdges(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'contracts/examples/manifest.json').read_text())
        self.original = (ROOT / self.manifest['data']['path']).read_text()

    def check_csv(self, text, accepted=False):
        # Recalculate the hash to ensure CSV rejection is not merely a hash failure.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input.csv').write_bytes(text.encode('utf-8'))
            manifest = copy.deepcopy(self.manifest)
            manifest['data'] = {'path': 'input.csv', 'sha256': hashlib.sha256(text.encode()).hexdigest()}
            if accepted:
                self.assertEqual(validate_manifest(manifest, root), 6)
            else:
                with self.assertRaises((ValueError, ValidationError)):
                    validate_manifest(manifest, root)

    def test_all_fields_reject_empty_or_whitespace(self):
        for position in range(3):
            for value in ['', ' ', '\t']:
                with self.subTest(position=position, value=value):
                    fields = ['2024-02', '2', '13']
                    fields[position] = value
                    self.check_csv(self.original.replace('2024-02,2,13', ','.join(fields)))

    def test_all_numeric_columns_reject_nonfinite_or_nondecimal_numbers(self):
        for position in range(1, 3):
            for value in ['NaN', 'nan', 'inf', '-Infinity', '1e999', 'abc', '0x10',
                          '1_000', '\uff11\uff12', ' 12', '12 ']:
                with self.subTest(position=position, value=value):
                    fields = ['2024-02', '2', '13']
                    fields[position] = value
                    self.check_csv(self.original.replace('2024-02,2,13', ','.join(fields)))

    def test_valid_numeric_notation_and_negative_continuous_outcome(self):
        self.check_csv(self.original.replace('2024-02,2,13', '2024-02,+2.0,-.5'), accepted=True)

    def test_quoted_fields_and_crlf_remain_valid(self):
        self.check_csv(self.original.replace('2024-02,2,13', '"2024-02","2","13"')
                       .replace('\n', '\r\n'), accepted=True)

    def test_malformed_csv_quoting_rejected(self):
        self.check_csv(self.original.replace('2024-02,2,13', '2024-02,"2,13'))

    def test_large_fractional_registration_count_cannot_round_to_integer(self):
        from support import template
        generator = template('generator')
        reference = (ROOT / generator['reference']['path']).read_text()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for count in ['12.5', '9007199254740992.5', '-1', 'NaN', '']:
                with self.subTest(count=count):
                    text = reference.replace('2024-02,12', '2024-02,' + count)
                    (root / 'reference.csv').write_text(text)
                    generator['reference'] = {'path': 'reference.csv', 'sha256': hashlib.sha256(text.encode()).hexdigest()}
                    with self.assertRaises(ValueError):
                        validate_generator(generator, root)

    def test_missing_field_and_blank_record_rejected(self):
        for text in [self.original.replace('2024-02,2,13', '2024-02,2'),
                     self.original.replace('2024-02,2,13', ''),
                     self.original.replace('2024-02,2,13', ',,')]:
            with self.subTest(text=text):
                self.check_csv(text)

    def test_empty_and_header_only_rejected(self):
        for text in ['', self.original.splitlines()[0] + '\n']:
            with self.subTest(text=text):
                self.check_csv(text)

    def test_missing_or_reordered_header_rejected(self):
        for header in ['period,synthetic_media',
                       'period,semi_synthetic_outcome,synthetic_media',
                       'period,synthetic_media,synthetic_media']:
            with self.subTest(header=header):
                self.check_csv(self.original.replace(self.original.splitlines()[0], header))

    def test_actual_month_gap_and_out_of_order_rejected(self):
        for text in [self.original.replace('2024-03,0,11\n', ''),
                     self.original.replace('2024-02,2,13\n2024-03,0,11',
                                           '2024-03,0,11\n2024-02,2,13')]:
            with self.subTest(text=text):
                self.check_csv(text)

    def test_invalid_csv_months_rejected(self):
        for period in ['2024-00', '2024-13', '2024-2', '0000-02', '2024-02-01', '2024/02']:
            with self.subTest(period=period):
                self.check_csv(self.original.replace('2024-02', period))

    def test_invalid_split_boundaries_rejected(self):
        variants = [{'train_start': '2024-02'}, {'test_end': '2024-05'},
                    {'train_end': '2024-03'}, {'test_start': '2024-06'},
                    {'train_start': '2024-04', 'train_end': '2024-02'},
                    {'test_start': '2024-06', 'test_end': '2024-05'},
                    {'train_start': '2023-12'}, {'test_end': '2024-07'}]
        for changes in variants:
            with self.subTest(changes=changes):
                manifest = copy.deepcopy(self.manifest)
                manifest['split'].update(changes)
                with self.assertRaises((ValueError, ValidationError)):
                    validate_manifest(manifest)

    def test_changed_data_with_unchanged_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input.csv').write_text(self.original.replace(',2,13', ',2,14'))
            self.manifest['data']['path'] = 'input.csv'
            with self.assertRaisesRegex(ValueError, 'checksum'):
                validate_manifest(self.manifest, root)

    def test_invalid_provenance_classes_and_reference_mismatch_rejected(self):
        for column in self.manifest['columns']:
            for classification in ['', 'unknown', 'Observed', 'media_spend']:
                with self.subTest(column=column, classification=classification):
                    manifest = copy.deepcopy(self.manifest)
                    manifest['columns'][column]['class'] = classification
                    with self.assertRaises(ValidationError):
                        validate_manifest(manifest)
        from support import template
        generator = template('generator')
        generator['reference_kind'] = 'observed_kba'
        with self.assertRaises(ValidationError):
            validate_generator(generator)

    def test_input_and_output_symlinks_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / 'project'
            root.mkdir()
            outside = parent / 'outside.csv'
            outside.write_text(self.original)
            (root / 'linked.csv').symlink_to(outside)
            (root / 'linked_dir').symlink_to(parent, target_is_directory=True)
            for input_path, output_path in [('linked.csv', 'result.json'),
                                            ('linked_dir/outside.csv', 'result.json'),
                                            ('input.csv', 'linked_dir/result.json')]:
                with self.subTest(input=input_path, output=output_path):
                    (root / 'input.csv').write_text(self.original)
                    manifest = copy.deepcopy(self.manifest)
                    manifest['data']['path'] = input_path
                    manifest['outputs']['result'] = output_path
                    with self.assertRaisesRegex(ValueError, 'inside the project root'):
                        validate_manifest(manifest, root)
            (root / 'local.csv').symlink_to(root / 'input.csv')
            manifest = copy.deepcopy(self.manifest)
            manifest['data']['path'] = 'local.csv'
            self.assertEqual(validate_manifest(manifest, root), 6)

    def test_nonfinite_manifest_parameters_rejected(self):
        for field in ['alpha', 'k', 'n']:
            for value in [float('nan'), float('inf'), float('-inf')]:
                with self.subTest(field=field, value=value):
                    manifest = copy.deepcopy(self.manifest)
                    manifest['estimation']['parameters'][field] = value
                    with self.assertRaises((ValidationError, ValueError)):
                        validate_manifest(manifest)
