
'''
This module contains function for operations on reinforced concrete sections.
'''

# Standard library imports

# Third party imports
import numpy as np
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import split
import shapely

# Project specific imports
import geometry as gm


# CONSTANTS
EC = 30 * 10**6
ES = 200 * 10**6

# TODO OBSOLETE FUNC I THINK; DELETE IF NOT NEEDED (18th Jan 2020)
# def section_split(section, neutral_axis, compr_above=True):
#     '''Return a cross section after split by a neutral axis.

#     Parameters
#     ----------
#     section : shapely Polygon
#         Polygon object describing the section geometry.
#     neutral_axis : shapely LineString
#         LineString object describing the neutral axis of the section.
#     compr_above : bool
#         Whether the compression zone is 'above' or 'below' the neutral axis.
#         The neutral axis is considered as a line going from the end with the
#         smallest x-coordinate to the end with the largest.
#         TODO (DONE!) IMPLEMENT THIS TO DETECT WHERE THE COMPRESSION/TENSION ZONES ARE!

#     Returns
#     -------
#     tuple
#         First and second element represents the compression and tension zone
#         of the cross section, respectively. Zones are in the form of shapely
#         Polygons, which are empty if not present.

#     Assumptions
#     -----------
#     Currently assumes that neutral axis is horizontal, i.e. angle=0
#     '''
#     # Get y-coordinate boundaries for section
#     _, miny, _, maxy = section.bounds

#     # Get y-coordinate of neutral axis (NOTE Assuming angle=0)
#     _, y_na, _, _ = neutral_axis.bounds

#     # Use neutral axis to split the cross section in compression and tension zone
#     # FIXME Find a robust way to know which polygon is compr and tension
#     if neutral_axis.crosses(section):
#         # Section is partly in compression partly in tension

#         # Split section into two polygons for compression and tension zone
#         compr, tension = split(section, neutral_axis)

#     elif maxy <= y_na:
#         # Section is in pure compression

#         # Set compression zone equal to the entire section
#         compr = section

#         # Set tension zone equal to an empty Polygon
#         tension = Polygon()

#     elif miny >= y_na:
#         # Section is in pure tension

#         # Set tension zone equal to the entire section
#         tension = section

#         # Set compression zone equal to an empty Polygon
#         compr = Polygon()

#     return compr, tension


def find_compr_tension_zones(section, neutral_axis, compr_above=True):
    '''Return the compression and tension zone of a cross section.

    Parameters
    ----------

    Returns
    -------
    '''
    # Get the line equation (angle and the y-intersection) of the neutral axis
    angle, y_int = gm.line_equation(neutral_axis)

    if not neutral_axis.crosses(section):
        # Neutral axis is outside of section

        # Extract x- and y-coordinate for centroid of section
        cx, cy = list(section.centroid.coords)[0]

        section_above = gm.evaluate_points(x=np.array([cx]),y=np.array([cy]),
                                           angle_deg=angle, y_intersect=y_int)

        if section_above:
            # Compression zone is above neutral axis

            # Set compression zone equal to the entire section if section is above
            # neutral axis, otherwise set it equal to an empty polygon
            compression_zone = section if compr_above else Polygon()

            # Set tension zone equal to the entire section if section is below
            # neutral axis, otherwise set it to an empty Polygon
            tension_zone = section if not compr_above else Polygon()

        else:
            # Compression zone is below neutral axis

            # Set compression zone equal to the entire section if section is below
            # neutral axis, otherwise set it equal to an empty polygon
            compression_zone = section if not compr_above else Polygon()

            # Set tension zone equal to the entire section if section is above
            # neutral axis, otherwise set it to an empty Polygon
            tension_zone = section if compr_above else Polygon()

        return compression_zone, tension_zone

    # Split section into two polygons by means of neutral axis
    zone1, zone2 = split(section, neutral_axis)

    # Find centroid of the two zones
    centroid_1, centroid_2 = zone1.centroid, zone2.centroid

    # Gather centroid points into arrays
    x_centroids = np.array([centroid_1.x, centroid_2.x])
    y_centroids = np.array([centroid_1.y, centroid_2.y])

    # Evaluate whether the centroid of the zones are above neutral axis
    zone1_above, zone2_above = gm.evaluate_points(x=x_centroids, y=y_centroids,
                                                  angle_deg=angle, y_intersect=y_int)

    # Find out which zone is tension and which is compression
    if zone1_above and not zone2_above:
        if compr_above:
            # Zone 1 is compressive (above neutral axis) and zone 2 is tensile
            compression_zone, tension_zone = zone1, zone2
        else:
            # Zone 1 is tensile and zone 2 is compressive (above neutral axis)
            compression_zone, tension_zone = zone2, zone1

    elif zone2_above and not zone1_above:
        if compr_above:
            # Zone 1 is tensile and zone 2 is compressive (above neutral axis)
            compression_zone, tension_zone = zone2, zone1
        else:
            # Zone 1 is compressive (above neutral axis) and zone 2 is tensile
            compression_zone, tension_zone = zone1, zone2

    else:
        raise Exception('''Compression and tension zones relative to neutral axis
     cannot be determined.''')

    return compression_zone, tension_zone


def split_compression_zone(compression_zone, neutral_axis, A_gross,
                           lambda_c=0.8):
    '''Return the compression block and the remainder of the compression zone.

    The compression zone is split into two parts:

        - compression block
        - remaining zone

    The line that splits the zone is created from a translation of the neutral
    axis. The translation is such that the height of the compression block
    becomes `lambda_c * x`, where `x` denoted the height of the entire
    compression zone that was inputted.
    This operation is used for analysis of a failure state of the cross section.

    Parameters
    ----------
    compression zone : shapely Polygon object
        The part of the cross section that is in compression.
    neutral axis : shapely LineString object
        A line representing the neutral axis of the cross section.
    A_gross : number
        The area of the entire uncracked concrete cross section.
    lambda_c : number, optional
        Coefficient for compression block height compared to compression
        zone height when examining a failure state of the cross section.
        .lambda_c * x, where x is entire height of compression zone.
        Must be less than 1.0. Defaults to 0.8 as per EN 1992-1-1.

    Returns
    -------
    tuple
        Tuple of two Shapely Polygon objects with the compression zone and the
        remainder as first and second element, respectively.

    Theory
    ------
    The compression zone in a failure state analysis consists of a compression
    block which has a height of `lambda_c * x` and a constant stress of `-fcd`
    (if the most common standard stress distribution is adopted). The
    remaining part of the compression zone with height `(1 - lambda_c) * x` is
    the "dead zone" or "remainder", which is not considered to have concrete
    in compression. This zone might have rebars in compression though.

    Note that in the a where the entire section is in full compression and the
    neutral axis just outside of the section, the compression block might not
    take up the entire section.
    '''

    # Get the point of extreme compression (point in compression furthest from na)
    p_max, _, = gm.furthest_vertex_from_line(compression_zone, neutral_axis)

    # Get coordinates for projection of extreme compression point onto neutral axis
    p_projected = gm.project_point_to_line(neutral_axis, p_max)

    # Create a shapely Point object from projected point coordinates
    p_projected = Point(p_projected)

    # Find vector for copying and transalting neutral axis to get splitting line
    dx, dy = gm.move_point_towards_point(p_projected, p_max, relativedist=(1-lambda_c))

    # Create the splitting line from translating the neutral axis
    spliting_line = shapely.affinity.translate(neutral_axis, xoff=dx, yoff=dy)

    # Split the compression zone by means of the moved neutral axis line
    poly_collection = split(compression_zone, spliting_line)

    # Check result of split operation and determine the compression block
    if len(poly_collection) == 2:
        # Extract the two polygons from polygon collection returned by split
        poly1, poly2 = poly_collection

        # Determine distance from neutral axis to centroid of each polygon
        d1 = neutral_axis.distance(poly1.centroid)
        d2 = neutral_axis.distance(poly2.centroid)

        # Check relation betwen distance and determine compression block form that
        if d1 > d2:
            # Polygon 1 is compression block as it has largest dist to neutral axis
            compression_block, remainder = poly1, poly2
        else:
            # Polygon 1 is remainder zone as it has larger dist to neutral axis
            compression_block, remainder = poly2, poly1

        return compression_block, remainder

    else:
        # The compression block consists of the entire setion, remainder is empty 
        return compression_zone, Polygon()


def concrete_contributions(A_compression, lever_arm, fcd, alpha_cc=1.0):
    '''
    Return the contribution from concrete to force and moment capacity of the
    section.

    Parameters
    ----------
    A_compr : number or numpy.ndarray
        Compression areas for each considered location of the neutral axis.
    lever_arm : number
        Lever arm between centroid of gross uncracked section and centroid
        of compression block. Can be negative depending on coordinate system.
    fcd : number
        Design concrete strength
    alpha_cc : number, optional
        Coefficient taking into account long term effects on the
        compressive strength of concrete and unfavorable effects from
        the way loads may be applied. Defaults to 1.0.
        Formula: fcd = alpha_cc * fck / gamma_c

    Returns
    -------
    Fc : number or numpy.ndarray
        Concrete force for each considered location of the neutral axis
    Mc : number or numpy.ndarray
        Concrete moment for each considered location of the neutral axis

    Assumptions:
        * Centroid of uncracked cross section is located at (0, 0)

    TODO Raise error is no split happens (clearly there must be a split)
    '''

    # Calculate force contribution from concrete (negative in compression)
    Fc = -alpha_cc * fcd * A_compression / 1000

    # Calculate moment contribution from concrete
    Mc = Fc * lever_arm / 1000

    return Fc, Mc


def points_distance_to_na(points, angle, y_intersect):
    '''Return the distance from each rebar to the neutral axis.

    Parameters
    ----------
    points : list (or like-like)
        List of shapely Point(s).
    angle : number
        The angle between the neutral axis horizontal [degrees].
    y_intersect : number
        The intersection between the neutral axis and the y-axis.

    Returns
    -------
    numpy ndarray
        Array with elements representing distance from neutral axis to each point.
    '''
    # Create a line representing the neutral axis
    neutral_axis = gm.create_line(angle=angle, y_intersect=y_intersect)

    # Return list of distances from each point to the neutral axis
    return np.array([neutral_axis.distance(point) for point in points])


def na_to_max_strain_circle(radius, yn, rs):
    '''

    TODO Assumes circular section. Stuff in this module should be universal!
    '''

    # Initiate array for storing dist from neutral axis to extreme strain point
    c_max = np.zeros(len(yn))

    # Get indices corresponding to pure tension
    idx_empty = np.where(yn >= radius)

    # Take dist from the neutral axis to rebar furthest away (strain will be eps_su there)
    # REVIEW NEED abs(max(...))?
    c_max[idx_empty] = [max(rebars_at_each_na) for rebars_at_each_na in rs[idx_empty]]

    # Get indices where at least some compression is present
    idx_other = np.where(yn < radius)

    # Take distance from neutral axis to extreme concrete compression fiber (strain will be eps_cu there)
    c_max[idx_other] = radius - yn[idx_other]

    return c_max


def rebar_strain_circle(r, yn, rs, ys, c_max, eps_cu3=0.0035, eps_c2=0.002, eps_su=0.025):

    eps_s = np.empty([len(rs), len(ys)])
    idx_empty = np.where(yn >= r)

    # Calculate {eps_su * rs_i / c_max_i} for all rebars at each na location
    eps_s[idx_empty] = [eps_su * rs[idx_empty][i] / c_max[i]
                        for i in range(len(rs[idx_empty]))]  # NOTE Will be an array

    # Calculate
    idx_full = np.where(yn <= -r)
    if idx_full[0].size != 0:
        eps_s[idx_full] = [eps_c2 * rs[idx_full][i] / c_max[i]
                           for i in range(len(rs[idx_full]))]  # NOTE Will be an array

    idx_partial = np.where((yn > -r) & (yn < r))
    eps_s[idx_partial] = [eps_cu3 * rs[idx_partial][i] / c_max[i]
                          for i in range(len(rs[idx_partial]))]  # NOTE Will be an array

    return eps_s


def rebar_strain(rebar_dist, failure_dist, eps_failure):
    '''

    Parameters
    ----------
    rebar_dist: numpy ndarray
        ...
    failure_dist: number
        Distance from neutral axis to point of failure strain, i.e. eps_failure

    For EN 1992-1-1:
        eps_cu=0.0035, eps_c2=0.002, eps_su=0.025
    '''
    return eps_failure * rebar_dist / failure_dist


def rebar_stress(eps_rebars, fyd=500/1.15, Es=200000):

    sigma_s = np.empty(eps_rebars.shape)

    for idx, na_location in enumerate(eps_rebars):
        sigma_s[idx] = [eps*Es if abs(eps*Es) < fyd else fyd for eps in na_location]

    return sigma_s


def rebar_force(sigma_s, As):
    '''
    Return the total forces generated by all rebars in a cross section given failure states with specific
    neutral axis locations.
    '''
    return sigma_s * As


def rebar_moment(rebar_forces, ys):
    return rebar_forces * ys


def totals(array_of_arrays):
    '''
    Return an array of the sum of each sub array.
    E.g. the sum of all forces for each considered location of the neutral axis.
    '''
    return np.array([np.sum(sub_array) for sub_array in array_of_arrays])


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import geometry as gm

    c_zone = Polygon([(0, 100), (0, 500), (250, 500), (250, 100)])
    na = gm.create_line(angle=0, y_intersect=100),
    A_gross = 125000
    r = split_compression_zone(c_zone, na[0], A_gross)
    # print(r[0].exterior.xy)

    c_zone_compr_vertices = r[0].exterior.xy
    c_zone_remainder_vertices = r[1].exterior.xy

    from shapely.geometry import MultiPolygon
    mp = MultiPolygon(r)
    print(mp)
    print(mp.equals(mp))

    print(c_zone_compr_vertices)
    print(c_zone_remainder_vertices)

    print(np.array(c_zone_compr_vertices))
    print(np.array(c_zone_remainder_vertices))

    c_zone_final = (*c_zone_compr_vertices, *c_zone_remainder_vertices)

    p1 = Polygon([(0, 100), (0, 500), (250, 500), (250, 100)])
    p2 = Polygon([(0, 500), (250, 500), (250, 100), (0, 100)])
    p3 = Polygon([(0, 100), (0, 500), (250, 500), (250, 100)])

    print(p1.is_valid)
    print(p2.is_valid)
    print(p3.is_valid)

    print(p1.equals(p2))
    print(p1.equals(p3))
    print(p1 == p2)
    print(p1 == p3)

    # plt.plot(*c_zone.exterior.xy, '.')
    # plt.plot(*r[0].exterior.xy)
    # plt.show()
