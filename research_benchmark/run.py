"""Research task-02 v1: preregistered synthetic operating characteristics, no tuning."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd
from hypoforge import FeatureSpec, evaluate
from hypoforge.media import geometric_adstock

from studio.generate import baseline
from studio.runtime import versions

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'benchmarks/task02/protocol.json'
PROTOCOL_SHA = '71b84713c9c980db172e7bf5692bc85d9912021f85c5f23701d68df67a4a0723'
Z = 1.959963984540054


def protocol():
    if hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() != PROTOCOL_SHA:
        raise ValueError('Frozen new-stage protocol hash mismatch')
    return json.loads(PROTOCOL.read_text())


def draws(n):
    spend, noise, rngs = [], [], []
    for seed in range(n):
        a, b = np.random.SeedSequence(seed).spawn(2)
        rng = np.random.Generator(np.random.PCG64(a))
        spend.append(100*np.exp(.3*rng.standard_normal(72)))
        noise.append(np.random.Generator(np.random.PCG64(b)).standard_normal(72))
        rngs.append(rng)
    return np.array(spend), np.array(noise), rngs


def spend_design(n, design, confounding, cfg):
    spend, noise, rngs = draws(n)
    t = np.arange(72)
    season, quarter = np.sin(2*np.pi*t/12), ((t+1) % 3 == 0)
    if confounding == 'calendar_aligned':
        spend *= np.exp(cfg['calendar_spend_season_strength']*season + cfg['calendar_spend_quarter_strength']*quarter)
    if design == 'flighting':
        weights = np.ones(72) if confounding == 'independent' else np.exp(
            cfg['flighting_selection_season_weight']*season+cfg['flighting_selection_quarter_weight']*quarter)
        on = np.zeros((n,72),dtype=bool)
        for i, rng in enumerate(rngs):
            for start, end, count in [(0,60,24),(60,72,5)]:
                p = weights[start:end]/weights[start:end].sum()
                on[i,start+rng.choice(end-start,count,replace=False,p=p)] = True
        spend = spend*on/.4
    elif design != 'always_on':
        raise ValueError('Undeclared spend design')
    return spend, noise


def transformed(spend, k=None):
    if spend.ndim != 2 or spend.shape[1] != 72 or not np.isfinite(spend).all() or np.any(spend<0):
        raise ValueError('Invalid generated spend')
    # Three zero slots between seed series clear a finite lag-3 kernel exactly.
    padded = np.pad(spend, ((0,0),(0,3)))
    adstock = np.asarray(geometric_adstock(padded.ravel(), alpha=.5, l_max=3, normalize=False)).reshape(padded.shape)[:,:72]
    if k is None:
        k = np.array([np.median(a[:60][s[:60]>0]) for a,s in zip(adstock,spend)])
    else:
        k = np.full(len(spend),float(k))
    if not np.isfinite(k).all() or np.any(k<=0):
        raise ValueError('Invalid train-only Hill scale')
    normalized = adstock/k[:,None]
    spec = FeatureSpec('scaled_hill','hill',('x',),(('k',1.0),('n',1.5)))
    h = evaluate(spec,pd.DataFrame({'x':normalized.ravel()})).to_numpy().reshape(spend.shape)
    return h, k


def isolated_estimate(y,h):
    with tempfile.TemporaryDirectory(prefix='task02-estimator-') as tmp:
        root = Path(tmp)
        shutil.copyfile(ROOT/'research_benchmark/estimator.py',root/'estimator.py')
        shutil.copyfile(ROOT/'studio/isolation.py',root/'isolation.py')
        np.savez(root/'safe.npz',y=y,h=h)
        env = {k:os.environ[k] for k in ('PATH','LANG','SYSTEMROOT') if k in os.environ}
        env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONHASHSEED='0')
        subprocess.run([sys.executable,'-I','-B','-c',"import sys;sys.path.insert(0,'.');import estimator;estimator.main()"],
                       cwd=root,env=env,check=True,capture_output=True)
        with np.load(root/'fit.npz',allow_pickle=False) as loaded:
            return {name:{k:loaded[name+'__'+k].copy() for k in ('beta','se','valid','reason')}
                    for name in ('with-quarter','without-quarter')}


def flags(beta, lower, upper, min_spend, mean_spend):
    sign = lower <= 0 <= upper
    return dict(sign_uncertain=bool(sign),not_identified=bool(sign or upper-lower>abs(beta)),
                extrapolated_counterfactual=bool(min_spend>.01*mean_spend))


def rate(success, scheduled):
    p = success/scheduled
    den=1+Z*Z/scheduled
    center=(p+Z*Z/(2*scheduled))/den
    half=Z*np.sqrt(p*(1-p)/scheduled+Z*Z/(4*scheduled**2))/den
    return dict(rate=p,mcse=float(np.sqrt(p*(1-p)/scheduled)),lower=float(max(0,center-half)),upper=float(min(1,center+half)))


def write_csv(path, rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def summarize(rows, scheduled):
    valid=[r for r in rows if r['status']=='estimated']
    ratios=[r['beta_ratio'] for r in valid if r['beta_ratio'] is not None]
    out=dict(cell=rows[0]['cell'],design=rows[0]['design'],confounding=rows[0]['confounding'],
             effect_fraction=rows[0]['effect_fraction'],model=rows[0]['model'],
             scheduled=scheduled,estimated=len(valid),failed=scheduled-len(valid),
             beta_ratio_q25=float(np.quantile(ratios,.25)) if ratios else None,
             beta_ratio_median=float(np.median(ratios)) if ratios else None,
             beta_ratio_q75=float(np.quantile(ratios,.75)) if ratios else None,
             snr_median=float(np.median([r['snr'] for r in rows])))
    for key in ('rejection','positive_detection','wrong_sign_rejection'):
        for metric,v in rate(sum(r[key] for r in valid),scheduled).items():out[key+'_'+metric]=v
    # Conditional coverage denominator is explicit; no failed fit is discarded silently.
    out['coverage_n']=len(valid)
    coverage=rate(sum(r['covers_truth'] for r in valid),len(valid)) if valid else dict.fromkeys(('rate','mcse','lower','upper'))
    out.update({'coverage_'+k:v for k,v in coverage.items()})
    for key in ('not_identified','sign_uncertain','extrapolated_counterfactual'):
        out[key+'_rate']=sum(r[key] for r in valid)/len(valid) if valid else None
    return out


def run(output,smoke=False):
    cfg=protocol();environment=versions()
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('New run directory required')
    n=20 if smoke else cfg['seeds']
    periods,B,_=baseline();B=np.asarray(B,dtype=float);sigma=.05*B[:60].mean()
    truth_rows=[];evaluations=[];summary=[]
    cells=[('legacy','always_on','independent',e,100) for e in (0,.08)]
    cells += [('grid',d,c,e,None) for d in cfg['spend_designs'] for c in cfg['confounding'] for e in (0,*cfg['effect_fractions'])]
    for family,design,confounding,effect,k_policy in cells:
        cell=f'{family}-{design}-{confounding}-{effect:g}'
        spend,noise=spend_design(n,design,confounding,cfg)
        h,k=transformed(spend,k_policy)
        beta=effect*B[:60].mean()/h[:,:60].mean(axis=1)
        contribution=beta[:,None]*h
        snr=np.std(contribution[:,:60],axis=1,ddof=1)/sigma
        y=B+contribution+sigma*noise
        fits=isolated_estimate(y,h)
        for seed in range(n):
            truth_rows.append(dict(cell=cell,seed=seed,effect_fraction=effect,design=design,confounding=confounding,
                beta=float(beta[seed]),noise_sd=float(sigma),hill_k=float(k[seed]),snr=float(snr[seed]),
                train_on_fraction=float(np.mean(spend[seed,:60]>0)),train_min_spend=float(np.min(spend[seed,:60]))))
        for model,fit in fits.items():
            rows=[]
            for seed in range(n):
                b,s=float(fit['beta'][seed]),float(fit['se'][seed]);ok=bool(fit['valid'][seed])
                lo,hi=(b-Z*s,b+Z*s) if ok else (None,None)
                f=flags(b,lo,hi,spend[seed,:60].min(),spend[seed,:60].mean()) if ok else dict.fromkeys(('sign_uncertain','not_identified','extrapolated_counterfactual'),False)
                row=dict(cell=cell,seed=seed,design=design,confounding=confounding,effect_fraction=effect,model=model,
                    status='estimated' if ok else 'not_estimable',reason=str(fit['reason'][seed]),
                    beta=b if ok else None,se=s if ok else None,lower=lo,upper=hi,
                    beta_ratio=b/beta[seed] if ok and beta[seed]!=0 else None,snr=float(snr[seed]),
                    rejection=bool(ok and (lo>0 or hi<0)),positive_detection=bool(ok and lo>0),
                    wrong_sign_rejection=bool(ok and hi<0),covers_truth=bool(ok and lo<=beta[seed]<=hi),**f)
                rows.append(row)
            evaluations.extend(rows);summary.append(summarize(rows,n))
    thresholds=[]
    for design in cfg['spend_designs']:
        for confounding in cfg['confounding']:
            for model in cfg['models']:
                selected=[s for s in summary if s['cell'].startswith('grid-') and (s['design'],s['confounding'],s['model'])==(design,confounding,model)]
                null=next(s for s in selected if s['effect_fraction']==0)
                candidates=[s for s in selected if s['effect_fraction']>0]
                row=dict(design=design,confounding=confounding,model=model,
                         null_rejection_rate=null['rejection_rate'],null_rejection_mcse=null['rejection_mcse'],
                         label='exploratory_tested_grid_threshold_not_validated_MDE')
                for key in ('rejection','positive_detection'):
                    reached=[s['effect_fraction'] for s in candidates if s[key+'_rate']>=.8]
                    row[key+'_grid_mde']=min(reached) if reached else None
                thresholds.append(row)
    out.mkdir(parents=True)
    write_csv(out/'truth.csv',truth_rows);write_csv(out/'evaluations.csv',evaluations)
    write_csv(out/'summary.csv',summary);write_csv(out/'mde.csv',thresholds)
    legacy=[r for r in evaluations if r['cell']=='legacy-always_on-independent-0.08' and r['seed']==42]
    if legacy:write_csv(out/'legacy_flags.csv',legacy)
    write_csv(out/'reference.csv',[dict(period=p,synthetic_reference=float(v)) for p,v in zip(periods,B)])
    (out/'protocol.json').write_bytes(PROTOCOL.read_bytes())
    plot(summary,out/'power.png')
    (out/'report.md').write_text(report(summary,thresholds,n,smoke))
    manifest=dict(stage='research-task-02',protocol_version=cfg['version'],protocol_sha256=PROTOCOL_SHA,
                  scope='SYNTHETIC_ONLY',seed_start=0,seeds_per_cell=n,smoke_only=smoke,
                  runtime=environment,statsmodels=importlib.metadata.version('statsmodels'),
                  code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},
                  implementation={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                      ('research_benchmark/run.py','research_benchmark/estimator.py','studio/generate.py','studio/isolation.py')},
                  disclaimer='Exploratory synthetic operating characteristics; no real causal ROI or validated continuous MDE')
    (out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n')
    return summary,thresholds


def plot(rows,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
    for ax,model in zip(axes,('with-quarter','without-quarter')):
        for design,color in [('always_on','#286493'),('flighting','#19816a')]:
            for confounding,style in [('independent','-'),('calendar_aligned','--')]:
                s=[r for r in rows if r['cell'].startswith('grid-') and (r['design'],r['confounding'],r['model'])==(design,confounding,model)]
                x=np.array([r['effect_fraction']*100 for r in s]);y=np.array([r['rejection_rate'] for r in s])
                ax.plot(x,y,style,marker='o',color=color,label=design+' / '+confounding)
                ax.fill_between(x,[r['rejection_lower'] for r in s],[r['rejection_upper'] for r in s],color=color,alpha=.09)
        ax.axhline(.8,color='#777',linestyle=':');ax.axhline(.05,color='#999',linestyle=':')
        ax.set(title=model,xlabel='Injected mean effect (%)',ylim=(0,1.02));ax.grid(alpha=.15)
    axes[0].set_ylabel('Nominal two-sided rejection rate (not necessarily valid power)')
    axes[1].legend(fontsize=7,loc='lower right')
    fig.suptitle('Synthetic benchmark — pointwise 95% Monte Carlo Wilson bands')
    fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)


def report(rows,thresholds,n,smoke):
    lines=['# Research task-02: when does the synthetic media effect recover?', '',
           f'{n} seeds per cell; '+('SMOKE ONLY — not scientific power evidence.' if smoke else 'full preregistered grid, no tuning.'),
           '','Only synthetic data. Rejection is not reliable recovery if null size, sign or coverage fails.', '',
           '| Cell | Model | SNR median | β̂/β median [Q1,Q3] | Rejection ± MCSE | Positive detection | Wrong-sign rejection | Coverage ± MCSE | Failed |',
           '|---|---|---:|---|---|---:|---:|---|---:|']
    fmt=lambda v: 'not_estimable' if v is None else f'{v:.3f}'
    for r in rows:
        ratio='undefined (null)' if r['beta_ratio_median'] is None else f"{r['beta_ratio_median']:.3f} [{r['beta_ratio_q25']:.3f}, {r['beta_ratio_q75']:.3f}]"
        lines.append(f"| {r['cell']} | {r['model']} | {r['snr_median']:.3f} | {ratio} | {r['rejection_rate']:.3f} ± {r['rejection_mcse']:.3f} | {r['positive_detection_rate']:.3f} | {r['wrong_sign_rejection_rate']:.3f} | {fmt(r['coverage_rate'])} ± {fmt(r['coverage_mcse'])} | {r['failed']} |")
    lines += ['', '## Grid thresholds (not validated MDE)', '', '| Design | Confounding | Model | Null rejection | Two-sided ≥80% grid threshold | Positive ≥80% grid threshold |','|---|---|---|---:|---|---|']
    for r in thresholds:
        show=lambda v: '>15% / not reached' if v is None else f'{v:.0%}'
        lines.append(f"| {r['design']} | {r['confounding']} | {r['model']} | {r['null_rejection_rate']:.3f} | {show(r['rejection_grid_mde'])} | {show(r['positive_detection_grid_mde'])} |")
    lines += ['', '## Interpretation limits', '',
              'The old small condition number/stability flags do not establish identification. New flags are interval/support heuristics, not causal tests.',
              'Always-on baseline misspecification, narrow transformed spend, confounding and finite-sample HAC calibration can drive bias, wrong signs and false positives.',
              'No curve fitting, lag search, scenario retuning or significance selection. No empirical data or real marketing ROI.',
              'Wilson bounds and denominators are in summary.csv; seed-level truth/evaluations include SNR and every failure. Continuous MDE and general coverage claims are not established.',
              '', '## Reproduction and artifact identity', '',
              '`python -m research_benchmark.run --output NEW_DIRECTORY` with pinned requirements-attention.lock and single-thread BLAS.',
              'The existing synthetic baseline, frozen new protocol, implementation versions and output hashes are bound in manifest.json only.', '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--smoke',action='store_true')
    args=p.parse_args();run(args.output,args.smoke)
    print('Completed synthetic research task-02 '+('smoke' if args.smoke else '1000-seed grid'))


if __name__=='__main__':main()
