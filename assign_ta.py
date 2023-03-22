from evo import Evo
import random as rnd
import numpy as np
from collections import Counter, defaultdict
from numpy import genfromtxt

def overallocation(L, max_labs_idx, ta_array):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (dict): details the TAs assigned to each lab, where the section id = key and a list of TAs in that lab = value
        max_labs_idx (integer): index of column with info on the max number of labs a TA can assist
        ta_array (array): original array containing information about TAs' availability
    """
    tas = []
    oa_sum = 0

    # PROBABLY COULD CHANGE THIS INTO FUNCTIONAL PROGRAMMING INSTEAD?

    # retrieve the maximum number of labs each TA is willing to work at
    ta_max_labs = ta_array[:, max_labs_idx]

    # create a dictionary where the key = a TA ID and the value = the number of labs assigned to that TA
    ta_lists = L.values()
    for ta_list in ta_lists:
        tas += ta_list
    ta_lab_counts = dict(Counter(tas))

    # determine whether each TA is over-allocated a certain number of labs
    for ta, labs in ta_lab_counts.items():
        for i in range(len(ta_max_labs)):
            if ta == i:
                # if a TA is assigned to more labs than they request, the number of labs they are over-allocated is
                # quantified as an overallocation penalty
                if labs > ta_max_labs[i]:
                    # sums the overallocation penalty over all TAs
                    oa_sum += (ta_max_labs[i] - labs)

    return oa_sum


def conflicts(L, time_idx, ta_array, sections_array):
    """ Number of TAs with one or more time conflicts
    Args:
        L (dict): details the TAs assigned to each lab, where the section id = key and a list of TAs in that lab = value
        time_idx (int): index of column with information on a lab's meeting time
        ta_array (array): original array containing information about TAs' availability
        sections_array (array): array containing information about each lab section

    Citation: https://stackoverflow.com/questions/1388818/how-can-i-compare-two-lists-in-python-and-return-matches
    """
    conflicts = 0
    labs_for_ta = defaultdict(list)
    lab_time_dict = defaultdict(list)

    # create a dictionary that maps times (key) to a list of labs that run at the same times (key)
    lab_times = sections_array[:, time_idx]
    for i in range(len(lab_times)):
        lab_time_dict[lab_times].append(i)

    # create a dictionary that maps each TA (key) to a list of labs they assist (value)
    for lab, tas in L.items():
        for ta in tas:
            labs_for_ta[ta].append(lab)

    # count the number of instances in which a TA is assigned to 2 or more labs that run at the same time
    for ta, labs in labs_for_ta.items():
        # if a TA has multiple time conflicts, this instance is counted as one overall time conflict for that TA
        ta_with_conflict = None
        for times, sections in lab_time_dict.items():
            if len(set(labs) & set(sections)) > 1:
                if ta_with_conflict is not None:
                    conflicts += 1
                    ta_with_conflict = ta

    return conflicts


def undersupport(L, min_ta_idx, sections_array):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (dict): details the TAs assigned to each lab, where the section id = key and a list of TAs in that lab = value
        min_ta_idx (integer): index of column with info on the min number of TAs a lab needs
        sections_array (array): array containing information about each lab section
    """
    undersupport_sum = 0

    # retrieve the minimum number of TAs each lab requires
    sections_min_tas = sections_array[:, min_ta_idx]

    # determine whether each lab needs more TAs
    for lab, tas in L.items():
        for i in range(len(sections_min_tas)):
            if i == lab:
                # if a lab is assigned less TAs than it needs, the additional number of TAs it needs is quantified as a
                # penalty
                if len(tas) < sections_min_tas[i]:
                    # sums the under-support penalty over all labs
                    undersupport_sum += (sections_min_tas[i] - len(tas))

    return undersupport_sum


def unwilling(L, availability_first_idx, availability_last_idx, ta_array, tas):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (dict): details the TAs assigned to each lab, where the section id = key and a list of TAs in that lab = value
        availability_first_idx (integer): index of the 1st column with info on a TA's availability
        availability_last_idx (integer): index of the last column with info on a TA's availability
        ta_array (array): original dataframe containing information about TAs' availability
        tas (int): the number of TAs available
    """
    unwilling = 0

    # gather information on each TA's availability for each lab section
    availability = ta_array[:, availability_first_idx:availability_last_idx + 1]

    # check the availability of each TA
    for i in range(len(tas)):
        ta_availability = list(availability[tas, :])
        for lab, ta in L.items():
            # count the number of times a TA is in a lab they are unwilling to help
            if i in ta and ta_availability[lab] == "U":
                unwilling += 1

    return unwilling


def unpreferred(L, availability_first_idx, availability_last_idx, ta_array, tas):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    Args:
        L (dict): details the TAs assigned to each lab, where the section id = key and a list of TAs in that lab = value
        availability_first_idx (integer): index of the 1st column with info on a TA's availability
        availability_last_idx (integer): index of the last column with info on a TA's availability
        ta_array (array): original dataframe containing information about TAs' availability
        tas (int): the number of TAs available
    """

    unpreferred = 0

    # gather information on each TA's availability for each lab section
    availability = ta_array[:, availability_first_idx:availability_last_idx + 1]

    # check the availability of each TA
    for i in range(len(tas)):
        ta_availability = list(availability[tas, :])
        for lab, ta in L.items():
            # count the number of times a TA is in a lab they are in an un-preferred section
            if i in ta and ta_availability[lab] == "W":
                unpreferred += 1

    return unwilling


# def sumstepsdown(L):
#     """ Objective: Count total magnitude of steps down (larger to smaller value) """
#     return sum([x - y for x, y in zip(L, L[1:]) if y < x])
#
#
# def sumratio(L):
#     """ Ratio of sum of first-half values to 2nd half values"""
#     sz = len(L)
#     return round(sum(L[:sz//2]) / sum(L[sz//2+1:]), 5)
#
#
# # Creating agents (all agents take in solutions)
# def swapper(solutions):
#     """ Swap two random values """
#     L = solutions[0]
#     i = rnd.randrange(0, len(L))
#     j = rnd.randrange(0, len(L))
#     L[i], L[j] = L[j], L[i]
#     return L
def add_ta(sections_array, min_ta_idx, ta_array, max_labs_idx, availability_first_idx, availability_last_idx, solutions,
           ta_num, num_tas):
    """ Assigning a TA to a certain lab section
    NEED TO ACCOUNT FOR TIME CONFLICTS
    Also need to consider preferred vs. willing
    This code is very messy and will likely need to be cleaned up
    Args:
        sections_array (array): array containing information about each lab section
        min_ta_idx (integer): index of column with info on the min number of TAs a lab needs
        ta_array (array): original array containing information about TAs' availability
        max_labs_idx (integer): index of column with info on the max number of labs a TA can assist
        availability_first_idx (integer): index of the 1st column with info on a TA's availability
        availability_last_idx (integer): index of the last column with info on a TA's availability
        solutions (list): a list of possible TA lab assignments that could be optimal
        ta_num (int): the maximum number of TAs
        num_tas (int): number of TAs available
    """
    labs_in_need = []
    L = solutions[0]
    ta_master_list = []
    preferred = []
    available_ta = False

    # retrieve the minimum number of TAs each lab requires
    sections_min_tas = sections_array[:, min_ta_idx]

    # determine which each lab needs more TAs
    for lab, tas in L.items():
        for i in range(len(sections_min_tas)):
            if i == lab:
                if len(tas) < sections_min_tas[i]:
                    labs_in_need.append(lab)

    # retrieve the maximum number of labs each TA is willing to work at
    ta_max_labs = ta_array[:, max_labs_idx]

    # create a dictionary where the key = a TA ID and the value = the number of labs assigned to that TA
    ta_lists = L.values()
    for ta_list in ta_lists:
        ta_master_list += ta_list
    ta_lab_counts = dict(Counter(ta_master_list))

    # determine which TAs are over-allocated a certain number of labs
    eligible_tas = [id for id in range[0, num_tas + 1]]
    for ta, labs in ta_lab_counts.items():
        for i in range(len(ta_max_labs)):
            if ta == i:
                if labs > ta_max_labs[i]:
                    eligible_tas.remove(ta)

    # choose a random lab that needs more TAs to receive a new TA
    lab_to_receive_ta = rnd.choice(labs_in_need)

    # gather the TAs that prefer to work at that lab section
    availability = ta_array[:, availability_first_idx:availability_last_idx + 1]
    ta_availability = list(availability[:, lab_to_receive_ta])
    for i in range(len(ta_availability)):
        if availability == "P":
            preferred.append(i)
        elif availability == "U":
            eligible_tas.remove(i)

    # choose a random TA to be assigned to a lab (prioritizing the TAs who want to work for that section)
    while not available_ta:
        if len(preferred) > 0:
            ta_to_be_assigned = rnd.choice(preferred)
        else:
            ta_to_be_assigned = rnd.choice(eligible_tas)

        # assign a TA to a lab if they aren't already assigned to that lab
        for lab, ta_list in L.values():
            if lab == lab_to_receive_ta and ta_to_be_assigned not in L[lab]:
                L[lab].append(ta_to_be_assigned)
                available_ta = True

    return L


def remove_ta(solutions, lab_num, ta_array, max_labs_idx, availability_first_idx, availability_last_idx):
    """ Removing a TA(s) from a certain lab section
    NEED TO ACCOUNT TIME CONFLICTS AND OVERALLOCATIONS
    Also need to consider preferred vs. willing
    This code is very messy and will likely need to be cleaned up
    Args:
        solutions (list): a list of possible TA lab assignments that could be optimal
        lab_num (int): the maximum number of labs
        ta_array (array): original array containing information about TAs' availability
        max_labs_idx (integer): index of column with info on the max number of labs a TA can assist
        availability_first_idx (integer): index of the 1st column with info on a TA's availability
        availability_last_idx (integer): index of the last column with info on a TA's availability
    """
    L = solutions[0]
    unpreferred_tas = []

    # gather the TAs that don't want to work at that lab section
    availability = ta_array[:, availability_first_idx:availability_last_idx + 1]
    for i in range(len(lab_num)):
        ta_availability = list(availability[:, i])
        for j in range(len(ta_availability)):
            if availability == "U":
                unpreferred_tas.append(j)

        # Remove a TA from a lab they don't want to work at if they are already assigned to that lab
        for unpreferred_ta in unpreferred_tas:
            for lab, ta_list in L.values():
                if lab == lab_num[i] and unpreferred_ta in L[lab]:
                    L[lab].remove(unpreferred_ta)

    return L


def main():
    # load the CSV file containing information about the sections and store the values into a numpy array
    sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
    # print(sections)

    # load the CSV file containing information about the TAs and store the values into an array
    tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)
    # print(tas)


# E = Evo()
#
# # Register some objectives
# E.add_fitness_criteria("ssd", sumstepsdown)
# E.add_fitness_criteria("ratio", sumratio)
#
# # Register some agents
# E.add_agent("swapper", swapper, k=1)
#
# Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
# # sections and 43 tas)
# 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
# N = 30
# L = {0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
#          30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 21, 42], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [],
#      10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: []}
# E.add_solution(L)
# print(E)
#
# # Run the evolver
# E.evolve(1000000, 100, 10000)
#
# # Print final results
# print(E)


if __name__ == '__main__':
    main()
