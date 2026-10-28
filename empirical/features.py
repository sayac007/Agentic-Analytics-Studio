"""Fixed causal lag/difference features through the audited HypoForge API."""
from functools import lru_cache
import importlib.metadata
import json
import numpy as np
import pandas as pd
from hypoforge import FeatureSpec, evaluate

COMMIT = 'c47f636d24a39a820574a13133d6af693134a180'


@lru_cache(maxsize=1)
def verify_library():
    dist = importlib.metadata.distribution('hypoforge')
    direct = json.loads(dist.read_text('direct_url.json') or '{}')
    if direct.get('vcs_info', {}).get('commit_id') != COMMIT:
        raise ValueError('HypoForge must match the audited pinned Git commit')
    return {'name': 'HypoForge-Python', 'version': dist.version, 'commit': COMMIT,
            'operations': ['diff', 'lag'], 'configured_exogenous_lags': [1, 2, 3]}


def feature(values, operation, periods=1):
    verify_library()
    if operation not in ('lag', 'diff') or type(periods) is not int or periods not in (1, 2, 3):
        raise ValueError('Only the predeclared causal lag/difference features are allowed')
    array = np.asarray(values, dtype=float)
    # Complete calendar slots are retained; missing observations are never dropped.
    frame = pd.DataFrame({'value': array}, index=pd.period_range('2018-01', periods=len(array), freq='M'))
    spec = FeatureSpec(f'fixed_{operation}_{periods}', operation, ('value',),
                       (('periods', periods),), lookback=periods)
    return evaluate(spec, frame).to_numpy(dtype=float)
