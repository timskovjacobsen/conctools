

"""Tests for `polysect` module."""

import os
import sys

import pytest

# Get project root directory
root = os.path.abspath('..')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools')

# Import module to test
import polysect     # noqa: 402


def test_polygon_area():

    # Define lists of vertex coordinates
    x = [3, 4, 7, 8, 8.5, 3]
    y = [5, 3, 0, 1, 3, 5]

    # Calculate area by calling the function
    polygon_area = polysect.polygon_area(x, y)

    assert polygon_area == 12.0


def test_polygon_centroid():

    # Define lists of vertex coordinates for testing
    x = [3, 4, 7, 8, 8.5, 3]
    y = [5, 3, 0, 1, 3, 5]

    # Compute centroid of polygon
    cx, cy = polysect.polygon_centroid(x, y)

    assert (cx, cy) == (6.083333333333333, 2.5833333333333335)


def test_stress_block_geometry():
    pass



if __name__ == '__main__':

    # Run some tests
    pass
