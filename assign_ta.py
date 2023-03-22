from evo import Evo
import random as rnd
import numpy as np
from collections import Counter, defaultdict
from collections import defaultdict


def overallocation(L, ta_array):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to

    Return:
        oa_penalty (int): total overallocation penalty across all tas
    """
    # initialize empty list and variables
    sum_total = []
    oa_penalty = 0

    for row in L:
        # get the sum of each row
        total = sum(row)
        # add it to the list
        sum_total.append(total)

    # convert 1d array to a list
    ta_array = list(ta_array)

    for a, b in zip(sum_total, ta_array):
        if a > b:
            # add to overallocation penalty the difference of how much was actually assigned and what
            # the ta said their max was
            oa_penalty += (a - b)

    return oa_penalty


def conflicts(L):
    """ Number of TAs with one or more time conflicts
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
    Return:
        total_conflict (int): number of tas with one or more time conflict
    """
    # NEED TO ACCOUNT FOR DIFFERENT SECTIONS THAT RUN AT THE SAME TIME
    # initialize default dict
    conflict_dict = defaultdict(int)

    for row in L:
        for item in row:
            if item > 1:
                # key: row as a tuple, value: number of overlaps
                conflict_dict[tuple(row)] += 1

    # determine number of tas that have time conflicts (assigned to more than 1 lab at a time)
    total_conflict = len(conflict_dict)

    return total_conflict


def undersupport(L, sections_array):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum ta number for each section
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """
    # initialize total for undersupport
    total_undersupport = 0

    # sum up each column of the array - number of tas for each column
    ta_num = list(map(sum, zip(*L)))

    sections_array = list(sections_array)

    for a, b in zip(ta_num, sections_array):
        if a < b:
            # add to total for undersupport
            total_undersupport += (b - a)

    return total_undersupport


def unwilling(L, sections_array):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
    Return:
        unwilling_total (int): total of allocation a ta to an unwilling section
    """
    # initialize counter for number of unwilling
    unwilling_total = 0

    # https://stackoverflow.com/questions/44639976/zip-three-2-d-arrays-into-tuples-of-3
    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((L, sections_array)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == 1 and item[1] == 'U':
            # increase the number of unwilling counter if the ta is assigned and they say they are unwilling for that
            unwilling_total += 1

    return unwilling_total


def unpreferred(L, preference_array):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
    Returns:
        unpreferred_total (int): total of allocation a ta to a willing section
    """
    # initialize counter for number of unwilling
    unpreferred_total = 0

    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((L, preference_array)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == 1 and item[1] == 'W':
            # increase the number of willing counter if the ta is assigned and they say they are willing for that
            unpreferred_total += 1

    return unpreferred_total


def add_ta(L, sections_array, ta_array, preference_array):
    """ Assigning a TA to a certain lab section
    This code is very messy and will likely need to be cleaned up
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum TA number for each section
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
    """
    candidate_tas = []
    lab_total = []

    # get the number of TAs each TA is assigned to and store those values in a list
    for row in L:
        # get the sum of each row
        total = sum(row)
        # add it to the list
        lab_total.append(total)

    # convert 1d array containing the max amount of labs each TA wants to be assigned to a list
    ta_array = list(ta_array)
    # sum up each column of the array - number of TAs assigned to each lab
    ta_num = list(map(sum, zip(*L)))
    # gather the minimum number of TAs each lab needs and store those values in a list
    sections_array = list(sections_array)

    # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
    # minimum number of TAs each lab needs
    assigned_vs_needed = list(zip(ta_num, sections_array))

    # get the preferences TAs have for working in particular sections and store them in a list
    preferences = list(preference_array).reshape(-1, 2)

    # can definitely break apart into functions

    for i in range(len(assigned_vs_needed)):
        # Labs that need more TAs are prioritized first
        if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
            lab_to_receive_ta = i
            # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
            # first element being from L and the second element being from sections_array
            for j in range(len(preferences)):
                # if a TA prefers to work in the lab to receive a TA and hasn't reached their section limit, they are
                # a candidate TA for that section
                if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
                    candidate_tas.append(j)

        # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
        # instead
        if len(candidate_tas == 0):
            for i in range(len(assigned_vs_needed)):
                lab_to_receive_ta = i
                if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
                    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
                    # first element being from L and the second element being from sections_array
                    for j in range(len(preferences)):
                        if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                            candidate_tas.append(j)

        # if there are candidate TAs available, choose one at random to be assigned to the lab
        if len(candidate_tas > 0):
            ta_to_be_assigned = rnd.choice(candidate_tas)
            while not ta_assigned:
                # only select from TAs who don't have time conflicts for that section
                if L[ta_to_be_assigned, lab_to_receive_ta] >= 1:
                    candidate_tas.remove(ta_to_be_assigned)
                    ta_to_be_assigned = rnd.choice(candidate_tas)
                else:
                    # assign a TA to a lab section if they don't have time conflicts
                    L[ta_to_be_assigned, lab_to_receive_ta] = 1
                    ta_assigned = True
        else:
            # now focus on labs that have enough TAs
            for i in range(len(assigned_vs_needed)):
                lab_to_receive_ta = i
                # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
                # first element being from L and the second element being from sections_array
                for j in range(len(preferences)):
                    # if a TA prefers to work in the lab to receive a TA and hasn't reached their section limit,
                    # they are a candidate TA for that section
                    if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
                        candidate_tas.append(j)

            # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
            # instead
            if len(candidate_tas == 0):
                for i in range(len(assigned_vs_needed)):
                    lab_to_receive_ta = i
                    if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
                        # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
                        # first element being from L and the second element being from sections_array
                        for j in range(len(preferences)):
                            if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                                candidate_tas.append(j)

            # if there are candidate TAs available, choose one at random to be assigned to the lab
            if len(candidate_tas > 0):
                ta_to_be_assigned = rnd.choice(candidate_tas)
                while not ta_assigned:
                    # only select from TAs who don't have time conflicts for that section
                    if L[ta_to_be_assigned, lab_to_receive_ta] >= 1:
                        candidate_tas.remove(ta_to_be_assigned)
                        ta_to_be_assigned = rnd.choice(candidate_tas)
                    else:
                        # assign a TA to a lab section if they don't have time conflicts
                        L[ta_to_be_assigned, lab_to_receive_ta] = 1
                        ta_assigned = True
            else:
                # don't assign a TA to the lab section to be assigned a new TA if no candidates are available
                break

    return L


def remove_ta(L, sections_array, ta_array, preference_array):
    """ Removing a TA(s) from a certain lab section
    NEED TO ACCOUNT TIME CONFLICTS AND OVERALLOCATIONS
    Also need to consider preferred vs. willing
    This code is very messy and will likely need to be cleaned up
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum TA number for each section
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
    """
    candidate_tas = []
    lab_total = []

    # get the number of TAs each TA is assigned to and store those values in a list
    for row in L:
        # get the sum of each row
        total = sum(row)
        # add it to the list
        lab_total.append(total)

    # convert 1d array containing the max amount of labs each TA wants to be assigned to a list
    ta_array = list(ta_array)
    # sum up each column of the array - number of TAs assigned to each lab
    ta_num = list(map(sum, zip(*L)))
    # gather the minimum number of TAs each lab needs and store those values in a list
    sections_array = list(sections_array)

    # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
    # minimum number of TAs each lab needs
    assigned_vs_needed = list(zip(ta_num, sections_array))

    # get the preferences TAs have for working in particular sections and store them in a list
    preferences = list(preference_array).reshape(-1, 2)

    # can definitely break apart into functions

    for i in range(len(assigned_vs_needed)):

        lab_to_lose_ta = i
        # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
        # first element being from L and the second element being from sections_array
        for j in range(len(preferences)):
            # if a TA does not prefer to work in a lab they are assigned to, remove them from that section
            if preferences[j][i] == 'U':
                candidate_tas.append(j)

        # if there are candidate TAs available to be removed, unassigned each one from the lab to lose a TA
        if len(candidate_tas > 0):
            for ta in candidate_tas:
                # only remove TAs from sections they were already assigned to
                if L[ta, lab_to_lose_ta] >= 1:
                    L[ta, lab_to_lose_ta] = 0

    return L


def main():
    # load the CSV file containing information about the sections and store the values into a numpy array
    sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
    # print(sections)

    # load the CSV file containing information about the TAs and store the values into an array
    tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)
    # print(tas)

    E = Evo()

    # Register some objectives
    E.add_fitness_criteria("overallocation", overallocation, ta_array=tas[:, 1])
    E.add_fitness_criteria("conflicts", conflicts)
    E.add_fitness_criteria("undersupport", undersupport, sections_array=sections[:, 6])
    E.add_fitness_criteria("unwilling", unwilling, sections_array=sections[1:, 3:])
    E.add_fitness_criteria("unpreferred", unpreferred, sections_array=sections[1:, 3:])


# # Register some agents
# E.add_agent("swapper", swapper, k=1)
#
# Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
# # sections and 43 tas)
# 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
# N = 30
# FIGURE OUT HOW TO GENERATE RANDOM 43 ROWS BY 17 COLUMNS OF 0 AND 1S TO REPRESENT L

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
