"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (agents.py)
March 28, 2023

agents.py - agents for the framework to modify solutions so they better align with the objectives
"""

import assign_ta as TA
import random as rnd
import numpy as np
from collections import defaultdict

def add_ta_preferred(solutions):
    """ Assigning a TA to a certain lab section they prefer to work at
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = TA.PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(TA.PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA would prefer working at
    good_labs = np.where(np.array(preference_list[ta]) == 'P')

    # if there are candidate labs available, assign a TA in a section they prefer
    if len(good_labs[0]) > 0:
        addition = rnd.choice(good_labs[0])
        L[ta, addition] = 1

    return L


def add_ta_undersupport(solutions):
    """ Assigning a TA to a certain lab section that needs more assistance
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # sum up each column of the array to get the number of TAs assigned to each lab
    ta_num = list(map(sum, zip(*L)))

    # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
    # minimum number of TAs each lab needs
    assigned_vs_needed = list(zip(ta_num, TA.MIN_TA_LIST))

    # store the labs that need more ta in a list
    labs_in_need = list(
        filter(lambda i: assigned_vs_needed[i][0] < assigned_vs_needed[i][1], range(len(assigned_vs_needed))))

    # if there are under-supported labs, assign a random TA to a random lab that needs more TAs
    if len(labs_in_need) > 0:
        lab = rnd.choice(labs_in_need)
        ta = rnd.randrange(0, 17)
        L[ta, lab] = 1

    return L


def remove_unpreferred(solutions):
    """ Removing a random TA who is only willing to work at a lab section they're assigned to
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = TA.PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(TA.PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA is only willing to work at
    bad_labs = np.where(np.array(preference_list[ta]) == 'W')

    # if there are candidate labs available, remove a TA from a section they don't prefer
    if len(bad_labs[0]) > 0:
        removal = rnd.choice(bad_labs[0])
        L[ta, removal] = 0

    return L


def remove_unwilling(solutions):
    """ Removing a random TA who is not willing to work for a lab section they're assigned to
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = TA.PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(TA.PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA does not want to work at
    bad_labs = np.where(np.array(preference_list[ta]) == 'U')

    # if there are candidate labs available, remove a TA from a section they don't want to work for
    if len(bad_labs[0]) > 0:
        removal = np.random.choice(bad_labs[0])
        L[ta, removal] = 0

    return L


def remove_time_conflict(solutions):
    """ Removing a random TA from a certain lab section if they have a time conflict
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # initialize variables and default dictionaries
    assignments_dict = defaultdict(list)
    day_dict = defaultdict(list)

    # extract a solution
    L = solutions[0]

    # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
    assignments = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section they are working at
    for assignment in assignments:
        if len(assignments_dict) != 0:
            assignments_dict[assignment[0]].append(int(assignment[1]))
        else:
            assignments_dict[assignment[0]] = [int(assignment[1])]

    # go through each TA and each of their assignments
    for ta, labs in assignments_dict.items():
        for lab in labs:
            # get the times for each section a TA is assigned to
            time = TA.DAYTIME_LIST[lab]
            # append to a new dictionary with key being the TA, value being the section times (list)
            day_dict[ta].append(time)

    # inspect TAs who are assigned to multiple labs
    if len(day_dict.values()) > 0:

        for ta, times in day_dict.items():

            # checking whether the number of unique times a TA must work at a lab for is equal to the number of
            # distinct times
            if set(times) != times:
                # empty list to hold the unique times that a TA must be at a lab
                ta_times = []

                # iterate through each time a TA must go to a lab for
                for time in times:
                    # store times not yet observed in a TA's list of lab times
                    if time not in times:
                        ta_times.append(time)
                    else:
                        # if a lab time is re-encountered, store it in a variable as well as that TA's id
                        bad_time = time
                        candidate_ta = ta
                        # break out of the loop once a problematic time is found
                        continue

    # locate a lab section that a TA has a time conflict for
    candidate_labs = np.where(np.array(TA.DAYTIME_LIST) == bad_time)

    # remove a TA from a lab due to time conflicts
    lab = rnd.choice(candidate_labs[0])
    L[candidate_ta, lab] = 0

    return L


def remove_ta_overallocated(solutions):
    """ Removing a random TA from a lab who is over-allocated too many labs
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # calculate the sum of each row in the solution to get the number of labs each TA is assigned to
    assigned = list(L.sum(axis=1))

    # create a list with tuples, where the first element is the number of labs a TA is assigned to and the second is
    # the maximum number of labs they want to work at
    assigned_vs_max = list(zip(assigned, TA.MAX_ASSIGNED_LIST))

    # store candidate tas based on if they are allocated to too many labs
    candidate_tas = list(
        filter(lambda i: assigned_vs_max[i][0] > assigned_vs_max[i][1], range(len(assigned_vs_max))))

    # if there are TAs available to choose from, select one that will lose a lab assignment
    if len(candidate_tas) > 0:
        ta = rnd.choice(candidate_tas)

        # get the labs the TA is assigned to
        candidate_labs = np.where(np.array(L[ta]) == 1)

        # remove a TA from a random lab they're assigned to
        # lab = rnd.choice(candidate_labs[0])
        lab = candidate_labs[0][np.random.randint(len(candidate_labs[0]))]
        L[ta, lab] = 0

    return L


def swap_assignment(solutions):
    """
    Swap two random TA-lab assignments
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    # extract a solution
    L = solutions[0]

    # get a random row in the solution, which contains lab assignments for one TA
    row = rnd.randrange(len(L))
    ta_assignments = L[row, :]

    # pick two random lab assignments (working/not working) for that TA
    i = rnd.randrange(0, len(ta_assignments))
    j = rnd.randrange(0, len(ta_assignments))

    # switch the two assignments
    ta_assignments[i], ta_assignments[j] = ta_assignments[j], ta_assignments[i]
    return L


def swap_labs(solutions):
    """
    Exchange the TAs between two labs
    Args:
        solutions (list of numpy arrays): a list containing possible TA-lab assignments that could work
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    # extract the solution
    L = solutions[0]

    # choose one random lab assignment
    lab1 = rnd.randrange(L.shape[1])

    # choose a random second lab assignment
    lab2 = rnd.randrange(L.shape[1])

    # exchange the TAs between two different labs
    L[:, [lab1, lab2]] = L[:, [lab2, lab1]]

    return L


def swap_tas(solutions):
    """
    Swap two random TAs to different labs
    Args:
        solutions (list of numpy arrays): a list containing possible TA-lab assignments that could work
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    # extract a solution
    L = solutions[0]

    # pick a random TA
    ta1 = rnd.randrange(L.shape[0])

    # pick a random second TA
    ta2 = rnd.randrange(L.shape[0])

    # exchange labs between two TAs
    L[[ta1, ta2]] = L[[ta2, ta1]]

    return L


def opposites(solutions):
    """
    Create the complete opposite solution of the input
    Args:
        solutions (list of numpy arrays): a list containing possible TA-lab assignments that could work
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes (all prior 0s are
                         1s and vice versa
    Citation: https://stackoverflow.com/questions/56594598/change-1s-to-0-and-0s-to-1-in-numpy-array-without-looping
    """
    # extract a solution
    L = solutions[0]

    # switch 1's (assignments) with 0's (non-assignments) and vice versa
    L = np.where((L == 0) | (L == 1), L ^ 1, L)

    return L
