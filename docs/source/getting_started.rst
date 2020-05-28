
===============
Getting Started
===============

.. Note::

    Make sure that you have installed the package by ``pip install conctools`` in your terminal, otherwise you will get and ``ImportError``.

To use conctools in a Python project, import it like this::

    import conctools


From there, you can use the functionality of the package. You could for example
create a reinforced concrete cross section by::

    conctools.Section(<inputs>)


Alternatively, you could::

    from conctools import Section

and create a cross section by::

    Section(<inputs>)
