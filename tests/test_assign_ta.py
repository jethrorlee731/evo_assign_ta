"""
Unit tests for assign_ta.py
"""
import pytest
from evo import Evo
import assign_ta
import numpy as np

@pytest.fixture
# function that creates the object
def evo():
    return Evo()

def test_overallocation(evo):
    """
    Check that the overallocation function is working correctly
    """
    assert evo.overallocation(np.array([[0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0],
                                        [1, 1, 0, 0, 0, 0, 0]]), np.array([1, 2, 3, 1])) == 4

def test_conflicts(evo):
    assert evo.conflicts(np.array([[0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0],
                                        [1, 1, 0, 0, 0, 0, 0]]), np.array(['R 1145-125', 'R 1145-125',
                                                                           'W 950-1130', 'W 950-1130',
                                                                           'W 250-430', 'W 250-430',
                                                                           'R 250-430'])) == 2
def test_undersupport(evo):
    assert evo.undersupport(np.array([[0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0],
                                        [1, 1, 0, 0, 0, 0, 0]]), np.array([4, 2, 1, 4, 2, 3, 1])) == 7

def test_unwilling(evo):
    assert evo.unwilling(np.array([[0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0],
                                        [1, 1, 0, 0, 0, 0, 0]]), np.array([['U', 'U', 'U', 'U', 'P', 'U', 'W'],
                                                                          ['U', 'U', 'P', 'W', 'P', 'U', 'U'],
                                                                          ['U', 'P', 'P', 'W', 'W', 'U', 'U'],
                                                                          ['U', 'P', 'W', 'U', 'U', 'U', 'U']])) == 5

def test_unpreferred(evo):
    assert evo.unpreferred(np.array([[0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0],
                                        [1, 1, 0, 0, 0, 0, 0]]), np.array([['U', 'U', 'U', 'U', 'P', 'U', 'W'],
                                                                          ['U', 'U', 'P', 'W', 'P', 'U', 'U'],
                                                                          ['U', 'P', 'P', 'W', 'W', 'U', 'U'],
                                                                          ['U', 'P', 'W', 'U', 'U', 'U', 'U']])) == 3