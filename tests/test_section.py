

"""Tests for `section` module."""

import os
import sys

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon

# Get project root directory
root = os.path.abspath('.')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools')

# Import module to test
import section as sec      # noqa: 402

# Other project specific imports
import geometry as gm      # noqa: 402


@pytest.fixture
def rectangular_section():
    # Define coordinates for rectangular section
    x = [0, 0, 250, 250]
    y = [0, 500, 500, 0]

    # Define rebar coordinates
    xs = [40, 125, 210, 40, 210]
    ys = [40, 40, 40, 460, 460]

    return x, y, xs, ys


def test_distance_to_na(rectangular_section):

    # ----- Setup --------
    x, y, xs, ys = rectangular_section

    # Create a shapely Point for each rebar
    rebars = [Point(xi, yi) for xi, yi in zip(xs, ys)]

    # Create neutral axis
    neutral_axis = LineString([(-10000, 300), (10000, 300)])

    desired = np.array([260, 260, 260, 160, 160])

    # ----- Exercise -----
    actual = sec.distance_to_na(rebars, neutral_axis)

    # ----- Verify -------
    assert_array_almost_equal(actual, desired)


# @pytest.mark.parameterize('angle', 'y_intersect', 'desired' [
#     # Neutral axis horizontal and above section
#     (0, 600, ),

#     # Neutral axis horizontal and in upper part of section
#     (0, 400),

#     # Neutral axis horizontal and in
# ])
# def find_compr_tension_zones(rectangular_section):
#     # ----- Setup -------
#     x, y, *_ = rectangular_section

#     # Create rectangle as shapely Polygon
#     rectangle = Polygon([(xi, yi) for xi, yi in zip(x, y)])

#     # Create neutral axis as shapely LineString
#     neutral_axis = gm.create_line(angle=0, y_intersect=600)

#     # Desired results
#     compression_zone = rectangle
#     tension_zone = Polygon()        # Empty Polygon
#     desired = (compression_zone, tension_zone)

#     # ----- Exercise -----
#     actual = sec.find_section_state(rectangle, neutral_axis)

#     # ----- Verify -------
#     assert actual == desired


@pytest.mark.parametrize('compr_zone, neutral_axis, A_gross, desired', [

    # Note: b x h =  250 x 500
    # Compression zone to be split by line
    (
        Polygon([(0, 300), (0, 500), (250, 500), (250, 300)]),
        gm.create_line(angle=0, y_intersect=300),
        125000,
        (
            # Desired (compression block and remaining block)
            Polygon([(0, 340), (0, 500), (250, 500), (250, 340)]),
            Polygon([(0, 300), (0, 340), (250, 340), (250, 300)])
        )
    ),

    # Compression zone after attempted split occupies the entire cross section
    # TODO

    # Tension zone after attempted split occupies the entire cross section
    # TODO

    # Example 4.10 from [1]
    # TODO
    # (Polygon([(0, 0), (0, 450), (350, 450), (350, 0)]),
    #  gm.create_line(angle=0, y_intersect=450-60),
    #  350*450,
    #  (
    #     Polygon([(), (), (), ()]),
    #     Polygon([(), (), (), ()])
    #  )
    # )
])
def test_split_compression_zone(compr_zone, neutral_axis, A_gross, desired):

    # ----- Setup --------
    # Turn tuple of desired polygons(s) into collection (MultiPolygon object)
    desired = MultiPolygon(desired)

    # ----- Exercise -----
    actual = sec.split_compression_zone(compr_zone, neutral_axis, A_gross)

    # Turn tuple of actual polygon(s) into collection (MultiPolygon object)
    actual = MultiPolygon(actual)

    # ----- Verify -------
    # Compare by shapely built-in method
    # FIXME Find out if this is actually a correct way to check if they are equal
    assert actual.equals(desired)


# def test_split_compression_zone_with_empty_zone(compr_zone, neutral_axis, A_gross,
#                                                 desired):
#     # ----- Setup --------
#     # Compression zone is empty

#     compr_zone = Polygon()
#     neutral_axis = gm.create_line(angle=0, y_intersect=600)
#     A_gross = 125000

#     # desired = # TODO How to test for exception?

#     # ----- Exercise -----
#     actual = sec.split_compression_zone(compr_zone, neutral_axis, A_gross)

#     # Turn tuple of actual polygon(s) into collection (MultiPolygon object)
#     actual = MultiPolygon(actual)

#     # ----- Verify -------
#     # Compare by shapely built-in method
#     assert actual.equals(desired)



# def test_concrete_contributions():

#     # ----- Setup --------
#     Ac = 16800
#     lever_arm =


#     # ----- Exercise -----

#     # ----- Verify -------

