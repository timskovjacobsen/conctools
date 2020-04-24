'''Top-level package for conctools.


How to use ``conctools`` in a project
-------------------------------------

    Alternative 1:
        >>> import conctools
        >>> conctools.Section(...)

    Alternative 2:
        >>> from conctools.conctools import Section
        >>> Section(...)

'''

__author__ = '''Tim Skov Jacobsen'''
__email__ = 'timskovjacobsen@gmail.com'
__version__ = '0.1.1'

# Import entire namespace from module conctools.py
from .section import *              # noqa
