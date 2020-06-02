'''
Module with utility functions used for plotting in the Section class.
'''


def plot_cover(ax, section):

    # Create a linestring from the polygon vertices
    section_linestring = section._to_linestring()

    # Offset linestring to get the line representing the cover
    cover_linestring = section_linestring.parallel_offset(
        distance=section.cover, side='left')

    # Extract cover coordinates and plot them
    cover_unzipped = list(zip(*cover_linestring.coords))
    x_cover, y_cover = cover_unzipped[0], cover_unzipped[1]

    ax.plot(x_cover, y_cover, ':', color='darkgrey', zorder=1)
