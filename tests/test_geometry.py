
"""Tests for `geometry` module."""

# Standard library imports
import os
import sys

# Third party imports
import numpy as np
from numpy.testing import assert_array_almost_equal
from shapely.geometry import Point
from shapely.geometry import Polygon

# Get project root directory
root = os.path.abspath('..')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools\\conctools')

# Import module to test
import _geometry as gm   # noqa: 402


def test_evaluate_points_1():

    # ----- Setup -----
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([-3, 0, 3, 6, 9])
    angle, y_intersect = 0, 2

    desired = np.array([False, False, True, True, True])

    # ----- Exercise -----
    actual = gm.evaluate_points(x, y, angle, y_intersect)

    # ----- Verify -----
    assert_array_almost_equal(actual, desired)


def test_evaluate_points_negative():
    # ----- Setup -----
    x = np.array([175, 175])
    y = np.array([-30, -255])
    angle, y_intersect = 0, -60

    desired = np.array([True, False])

    # ----- Exercise -----
    actual = gm.evaluate_points(x, y, angle, y_intersect)

    # ----- Verify -----
    assert_array_almost_equal(actual, desired)


def test_points_in_polygon_rectangle():

    # ----- Setup -----
    x = [0, 0, 250, 250]
    y = [0, 300, 300, 0]
    xs = [40, 125, 210, 40, 210]
    ys = [40, 40, 40, 460, 460]

    # Create a shapely polygon from cross section vertices
    polygon = Polygon([(xi, yi) for xi, yi in zip(x, y)])

    # Create a list of shapely points from rebar coordinates
    points = [Point(xr, yr) for xr, yr in zip(xs, ys)]

    desired = np.array([True, True, True, False, False])

    # ----- Exercise -----
    actual = gm.points_in_polygon(points=points, polygon=polygon)

    # ----- Verify -----
    assert_array_almost_equal(actual, desired)


def test_create_line():
    pass


def translate_line():
    '''
    '''
    pass
