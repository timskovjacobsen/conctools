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

    The example comoutes the interaction diagram for a rectangular reinforced
    concrete cross section.
    '''

    x = [0, 0, 350, 350]
    y = [0, -450, -450, 0]

    fck = 25
    fyk = 500
    gamma_c = 1.5
    gamma_s = 1.15
    alpha_cc = 0.85

    # Rebar coordinates and diameters
    xs = [60, 290, 60, 290]
    ys = [-60, -60, -390, -390]
    ds = [32, 32, 25, 25]

    # Neutral axis locations (Note: in the example it is measured from the top of
    # the section, but here it's converted to be from the bottom)
    na_locs = [-60, -158, -241, -390, -450, -9999]

    # Normal force and moment capacities
    # Note: The values have small deviations compared to the textbook example
    #       because of numerical roundoff in the book.
    N = [189, -898, -1230, -2246, -2576, -3357]
    M = [121, 275, 292, 192, 146, 0]

    return x, y, xs, ys, ds, fck, fyk, gamma_c, gamma_s, alpha_cc, na_locs, N, M


def test_capacity_diagram_ref1_example_4_10(ref1_example_4_10):
    '''Test the capacity diagram against known values from example in ref [1].'''

    # ----- Setup --------
    # Get values from fixture for example 4.10
    res = ref1_example_4_10
    x, y, xs, ys, ds, fck, fyk, gamma_c, gamma_s, alpha_cc, na_locs, N, M = res

    # Initiate class instance
    section = Section(vertices=[x, y], rebars=[xs, ys, ds], fck=fck, fyk=fyk,
                      gamma_c=gamma_c, gamma_s=gamma_s, alpha_cc=alpha_cc,
                      eps_c=0.0035)

    desired = (N, M)

    # ----- Exercise -----
    # Compute actual capacity diagram (without metadata)
    Na, Ma, _ = section.capacity_diagram(neutral_axis_locations=na_locs)

    # Remove that points in the computed diagram that is not present in the example
    actual = (Na[:6], Ma[:6])

    # ----- Verify -------
    assert_array_almost_equal(desired, actual, decimal=0)


# def test_elastic_centroid(self):
#     '''TODO'''
#     pass


def test_plastic_centroid_ref1_example_4_10():
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


def test_transformed_area_rectangle():
    pass
