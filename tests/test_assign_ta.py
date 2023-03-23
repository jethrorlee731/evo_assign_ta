"""
Unit tests for assign_ta.py
"""

import pytest
import assign_ta

# tagging it as a fixture - it knows when it sees stack
# it is the function it needs to call
@pytest.fixture
# function that creates the object
def evo():
    return Evo()

# should have a test for each method from stack.py

# test the __init__
def test_constructor():
    # verify that an instance is created
    s = Stack()
    assert isinstance(s, Stack), "Did not construct a stack"

    # check to see that stack is empty
    assert s.size()==0, "Stack is not empty"

    # this works after doing __len__
    assert len(s) == 0, "Stack is not empty"

# parameter is the stack function
def test_push(stack):
    # s = Stack()
    stack.push(3)
    stack.push(4)
    assert len(stack) == 2
    assert stack.top() == 4

def test_pop(stack):
    stack.push('a')
    stack.push('b')
    assert stack.pop() == 'b', 'wrong value popped'
    assert stack.pop() == 'a', 'wrong value popped'
    assert stack.pop() is None, 'wrong value popped'
    assert stack.top() is None, 'Stack should be empty but it is not'


def test_top(stack):
    stack.push(1)
    stack.push(2)
    stack.push(3)
    assert stack.top() == 3, 'wrong value on the top'
    stack.pop()
    stack.pop()
    assert stack.top() == 1, 'wrong value on the top'
    stack.pop()
    assert stack.top() is None, 'Stack should be empty '

