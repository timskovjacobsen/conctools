
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
import conctools._geometry as gm


# CONSTANTS
EC = 30 * 10**6
ES = 200 * 10**6


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

        section_above = gm.evaluate_points(x=np.array([cx]), y=np.array([cy]),
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
    # Test if input polygon representing compression zone is non-empty
    if compression_zone.is_empty:
        raise Exception('''Cannot split empty compression zone.''')

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


def full_compression(section, compr_zone, neutral_axis):

    # Split compression zone into compression block and remainder
    compr_block, _ = split_compression_zone(compr_zone, neutral_axis,
                                            section.area, lambda_c=0.8)

    # Set area of concrete in compression to full cross section area
    Ac = compr_block.area

    # Find y-coordinate for centroid compression block
    cy = list(compr_block.centroid.coords)[0][1]

    # Signed dist btw. y-coord of plastic center and centroid of compr block
    arm = section.plastic_centroid[1] - cy

    # Find force and moment contributions to capacity from the concrete
    Fc, Mc = concrete_contributions(Ac, arm, section.fcd, section.alpha_cc)

    # Find distance from each rebar to neutral axis
    rd = distance_to_na(section.rebars, neutral_axis)

    # Make all rebar distances negative, since there's full compression
    rd *= -1

    # Find dist from extreme compression point to neutral axis
    _, failure_dist = gm.furthest_vertex_from_line(compr_zone, neutral_axis)

    return Fc, Mc, rd, failure_dist, compr_block


def full_tension(rebars, neutral_axis):
    '''Return ...

    Parameters
    ----------

    Returns
    -------

    '''
    # Set compression block to empty polygon
    compr_block = Polygon()

    # No concrete in compression => does not contribute to capacity
    Fc, Mc = 0, 0

    # Find distance from each rebar to neutral axis
    rd = distance_to_na(rebars, neutral_axis)

    # Set dist to failure strain point as dist to rebar furthest from na
    failure_dist = abs(max(rd, key=abs))

    return Fc, Mc, rd, failure_dist, compr_block


def mixed_compr_tension(section, compr_zone, tension_zone, neutral_axis):
    '''Return ...

    Parameters
    ----------

    Returns
    -------
    '''
    # Find extreme compression point and dist from that to neutral axis
    p_max, c_max = gm.furthest_vertex_from_line(compr_zone, neutral_axis)

    # Split compression zone into compression block and remainder
    compr_block, _ = split_compression_zone(compr_zone, neutral_axis,
                                            section.area, lambda_c=0.8)

    # Find area of concrete in compression
    Ac = compr_block.area

    # Find centroid height (y-coord) of compr. zone
    cy = compr_block.centroid.y

    # Get y-coordinate of the plastic centroid of the section
    y_plastic_centroid = section.plastic_centroid[1]

    # Dist btw. plastic center of gross section to centroid of compr block
    arm = y_plastic_centroid - cy

    # Find force and moment contributions to capacity from the concrete
    Fc, Mc = concrete_contributions(Ac, arm, section.fcd, section.alpha_cc)

    # Create array w. True for rebars in tension zone, False otherwise
    rebars_tension = gm.points_in_polygon(section.rebars, tension_zone)

    # Find rebars in compression by inverting boolean tension array
    rebars_compr = np.invert(rebars_tension)

    # Find distance from each rebar to neutral axis
    rd = distance_to_na(section.rebars, neutral_axis)

    # Make distance negative for rebars in compression
    rd[rebars_compr] *= -1

    # Compr. and tension, use c_max as dist (with eps_cu3 as failure strain)
    failure_dist = c_max

    return Fc, Mc, rd, failure_dist, compr_block


def find_section_state():
    pass


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
    '''

    # Calculate force contribution from concrete (negative in compression)
    Fc = -alpha_cc * fcd * A_compression / 1000

    # Calculate moment contribution from concrete
    Mc = Fc * lever_arm / 1000

    return Fc, Mc


def steel_contribution(section, rd, failure_dist, eps_failure, Es=200000):
    '''Return ...

    Parameters
    ----------

    Returns
    -------

    Todo
    ----
    * Consider returning a dict with  strains, stresses, forces, arms and
      moments as these are often not directly needed in further
      calculations, but might be valuable for tables, plotting etc.
    '''
    # Compute strain in each rebar
    strains = rebar_strain(rd, failure_dist, eps_failure)

    # Compute rebar stresses
    stresses = strains * Es
    stresses = np.clip(stresses, -section.fyd, section.fyd)

    # Compute rebar force
    forces = stresses * section.As / 1000

    # Get y-coordinate of plastic centroid of section
    y_plastic_centroid = section.plastic_centroid[1]

    # Compute rebar moment
    arms = y_plastic_centroid - section.ys
    moments = forces * arms / 1000

    # Compute total rebar force and moment
    Fs = np.sum(forces)
    Ms = np.sum(moments)

    # Create dict of metadata from calculation
    rebar_metadata = {
        'strains': strains,
        'stresses': stresses,
        'forces': forces,
        'arms': arms,
        'moments': moments,
    }

    return Fs, Ms, rebar_metadata


def distance_to_na(points, neutral_axis):
    '''Return the distance from each rebar to the neutral axis.

    Parameters
    ----------
    points : list (or like-like)
        List of shapely Point(s).
    neutral_axis : shapely LineStrin object
        Line representing the neutral axis.

    Returns
    -------
    numpy ndarray
        Array with elements representing distance from neutral axis to each point.
    '''
    # Return list of distances from each point to the neutral axis
    return np.array([neutral_axis.distance(point) for point in points])


def strain(section, neutral_axis, y_seek=None, eps_c=None, eps_cu=None,
           compr_above=True):
    '''Return the strain at a location for a given cross section state.

    section : shapely Polygon
        Section geometry.
    neutral axis : shapely LineString
        Line consisting of exactly two points defining the neutral axis.
    y_seek : number, optional
        y-coordinate at which strain is desired. Defaults to `None`, and thereby using
        the point in the cross section that has the maximum strain.
    eps_c : number, optional
        Failure strain of concrete when section is subjected to uniform
        compression.
        Defaults to the value embedded in `section`.
    eps_cu : number, optional
        Failure strain of concrete under combined effects.
        Defaults to the value embedded in `section`.
    compr_above : bool, optional
        Whether compression is considered to be above or below the neutral
        axis. Defaults to `True`.

    Returns
    -------
    number
        The strain at the y-coordinate `y_seek`.

    Notes
    -----
    When the section is in full tension, the strain is taken as 0.0035 as for
    case with a mixed compression/tension section. In reality the failure
    strain will be the steel tensile failure strain, but since the rebars are
    sure to have yielded at a strain of 0.0035 the forces (and thereby the
    capacity) will be the same.

    TODO Setup tests!
    '''

    # Set failure strains to those of `section` if they were not inputted
    if not eps_c:
        eps_c = section.eps_c
    if not eps_cu:
        eps_cu = section.eps_cu

    # Extract the two y-coordinates of the netural axis
    ys = [sublist[1] for sublist in list(neutral_axis.coords)]

    # Check if neutral axis is horizontal, if not raise an error
    if not ys[0] == ys[1]:
        raise NotImplementedError(f'''
    Currently this function only supports cases with horizontal neutral axis.
    The inputted neutral axis has y1={ys[0]} and y2={ys[1]}.''')

    # Get upper and lower bound of cross section
    _, miny, _, maxy = section.bounds

    # Set up coordinates for linear interpolation
    x1 = ys[0]
    y1 = 0
    x2 = (miny + maxy) / 2
    y2 = eps_c

    # If `y_seek` was not input, use the y-coord of max strain in the section
    if not y_seek:
        y_seek = maxy if compr_above else miny

    # Calculate strain at desired point by linear interpolation
    # Note: `y_seek` is technically an x-coordinate in the interpolation
    try:
        eps = (y2 - y1) / (x2 - x1) * (y_seek - x1) + y1
    except ZeroDivisionError:
        eps = 0

    # Set the y-coord. at which the section enters full compr. state (top or bottom)
    y_full_compression = miny if compr_above else maxy

    if compr_above:
        # Return computed strain if section is in full compression, eps_cu otherwise
        return eps if x1 < y_full_compression else 0.0035
    else:
        return eps if x1 > y_full_compression else 0.0035


def rebar_strain(rebar_dist, failure_dist, eps_failure):
    '''

    Parameters
    ----------
    rebar_dist : numpy ndarray
        ...
    failure_dist : number
        Distance from neutral axis to point of failure strain, i.e. eps_failure

    For EN 1992-1-1:
        eps_cu=0.0035, eps_c2=0.002, eps_su=0.025
    '''
    return eps_failure * rebar_dist / failure_dist


if __name__ == '__main__':
    pass
