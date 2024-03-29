# coding=utf-8

# Third party imports
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LinearRing
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import matplotlib as mpl

# Project specific imports
import conctools._geometry as gm
import conctools._section_utils as su
import conctools._section_plot as sp
from conctools._sectiongen import neutral_axis_locs

mpl.rcParams['font.family'] = 'roboto'
plt.style.use('seaborn-whitegrid')


# Default number of locations for production of NM-diagram
N_LOCATIONS = 60


class Section:
    '''Class for defining a reinforced concrete section.

    The section can have any non-convex polygon shape.

    '''
    '''TODO:
    * Implement high strength concretes (fck > 50 MPa). The additional logic required
      is not currently implemented and there is no warning about it.
    * Create alternative constructor for circular sections.
    * Create alternative constructor for smeared out reinforcement.
    '''

    def __init__(self, vertices, rebars, fck, fyk, cover=45, gamma_c=1.5, gamma_s=1.15,
                 alpha_cc=1.0, eps_cu=0.0035, eps_c=0.00175):
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
        fck : number
            Concrete strength in [MPa].
        fyk : number
            Yield stress of reinforcement steel in [MPa].
        cover : number, optional
            Concrete cover in [mm]. Minimum distance from the concrete edge to any
            steel fiber in the cross section. Defaults to 45 mm.
        alpha_cc : number, optional
            Coefficient taking into account long term effects on the
            compressive strength of concrete and unfavorable effects from
            the way loads may be applied. Defaults to 1.0.
            Formula: fcd = alpha_cc * fck / gamma_c
        eps_cu : number, optional
            Failure strain of concrete under combined effects.
            Defaults to 0.0035 as per EN-1992-1-1, Table 3.1 for normal strength
            concrete.
        eps_c : number, optional
            Failure strain of concrete for pure, uniform compression. I.e. with the
            section in compression and neutral axis at infinity.
            Defaults to 0.00175 as per EN-1992-1-1, Table 3.1 for normal strength
            concrete.

        '''
        ''' TODO:
        eps_cu, eps_cu and all the other strength and deformation characteristics
        for concrete should be automaticall calculated based on the concrete
        strengths and the analytical expressions given in EN-1992-1-1, Table 3.1.
        '''

        # Create instance attributes for x- and y-coordinates
        self.x = vertices[0]
        self.y = vertices[1]
        self.fck = fck
        self.fyk = fyk
        self.cover = cover  # TODO: Check if all rebers are completely inside the cover
        self.alpha_cc = alpha_cc

        self.gamma_c = gamma_c
        self.fcd = self.fck / self.gamma_c
        self.gamma_s = gamma_s
        self.fyd = self.fyk / self.gamma_s
        self.eps_cu = eps_cu
        self.eps_c = eps_c

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

        # Set boundaries of section (minx, miny, maxx, maxy)
        self.bounds = self.polygon.bounds

    @property
    def plastic_centroid(self):
        '''Return plastic centroid of the reinforced concrete section.

        Returns
        -------
        tuple
            Coordinates of the the plastic centroid in the format (x_pl, y_pl)
        '''

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

    @property
    def xy_coords(self):
        '''Return the x- and y-coordinates of the section.

        Returns
        -------
        tuple
            The first element is a list of the x-coordinates of the section and the
            second element of the y-coordinates.
        '''

        unzipped = list(zip(*self.polygon.exterior.coords))
        x, y = unzipped[0], unzipped[1]
        return x, y

    def _to_linestring(self):
        return LineString([*self.polygon.exterior.coords])

    def capacity_diagram(self, neutral_axis_locations=None, n_locations=N_LOCATIONS):
        '''Return the capacity diagram of the reinforced concrete section.

        Parameters
        ----------
        neutral_axes_locations : list or like-like, optional
            Neutral axis locations to compute the capacity diagram from. Defaults to
            an auto generated sequence spanning the entire section and extending
            beyond both ends.
            If this parameter is given, it will take priorit over `n_locations`.
        n_locations : int
            Number of neutral axis locations to examine for creating the capacity
            diagram.

        Returns
        -------
        tuple
            A tuple in the format `(N, M, metadata)`. `N` and `M` are a lists of normal
            forces and moments for each neutral axis location considered. `metadata` is
            a dictionary containing detailed information about the calucalation of of
            each (N, M)-pair.
        '''
        '''TODO:
        Return dict of all relevant info for each na location, otherwise
        it's hard to track each calc.
        '''

        # Get y-coordinate boundaries for section
        _, miny, _, maxy = self.bounds

        # Initialize lists for holding final N-M pairs
        N, M = [], []

        # Create dict of metadata for results of each neutral axis location
        metadata = {
            'neutral_axis': [],
            'compr_above_na': [],
            'compression_zone': [],
            'tension_zone': [],
            'compression_block': [],
            'failure_strain': [],
            'Fc': [],
            'Mc': [],
            'Fs': [],
            'Ms': [],
            'N': [],
            'M': [],
            }

        for compr_above in [True, False]:

            # Check if custom neutral axis locations were input, otherwise auto-generate
            if neutral_axis_locations is None:
                # Set boundaries for neutral axis locs to avoid analysing locs where
                # where section is in full tension but rebars are not yielding.
                # TODO: Refer to more detailed description
                max_na = maxy if compr_above else maxy+1000
                min_na = miny-1000 if compr_above else miny

                # Generate neutral axis location across the section
                n_locations_half = int(n_locations / 2)
                neutralaxis_locations = neutral_axis_locs((min_na, max_na),
                                                          n_locations_half,
                                                          traverse_upwards=True)
            else:
                # Set neutral axis locations to what was specifically inputted
                neutralaxis_locations = neutral_axis_locations

            # Loop over neutral axis locations
            for y_na in neutralaxis_locations:

                # Create line representing neutral axis
                neutral_axis = gm.create_line(angle=0, y_intersect=y_na)

                # Find the cross section state (pure compression, pure tension or mix)
                compr_zone, tension_zone = su.find_compr_tension_zones(
                    self.polygon, neutral_axis, compr_above=compr_above)

                # Determine y-coord. of failure strain based in neutral axis
                eps_failure = su.strain(self, neutral_axis, y_seek=None,
                                        compr_above=compr_above)
                # Determine state of the section and perform computations accordingly
                if not compr_zone.is_empty and tension_zone.is_empty:
                    # --- SECTION IN IN FULL COMPRESSION ---

                    # Perform full compression analysis and get relevant results
                    Fc, Mc, rd, failure_dist, compr_block = su.full_compression(
                        self, compr_zone, neutral_axis)

                elif compr_zone.is_empty and not tension_zone.is_empty:
                    # --- SECTION IS IN FULL TENSION ---

                    Fc, Mc, rd, failure_dist, compr_block = su.full_tension(
                        self.rebars, neutral_axis)

                elif not compr_zone.is_empty and not tension_zone.is_empty:
                    # --- SECTION IS IN PARTIAL COMPRESSION AND PARTIAL TENSION ---

                    Fc, Mc, rd, failure_dist, compr_block = su.mixed_compr_tension(
                        self, compr_zone, tension_zone, neutral_axis)

                Fs, Ms, _ = su.steel_contribution(
                    self, rd, failure_dist, eps_failure, Es=200000)

                # Compute total resisting force and moment (capacities)
                N_final = Fs + Fc
                M_final = Mc + Ms
                N.append(N_final)
                M.append(M_final)

                # Update dict of section metadata for calculation
                metadata['neutral_axis'].append(y_na)
                metadata['compr_above_na'].append(compr_above)
                metadata['compression_zone'].append(compr_zone)
                metadata['tension_zone'].append(tension_zone)
                metadata['compression_block'].append(compr_block)
                metadata['failure_strain'].append(eps_failure)
                metadata['Fc'].append(Fc)
                metadata['Mc'].append(Mc)
                metadata['Fs'].append(Fs)
                metadata['Ms'].append(Ms)
                metadata['N'].append(N)
                metadata['M'].append(N)

        return N, M, metadata

    def plot(self, title='', plot_cover=True):
        '''Plot the reinforced concrete section.

        Parameters
        ----------
        No input parameters, as they are all stored in the object.

        Returns
        -------
        `None`
        '''

        fig, ax = plt.subplots()

        ax.fill(*self.xy_coords, facecolor='silver', edgecolor='k',
                alpha=0.75)

        # Loop over rebars and plot them with true size
        for x, y, r in zip(self.xs, self.ys, self.ds/2):
            # Create and add circle patch for rebar with center (x, y) and radius r
            rebar = plt.Circle((x, y), r, color='k', alpha=0.5)
            ax.add_artist(rebar)

            # Add annotations for each rebar
            ax.annotate(f'Ø{2*r:.0f}', xy=(x, y), xytext=(x, y - r*1.02),
                        va='top', ha='center', fontsize=9)

        if title:
            plt.title(title)

        if plot_cover:
            sp.plot_cover(ax, self)

        ax.set_xlabel('$x$ [mm]', fontsize=12)
        ax.set_ylabel('$y$ [mm]', fontsize=12)

        plt.axis('equal')
        plt.show()

    def plot_capacity_diagram(self, n_locations=N_LOCATIONS, NM=None,
                              flip_axes=False, title='',
                              **kwargs):
        '''Plot the capacity diagram for the section.

        Note that the plt.show() must be called after the method call to show the
        plot. The method only generates the axis, ready to be shown.

        Parameters
        ----------
        n_locations : str, optional
            Number of strain states (or neutral axis locations) to analyse.
            The number of points in the diagram will be `n_locations`.
            Defaults to 60.
        NM: tuple, optional
            Tuple of arrays for potentially pre-computed normal force and moments
            (N, M). This can be used to avoid re-computing the diagram if it
            already has been done once. If not given, the function computes the
            values.
        flip_axes : bool
            Whether to flip the axes in the resulting plot. If `True`, plot normal
            force (N) on x-axis and moment (M) on y-axis. Vice versa if `False`.
            Defaults to `True`.
        title : str
            Title of the plot. Defaults to 'Interaction Diagram' if input string is
            left empty.
        **kwargs : dict
            Keyword arguments to forward to the matplotlib line plot for customization.
            See https://matplotlib.org/3.2.0/api/_as_gen/matplotlib.pyplot.plot.html
            for more info.
            Note that some default keyword arguments for styling the plot are defined
            by this method in case no arguments are specified by the method call.
            Any specific user inputted keyword argument will take priority over a
            potential deafault value.

        Returns
        -------
        `None`
        '''
        '''TODO:
        * Create a custom "good looking" plot if **kwargs is not given.
        '''

        fig, ax = plt.subplots()

        if not NM:
            N, M, _ = self.capacity_diagram(n_locations=n_locations)
        else:
            N, M = NM

        data = (M, N) if flip_axes else (N, M)
        labels = ('M [kNm', 'N [kN]') if flip_axes else ('N [kN]', 'M [kNm]')

        # Define some deafault keyword arguments
        default_kwargs = {'color': 'tomato'}

        # Construct final keyword argument with priority to user inputs
        plot_kwargs = {**default_kwargs, **kwargs}

        ax.plot(*data, **plot_kwargs)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])

        default_title = 'Interaction Diagram'

        if title:
            plt.title(title)
        else:
            plt.title(default_title)

    def __repr__(self):
        fck, fyk = self.fck, self.fyk
        lv, lr = len(self.x), len(self.xs)
        s = "class (RC) 'Section'"
        return f'''{s} with [fck={fck}, fyk={fyk}, vertices: {lv}, rebars: {lr}]'''
