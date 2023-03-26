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
    assert evo.overallocation(test1) == 37
    assert evo.overallocation(test2) == 41
    assert evo.overallocation(test3) == 23


def test_conflicts(evo):
    """
    Check that conflicts function is working correctly
    """
    assert evo.conflicts(test1) == 8
    assert evo.conflicts(test2) == 5
    assert evo.conflicts(test3) == 2


def test_undersupport(evo):
    """
    Check that undersupport function is working correctly
    """
    assert evo.undersupport(test1) == 1
    assert evo.undersupport(test2) == 0
    assert evo.undersupport(test3) == 7


def test_unwilling(evo):
    """
    Check that unwilling function is working correctly
    """
    assert evo.unwilling(test1) == 53
    assert evo.unwilling(test2) == 58
    assert evo.unwilling(test3) == 43


def test_unpreferred(evo):
    """
    Check that unpreferred function is working correctly
    """
    assert evo.unpreferred(test1) == 15
    assert evo.unpreferred(test2) == 19
    assert evo.unpreferred(test3) == 10
