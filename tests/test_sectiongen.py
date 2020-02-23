
"""Tests for `sectiongen` module."""

import os
import sys

# import numpy as np
# from numpy.testing import assert_almost_equal, assert_array_almost_equal

# Get project root directory
root = os.path.abspath('..')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools\\conctools')

# Import module to test
import conctools.sectiongen as sg    # noqa: 402


# TODO Adjust tests below after code to be tested was changed.

# def test_neutral_axis_locs_traverse_upwards():

#     # ----- Setup -----
#     bounds = (-300, 300)
#     n_locations = 7

#     desired = np.array([-300, -200, -100, 0, 100, 200, 300])

#     # ----- Exercise -----
#     locations = sg.neutral_axis_locs(bounds, n_locations, traverse_upwards=True)

#     # Unpack generator into array
#     actual = np.array([*locations])

#     # ----- Verify -----
#     assert_array_almost_equal(actual, desired)


# def test_neutral_axis_locs_traverse_downwards():

#     # ----- Setup -----
#     bounds = (-300, 300)
#     n_locations = 7

#     desired = np.array([300, 200, 100, 0, -100, -200, -300])

#     # ----- Exercise -----
#     locations = sg.neutral_axis_locs(bounds, n_locations, traverse_upwards=False)

#     # Unpack generator into array
#     actual = np.array([*locations])

#     # ----- Verify -----
#     assert_array_almost_equal(actual, desired)
