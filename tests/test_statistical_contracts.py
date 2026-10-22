"""Separation, provenance admission and Stability file semantics; no MMM fitting."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
import contracts.validate as v
from support import graph, template, store, artifact, interval


class StatisticalContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.docs=graph(self.root)

    def reject(self, validator, document, mutate):
        changed=copy.deepcopy(document)
        mutate(changed)
        with self.assertRaises((ValueError,ValidationError)):
            validator(changed,self.root)

    def test_positive_file_graph_and_shared_truth(self):
        v.validate_generator(self.docs['generator'],self.root)
        v.validate_truth(self.docs['truth'],self.root)
        v.validate_result(self.docs['result'],self.root)
        v.validate_comparison(self.docs['comparison'],self.root)
        v.validate_evaluation(self.docs['evaluation'],self.root)
        second=copy.deepcopy(self.docs['evaluation'])
        second['run_id']='right'
        second['result']=artifact(self.root,'right.json')
        v.validate_evaluation(second,self.root)

    def test_estimator_never_reads_private_reference_or_truth(self):
        manifest=json.loads((self.root/'left-manifest.json').read_text())
        original=v.artifact_bytes
        paths=[]
        def record(artifact,root):
            paths.append(artifact['path'])
            return original(artifact,root)
        with patch.object(v,'artifact_bytes',side_effect=record):
            v.validate_manifest(manifest,self.root)
        self.assertEqual(paths,['data.csv'])
        for name in ['reference.csv','truth.json','generator.json']:(self.root/name).unlink()
        self.assertEqual(v.validate_manifest(manifest,self.root),60)

    def test_no_observed_reference_or_truth_fields_on_estimator_interface(self):
        for field,value in [('reference',{'path':'reference.csv','sha256':'0'*64}),
                            ('observed_registrations',[1,2]),('observed_reference',[1,2]),
                            ('truth',{'media_coefficient':1}),('coefficients',{'media':1})]:
            for location in [(),('estimation',),('estimation','controls'),('estimation','parameters')]:
                with self.subTest(field=field,location=location):
                    manifest=template()
                    target=manifest
                    for key in location:target=target[key]
                    target[field]=value
                    with self.assertRaises(ValidationError):v.validate_manifest(manifest)
        for field in ['observed_registrations','media_coefficient','ground_truth']:
            manifest=template()
            manifest['columns'][field]=copy.deepcopy(manifest['columns']['synthetic_media'])
            with self.assertRaises(ValidationError):v.validate_manifest(manifest)

    def test_estimator_csv_rejects_reference_and_truth_columns(self):
        manifest=json.loads((self.root/'left-manifest.json').read_text())
        original=(self.root/'data.csv').read_text()
        for column in ['observed_registrations','truth_media_coefficient']:
            text='\n'.join(line+(','+column if index==0 else ',12')
                           for index,line in enumerate(original.splitlines()))+'\n'
            (self.root/'injected.csv').write_text(text)
            manifest['data']=artifact(self.root,'injected.csv')
            with self.subTest(column=column),self.assertRaises(ValueError):
                v.validate_manifest(manifest,self.root)
        manifest['data']=artifact(self.root,'reference.csv')
        with self.assertRaises(ValueError):v.validate_manifest(manifest,self.root)

    def test_contract_fixture_cannot_be_a_benchmark(self):
        with self.assertRaises(ValueError):v.validate_manifest(template(),require_benchmark=True)
        short=template();short['purpose']='development_benchmark'
        with self.assertRaises(ValueError):v.validate_manifest(short)
        full=json.loads((self.root/'left-manifest.json').read_text())
        full['purpose']='development_benchmark'
        self.assertEqual(v.validate_manifest(full,self.root,require_benchmark=True),60)
        full['split'].update(train_end='2022-11',test_start='2022-12')
        with self.assertRaises(ValueError):v.validate_manifest(full,self.root)
        full['split'].update(train_end='2023-01',test_start='2023-02')
        with self.assertRaises(ValueError):v.validate_manifest(full,self.root)

    def test_generator_reference_output_separation(self):
        for field in ['estimator_data','truth']:
            self.reject(v.validate_generator,self.docs['generator'],
                        lambda g:g['outputs'].update({field:'reference.csv'}))
        self.reject(v.validate_generator,self.docs['generator'],
                    lambda g:g['outputs'].update(truth='data.csv'))

    def test_structural_breaks_need_prespecified_evidence(self):
        manifest=json.loads((self.root/'left-manifest.json').read_text())
        manifest['estimation']['specified_on']='2022-12-31'
        change={'id':'example_only','start':'2020-01','evidence_url':'https://example.org/dated-notice',
                'evidence_sha256':'0'*64,'published_on':'2019-12-01','rationale':'Shape-test evidence only'}
        manifest['estimation']['controls']['structural_breaks']=[change]
        self.assertEqual(v.validate_manifest(manifest,self.root),60)
        for mutate in [lambda b:b.pop('evidence_url'),lambda b:b.pop('evidence_sha256'),
                       lambda b:b.update(published_on='2023-01-01'),
                       lambda b:b.update(start='2019-01'),lambda b:b.update(start='2023-01'),
                       lambda b:b.update(evidence_url='file:///reference.csv')]:
            changed=copy.deepcopy(manifest);mutate(changed['estimation']['controls']['structural_breaks'][0])
            with self.subTest(change=changed),self.assertRaises((ValueError,ValidationError)):
                v.validate_manifest(changed,self.root)
        manifest['estimation']['controls']['structural_breaks'].append(copy.deepcopy(change))
        with self.assertRaises(ValueError):v.validate_manifest(manifest,self.root)

    def test_reference_coverage_and_release_ledger(self):
        generator=copy.deepcopy(self.docs['generator'])
        generator['reference_kind']='observed_kba'
        generator['reference_columns']['observed_registrations']['class']='observed'
        periods=[line.split(',')[0] for line in (self.root/'reference.csv').read_text().splitlines()[1:]]
        generator['release_records']=[{'period':p,'source_url':'https://example.org/test-only.xlsx',
                                      'sha256':'0'*64,'version':'test-only','published_on':p+'-01',
                                      'license_identifier':'shape-only','license_url':'https://example.org/license',
                                      'rights_verified':True} for p in periods]
        v.validate_generator(generator,self.root)
        for mutate in [lambda g:g['release_records'].pop(),
                       lambda g:g['release_records'].append(copy.deepcopy(g['release_records'][0])),
                       lambda g:g['coverage'].update(end='2023-11'),
                       lambda g:g['reference_columns']['observed_registrations'].update(redistribution='unknown'),
                       lambda g:g['release_records'][0].update(rights_verified=False)]:
            self.reject(v.validate_generator,generator,mutate)

    def test_confounding_declaration_must_be_consistent(self):
        self.reject(v.validate_generator,self.docs['generator'],
                    lambda g:g['generation'].update(confounding_strength=1))
        self.reject(v.validate_generator,self.docs['generator'],
                    lambda g:g['generation'].update(confounding='quarter_end_and_baseline_peaks'))
        confounded=copy.deepcopy(self.docs['generator'])
        confounded['generation'].update(confounding='quarter_end_and_baseline_peaks',confounding_strength=.5)
        v.validate_generator(confounded,self.root)

    def test_grid_must_be_ordered_distinct_and_inside_training_support(self):
        manifest=json.loads((self.root/'left-manifest.json').read_text())
        for points in [[0,0,2],[0,2,1],[-1,1,2],[0,1,3]]:
            self.reject(v.validate_manifest,manifest,lambda m:m['response_grid'].update(spend=points))

    def test_intervals_contributions_and_curve_semantics(self):
        result=self.docs['result']
        for mutate in [lambda r:r['coefficients']['media'].update(lower=10),
                       lambda r:r['coefficients']['media'].update(standard_error=-1),
                       lambda r:r['contribution'].update(start='2022-12'),
                       lambda r:r['contribution']['monthly_estimate'].pop(),
                       lambda r:r['contribution']['total'].update(estimate=6.1),
                       lambda r:r['contribution'].update(unit='causal_euro_roi'),
                       lambda r:r['response_curve']['upper'].pop(),
                       lambda r:r['response_curve']['lower'].__setitem__(1,10),
                       lambda r:r['response_grid'].update(spend=[0,.5,2])]:
            self.reject(v.validate_result,result,mutate)

    def test_diagnostics_follow_rule_and_failed_rank_cannot_claim_success(self):
        result=copy.deepcopy(self.docs['result'])
        result['diagnostics'].update(scaled_condition_number=1e8,flags=['weak_identification'])
        v.validate_result(result,self.root)
        for mutate in [lambda r:r['diagnostics'].update(flags=[]),
                       lambda r:r['diagnostics'].update(rank=5),
                       lambda r:r['diagnostics'].update(condition_number_limit=1e9),
                       lambda r:r['metrics']['test'].update(n=11)]:
            self.reject(v.validate_result,result,mutate)

    def test_comparison_recomputes_summaries_and_verifies_artifacts(self):
        comparison=self.docs['comparison']
        for mutate in [lambda c:c.update(test_rmse_delta_right_minus_left=1),
                       lambda c:c.update(contribution_delta_right_minus_left=1),
                       lambda c:c.update(response_curve_rmse=1),
                       lambda c:c['response_curve_delta_right_minus_left'].__setitem__(1,1),
                       lambda c:c.update(flags=['unstable_results']),
                       lambda c:c['right'].update(run_id='wrong'),
                       lambda c:c['right']['result'].update(sha256='0'*64)]:
            self.reject(v.validate_comparison,comparison,mutate)
        right=json.loads((self.root/'right.json').read_text())
        right['data_sha256']='0'*64
        changed=copy.deepcopy(comparison)
        changed['right']['result']=store(self.root,'right.json',right)
        with self.assertRaises(ValueError):v.validate_comparison(changed,self.root)

    def test_nonzero_comparison_and_instability_flags(self):
        right=json.loads((self.root/'right.json').read_text())
        right['coefficients']['media']=interval(1.5)
        right['contribution'].update(monthly_estimate=[.75]*12,total=interval(9))
        right['response_curve'].update(estimate=[0,.75,1.5],lower=[-.1,.65,1.4],upper=[.1,.85,1.6])
        right['metrics']['test']['rmse']=2
        right['diagnostics'].update(scaled_condition_number=1e9,flags=['weak_identification'])
        comparison=copy.deepcopy(self.docs['comparison'])
        comparison['right']['result']=store(self.root,'right.json',right)
        comparison.update(test_rmse_delta_right_minus_left=1,
                          media_coefficient_delta_right_minus_left=.5,
                          contribution_delta_right_minus_left=3,
                          response_curve_delta_right_minus_left=[0,.25,.5],
                          response_curve_rmse=((.25**2+.5**2)/3)**.5,
                          relative_curve_change=1/3,flags=['weak_identification','unstable_results'])
        v.validate_comparison(comparison,self.root)

    def test_individually_valid_but_different_grids_cannot_be_compared(self):
        manifest=json.loads((self.root/'right-manifest.json').read_text())
        manifest['response_grid']['spend']=[0,.5,2]
        right=json.loads((self.root/'right.json').read_text())
        right['manifest']=store(self.root,'right-manifest.json',manifest)
        right['response_grid']=manifest['response_grid']
        v.validate_result(right,self.root)
        comparison=copy.deepcopy(self.docs['comparison'])
        comparison['right']['result']=store(self.root,'right.json',right)
        with self.assertRaisesRegex(ValueError,'Comparison support mismatch'):
            v.validate_comparison(comparison,self.root)

    def test_negative_significant_estimate_is_not_positive_detection(self):
        left=json.loads((self.root/'left.json').read_text())
        left['coefficients']['media']=interval(-1)
        left['contribution'].update(monthly_estimate=[-.5]*12,total=interval(-6))
        left['response_curve'].update(estimate=[0,-.5,-1],lower=[-.1,-.6,-1.1],upper=[.1,-.4,-.9])
        evaluation=copy.deepcopy(self.docs['evaluation'])
        evaluation['result']=store(self.root,'left.json',left)
        evaluation.update(media_coefficient_error=-1.9,holdout_contribution_error=-10.8,
                          response_curve_rmse=((.9**2+1.8**2)/3)**.5,
                          media_interval_covers_truth=False,positive_detection=False,two_sided_rejection=True)
        v.validate_evaluation(evaluation,self.root)

    def test_uncalibrated_detection_limit_flag_is_impossible(self):
        for name in ['comparison','evaluation']:
            for field,value in [('effect_below_detection_limit',True),
                                ('effect_below_detection_limit',False),
                                ('detection_limit_status','calibrated')]:
                doc=copy.deepcopy(self.docs[name]);doc[field]=value
                with self.subTest(name=name,field=field),self.assertRaises(ValidationError):
                    v.validate_document(name,doc)
        result=copy.deepcopy(self.docs['result'])
        result['diagnostics']['flags']=['effect_below_detection_limit']
        with self.assertRaises(ValidationError):v.validate_document('result',result)

    def test_evaluator_checks_truth_bindings_and_detection_arithmetic(self):
        for mutate in [lambda e:e.update(media_interval_covers_truth=False),
                       lambda e:e.update(positive_detection=False),
                       lambda e:e.update(response_curve_rmse=100),
                       lambda e:e.update(holdout_contribution_error=0),
                       lambda e:e.update(run_id='wrong')]:
            self.reject(v.validate_evaluation,self.docs['evaluation'],mutate)
        truth=copy.deepcopy(self.docs['truth']);truth['parameters']['alpha']=.7
        changed=copy.deepcopy(self.docs['evaluation'])
        changed['truth']=store(self.root,'truth.json',truth)
        with self.assertRaises(ValueError):v.validate_evaluation(changed,self.root)

    def test_schema_references_resolve_offline(self):
        def references(node):
            if isinstance(node,dict):
                if '$ref' in node:yield node['$ref']
                for value in node.values():yield from references(value)
            elif isinstance(node,list):
                for value in node:yield from references(value)
        for name,schema in v.SCHEMAS.items():
            for reference in references(schema):
                with self.subTest(schema=name,reference=reference):
                    resolved=v.REGISTRY.resolver(schema['$id']).lookup(reference)
                    self.assertIsInstance(resolved.contents,dict)
