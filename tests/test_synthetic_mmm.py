"""Numerical checks and actual isolated execution of the approved single-seed DGP."""
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from contracts import validate as v
from studio.files import artifact, csv_bytes, store, write_once
from studio.generate import baseline, generate
from studio.isolation import stage_workspace
from studio.pipeline import run
from studio.estimate import estimate
from studio.evaluate import verify_bundle
from studio.statistics import design, interval, ols_hac, NORMAL_95
from studio.transforms import hill, media_feature, steady_response_feature
from studio.runtime import versions, HYPOFORGE_COMMIT

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads((ROOT/'config/task-01a.json').read_text())


class Arithmetic(unittest.TestCase):
    def test_audited_dependency_and_hypoforge_transform_values(self):
        self.assertEqual(versions()['hypoforge_commit'],HYPOFORGE_COMMIT)
        parameters=PROTOCOL['parameters']
        from hypoforge.media import geometric_adstock
        np.testing.assert_allclose(geometric_adstock([1,0,0,0,0],alpha=.5,l_max=3,normalize=False),
                                   [1,.5,.25,.125,0],rtol=0,atol=1e-15)
        np.testing.assert_allclose(hill([0,100,200],parameters),
                                   [0,.5,2*math.sqrt(2)/(1+2*math.sqrt(2))],rtol=1e-14)
        for invalid in [[1,np.nan],[1,np.inf],[-1,2]]:
            with self.assertRaises(ValueError):media_feature(invalid,parameters)

    def test_ols_and_three_lag_hac_hand_calculated_example(self):
        # x=-2..2, y=1,0,2,4,3 -> beta=(2,4/5), e=(3,-6,0,6,-3)/5.
        # Bartlett L=3 score meat is diag(18/25,36/25), X'X=diag(5,10).
        # Multiplying by bread twice and 5/(5-2) gives diag(6/125,3/125).
        X=np.column_stack([np.ones(5),[-2,-1,0,1,2]])
        beta,covariance,rank,condition=ols_hac(X,np.array([1,0,2,4,3]),3)
        np.testing.assert_allclose(beta,[2,4/5],rtol=0,atol=1e-14)
        np.testing.assert_allclose(covariance,[[6/125,0],[0,3/125]],rtol=0,atol=1e-14)
        self.assertEqual(rank,2)
        self.assertGreaterEqual(condition,1)
        ci=interval(beta[1],math.sqrt(3/125))
        self.assertAlmostEqual(ci['lower'],.8-1.959963984540054*math.sqrt(.024),14)

    def test_hac_zero_lags_and_finite_sample_correction(self):
        X=np.column_stack([np.ones(5),[-2,-1,0,1,2]])
        _,covariance,_,_=ols_hac(X,np.array([1,0,2,4,3]),0)
        # No autocovariance: meat diag(18/5,144/25), bread diag(1/5,1/10).
        np.testing.assert_allclose(covariance,[[6/25,0],[0,12/125]],atol=1e-14)

    def test_invalid_numeric_and_rank_deficient_fits(self):
        for X,y,lags in [(np.ones((5,2)),np.arange(5),3),
                         (np.eye(2),np.arange(2),1),
                         (np.array([[1,0],[1,np.inf],[1,2]]),np.arange(3),1),
                         (np.column_stack([np.ones(5),np.arange(5)]),np.array([1,2,np.nan,3,4]),3),
                         (np.column_stack([np.ones(5),np.arange(5)]),np.arange(5),5)]:
            with self.subTest(X=X,lags=lags),self.assertRaises(ValueError):ols_hac(X,y,lags)

    def test_baseline_known_components_and_dates(self):
        periods,reference,quarter=baseline()
        self.assertEqual((periods[0],periods[-1],len(periods)),('2018-01','2023-12',72))
        self.assertEqual(reference[[0,2,36,50,71]].tolist(),[2000,2547,3140,4767,3840])
        self.assertEqual(quarter[:12].tolist(),[0,0,1,0,0,1,0,0,1,0,0,1])

    def test_steady_curve_matches_full_constant_spend_history(self):
        parameters=PROTOCOL['parameters']
        for spend in [0,10,100,400]:
            expected=media_feature([spend]*4,parameters)[-1]
            self.assertAlmostEqual(steady_response_feature([spend],parameters)[0],expected,14)

    def test_history_boundary_and_future_causality(self):
        spend=np.arange(1.,73.)
        parameters=PROTOCOL['parameters']
        full=media_feature(spend,parameters)
        accumulated=61+.5*60+.25*59+.125*58
        expected=accumulated**1.5/(100**1.5+accumulated**1.5)
        self.assertAlmostEqual(full[60],expected,14)
        self.assertNotAlmostEqual(full[60],media_feature(spend[60:],parameters)[0],5)
        future=spend.copy();future[60:]=100000
        np.testing.assert_array_equal(full[:60],media_feature(future,parameters)[:60])


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aas-numerical-tests-')
        cls.parent=Path(cls.temp.name)
        cls.bundle=run(cls.parent/'complete')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def result(self,name='with-quarter'):
        return json.loads((self.bundle/f'safe/{name}.result.json').read_text())

    def make_candidate(self,folder,mutate=None):
        folder.mkdir()
        (folder/'safe').mkdir()
        data=(self.bundle/'safe/data.csv').read_bytes()
        (folder/'safe/data.csv').write_bytes(data)
        manifest=json.loads((self.bundle/'safe/with-quarter.manifest.json').read_text())
        manifest['outputs']['result']='safe/candidate.result.json'
        if mutate is not None:mutate(folder,manifest)
        store(folder/'safe/candidate.manifest.json',manifest)
        return manifest

    def test_complete_contract_validated_end_to_end(self):
        inventory=verify_bundle(self.bundle)
        truth=json.loads((self.bundle/'private/truth.json').read_text())
        self.assertEqual(len(truth['true_contribution_monthly']),72)
        for name in ['with-quarter','without-quarter']:
            result=self.result(name)
            self.assertEqual([result['metrics'][p]['n'] for p in ['train','test']],[60,12])
            self.assertEqual(len(result['response_curve']['estimate']),21)
            self.assertEqual(result['software']['hypoforge_commit'],HYPOFORGE_COMMIT)
        self.assertIsNone(self.result('without-quarter')['coefficients']['quarter_end'])
        comparison=json.loads((self.bundle/'comparison.json').read_text())
        self.assertIsNone(comparison['effect_below_detection_limit'])
        self.assertEqual(comparison['detection_limit_status'],'not_calibrated')
        self.assertIn('safe/with-quarter.result.predictions.csv',inventory['artifacts'])

    def test_reference_frozen_before_media_and_never_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_once(root/'protocol.json',(ROOT/'config/task-01a.json').read_bytes())
            original_feature=media_feature
            def inspect(*args):
                reference=root/'private/reference.csv'
                generator=json.loads((root/'private/generator.json').read_text())
                self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(),generator['reference']['sha256'])
                self.assertEqual(reference.stat().st_mode & 0o222,0)
                return original_feature(*args)
            with patch('studio.generate.media_feature',side_effect=inspect):generate(root,PROTOCOL)
            self.assertEqual((root/'private/reference.csv').read_bytes(),(self.bundle/'private/reference.csv').read_bytes())

    def test_deterministic_generation_and_separate_noise_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_once(root/'protocol.json',(ROOT/'config/task-01a.json').read_bytes())
            generate(root,PROTOCOL)
            for name in ['private/reference.csv','private/generator.json','safe/data.csv','private/truth.json',
                         'safe/with-quarter.manifest.json','safe/without-quarter.manifest.json']:
                self.assertEqual((root/name).read_bytes(),(self.bundle/name).read_bytes(),name)
        truth=json.loads((self.bundle/'private/truth.json').read_text())
        rows=v.csv_rows(artifact(self.bundle,'safe/data.csv'),v.COLUMNS,self.bundle)
        _,reference,_=baseline()
        self.assertAlmostEqual(truth['noise_sd'],.05*reference[:60].mean())
        self.assertNotAlmostEqual(truth['noise_sd'],.05*reference.mean())
        noise_seed=np.random.SeedSequence(42).spawn(2)[1]
        noise=np.random.Generator(np.random.PCG64(noise_seed)).normal(0,truth['noise_sd'],72)
        recovered=np.array([float(r['semi_synthetic_outcome']) for r in rows])-reference-np.array(truth['true_contribution_monthly'])
        np.testing.assert_allclose(recovered,noise,rtol=0,atol=1e-12)
        h=media_feature([float(r['synthetic_media']) for r in rows],PROTOCOL['parameters'])
        self.assertAlmostEqual(np.mean(truth['true_contribution_monthly'][:60])/reference[:60].mean(),.08,14)
        self.assertAlmostEqual(truth['media_coefficient'],.08*reference[:60].mean()/h[:60].mean(),12)

    def test_actual_subprocess_has_no_private_files_and_audited_data_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace=Path(directory)
            stage_workspace(self.bundle,workspace,'safe/with-quarter.manifest.json')
            self.assertFalse((workspace/'private').exists())
            self.assertFalse((workspace/'studio/generate.py').exists())
            command=[sys.executable,'-I','-B','-c',
                     "import sys;sys.path.insert(0,'.');from studio.estimate import main;main()",
                     '--root','.', '--manifest','safe/with-quarter.manifest.json']
            subprocess.run(command,cwd=workspace,check=True,capture_output=True,text=True)
            produced=json.loads((workspace/'safe/with-quarter.result.json').read_text())
            self.assertEqual(produced,self.result())
            access=json.loads((workspace/'safe/with-quarter.access.json').read_text())
            self.assertEqual(access['reads'],['safe/data.csv','safe/with-quarter.manifest.json'])
            self.assertFalse((workspace/'private').exists())

    def test_python_data_guard_denies_external_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace=Path(directory)
            stage_workspace(self.bundle,workspace,'safe/with-quarter.manifest.json')
            code="import sys;sys.path.insert(0,'.');from studio.isolation import guard;guard(__import__('pathlib').Path('.'));open(sys.argv[1]).read()"
            failed=subprocess.run([sys.executable,'-I','-B','-c',code,str(self.bundle/'private/reference.csv')],
                                  cwd=workspace,capture_output=True,text=True)
            self.assertNotEqual(failed.returncode,0)
            self.assertIn('PermissionError',failed.stderr)

    def test_missing_dependencies_cannot_emit_successful_result(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace=Path(directory)
            stage_workspace(self.bundle,workspace,'safe/with-quarter.manifest.json')
            code="import sys;sys.path.insert(0,'.');from studio.estimate import main;main()"
            failed=subprocess.run([sys.executable,'-I','-S','-B','-c',code,'--root','.',
                                   '--manifest','safe/with-quarter.manifest.json'],cwd=workspace,capture_output=True,text=True)
            self.assertNotEqual(failed.returncode,0)
            self.assertIn('ModuleNotFoundError',failed.stderr)
            self.assertFalse((workspace/'safe/with-quarter.result.json').exists())

    def test_holdout_target_and_future_spend_cannot_change_fitted_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'candidate'
            def mutate(folder,manifest):
                rows=list(csv.reader((folder/'safe/data.csv').read_text().splitlines()))
                for row in rows[61:]:row[2]=str(float(row[2])+1e6)
                rows[-1][1]='100000'
                (folder/'safe/data.csv').write_bytes(csv_bytes(rows[0],rows[1:]))
                manifest['data']=artifact(folder,'safe/data.csv')
            self.make_candidate(root,mutate)
            changed=estimate(root,'safe/candidate.manifest.json')
            self.assertEqual(changed['coefficients'],self.result()['coefficients'])
            self.assertEqual(changed['response_curve'],self.result()['response_curve'])
            self.assertGreater(changed['metrics']['test']['rmse'],900000)

    def test_real_ols_media_coefficient_matches_independent_fwl_projection(self):
        result=self.result()
        manifest=v.artifact_json(result['manifest'],self.bundle)
        rows=v.csv_rows(manifest['data'],v.COLUMNS,self.bundle)
        X,names=design([r['period'] for r in rows],[float(r['synthetic_media']) for r in rows],manifest['estimation'])
        index=names.index('media')
        nuisance=np.delete(X[:60],index,axis=1)
        q,_=np.linalg.qr(nuisance)
        residual_media=X[:60,index]-q@(q.T@X[:60,index])
        y=np.array([float(r['semi_synthetic_outcome']) for r in rows[:60]])
        beta=float(residual_media@y/(residual_media@residual_media))
        self.assertAlmostEqual(beta,result['coefficients']['media']['estimate'],7)

    def test_contribution_curve_and_first_holdout_prediction(self):
        result=self.result()
        rows=v.csv_rows(artifact(self.bundle,'safe/data.csv'),v.COLUMNS,self.bundle)
        spend=[float(r['synthetic_media']) for r in rows]
        h=media_feature(spend,PROTOCOL['parameters'])
        beta=result['coefficients']['media']['estimate'];se=result['coefficients']['media']['standard_error']
        np.testing.assert_allclose(result['contribution']['monthly_estimate'],beta*h[60:],rtol=1e-14)
        self.assertAlmostEqual(result['contribution']['total']['standard_error'],h[60:].sum()*se,9)
        feature=steady_response_feature(result['response_grid']['spend'],PROTOCOL['parameters'])
        np.testing.assert_allclose(result['response_curve']['lower'],beta*feature-NORMAL_95*se*feature,rtol=1e-14)
        with (self.bundle/'safe/with-quarter.result.predictions.csv').open() as stream:
            first=next(csv.DictReader(stream))
        b={name:interval['estimate'] for name,interval in result['coefficients'].items()}
        expected=b['intercept']+60*b['trend']+b['annual_cos_1']+h[60]*b['media']
        self.assertEqual(first['period'],'2023-01')
        self.assertAlmostEqual(float(first['prediction']),expected,9)

    def test_rank_deficient_actual_estimator_refuses_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'rank-failure'
            def mutate(folder,manifest):
                h=.2+.005*np.arange(72)
                accumulated=100*(h/(1-h))**(1/1.5)
                spend=[]
                for i,target in enumerate(accumulated):
                    spend.append(target-sum(.5**lag*spend[i-lag] for lag in range(1,min(i,3)+1)))
                self.assertGreater(min(spend),0)
                rows=list(csv.reader((folder/'safe/data.csv').read_text().splitlines()))
                for row,x in zip(rows[1:],spend):row[1]=format(x,'.17g')
                (folder/'safe/data.csv').write_bytes(csv_bytes(rows[0],rows[1:]))
                manifest['data']=artifact(folder,'safe/data.csv')
                manifest['response_grid']['spend']=np.linspace(min(spend[:60]),max(spend[:60]),21).tolist()
            self.make_candidate(root,mutate)
            with self.assertRaisesRegex(ValueError,'Rank-deficient'):estimate(root,'safe/candidate.manifest.json')
            self.assertFalse((root/'safe/candidate.result.json').exists())

    def test_invalid_inputs_and_dependency_mismatch_produce_no_success(self):
        variants=['nonfinite','missing_month','hash','version']
        for variant in variants:
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)/'invalid'
                def mutate(folder,manifest):
                    rows=list(csv.reader((folder/'safe/data.csv').read_text().splitlines()))
                    if variant=='nonfinite':rows[2][2]='NaN'
                    if variant=='missing_month':rows.pop(10)
                    if variant in ['nonfinite','missing_month']:
                        (folder/'safe/data.csv').write_bytes(csv_bytes(rows[0],rows[1:]))
                        manifest['data']=artifact(folder,'safe/data.csv')
                    if variant=='hash':manifest['data']['sha256']='0'*64
                self.make_candidate(root,mutate)
                if variant=='version':
                    with patch('studio.estimate.versions',side_effect=RuntimeError('missing pinned dependency')):
                        with self.assertRaises(RuntimeError):estimate(root,'safe/candidate.manifest.json')
                else:
                    with self.assertRaises(ValueError):estimate(root,'safe/candidate.manifest.json')
                self.assertFalse((root/'safe/candidate.result.json').exists())

    def test_existing_result_and_output_bundle_are_not_overwritten(self):
        before=(self.bundle/'inventory.json').read_bytes()
        with self.assertRaises(FileExistsError):run(self.bundle)
        self.assertEqual((self.bundle/'inventory.json').read_bytes(),before)
        with self.assertRaises(FileExistsError):estimate(self.bundle,'safe/with-quarter.manifest.json')
        verify_bundle(self.bundle)

    def test_run_identifier_is_not_an_output_path(self):
        with tempfile.TemporaryDirectory() as directory:
            parent=Path(directory);root=parent/'identifier'
            self.make_candidate(root,lambda folder,manifest:manifest.update(run_id='../../not-a-path'))
            workspace=parent/'isolated';workspace.mkdir()
            stage_workspace(root,workspace,'safe/candidate.manifest.json')
            code="import sys;sys.path.insert(0,'.');from studio.estimate import main;main()"
            subprocess.run([sys.executable,'-I','-B','-c',code,'--root','.',
                            '--manifest','safe/candidate.manifest.json'],cwd=workspace,
                           check=True,capture_output=True,text=True)
            self.assertTrue((workspace/'safe/candidate.result.json').exists())
            self.assertTrue((workspace/'safe/candidate.access.json').exists())
            self.assertFalse((parent/'not-a-path.access.json').exists())

    def test_wrong_dependency_commit_is_rejected(self):
        from unittest.mock import Mock
        from studio.runtime import metadata
        original=metadata.distribution
        wrong=Mock();wrong.version='0.4.0'
        wrong.read_text.return_value=json.dumps({'vcs_info':{'commit_id':'0'*40}})
        with patch('studio.runtime.metadata.distribution',side_effect=lambda name:wrong if name=='hypoforge' else original(name)):
            with self.assertRaisesRegex(RuntimeError,'audited Git commit'):versions()

    def test_inventory_detects_prediction_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            import shutil
            root=Path(directory)/'tampered'
            shutil.copytree(self.bundle,root)
            path=root/'safe/with-quarter.result.predictions.csv'
            path.chmod(0o644)
            path.write_bytes(path.read_bytes().replace(b'2023-01',b'2023-02'))
            with self.assertRaisesRegex(ValueError,'checksum'):verify_bundle(root)

    def test_unlisted_nested_inventory_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            import shutil
            root=Path(directory)/'extra'
            shutil.copytree(self.bundle,root)
            (root/'safe/inventory.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'membership'):verify_bundle(root)

    def test_all_bundle_hashes_reproduce_in_a_second_run(self):
        second=run(self.parent/'repeat')
        self.assertEqual((second/'inventory.json').read_bytes(),(self.bundle/'inventory.json').read_bytes())
        verify_bundle(second)
