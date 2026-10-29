"""Small synthetic numerical checks; no empirical model is fit in CI."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_allclose
from scipy.stats import multivariate_normal
from regimes import data
from regimes.data import system,PERIODS
from regimes.kalman import filter_numpy,filter_jax,smoothing_mean
from regimes.reference import Reference,covariance
from regimes.evaluation import decompose,forecast
from regimes.inference import prior_graph,numpyro_model,fit,posterior_draws,loglikelihoods
from regimes.recovery import simulate


class CalendarAndData(unittest.TestCase):
    def test_national_weekdays_and_absolute_phase(self):
        cal=data.calendars(("2023-05","2023-12"))
        self.assertEqual(cal[:,3].tolist(),[20,19])
        assert_allclose(cal[0,0],np.sin(2*np.pi*4/12))
        self.assertEqual(cal[:,2].tolist(),[0,1])

    def test_policy_future_knowledge_is_not_retroactive(self):
        p=data.policy(origin="2025-12")
        self.assertTrue(np.all(p[60:,3]==0))
        p=data.policy(origin="2026-01")
        self.assertTrue(np.all(p[60:,3]==1))
        p=data.policy(origin="2026-04",portal=True)
        self.assertEqual(p[64,3],0)
        self.assertEqual(data.policy(origin="2026-05",portal=True)[64,3],1)
        self.assertEqual(data.policy()[35,4],1)
        self.assertEqual(data.policy()[36,5],1)

    def test_design_same_slope_variance_and_exact_state_partition(self):
        for sd in (.10,.05,.03):
            H,F,Q,m,P,n=system("M2",sd,48)
            assert_allclose(np.diag(Q)[:4],[sd*sd,.0001,sd*sd,sd*sd])
            self.assertEqual(H.shape,(69,3,22))
            self.assertEqual(len(n),18)
            self.assertTrue(np.all(H[60:,0,11]==0)) # 2026 intervention unknown at Dec2024.
        with self.assertRaises(ValueError):system("not_prespecified",.03,48)

    def test_read_observed_matches_bound_extraction(self):
        records,counts,y=data.read_observed()
        self.assertEqual(len(records),69)
        self.assertEqual(int(counts[48:60,0].sum()),545142)
        self.assertEqual(int(counts[48:60,1].sum()),19390)
        self.assertTrue(np.isfinite(y).all())

    def test_tampered_audit_and_missing_month_rejected(self):
        original=json.loads((data.ROOT/"data/task04_regimes/data_audit.json").read_text())
        for mutate in ("outcome","month"):
            with tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)
                for name in original["inputs_sha256"]:
                    target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((data.ROOT/name).read_bytes())
                obj=copy.deepcopy(original)
                if mutate=="outcome":obj["monthly"][0]["Tesla"]+=1
                else:obj["monthly"].pop()
                f=root/"data/task04_regimes/data_audit.json";f.parent.mkdir(parents=True);f.write_text(json.dumps(obj))
                with patch.object(data,"ROOT",root),self.assertRaises(ValueError):data.read_observed()

    def test_recovery_is_deterministic_and_separate(self):
        p=json.loads((data.ROOT/"data/task04_regimes/recovery_plan.json").read_text())
        with patch.object(data,"read_observed",side_effect=AssertionError("No observed outcomes")):
            a=simulate(p["cases"][0],p);b=simulate(p["cases"][0],p)
        assert_allclose(a,b,rtol=0,atol=0)
        self.assertEqual(a.shape,(69,3))


class GaussianMath(unittest.TestCase):
    def setUp(self):
        self.S=system("M2",.05,6,periods=PERIODS[:6])
        self.y=np.random.default_rng(8).normal(size=(6,3))
        self.y[:,0]+=np.log(50000)
        self.p=np.array([np.log(.25),.02,np.log(.5),-.01,.04,np.log(.4)])
        self.R=covariance(self.p)

    def dense(self):
        H,F,Q,m,P,_=self.S;n=len(H)
        powers=[np.linalg.matrix_power(F,i)for i in range(n)]
        means=np.array([H[t]@powers[t]@m for t in range(n)])
        C=np.zeros((n,3,n,3))
        for t in range(n):
            for s in range(n):
                V=powers[t]@P@powers[s].T
                for k in range(1,min(t,s)+1):V+=powers[t-k]@Q@powers[s-k].T
                C[t,:,s,:]=H[t]@V@H[s].T+(self.R if t==s else 0)
        return multivariate_normal.logpdf(self.y.ravel(),mean=means.ravel(),cov=C.reshape(3*n,3*n))

    def test_independent_dense_numpy_jax_statsmodels_likelihoods(self):
        import jax.numpy as j
        a=filter_numpy(self.y,*self.S[:5],self.R)[0]
        H,F,Q,m,P,_=self.S
        b=filter_jax(*map(j.asarray,(self.y,H,np.ones(6,dtype=bool),F,Q,m,P,self.R)))[2]
        c=Reference(self.y,self.S).loglike(self.p)
        assert_allclose([a,float(b),c],self.dense(),rtol=1e-9,atol=1e-8)

    def test_pymc_prior_and_numpyro_density_cancel_auxiliary_prior(self):
        import jax.numpy as j
        from numpyro.infer.util import log_density
        lp,R=prior_graph()(j.asarray(self.p))
        assert_allclose(np.asarray(R),self.R,atol=1e-12)
        H,F,Q,m,P,_=self.S
        args=tuple(map(j.asarray,(self.y,H,np.ones(6,dtype=bool),F,Q,m,P)))
        actual,_=log_density(numpyro_model,args,{},{"packed":j.asarray(self.p)})
        assert_allclose(float(actual),float(lp)+self.dense(),atol=1e-8)

    def test_gradient_matches_central_difference(self):
        import jax,jax.numpy as j
        H,F,Q,m,P,_=self.S
        def objective(p):
            _,R=prior_graph()(p)
            return filter_jax(*map(j.asarray,(self.y,H,np.ones(6,dtype=bool),F,Q,m,P)),R)[2]
        grad=np.asarray(jax.grad(objective)(j.asarray(self.p)))
        numeric=[]
        for i in range(6):
            eps=np.zeros(6);eps[i]=1e-5
            a=filter_numpy(self.y,*self.S[:5],covariance(self.p+eps))[0]
            b=filter_numpy(self.y,*self.S[:5],covariance(self.p-eps))[0]
            numeric.append((a-b)/2e-5)
        assert_allclose(grad,numeric,rtol=1e-5,atol=1e-5)

    def test_no_future_outcomes_accepted(self):
        y=np.zeros((6,3));y[4]=1
        with self.assertRaises(ValueError):fit(y,self.S,4,draws=5,tune=5,chains=1)
        with self.assertRaises(ValueError):loglikelihoods(np.tile(self.p,(1,5,1)),y,self.S,4)
        y[:]=np.nan
        with self.assertRaises(ValueError):fit(y,self.S,6,draws=5,tune=5,chains=1)

    def test_prefix_filter_equal_padded_no_future_updates(self):
        import jax.numpy as j
        H,F,Q,m,P,_=self.S
        padded=np.zeros_like(self.y);padded[:4]=self.y[:4]
        ll,a,C,_,_=filter_numpy(self.y[:4],H[:4],F,Q,m,P,self.R)
        got=filter_jax(*map(j.asarray,(padded,H,np.arange(6)<4,F,Q,m,P,self.R)))
        assert_allclose(np.asarray(got[0]),a[-1],atol=1e-9)
        assert_allclose(np.asarray(got[1]),C[-1],atol=1e-9)
        self.assertAlmostEqual(float(got[2]),ll,places=8)

    def test_conditional_draw_moments_and_smoothing(self):
        # Every covariance draw fixed: isolate exact Gaussian conditional sampler.
        result={"packed":np.tile(self.p,(4,500,1)),"ntrain":6,"draws":500,"chains":4}
        end,R,path=posterior_draws(result,self.y,self.S,history=True,seed=15)
        ll,ms,ps,_,_=filter_numpy(self.y,*self.S[:5],self.R)
        expected,_=smoothing_mean(ms,ps,self.S[1],self.S[2])
        se=np.sqrt(np.diag(ps[-1])/len(end))
        self.assertTrue(np.all(abs(end.mean(0)-ms[-1])<6*se+1e-8))
        assert_allclose(path.mean(0),expected[:,:4],atol=.10)

    def test_coherent_counts_and_forecast(self):
        end=np.tile(self.S[3],(100,1));R=np.tile(self.R,(100,1,1))
        values=np.column_stack([np.full(69,100),np.full(69,10),np.full(69,20),np.full(69,1000)])
        S=system("M2",.05,48)
        end=np.tile(S[3],(100,1))
        out=forecast(end,R,S,48,values,[1,3],20)
        for a in out.values():
            self.assertTrue((a>0).all())
            assert_allclose(a[:,1:].sum(axis=1),a[:,0],rtol=1e-12)


class Accounting(unittest.TestCase):
    def test_year_sum_and_ytd_identity(self):
        market=np.arange(69)+100
        tesla=market*(.1+.03*np.sin(np.arange(69)))
        values=np.column_stack([market,tesla,market*.2,market*5])
        rs=decompose(values)
        self.assertEqual(rs[-1]["months"],9)
        for r in rs:
            self.assertAlmostEqual(r["market_component"]+r["share_component"],r["Tesla_change"],places=9)
        self.assertAlmostEqual(rs[-1]["Tesla_after"],tesla[60:69].sum())


class IsolatedRuntime(unittest.TestCase):
    def test_first_use_parallel_prior_then_conditional_draws(self):
        import os,subprocess,sys
        code="""
import numpy as np
from regimes.data import system,PERIODS
from regimes.inference import fit,posterior_draws
S=system('M1',.03,6,periods=PERIODS[:6])
y=np.random.default_rng(8).normal(size=(6,3));y[:,0]+=np.log(50000)
f=fit(y,S,6,draws=10,tune=20,chains=2)
a,R=posterior_draws(f,y,S)
assert a.shape==(20,16) and np.isfinite(a).all()
assert not f['diagnostics']['passed'], 'A 20-draw smoke is not a validated fit'
"""
        env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
        run=__import__("subprocess").run([sys.executable,"-c",code],env=env,cwd=data.ROOT,
                                       capture_output=True,text=True,timeout=120)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_full_sample_proposal_for_rolling_origin_rejected(self):
        from regimes.inference import importance_update
        previous={"ntrain":69,"packed":np.zeros((4,2,6))}
        with self.assertRaises(ValueError):
            importance_update(previous,np.zeros((69,3)),system("M2",.03,48),48)


class ImportanceArithmetic(unittest.TestCase):
    def test_exact_unsmoothed_ratio_weights(self):
        from regimes.inference import importance_update
        previous={"ntrain":48,"packed":np.zeros((2,2,6)),
                  "loglikelihood":np.zeros(4),"logweights":np.full(4,-np.log(4))}
        with patch("regimes.inference.loglikelihoods",return_value=np.log([1,2,3,4])), \
             patch("arviz.psislw",return_value=(np.log([.4,.3,.2,.1]),.2)):
            updated,diag=importance_update(previous,np.zeros((69,3)),system("M2",.03,49),49)
        assert_allclose(np.exp(updated["logweights"]),[.1,.2,.3,.4])
        self.assertAlmostEqual(diag["weight_ess"],1/.3)
        assert_allclose(previous["logweights"],np.full(4,-np.log(4)))

    def test_same_prefix_variant_never_accepts_future_proposal(self):
        from regimes.inference import importance_update
        with self.assertRaises(ValueError):
            importance_update({"ntrain":69},np.zeros((69,3)),system("M2",.03,48),48,same_prefix=True)


class InnovationUnits(unittest.TestCase):
    def test_marginal_standardisation_keeps_target_meaning(self):
        S=system("M1",.03,3,periods=PERIODS[:3]);H,F,Q,m,P,_=S
        R=np.array([[.1,.02,0],[.02,.3,.03],[0,.03,.2]])
        y=np.array([[11.,-.5,.2],[10.9,-.7,.1],[11.1,-.6,.2]])
        _,_,_,err,z=filter_numpy(y,H,F,Q,m,P,R)
        expected=err[0]/np.sqrt(np.diag(H[0]@P@H[0].T+R))
        assert_allclose(z[0],expected)


class PairedInfluence(unittest.TestCase):
    def test_single_target_influence_is_metric_only_not_refit(self):
        from regimes.evaluation import paired_metrics
        rows=[]
        for model,errors in {"M0":[1,1,10],"M1":[1,1,8],"M2":[2,2,1]}.items():
            for i,e in enumerate(errors):
                rows.append(dict(model=model,outcome="Tesla",horizon=1,year=2025,origin=str(i),target=str(i+1),
                                 prediction_mean=100+e,actual=100,lower95=90,upper95=120,scaled_absolute_error=abs(e)))
        rs=paired_metrics(rows);r=next(x for x in rs if x["model"]=="M2")
        self.assertLess(r["rmse_difference"],0)
        self.assertAlmostEqual(r["leave_one_max_difference_vs_M0"],1)
        self.assertAlmostEqual(r["leave_one_max_difference_vs_M1"],1)


class JointUncertainty(unittest.TestCase):
    def test_product_is_taken_before_posterior_average(self):
        coordinates=np.array([[np.log(100),np.log(.1/.8),np.log(.1/.8)],
                              [np.log(200),np.log(.5/.4),np.log(.1/.4)]])
        v=data.counts(coordinates)
        self.assertAlmostEqual(v[:,1].mean(),55)
        self.assertAlmostEqual(v[:,0].mean()*(v[:,1]/v[:,0]).mean(),45)

    def test_latent_draw_decomposition_has_additive_means(self):
        from regimes.assessments import latent_decomposition
        rng=np.random.default_rng(12)
        co=rng.normal(0,.1,(64,69,3));co[:,:,0]+=np.log(1000);co[:,:,1:]-=1
        rows=latent_decomposition("SYNTHETIC",co)
        self.assertEqual(len(rows),5)
        for r in rows:
            self.assertAlmostEqual(r["market_component_mean"]+r["share_component_mean"],r["change_mean"],places=8)
        self.assertEqual(rows[-1]["months"],9)

    def test_diagnostics_covariance_cannot_use_future_prefix(self):
        from regimes.assessments import rolling_diagnostics
        with self.assertRaises(ValueError):
            rolling_diagnostics(np.zeros((48,3)),system("M2",.03,48),{"ntrain":69})


class SupplementaryDiagnostics(unittest.TestCase):
    def test_fixed_burn_in_and_all_annual_windows(self):
        from scripts.task04_diagnostics import summarize
        z=np.random.default_rng(20261029).normal(size=(69,3))
        z[0,0]=9999;z[12,0]=100
        a,o,v=summarize(z)
        self.assertEqual(len(a),36);self.assertEqual(len(o),15);self.assertEqual(len(v),15)
        self.assertEqual(o[0]['period'],'2022-01')
        self.assertEqual(o[0]['standardized_innovation'],100)
        self.assertTrue(all(r['n']==57 for r in a))
        self.assertEqual([r['n'] for r in v[:5]],[12,12,12,12,9])
        self.assertAlmostEqual(v[0]['sd'],z[12:24,0].std(ddof=1))
        self.assertTrue(all(abs(r['acf'])<=1 for r in a))

    def test_truncated_nonfinite_or_constant_diagnostics_refused(self):
        from scripts.task04_diagnostics import summarize
        z=np.random.default_rng(0).normal(size=(69,3))
        for bad in (z[:-1],z*np.nan,np.zeros((69,3))):
            with self.assertRaises(ValueError):summarize(bad)
