"""Use the audited public HypoForge APIs as the single transform implementation."""
import numpy as np
import pandas as pd
from hypoforge import FeatureSpec, evaluate
from hypoforge.media import geometric_adstock


def finite(values):
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite numerical input or output')
    return values


def hill(values, parameters):
    values = finite(values)
    if np.any(values < 0):
        raise ValueError('Exposure must be nonnegative')
    spec = FeatureSpec('hill_media', 'hill', ('x',),
                       (('k', parameters['k']), ('n', parameters['n'])))
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        return finite(evaluate(spec, pd.DataFrame({'x': values})).to_numpy())


def media_feature(spend, parameters):
    spend = finite(spend)
    if np.any(spend < 0):
        raise ValueError('Spend must be nonnegative')
    adstock = geometric_adstock(spend, alpha=parameters['alpha'],
                               l_max=parameters['l_max'], normalize=parameters['normalize'])
    return hill(adstock, parameters)


def steady_response_feature(spend_grid, parameters):
    # This is the contract's constant-spend history, not a second adstock implementation.
    gain = sum(parameters['alpha'] ** lag for lag in range(parameters['l_max'] + 1))
    return hill(finite(spend_grid) * gain, parameters)
