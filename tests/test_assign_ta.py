"""
Unit tests for assign_ta.py
"""
import pytest
from evo import Evo
import assign_ta
import numpy as np

sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

test1 = np.loadtxt('test1.csv', delimiter=',', dtype=int)
test2 = np.loadtxt('test2.csv', delimiter=',', dtype=int)
test3 = np.loadtxt('test3.csv', delimiter=',', dtype=int)

@pytest.fixture
# function that creates the object
def evo():
    return Evo()

def test_overallocation(evo):
    """
    Check that the overallocation function is working correctly
    """
    assert evo.overallocation(test1, tas[:, 2]) == 37
    assert evo.overallocation(test2, tas[:, 2]) == 41
    assert evo.overallocation(test3, tas[:, 2]) == 23

def test_conflicts(evo):
    """
    Check that conflicts function is working correctly
    """
    assert evo.conflicts(test1, sections[:, 2]) == 8
    assert evo.conflicts(test2, sections[:, 2]) == 5
    assert evo.conflicts(test3, sections[:, 2]) == 2

def test_undersupport(evo):
    """
    Check that undersupport function is working correctly
    """
    assert evo.undersupport(test1, sections[:, 6]) == 1
    assert evo.undersupport(test2, sections[:, 6]) == 0
    assert evo.undersupport(test3, sections[:, 6]) == 7

def test_unwilling(evo):
    """
    Check that unwilling function is working correctly
    """
    assert evo.unwilling(test1, sections[1:, 3:]) == 53
    assert evo.unwilling(test2, sections[1:, 3:]) == 58
    assert evo.unwilling(test3, sections[1:, 3:]) == 43

def test_unpreferred(evo):
    """
    Check that unpreferred function is working correctly
    """
    assert evo.unpreferred(test1, sections[1:, 3:]) == 15
    assert evo.unpreferred(test2, sections[1:, 3:]) == 19
    assert evo.unpreferred(test3, sections[1:, 3:]) == 10
