from math import cos, sin, pi, acos
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def circle_segment_area_cog(d, y):
    '''
    Return the area and centre of gravity for a circle segment from a circle
    with radius `r`. The circle segment is defined by a horizontal chord at 
    the vertical coordinate `y`.
    '''
    # Initiate arrays with zeros
    n = len(y)
    A, cog, theta = np.zeros(n), np.zeros(n), np.zeros(n)

    # Get indices of y-coordinates corresponding to pure compression
    r = 0.5 * d
    idx_full = np.where(y <= -r)

    # Set area of centre of gravity for pure compression cases
    A[idx_full] = pi * d**2 / 4
    cog[idx_full] = 0

    # Get indices of y-coordinates corresponding to pure tension
    idx_empty = np.where(y >= r)

    # Set area and centre of gravity for pure tension cases
    A[idx_empty] = 0
    cog[idx_empty] = 0

    # Get indices of y-coordinates corresponding to partial compression/tension (circle segment)
    idx_partial = np.where((-r < y) & (y < r))

    # Compute the angle defining the circle segment, i.e. angle between chord and circumference
    theta = 2 * np.arccos(y[idx_partial] / r)

    # Compute area of circle segment
    A[idx_partial] = r**2 / 2 * (theta - np.sin(theta))

    # Compute centre of gravity of circle segment
    cog[idx_partial] = (2 * r * np.sin(theta / 2))**2 / (12 * A[idx_partial])
    chordlength = chord_length(r, theta)
    cog[idx_partial] = circle_segment_cog(A[idx_partial], chordlength)

    for th, a, cogg in zip(theta, A[idx_partial], cog[idx_partial]):
        print(f'{th:.2f}     {a:.2f}    {cogg:.2f}')

    return A, cog*10


def circle_segment_angle(radius, y_chord):
    ''' Return the angle between the lines from the circle center
    to each of the intersections between chord and circle circumference '''
    return 2 * np.arccos(y_chord / radius)


def circle_segment_area(radius, y):
    '''
    Return the area of the circle segment defined by `theta`.

    Parameters
    ----------
    radius : float
        Radius of the full circle.
    y : array
        Array of y-coordinates to compute circle segment area for

    '''
    area = np.zeros(len(y))

    idx_compr = np.where(y < radius)
    area[idx_compr] = pi * radius**2

    idx_tens = np.where(y >= radius)
    area[idx_tens] = 0

    idx_mix = np.where((y > -r) & (y < r))
    theta = circle_segment_angle(radius, y[idx_mix])
    area[idx_mix] = radius**2 / 2 * (theta - np.sin(theta))

    return area


def chord_length(radius, y_chord):
    ''' Return the length of the circle chord defined by `y_chord`
    Circle assumed to have center in (0, 0).
    '''
    theta = circle_segment_angle(radius, y_chord)

    return (2*radius * np.sin(theta / 2))**2


def circle_segment_cog(radius, y_chord):
    print(y_chord)

    area = circle_segment_area(radius, y_chord)

    return chord_length(radius, y_chord) / (12 * area)


if __name__ == '__main__':
    d = 600
    r = d/2
    ns = 10
    ø = 25
    c = 45
    As = pi*ø**2/4
    n_loc = 20

    import sectiongen as sg
    yn = sg.na_locations(d/2, n_loc, direction='downwards')
    # yn = sg.na_locations(d/2, n_loc, direction='upwards')
    print(yn)

    A = circle_segment_area(r, yn)
    print(A)

    cog = circle_segment_cog(r, yn)
    print(cog)


# class CircularSection():

#     def __init__(self, r, n_bars, d_bars):

#         # Initiate instance variables
#         self.d = d
#         self.r = d/2
#         self.n_bars = n_bars
#         self.d_bars = d_bars

#         # Calculate area of ciruclar concrete column
#         self.Ac = pi * self.r**2


# section = CircularSection(d, ns, ø)
