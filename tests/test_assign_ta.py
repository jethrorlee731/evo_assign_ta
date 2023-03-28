"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (test_objectives.py)
March 27, 2023
Unit tests for assign_ta.py
"""

from evo_assign_ta import assign_ta as assign
import numpy as np

# load the CSV file containing information about the sections and store the values into a numpy array
SECTIONS = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)

# load the CSV file containing information about the TAs and store the values into an array
TAS = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

# load in the CSV files that contain the test cases for the pytest unit tests
test1 = np.loadtxt('test1.csv', delimiter=',', dtype=int)
test2 = np.loadtxt('test2.csv', delimiter=',', dtype=int)
test3 = np.loadtxt('test3.csv', delimiter=',', dtype=int)


def test_overallocation():
    """
    Check that the overallocation function is working correctly
    """
    assert assign.overallocation(test1) == 37
    assert assign.overallocation(test2) == 41
    assert assign.overallocation(test3) == 23


def test_conflicts():
    """
    Check that the conflicts function is working correctly
    """
    assert assign.conflicts(test1) == 8
    assert assign.conflicts(test2) == 5
    assert assign.conflicts(test3) == 2


def test_undersupport():
    """
    Check that the undersupport function is working correctly
    """
    assert assign.undersupport(test1) == 1
    assert assign.undersupport(test2) == 0
    assert assign.undersupport(test3) == 7


def test_unwilling():
    """
    Check that the unwilling function is working correctly
    """
    assert assign.unwilling(test1) == 53
    assert assign.unwilling(test2) == 58
    assert assign.unwilling(test3) == 43


def test_unpreferred():
    """
    Check that the unpreferred function is working correctly
    """
    assert assign.unpreferred(test1) == 15
    assert assign.unpreferred(test2) == 19
    assert assign.unpreferred(test3) == 10
