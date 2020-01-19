# coding=utf-8

"""Main module.


Abbreviations used in comments
    - na : neutral axis

"""


# Third party imports
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
import matplotlib.pyplot as plt

# Project specific imports
import geometry as gm
from sectiongen import neutral_axis_locs
import section as sec


# def pløt_soiction(polygon, na, compr_zone, compr_block):

#     plt.plot(*polygon.exterior.xy)
#     x1, y1, x2, y2 = na.bounds
#     plt.plot([x1, x2], [y1, y2])
#     plt.plot(*compr_zone.exterior.xy)
#     plt.plot(*compr_block.exterior.xy)
#     plt.show()


class Section:
    '''Class for defining a concrete section

    The section can have any non-convex polygon shape.
    '''

    def __init__(self, vertices, rebars, fck, fyk, gamma_c=1.5, gamma_s=1.15,
                 alpha_cc=1.0):
        '''Create a section from coordinates of its vertices.

        Parameters
        ----------
        vertices : list (or like-like)
            List with an array of x-coordinates of the section vertices as first
            element and an array of y-coordinates as second element. Unit: [mm].
        rebars : list (or like-like)
            List with an array of x-coordinates of the rebars as first element, an
            array of y-coordinates of rebars as second element and an array of rebar
            diameters as third element. Unit: [mm] for all three sublists.
        alpha_cc : number
            Coefficient taking into account long term effects on the
            compressive strength of concrete and unfavorable effects from
            the way loads may be applied. Defaults to 1.0.
            Formula: fcd = alpha_cc * fck / gamma_c

        '''
        # Create instance attributes for x- and y-coordinates
        self.x = vertices[0]
        self.y = vertices[1]
        self.fck = fck
        self.fyk = fyk
        self.alpha_cc = alpha_cc

        self.gamma_c = gamma_c
        self.fcd = self.fck / self.gamma_c
        self.gamma_s = gamma_s
        self.fyd = self.fyk / self.gamma_s

        # Create attributes of numpy arrays for rebar coordinates
        self.rebars_list = rebars
        try:
            self.xs = np.array(self.rebars_list[0])
            self.ys = np.array(self.rebars_list[1])
            self.ds = np.array(self.rebars_list[2])
        except IndexError as e:
            print(f'''{e}:
            The rebar input must be a list consisting of exactly three
            lists/arrays. So: rebars=[xs, ys, ds], where `xs`, `ys` and `ds` are
            lists of x- and y-coordinates and diameters, respectively.
            All in [mm].''')

        # Calculate area of rebars
        self.As = np.pi * self.ds**2 / 4

        # Create a shapely Point for each rebar
        self.rebars = [Point(x, y) for x, y in zip(self.xs, self.ys)]

        # Create a shapely polygon object from input vertices
        self.polygon = Polygon([(x, y) for x, y, in zip(self.x, self.y)])

        # Set area as instance attribute
        self.area = self.polygon.area

        # Compute geometric centroid of section and set it as attributes
        self.geometric_centroid = self.polygon.centroid.x, self.polygon.centroid.y

        # Compute elastic centroid of section and set it as attribute
        # self.elastic_centroid = sec.elastic_centroid()

        # Compute plastic centroid of section and set it as attribute
        self.plastic_centroid = self.plastic_centroid()

        # Set boundaries of section (minx, miny, maxx, maxy)
        self.bounds = self.polygon.bounds

    def elastic_centroid(x, y, xr, yr, dia, Ec=30*10**6, Es=200*10**6):
        '''Compute elastic centroid of a reinforced concrete section.

        Return elastic centroid of a transformed reinforced concrete sections.
        Rebars located outside of the concrete defined by x and y is assumed to be
        surrounded by ineffective/cracked concrete.

        Args:
            par1 (type) :
            dia (list) : Rebars diameters

        Returns:
            ret1 (type) :
        TODO REWRITE ENTIRE METHOD (PREVIOUSLY A FUNCTION, BUT NOT DONE WELL)
        '''

        # Stiffness ratio
        n = Es / Ec

        # Number of rebars
        nb = len(dia)

        # Rebars that are surrounded by ineffective/cracked concrete will have a
        # transformed stiffness of 'n', while rebars in the compression zone
        # has 'n-1'. This is due to the fact that rebars in compression have displaced
        # concrete that would have had stiffness of 'Ec'.

        # Evaluate if rebars are inside or outside stress block (returns list with 'True' or 'False')
        rebar_eval = rebars_in_stress_block(x, y, xr, yr)

        # Extract rebars in compression
        dia_comp = [dia[i] for i in range(nb) if rebar_eval[i]]
        xr_comp = [xr[i] for i in range(nb) if rebar_eval[i]]
        yr_comp = [yr[i] for i in range(nb) if rebar_eval[i]]

        # Extract rebars in tension
        dia_tens = [dia[i] for i in range(nb) if not rebar_eval[i]]
        xr_tens = [xr[i] for i in range(nb) if not rebar_eval[i]]
        yr_tens = [yr[i] for i in range(nb) if not rebar_eval[i]]

        # Compute centroid and area of concrete polygon
        xc, yc, Ac = geometry.polygon_centroid(x, y, return_area=True)

        # Compute total transformed area of section
        A_comp = sum([n * pi*d**2/4 for d in dia_tens])
        A_tens = sum([(n-1) * pi*d**2/4 for d in dia_comp])
        A = Ac + A_comp + A_tens

        # Compute total 'moment area', i.e. area times moment arm
        Acx = Ac * abs(xc)
        Asx_comp = sum([(n-1) * pi*dia_comp[i]**2/4 * xr_comp[i]
                        for i in range(len(dia_comp))])
        Asx_tens = sum([n * pi*dia_tens[i]**2/4 * xr_tens[i]
                        for i in range(len(dia_tens))])

        Acy = Ac * abs(yc)
        Asy_comp = sum([(n-1) * pi*dia_comp[i]**2/4 * yr_comp[i]
                        for i in range(len(dia_comp))])
        Asy_tens = sum([n * pi*dia_tens[i]**2/4 * yr_tens[i]
                        for i in range(len(dia_tens))])

        # Compute x- and y-coordinate of elastic centroid for transformed section
        xel = (Acx + Asx_comp + Asx_tens) / A
        yel = (Acy + Asy_comp + Asy_tens) / A

        return xel, yel

    def plastic_centroid(self):
        ''' Return plastic centroid of a reinforced concrete section.'''

        # Find geometric centroid of the concrete alone
        cx, cy = self.geometric_centroid

        # Find forces in concrete and steel
        Fc = self.alpha_cc * self.fcd * self.area
        Fs = sum(self.As) * self.fyd

        # Find concrete and steel moment about x-axis
        Mcx = self.alpha_cc * self.fcd * self.area * cx
        Msx = sum(self.As * self.xs) * self.fyd

        # Find concrete and steel moment about y-axis
        Mcy = self.alpha_cc * self.fcd * self.area * cy
        Msy = sum(self.As * self.ys) * self.fyd

        # Calculate x and y-coordinate of plastic centroid
        x_pl = (Mcx + Msx) / (Fc + Fs)
        y_pl = (Mcy + Msy) / (Fc + Fs)

        return x_pl, y_pl

    def capacity_diagram(self, neutral_axis_locations=None, n_locations=30):
        '''

        Parameters
        ----------
        neutral_axes: list or like-like, optional
            Neutral axis locations to compute the capacity diagram from. Defaults to
            an auto generated sequence spanning the entire section and extending
            beyond both ends.

        TODO Clean up to smaller functions.
        '''
        # Get y-coordinate boundaries for section
        _, miny, _, maxy = self.bounds

        # Check if custom neutral axis locations were input, otherwise auto-generate
        if neutral_axis_locations is None:
            # Generate neutral axis location across the section
            neutral_axis_locations = neutral_axis_locs((miny-2000, maxy+2000),
                                                       n_locations,
                                                       traverse_upwards=False)

        # Get y-coordinate of the plastic centroid of the section
        y_plastic_centroid = self.plastic_centroid[1]

        NN, MM = [], []

        # Loop over neutral axis locations
        for y_na in neutral_axis_locations:
            print('--------------------------------------------')
            print(f'Computation for neutral axis at y = {y_na}')

            # Create line representing neutral axis
            neutral_axis = gm.create_line(angle=0, y_intersect=y_na)

            # Find the cross section state (pure compression, pure tension or mix)
            compr_zone, tension_zone = sec.find_compr_tension_zones(self.polygon,
                                                                    neutral_axis,
                                                                    compr_above=False)

            # Determine state of the section and perform computations accordingly
            if not compr_zone.is_empty and tension_zone.is_empty:
                # --- SECTION IN IN FULL COMPRESSION ---
                print('# --- SECTION IN IN FULL COMPRESSION ---')

                # Split compression zone into compression block and remainder
                compr_block, _ = sec.split_compression_zone(compr_zone, neutral_axis,
                                                            self.area, lambda_c=0.8)

                # Set area of concrete in compression to full cross section area
                Ac = compr_block.area

                # Find centroid height (y-coord) of compr. zone
                cy = list(compr_block.centroid.coords)[0][1]

                # Dist btw. plastic center of gross section to centr of compr block
                arm = y_plastic_centroid - cy

                # Find force and moment contributions to capacity from the concrete
                Fc, Mc = sec.concrete_contributions(Ac, arm, self.fcd, self.alpha_cc)

                # Find distance from each rebar to neutral axis
                rd = sec.points_distance_to_na(points=self.rebars, angle=0,
                                               y_intersect=y_na)

                # Make all rebar distances negative, since there's full compression
                rd *= -1

                # Find extreme compression point and dist from that to neutral axis
                p_max, c_max = gm.furthest_vertex_from_line(compr_zone, neutral_axis)
                print(p_max)
                print(f'c_max = {c_max}')

                # ----- Find rebar strain ------
                # Full compr. => use c_max as dist and eps_c2 as failure strain
                # TODO Should be input
                failure_dist, eps_failure = c_max, 0.0035
                print(f'strain = {eps_failure * rd / failure_dist}')

            elif compr_zone.is_empty and not tension_zone.is_empty:
                # --- SECTION IS IN FULL TENSION ---
                print('# --- SECTION IS IN FULL TENSION ---')

                # Set compression block to empty polygon
                compr_block = Polygon()

                # No concrete in compression => does not contribute to capacity
                Fc, Mc = 0, 0

                # Find distance from each rebar to neutral axis
                rd = sec.points_distance_to_na(points=self.rebars, angle=0,
                                               y_intersect=y_na)

                # Section is in full tension, use eps_su as failure strain
                # TODO Should be input
                eps_failure = 0.0217

                # Set dist to failure strain point as dist to rebar furthest from na
                failure_dist = abs(max(rd, key=abs))

            elif not compr_zone.is_empty and not tension_zone.is_empty:
                # --- SECTION IS IN PARTIAL COMPRESSION AND PARTIAL TENSION ---
                print('# --- SECTION IS IN PARTIAL COMPRESSION AND PARTIAL TENSION ---')

                # Find extreme compression point and dist from that to neutral axis
                p_max, c_max = gm.furthest_vertex_from_line(compr_zone, neutral_axis)

                # Split compression zone into compression block and remainder
                compr_block, _ = sec.split_compression_zone(compr_zone, neutral_axis,
                                                            self.area, lambda_c=0.8)

                # Find area of concrete in compression
                Ac = compr_block.area

                # Find centroid height (y-coord) of compr. zone
                cy = compr_block.centroid.y

                # Dist btw. plastic center of gross section to centr of compr block
                arm = y_plastic_centroid - cy

                # Find force and moment contributions to capacity from the concrete
                Fc, Mc = sec.concrete_contributions(Ac, arm, self.fcd, self.alpha_cc)

                # Create array w. True for rebars in tension zone, False otherwise
                rebars_tension = gm.points_in_polygon(self.rebars, tension_zone)

                # Find rebars in compression by inverting boolean tension array
                rebars_compr = np.invert(rebars_tension)

                # Find distance from each rebar to neutral axis
                rd = sec.points_distance_to_na(points=self.rebars, angle=0,
                                               y_intersect=y_na)

                # Make distance negative for rebars in compression
                rd[rebars_compr] *= -1

                # Compr. and tension, use c_max as dist and eps_cu3 as failure strain
                failure_dist, eps_failure = c_max, 0.0035

            print(f'compr_block = {compr_block}')
            print(f'compr_zone dddd= {compr_zone}')
            print(f'tension_zone = {tension_zone}')
            # print(f'Ac = {Ac}')
            print(f'Fc = {Fc}')
            print(f'Mc = {Mc}')

            # ----- Compute rebar strains ------
            rebar_strain = sec.rebar_strain(rd, failure_dist, eps_failure)
            print(f'rebar_strain = {rebar_strain}')

            # ----- Compute rebar stresses ------
            Es = 200000     # TODO Input
            rebar_stress = rebar_strain * Es
            rebar_stress = np.clip(rebar_stress, -self.fyd, self.fyd)
            print(f'rebar_stress = {rebar_stress}')

            # ----- Compute rebar force -----
            As = np.pi * self.ds**2 / 4
            rebar_force = rebar_stress * As / 1000
            print(f'rebar_force = {rebar_force}')

            # ----- Compute rebar moment -----
            # rebar_moment = abs(rebar_force) * abs((self.ys - y_plastic_centroid)) / 1000
            rebar_moment = (rebar_force) * (y_plastic_centroid - self.ys) / 1000
            print(f'rebar moment arm = {(y_plastic_centroid -self.ys)}')
            print(f'rebar_moment = {rebar_moment}')

            # ----- Compute total rebar force and moment
            Fs = np.sum(rebar_force)
            Ms = np.sum(rebar_moment)
            print(f'Fs = {Fs}')
            print(f'Ms = {Ms}')

            # ----- Compute total resisting force and moment (capacities)
            N = (Fs + Fc)
            M = (Mc + Ms)
            print(f'N = {N}')
            print(f'M = {M}')
            NN.append(N)
            MM.append(M)

        # TODO Return dict of all relevant info for each na location, otherwise
        #      it's hard to track each calc. 
        return NN, MM
        # return NN, MM

    def plot(self):
        '''
        TODO Create rebars with exact radius.
        '''

        # print('y_na', y_na)

        plt.plot(*self.polygon.exterior.xy)
        plt.plot(self.xs, self.ys, '.', color='k')
        # print(neutral_axis)
        # plt.plot(*neutral_axis.xy)
        plt.axis('equal')
        plt.show()
