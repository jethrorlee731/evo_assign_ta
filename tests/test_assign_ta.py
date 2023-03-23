"""
Unit tests for assign_ta.py
"""

import pytest
from evo import Evo
import assign_ta


def test_overallocation():
    pass

def test_conflicts():
    pass

def test_undersupport():
    pass

def test_unwilling():
    pass

def test_unpreferred():
    pass


# @pytest.fixture
# # function that creates the object
# def evo():
#     return Evo()
#
# # test the __init__
# def test_constructor():
#     # verify that an instance is created
#     e = Evo()
#     assert isinstance(e, Evo), "Did not construct a stack"
#
#     # check to see that stack is empty
#     assert evo.size() == 0, "Stack is not empty"
#
#     # this works after doing __len__
#     assert len(evo) == 0, "Stack is not empty"
#
# # parameter is the stack function
# def test_push(evo):
#     # s = Stack()
#     evo.push(3)
#     evo.push(4)
#     assert len(evo) == 2
#     assert evo.top() == 4
#
# def test_pop(evo):
#     evo.push('a')
#     evo.push('b')
#     assert evo.pop() == 'b', 'wrong value popped'
#     assert evo.pop() == 'a', 'wrong value popped'
#     assert evo.pop() is None, 'wrong value popped'
#     assert evo.top() is None, 'Stack should be empty but it is not'
#
#
# def test_top(evo):
#     evo.push(1)
#     evo.push(2)
#     evo.push(3)
#     assert evo.top() == 3, 'wrong value on the top'
#     evo.pop()
#     evo.pop()
#     assert evo.top() == 1, 'wrong value on the top'
#     evo.pop()
#     assert evo.top() is None, 'Stack should be empty '
#
