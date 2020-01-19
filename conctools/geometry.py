# coding=utf-8


''' Module containing utility functions for use in various other modules. 


--- Todo ---
1. Find stress block geometry
    a. Create a line representing the neutral axis (must extend outside of section)
    b. Find intersections between neutral axis and section
    c. Trim neutral axis to section
    d. Split section by neutral axis


'''

# Standard library imports
from math import atan

# Third party imports
import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString


def create_line(angle, y_intersect):
    '''
    '''
    # Convert angle to radians
    angle = np.radians(angle)

    # Create points (-100000, y1) and (100000, y2) on the line
    y1 = np.tan(angle) * -100000 + y_intersect
    y2 = np.tan(angle) * 100000 + y_intersect

    # Create and return a line from the two points
    return LineString([(-100000, y1), (100000, y2)])


def points_in_polygon(points, polygon):
    '''Return a boolean array indicating whether each point is inside the polygon.

    Parameters
    ----------
    points : list (or list-like)
        List of shapely Point(s) to test
    polygon : polygon object
        Shapely Polygon object

    Returns
    -------
    numpy ndarray
        Boolean array indicating whether each test point is contained by the
        polygon or not.
    '''
    return np.array([polygon.contains(point) for point in points])


def polygon_line_intersections(polygon, line):
    '''
    '''
    return polygon.intersection(line)


def polygon_height(polygon):
    '''Return the height in y-direction of a polygon.

    '''
    # Get zone boundaries
    _, ycmin, _, ycmax = polygon.bounds

    # Compute height and return
    return ycmax - ycmin


def evaluate_points(x, y, angle_deg, y_intersect):
    '''Return a boolean array indicating whether each point is above the line.

    The returned array has elements True or False depending on whether the
    point is above or below the line, respectively.

    Points that are exactly on the line will evaluate to True.

    Parameters
    ----------


    Returns
    -------
    array
        Array of evaluation values for each input point

    Theory
    ------
    A straight line is defined as

            y = a * x + b

    Given a point P(x, y), the point can be evaluated by use of the line as

            point_evaluation = a * x + b - y

    The line orientation is such that points above the line will evaluate to
    positive values if

        0 < `angle_deg` < 90    and     270 < `angle_deg` < 360

    And negative values if

       90 < `angle_deg` < 270

    After this evaluation the values are converted to True and
    False where True will always mean 'above' the line.

    Notes
    ----

    '''
    # Find which interval the angle resides in
    if 0 <= angle_deg <= 270:
        pass

    # Convert input angle from [deg] to [rad]
    angle = np.radians(angle_deg)

    # Evaluate all points
    eval_points = angle * x + y_intersect - y

    # Create boolean array and return (True for points above line and False for below)
    return eval_points <= 0


def line_equation(linestring):
    '''Return the mathematical line equation of a Shapely LineString.

    The line equation has the format `y = m * x + b`. The function will return
    the slope in degrees and the y-coordinate of the line's intersection with
    the y-axis.

    Parameters
    ----------
    linestring : Shapely LineString object
        A LineString with exactly two points defining a straight line.

    Returns
    -------
    tuple
        The angle between the line and the x-axis and as first element and the
        intersection between the line and the y-axis as second elemnet.

    '''
    # Create a shapely LineString representing the y-axis
    y_axis = LineString([(0, -100000), (0, 100000)])

    # Find y-coordinate of intersection between neutral axis and y-axis
    y_intersect = linestring.intersection(y_axis).y

    # Extract start and end point coordinates for neutral axis
    p1, p2 = list(linestring.coords)[0], list(linestring.coords)[1]

    try:
        # Calcultate slope of neutral axis
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    except ZeroDivisionError:
        # x-coordinates of point 1 and 2 must be equal => slope is 0
        slope = 0

    # Find angle for neutral axis
    angle = atan(slope)

    return angle, y_intersect


def project_point_to_line(linestring, point):
    '''Return coordinates of point projected onto a line.'''

    # Get x- and y-coordinates (u and v) for line start and end points
    u, v = np.array(linestring.coords[0]), np.array(linestring.coords[1])

    # Get coordinates of point
    p = np.array(point.coords[0])

    # Distance between desired projection point and the given point
    d = np.dot(v - u, p - u) / np.linalg.norm(v - u)

    # Calculate coordinates of projected point as array
    projected_coordinates = u + d * (v - u) / np.linalg.norm(v - u)

    return projected_coordinates


def move_point_towards_point(startpoint, directionpoint, relativedist=1.0):
    '''Return the vector that offsets a point a distance towards another point.

    Parameters
    ----------
    startpoint : shapely Point object
        Start point for offset, in format (x, y).
    directionpoint : shapely Point object
        Point that the offset will travel towards, in the format (x, y).
    relativedist : number, optional
        The relative distance for the offset compared to the full distance
        between the points. Defaults to 1.0, meaning the offset is equal to
        the full distance.

    Returns
    -------
    TODO
    '''
    # Get the coordinates of the points
    x1, y1 = list(startpoint.coords)[0]
    x2, y2 = list(directionpoint.coords)[0]

    # Compute destinateion coordinates after desired move
    x_destination = (1 - relativedist) * x1 + relativedist * x2
    y_destination = (1 - relativedist) * y1 + relativedist * y2

    # Compute offsets in each direction required to move to destination point
    x_offset = x_destination - x1
    y_offset = y_destination - y1

    return x_offset, y_offset


def furthest_vertex_from_line(polygon, linestring):
    '''Return the polygon vertex furthest from a line along with the distance.'''
    # Get all polygon vertices
    vertices = polygon.exterior.coords

    # Create a shapely Point object at each vertex
    points = [Point(vertex) for vertex in vertices]

    # Compute distance from line to all polygon vertices
    vertex_dist = [linestring.distance(point) for point in points]

    # Get index of maximum distance
    idx_max = np.argmax(vertex_dist)

    # Extract and return largest distance
    return points[idx_max], vertex_dist[idx_max]


if __name__ == '__main__':
    x = np.array([-100, 100])
    y = np.array([-100, -100])
    y_intersect = -150
    angle = 89
    ep = evaluate_points(x, y, angle, y_intersect)
    print(ep)

    import matplotlib.pyplot as plt

    x1, x2 = 0, 0
    y1 = np.radians(angle) * x1 + y_intersect
    y2 = np.radians(angle) * x2 + y_intersect

    plt.plot(x, y, '.')
    plt.plot([x1, x2], [y1, y2])
    plt.axis('equal')
    plt.show()

