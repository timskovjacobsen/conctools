Introduction
============

``conctools`` is a high-level Python package which aims to provide an easy and
an intuitive way to work with design and verifications of reinforced concrete sections.

**Users should always be able to trace calculations from origin to
destination.** 

Getting easy access to all intermediate calculation steps to
maximize user comprehension of what has been performed is of utmost
importance.
That is why this package strives to make every calculation as transparent as possible.

.. note::
    In case you have any experience contradicting the above, please open an
    `issue <https://github.com/timskovjacobsen/conctools/issues>`_ on GitHub
    describing the scenario.

As transparency is in focus, it will be prioritized over the implementation of
new features.

Having a Python API for reinforced concrete design can be a great benefit as
it can combine nicely with some of Python's strengths. Powerful automation
workflows can be set up with code that is easy to read for non-computer
scientists. 

Some examples of features that might be used in conjunction with this package are:

- Importing data (e.g. from a Finite Element calculation)

- Data manipulation with custom code

- Exporting of data to another format (Excel, csv, database, etc)

- Plotting of data

Benchmarks
************
As part of the transparency described above, this documentation includes
benchmarking of the results that the algorithms in this package provides.
This means that a large extent of the outputs are compared with results
gathered from well-known textbooks written by scientists in the field.   

The benchmarks presented are implemented in the underlying code as automatic
tests together with many other more specialized tests with a much narrower scope. 

See benchmarks here **{TODO: INSERT LINK}** 

Limitations
***********

The initial releases of this package have a focus on only a small set of
features. Thus, other tools will most likely be necessary to perform a
satisfactory structural documentation. 
