Examples
=============

Create a Reinforced Concrete Section
--------------------------------------

This example demonstrates how to use conctools to create a reinforced concrete
cross section and plot its geometry.

The created cross section resembles the one treated in Example 4.10 from *Reinforced
Concrete Design to Eurocode by Bill Mosley and Ray Hulse.*

.. code-block:: python

    from conctools import Section
    import matplotlib.pyplot as plt

    # Define concrete geometry by x-and y-coordinates of section vertices
    x = [0, 0, 350, 350]
    y = [0, -450, -450, 0]

    # Define rebar locations and diameters
    xs = [60, 290, 60, 290]
    ys = [-60, -60, -390, -390]
    ds = [32, 32, 25, 25]

    # Define material strengths
    fck = 25
    fyk = 500

    # Create a reinforced concrete section object
    section = Section(vertices=[x, y], rebars=[xs, ys, ds], fck=fck, fyk=fyk,
                    gamma_c=1.5, alpha_cc=0.85)

    # Plot the section
    section.plot()
    plt.show()

This example code provides the basis for the code in the sections below. 

.. Note::

    The parameters ``gamma_c`` and ``alpha_cc`` are optional when creating a section.
    They are used in the code above since the example in the textbook uses values that
    are different from the defaults implemented in **conctools**.

Calculate The Plastic Centroid
******************************

The plastic centroid of the cross section taking into account the
contributions from concrete and reinforcement can be found as

.. code-block:: python

    plastic_centroid = section.plastic_centroid

Plot The Capacity Diagram
*****************************

Building on the example from above where a section is created, the capacity diagram
can be plotted as simply as

.. code-block:: python

    section.plot_capacity_diagram()


Calculate The Elastic Centroid
******************************

*Coming soon*

*Want to help implement the feature? Take a look at the Contributions tab*

Calculate The Neutral Axis Location
***********************************

*Coming soon*

*Want to help implement the feature? Take a look at the Contributions tab*

