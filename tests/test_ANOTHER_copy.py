"""
Unit tests for assign_ta.py
"""
import pytest
from evo import Evo
import ANOTHER_copy as ac
import numpy as np

sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

test1 = np.loadtxt('test1.csv', delimiter=',', dtype=int)
test2 = np.loadtxt('test2.csv', delimiter=',', dtype=int)
test3 = np.loadtxt('test3.csv', delimiter=',', dtype=int)


# @pytest.fixture
# # function that creates the object
# def evo():
#     return Evo()


def test_overallocation():
    """
    Check that the overallocation function is working correctly
    """
    assert ac.overallocation(test1) == 37
    assert ac.overallocation(test2) == 41
    assert ac.overallocation(test3) == 23


def test_conflicts():
    """
    Check that conflicts function is working correctly
    """
    assert ac.conflicts(test1) == 8
    assert ac.conflicts(test2) == 5
    assert ac.conflicts(test3) == 2


def test_undersupport():
    """
    Check that undersupport function is working correctly
    """
    assert ac.undersupport(test1) == 1
    assert ac.undersupport(test2) == 0
    assert ac.undersupport(test3) == 7


def test_unwilling():
    """
    Check that unwilling function is working correctly
    """
    assert ac.unwilling(test1) == 53
    assert ac.unwilling(test2) == 58
    assert ac.unwilling(test3) == 43


def test_unpreferred():
    """
    Check that unpreferred function is working correctly
    """
    assert ac.unpreferred(test1) == 15
    assert ac.unpreferred(test2) == 19
    assert ac.unpreferred(test3) == 10
