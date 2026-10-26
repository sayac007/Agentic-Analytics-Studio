"""Public-export boundary: complete synthetic bundle only, never private empirics."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from studio.export import require_synthetic, verify_export

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/task-01a'


class ResultsExportTests(unittest.TestCase):
    def test_existing_synthetic_bundle_is_exportable_without_modification(self):
        self.assertEqual(verify_export(EXAMPLE), 20)

    def test_observed_or_unapproved_reference_is_refused(self):
        original = json.loads((EXAMPLE/'private/generator.json').read_text())
        for kind in ('observed_retrospective', 'observed', None):
            changed = copy.deepcopy(original)
            changed['reference_kind'] = kind
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                require_synthetic(changed)
        for key, value in [('class', 'observed'), ('redistribution', 'unknown')]:
            changed = copy.deepcopy(original)
            changed['reference_columns']['observed_registrations'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                require_synthetic(changed)

    def test_extra_file_refused_even_with_updated_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'bundle'
            shutil.copytree(EXAMPLE, root)
            (root/'unrelated.txt').write_text('unrelated, not an authorised export member')
            from studio.files import artifact
            inventory = json.loads((root/'inventory.json').read_text())
            inventory['artifacts']['unrelated.txt'] = artifact(root, 'unrelated.txt')['sha256']
            (root/'inventory.json').write_text(json.dumps(inventory))
            with self.assertRaisesRegex(ValueError, 'Unexpected export membership'):
                verify_export(root)


if __name__ == '__main__':
    unittest.main()
