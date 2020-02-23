'''Top-level package for conctools.


Explanation of the import statements below
------------------------------------------

*   The purpose of the `from .module_name import *` statements is to import the
    namespace of the modules at import on user side.
    E.g.

    Alternative 1:
        >>> import conctools
        >>> conctools.Section(...)

    Alternative 2:
        >>> from conctools.conctools import Section
        >>> Section(...)

'''

__author__ = '''Tim Skov Jacobsen'''
__email__ = 'timskovjacobsen@gmail.com'
__version__ = '0.1.0'

# Import entire namespace from module conctools.py
from .section import *              # noqa
from .sectiongen import *           # noqa
