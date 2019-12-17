
"""Tests for `section` module."""

import os
import sys

import pytest

# Get project root directory
root = os.path.abspath('.')

# Insert directory for module to test into path
sys.path.insert(0, f'{root}\\conctools')

# Import module to test 
import section


def test_passing():

    assert (1, 2, 3) == (1, 2, 3)

