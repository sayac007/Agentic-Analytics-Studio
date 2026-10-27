"""Synthetic operating-characteristic checks; no outcome-driven specification changes."""
import json
import hashlib
import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from hypoforge.media import geometric_adstock
from research_benchmark import run as r
from research_benchmark.estimator import estimate
from studio.statistics import design, ols_hac
from studio.transforms import hill


class IdentifiabilityTests(unittest.TestCase):
    @staticmethod
    def archived_rows(name):
        with (r.ROOT / 'results/task02' / name).open(newline='') as stream:
            return list(csv.DictReader(stream))

    def test_preserved_original_manifest_and_complete_1000_seed_grid(self):
        from research_benchmark.verify import verify
        root = r.ROOT / 'results/task02'
        # This is the unmodified original manifest of CI artifact 12721762336.
        self.assertEqual(hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest(),
                         '3b14c47febcad8d776f3d6dbb56a3e93ce4c734f013613f26a300952be8a6807')
        verify(root)
        manifest = json.loads((root/'manifest.json').read_text())
        self.assertEqual(manifest['code_commit'], 'f144c72140285533246f8ca0af6e347beeecb48e')
        self.assertEqual((manifest['seeds_per_cell'], manifest['seed_start'], manifest['smoke_only']), (1000, 0, False))
        cfg = r.protocol()
        cells = {f'legacy-always_on-independent-{e:g}' for e in (0, .08)}
        cells |= {f'grid-{d}-{c}-{e:g}' for d in cfg['spend_designs']
                  for c in cfg['confounding'] for e in (0, *cfg['effect_fractions'])}
        truth, fits = self.archived_rows('truth.csv'), self.archived_rows('evaluations.csv')
        self.assertEqual(len(cells), 18)
        self.assertEqual(len(truth), 18000)
        self.assertEqual(len(fits), 36000)
        self.assertEqual({(v['cell'], int(v['seed'])) for v in truth},
                         {(c, seed) for c in cells for seed in range(1000)})
        self.assertEqual({(v['cell'], int(v['seed']), v['model']) for v in fits},
                         {(c, seed, model) for c in cells for seed in range(1000) for model in cfg['models']})
        summaries = self.archived_rows('summary.csv')
        self.assertEqual(len(summaries), 36)
        self.assertEqual({(s['cell'], s['model']) for s in summaries},
                         {(c, model) for c in cells for model in cfg['models']})
        legacy = [v for v in fits if v['cell'] == 'legacy-always_on-independent-0.08' and v['seed'] == '42']
        self.assertEqual(self.archived_rows('legacy_flags.csv'), legacy)
        self.assertEqual(len(legacy), 2)

    def test_preserved_summary_rates_and_thresholds_from_original_seed_records(self):
        # Arithmetic verification of stored records, with no generator or estimator call.
        from collections import defaultdict
        groups = defaultdict(list)
        truth = {(v['cell'], v['seed']): v for v in self.archived_rows('truth.csv')}
        boolean_fields = ('rejection', 'positive_detection', 'wrong_sign_rejection', 'covers_truth',
                          'sign_uncertain', 'not_identified', 'extrapolated_counterfactual')
        for raw in self.archived_rows('evaluations.csv'):
            row = dict(raw)
            for key in boolean_fields:
                self.assertIn(row[key], ('True', 'False'))
                row[key] = row[key] == 'True'
            for key in ('effect_fraction', 'beta', 'se', 'lower', 'upper', 'beta_ratio', 'snr'):
                row[key] = float(row[key]) if row[key] else None
            if row['status'] == 'estimated':
                beta, lower, upper = row['beta'], row['lower'], row['upper']
                planted = float(truth[(row['cell'], row['seed'])]['beta'])
                self.assertAlmostEqual(lower, beta-r.Z*row['se'])
                self.assertAlmostEqual(upper, beta+r.Z*row['se'])
                self.assertEqual(row['rejection'], lower > 0 or upper < 0)
                self.assertEqual(row['positive_detection'], lower > 0)
                self.assertEqual(row['wrong_sign_rejection'], upper < 0)
                self.assertEqual(row['covers_truth'], lower <= planted <= upper)
                if planted:
                    self.assertAlmostEqual(row['beta_ratio'], beta/planted)
                else:
                    self.assertIsNone(row['beta_ratio'])
            groups[(row['cell'], row['model'])].append(row)
        saved = self.archived_rows('summary.csv')
        for row in saved:
            calculated = r.summarize(groups[(row['cell'], row['model'])], 1000)
            self.assertEqual(set(row), set(calculated))
            for key, value in calculated.items():
                if value is None:
                    self.assertEqual(row[key], '')
                elif isinstance(value, (int, float)):
                    np.testing.assert_allclose(float(row[key]), value, rtol=1e-12, atol=1e-12)
                else:
                    self.assertEqual(row[key], value)
        thresholds = self.archived_rows('mde.csv')
        self.assertEqual(len(thresholds), 8)
        cfg = r.protocol()
        self.assertEqual({(t['design'], t['confounding'], t['model']) for t in thresholds},
                         {(d, c, m) for d in cfg['spend_designs'] for c in cfg['confounding'] for m in cfg['models']})
        for threshold in thresholds:
            selected = [s for s in saved if s['cell'].startswith('grid-') and
                        all(s[k] == threshold[k] for k in ('design', 'confounding', 'model'))]
            null = next(s for s in selected if float(s['effect_fraction']) == 0)
            self.assertEqual(threshold['null_rejection_rate'], null['rejection_rate'])
            self.assertEqual(threshold['null_rejection_mcse'], null['rejection_mcse'])
            self.assertEqual(threshold['label'], 'exploratory_tested_grid_threshold_not_validated_MDE')
            for key in ('rejection', 'positive_detection'):
                reached = [float(s['effect_fraction']) for s in selected if float(s['effect_fraction']) > 0
                           and float(s[key+'_rate']) >= cfg['power_target']]
                self.assertEqual(threshold[key+'_grid_mde'], str(min(reached)) if reached else '')

    def test_frozen_new_stage_and_padded_transform_no_cross_seed_history(self):
        cfg=r.protocol()
        spend,_,_=r.draws(5)
        h,k=r.transformed(spend,100)
        for i in range(5):
            expected=hill(geometric_adstock(spend[i],alpha=.5,l_max=3,normalize=False),{'k':100,'n':1.5})
            np.testing.assert_allclose(h[i],expected,atol=2e-15,rtol=2e-15)
        changed=spend.copy();changed[:,60:]*=100
        _,k1=r.transformed(spend);_,k2=r.transformed(changed)
        np.testing.assert_array_equal(k1,k2)
        flight,_=r.spend_design(5,'flighting','calendar_aligned',cfg)
        np.testing.assert_array_equal(np.sum(flight[:,:60]>0,axis=1),24)
        np.testing.assert_array_equal(np.sum(flight[:,60:]>0,axis=1),5)

    def test_batch_fwl_matches_full_lstsq_and_hac_and_original_seed42(self):
        spend,noise,_=r.draws(43)
        h,_=r.transformed(spend,100)
        periods,B,_=r.baseline();B=np.asarray(B)
        beta=.08*B[:60].mean()/h[:,:60].mean(axis=1)
        y=B+beta[:,None]*h+.05*B[:60].mean()*noise
        for include,name in [(True,'with-quarter'),(False,'without-quarter')]:
            fitted=estimate(y,h,include)
            spec={'parameters':{'alpha':.5,'l_max':3,'normalize':False,'k':100,'n':1.5},
                  'controls':{'include_quarter_end':include,'structural_breaks':[]}}
            x,names=design(periods,spend[42],spec)
            b,cov,_,_=ols_hac(x[:60],y[42,:60])
            index=names.index('media')
            self.assertAlmostEqual(fitted['beta'][42],b[index],places=7)
            self.assertAlmostEqual(fitted['se'][42],np.sqrt(cov[index,index]),places=7)
            original=json.loads((r.ROOT/f'examples/task-01a/safe/{name}.result.json').read_text())
            self.assertAlmostEqual(fitted['beta'][42],original['coefficients']['media']['estimate'],places=7)
            self.assertAlmostEqual(fitted['se'][42],original['coefficients']['media']['standard_error'],places=7)
            changed=y.copy();changed[:,60:]+=99999
            np.testing.assert_array_equal(estimate(changed,h,include)['beta'],fitted['beta'])
            f=r.flags(b[index],original['coefficients']['media']['lower'],original['coefficients']['media']['upper'],spend[42,:60].min(),spend[42,:60].mean())
            self.assertTrue(f['not_identified']);self.assertTrue(f['sign_uncertain']);self.assertTrue(f['extrapolated_counterfactual'])

    def test_fits_execute_without_private_files_or_generator_modules(self):
        spend,noise,_=r.draws(3);h,_=r.transformed(spend,100)
        expected=estimate(2000+20*h+noise,h,True)
        isolated=r.isolated_estimate(2000+20*h+noise,h)['with-quarter']
        np.testing.assert_array_equal(expected['beta'],isolated['beta'])
        # Actual access guard rejects a deliberately offered external synthetic file.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);safe=root/'safe';safe.mkdir();private=root/'private.txt';private.write_text('synthetic secret')
            shutil.copyfile(r.ROOT/'studio/isolation.py',safe/'isolation.py')
            probe="import sys;sys.path.insert(0,'.');from pathlib import Path;from isolation import guard;guard(Path('.').resolve());Path(sys.argv[1]).read_text()"
            env={k:os.environ[k] for k in ('PATH','LANG') if k in os.environ}
            completed=subprocess.run([sys.executable,'-I','-B','-c',probe,str(private)],cwd=safe,env=env,capture_output=True,text=True)
            self.assertNotEqual(completed.returncode,0);self.assertIn('PermissionError',completed.stderr)

    def test_complete_smoke_determinism_and_manifest_tampering(self):
        from research_benchmark.verify import verify
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            r.run(a,smoke=True);r.run(b,smoke=True)
            verify(a)
            self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},
                             {p.name:p.read_bytes() for p in b.iterdir()})
            with (a/'summary.csv').open() as f:
                import csv
                summaries=list(csv.DictReader(f))
            self.assertEqual(len(summaries),36)
            self.assertTrue(all(int(s['estimated'])+int(s['failed'])==20 for s in summaries))
            # Even refreshing the file hash cannot hide a missing seed/grid row.
            lines=(a/'evaluations.csv').read_text().splitlines()
            (a/'evaluations.csv').write_text('\n'.join(lines[:-1])+'\n')
            m=json.loads((a/'manifest.json').read_text())
            m['files']['evaluations.csv']=hashlib.sha256((a/'evaluations.csv').read_bytes()).hexdigest()
            (a/'manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,'Incomplete grid'):
                verify(a)

    def test_failure_and_rate_denominators(self):
        fitted=estimate(np.ones((2,72)),np.ones((2,72)),True)
        self.assertFalse(fitted['valid'].any())
        self.assertTrue(np.isnan(fitted['beta']).all())
        with self.assertRaises(ValueError):estimate(np.zeros((1,71)),np.zeros((1,71)),True)
        with self.assertRaises(ValueError):estimate(np.full((1,72),np.nan),np.zeros((1,72)),True)
        rate=r.rate(5,100)
        self.assertAlmostEqual(rate['rate'],.05)
        self.assertAlmostEqual(rate['mcse'],np.sqrt(.05*.95/100))
        self.assertLess(rate['lower'],.05);self.assertGreater(rate['upper'],.05)


if __name__=='__main__':unittest.main()
