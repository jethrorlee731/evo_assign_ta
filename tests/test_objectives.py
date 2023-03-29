"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (test_objectives.py)
March 28, 2023

test_objectives.py - Unit tests for objectives.py
"""
import objectives as obj
import numpy as np

# load in the CSV files that contain the test cases for the pytest unit tests
test1 = np.loadtxt('test1.csv', delimiter=',', dtype=int)
test2 = np.loadtxt('test2.csv', delimiter=',', dtype=int)
test3 = np.loadtxt('test3.csv', delimiter=',', dtype=int)


def test_overallocation():
    """
    Check that the overallocation function is working correctly
    """
    assert obj.overallocation(test1) == 37
    assert obj.overallocation(test2) == 41
    assert obj.overallocation(test3) == 23


def test_conflicts():
    """
    Check that the conflicts function is working correctly
    """
    assert obj.conflicts(test1) == 8
    assert obj.conflicts(test2) == 5
    assert obj.conflicts(test3) == 2


def test_undersupport():
    """
    Check that the undersupport function is working correctly
    """
    assert obj.undersupport(test1) == 1
    assert obj.undersupport(test2) == 0
    assert obj.undersupport(test3) == 7


def test_unwilling():
    """
    Check that the unwilling function is working correctly
    """
    assert obj.unwilling(test1) == 53
    assert obj.unwilling(test2) == 58
    assert obj.unwilling(test3) == 43


def test_unpreferred():
    """
    Check that the unpreferred function is working correctly
    """
    assert obj.unpreferred(test1) == 15
    assert obj.unpreferred(test2) == 19
    assert obj.unpreferred(test3) == 10
