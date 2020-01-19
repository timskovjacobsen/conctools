#!/usr/bin/env python

"""
Tests for `conctools` package.

References used for tests
    [1]: Reinforced Concrete Design to Eurocode 2, 7th Edition
            Bill Mosley, John Bungey and Ray Hulse
"""

# Standard library imports
import sys
import os

# Third party imports
import pytest
import numpy as np
from numpy.testing import assert_almost_equal
from numpy.testing import assert_array_almost_equal

# Get project root directory
root = os.path.abspath('.')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools')

# Import module to test and other project specific imports
from conctools import Section       # noqa: 402


@pytest.fixture
def ref1_example_4_10():
    '''
    Fixture for example 4.10 in [1].
    '''

    x = [0, 0, 350, 350]
    y = [0, 450, 450]

    fck = 25
    fyk = 500

    # Rebar coordinates and diameters
    xs = [60, 290, 60, 290]
    ys = [60, 60, 390, 390]
    ds = [25, 25, 32, 32]

    # Neutral axis locations (Note: in the example it is measured from the top of
    # the section, but here it's converted to be from the bottom)
    na = [450-60, 450-158, 450-241, 60, 0, -np.Infinity]

    # Normal force and moment capacities
    N = [189, -899, 1229, 2248, 2580, 3361]
    M = [121, 275, 292, 192, 146, 0]

    return x, y, fck, fyk, xs, ys, ds, na, N, M


def test_capacity_diagram_ref1_example_4_10(ref1_example_4_10):
    '''  '''
    #
    # ----- Setup --------
    # Get values from fixture for example 4.10
    x, y, fck, fyk, xs, ys, ds, na, N, M = ref1_example_4_10

    # Initiate class instance
    section = Section(vertices=[x, y], rebars=[xs, ys, ds], fck=fck, fyk=fyk)

    desired = (N, M)

    # ----- Exercise -----
    actual = section.capacity_diagram()

    # ----- Verify -------
    assert_array_almost_equal(desired, actual)


# def test_elastic_centroid(self):
#     '''TODO'''
#     pass


def test_plastic_centroid():
    '''Test against example 4.10 from ref. [1] above.'''
    # ----- Setup --------
    x = [0, 350, 350, 0]
    y = [0, 0, 450, 450]
    xs = [60, 290, 60, 290]
    ys = [60, 60, 390, 390]
    ds = [25, 25, 32, 32]
    fck, fyk = 25, 500
    alpha_cc = 0.85

    # Create a cross section instance based on input from example
    section = Section(vertices=[x, y], rebars=[xs, ys, ds], fck=fck, fyk=fyk,
                      gamma_c=1.5, gamma_s=1.15, alpha_cc=alpha_cc)

    desired = (175, 238)

    # ----- Exercise -----
    actual = section.plastic_centroid

    # ----- Verify -------
    assert_almost_equal(desired, actual, decimal=0)
