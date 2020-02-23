

'''
'''
# Standard library imports
from math import pi

# Third party imports
import numpy as np


def rebar_coordinates(r_rebars, n_rebars):
    '''
    Return evenly spaced rebars on a circle perimeter.

    Parameters
    ----------
    r_rebars : ...
        ...

    Returns
    -------
        ...
    '''

    theta = np.linspace(0, 2*pi-2*pi/n_rebars, n_rebars)

    return r_rebars * np.cos(theta), r_rebars * np.sin(theta)


def _neutral_axis_locs(bounds, n_locations, traverse_upwards=True):
    '''
    Parameters
    ----------

    Yields
    ------
    number
        ...

    Todo
    ----
    '''
    # Unpack boundary values for traversal
    ymin, ymax = bounds

    # Generate points over the interval
    y_locations = np.linspace(ymin, ymax, n_locations)

    y_locations[0] = -99999
    y_locations[-1] = 99999

    return y_locations if traverse_upwards else np.flip(y_locations)
