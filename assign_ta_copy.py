import pandas as pd

from evo_copy import Evo
import random as rnd
import numpy as np
from collections import Counter, defaultdict
from collections import defaultdict
from numpy import random


def overallocation(L, ta_array=None):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (numpy array): a 2D array with sections as columns and TAs as rows
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to

    Return:
        oa_penalty (int): total overallocation penalty across all tas
    """
    # initialize empty list and variables
    oa_penalty = 0
    lab_totals = []

    print(L)
    #
    # # calculate how many labs each TA is assigned to
    for sol in L:
        print(sol)

    # for assignments in L:
    #     lab_totals.append(sum(assignments))
    #     print(lab_totals)
    # print('lab_tot1', len(lab_totals))
    # if ta_array is not None:
    #     # convert 1d array to a list of integers
    #     max_labs = [int(lab_num) for lab_num in ta_array]
    #     # WEIRD ERROR - MAX_LABS KEEPS CONVERTING BACK INTO AN ARRAY, CAUSING ISSUES
    #     print('lab_tot', len(lab_totals))
    #     print('max_lab', len(max_labs))
    #     for assigned, limit in list(zip(lab_totals, max_labs)):
    #         if assigned > limit:
    #             # add to overallocation penalty the difference of how much was actually assigned and what
    #             # the ta said their max was
    #             oa_penalty += (assigned - limit)
    #
    #     return oa_penalty


def conflicts(L, daytime_array=None):
    """ Number of TAs with one or more time conflicts
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        daytime_array (numpy array): 1d array of the times for each of the 17 sections
    Return:
        total_conflict (int): number of tas with one or more time conflict
    """
    # initialize variables and default dictionaries
    total_conflict = 0
    solutions_dict = defaultdict(int)
    day_dict = defaultdict(list)

    # numpy array containing index of where 1 is present in the L array
    solutions = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section
    for solution in solutions:
        solutions_dict[solution[0]] = solution[1]

    if daytime_array is not None:
        for key, value in solutions_dict.items():
            # append to a new dictionary with key being the ta, value being the section time
            day_dict[key].append(daytime_array[value])

        for value in day_dict.values():
            if len(set(value)) != len(value):
                # there is a ta assigned to the same lab time over more than one section - add one to the counter
                total_conflict += 1

        return total_conflict


def undersupport(L, sections_array=None):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
        sections_array (numpy array): 1d array with the minimum TA number each section needs
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """
    # initialize total for undersupport
    total_undersupport = 0

    # sum up each column of the array to get the number of TAs assigned to each lab
    #for assignments in L.transpose():
    ta_num = np.sum(L, axis=1).tolist()

    if sections_array is not None:
        min_ta = [int(min) for min in sections_array]

        for assigned, min in list(zip(ta_num, min_ta)):
            if assigned < min:
                # add to total for undersupport
                total_undersupport += (min - assigned)

        return total_undersupport


def unwilling(L, preference_array=None):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
        preference_array (numpy array): 2D array of whether a TA is unwilling, willing, or preferred for each section
    Return:
        unwilling_total (int): total of allocation a ta to an unwilling section
    """
    # initialize counter for the number of TAs in a section they are unwilling to work for
    unwilling_total = 0

    # https://stackoverflow.com/questions/44639976/zip-three-2-d-arrays-into-tuples-of-3
    # pair up one by one the two 2D arrays element by element; assignments is a list of tuples with the first element
    # indicating whether a TA is assigned to a lab (1) or not (0), and the second element indicating the respective lab
    if preference_array is not None:
        for i in range(len(preference_array)):
            for j in range(len(preference_array[i])):
                if preference_array[i][j] == '1' and L[i][j] == 'W':
                    # increase the unwilling counter if the TA is assigned to a lab they're unwilling to work for
                    unwilling_total += 1

        return unwilling_total


def unpreferred(L, preference_array=None):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
    Returns:
        unpreferred_total (int): total of allocation a ta to a willing section
    """
    # initialize counter for the number of TAs that are in a section they don't prefer
    unpreferred_total = 0

    # https://stackoverflow.com/questions/44639976/zip-three-2-d-arrays-into-tuples-of-3
    # pair up one by one the two 2D arrays element by element; assignments is a list of tuples with the first element
    # indicating whether a TA is assigned to a lab (1) or not (0), and the second element indicating the respective lab
    if preference_array is not None:
        for i in range(len(preference_array)):
            for j in range(len(preference_array[i])):
                if preference_array[i][j] == '1' and L[i][j] == 'U':
                    # increase the unpreferred counter if the TA is assigned to a lab they're unwilling to work for
                    unpreferred_total += 1

        return unpreferred_total


def add_ta(L, sections_array, ta_array, preference_array, daytime_array):
    """ Assigning a TA to a certain lab section
    This code is very messy and will likely need to be cleaned up
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum TA number for each section
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
        daytime_array (numpy array): 1d array of the times for each of the 17 sections
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    candidate_tas = []
    lab_total = []
    solutions_dict = defaultdict(int)
    day_dict = defaultdict(list)

    # get the number of labs each TA is assigned to and store those values in a list
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
    preferences = list(preference_array)

    # numpy array containing index of where 1 is present in the L array
    solutions = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section
    for solution in solutions:
        solutions_dict[solution[0]] = solution[1]

    for key, value in solutions_dict.items():
        # append to a new dictionary with key being the ta, value being the section time
        day_dict[key] = daytime_array[value]

    # can definitely break apart into functions

    for i in range(len(assigned_vs_needed)):
        # Labs that need more TAs are prioritized first
        if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
            lab_to_receive_ta = i
            # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
            # first element being from L and the second element being from sections_array
            for j in range(len(preferences)):
                # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit, and would have
                # no time conflicts, they are a candidate TA for that section
                if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
                    lab_time = daytime_array[lab_to_receive_ta]
                    for key, value in day_dict.items():
                        if key == j and lab_time not in value:
                            candidate_tas.append(j)

        # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
        # instead
        if len(candidate_tas == 0):
            for j in range(len(preferences)):
                # if a TA is willing to work in the lab to receive a TA, hasn't reached their section limit,
                # and has no time conflicts with that section, they are a candidate TA for that section
                if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                    lab_time = daytime_array[lab_to_receive_ta]
                    for key, value in day_dict.items():
                        if key == j and lab_time not in value:
                            candidate_tas.append(j)

        # if there are candidate TAs available, choose one at random to be assigned to the lab
        if len(candidate_tas > 0):
            ta_to_be_assigned = rnd.choice(candidate_tas)
            L[ta_to_be_assigned, lab_to_receive_ta] = 1

        else:
            # now focus on labs that have enough TAs
            if assigned_vs_needed[i][0] >= assigned_vs_needed[i][1]:
                lab_to_receive_ta = i
                # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
                # first element being from L and the second element being from sections_array
                for j in range(len(preferences)):
                    # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit, and has
                    # no time conflicts with that section, they are a candidate TA for that section
                    if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
                        candidate_tas.append(j)

            # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
            # instead
            if len(candidate_tas == 0):
                for j in range(len(preferences)):
                    # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit,
                    # and has no time conflicts with that section, they are a candidate TA for that section
                    if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                        lab_time = daytime_array[lab_to_receive_ta]
                        for key, value in day_dict.items():
                            if key == j and lab_time not in value:
                                candidate_tas.append(j)

            # if there are candidate TAs available, choose one at random to be assigned to the lab
            if len(candidate_tas > 0):
                ta_to_be_assigned = rnd.choice(candidate_tas)
                L[ta_to_be_assigned, lab_to_receive_ta] = 1

            else:
                # don't assign a TA to the lab section to be assigned a new TA if no candidates are available
                break

    return L


def remove_ta(L, sections_array, ta_array, preference_array, daytime_array):
    """ Removing a TA(s) from a certain lab section
    NEED TO ACCOUNT TIME CONFLICTS AND OVERALLOCATIONS
    Also need to consider preferred vs. willing
    This code is very messy and will likely need to be cleaned up
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum TA number for each section
        ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
        preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
        daytime_array (numpy array): 1d array of the times for each of the 17 sections
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    unassigned_tas = []
    lab_total = []
    day_dict = defaultdict(list)

    # get the labs of TAs each TA is assigned to and store those values in a list
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
    preferences = list(preference_array)

    # can definitely break apart into functions

    for i in range(len(assigned_vs_needed)):

        lab_to_lose_ta = i
        # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
        # first element being from L and the second element being from sections_array
        for j in range(len(preferences)):
            # if a TA does not prefer to work in a lab they are assigned to, remove them from that section
            if preferences[j][i] == 'U':
                unassigned_tas.append(j)

            # if a TA has a time conflict in a lab they are assigned to, remove them from that section
            lab_time = daytime_array[lab_to_lose_ta]
            for key, value in day_dict.items():
                if key == j and lab_time in value:
                    unassigned_tas.append(j)

            # if the TA is assigned too many labs and is only willing to work for the section to lose a TA, remove them
            # from that section
            for a, b in zip(lab_total, ta_array):
                if a > b and preferences[j][i] == 'W':
                    unassigned_tas.append(j)

        # if there are candidate TAs available to be removed, unassigned each one from the lab to lose a TA
        if len(unassigned_tas > 0):
            for ta in unassigned_tas:
                # only remove TAs from sections they were already assigned to
                if L[ta, lab_to_lose_ta] >= 1:
                    L[ta, lab_to_lose_ta] = 0

    return L


def swapper(L):
    """
    Swap two random values in each row for a specified row
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    # uncomment the following to iterate swapper
    # over multiple rows at a time
    # for val in range(rows):
    row = rnd.randrange(len(L))
    section = L[row]
    i = rnd.randrange(0, len(section))
    j = rnd.randrange(0, len(section))

    section[i], section[j] = section[j], section[i]
    return L


# def opposites(solution):
#     """
#     Create the complete opposite solution of the input
#     :param solution: (arr) one possible solution for the assignment
#     of TAs to sections
#     :return: solution: (arr) the solution, but all prior 0s are 1s
#     and vice versa
#     """
#     for row in solution:
#         for ind, num in enumerate(row):
#             if num == 0:
#                 row[ind] = 1
#             else:
#                 row[ind] = 0
#     return solution


def main():
    # load the CSV file containing information about the sections and store the values into a numpy array
    sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)

    # load the CSV file containing information about the TAs and store the values into an array
    tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

    E = Evo()

    # create arrays with crucial information for the objective functions to run (refer to documentation in each function
    # definition)
    ta_array = tas[:, 2]
    daytime_array = sections[:, 2]
    sections_array = sections[:, 6]
    preference_array = tas[:, 3:]

    # Register some objectives
    E.add_fitness_criteria("overallocation", overallocation, ta_array=ta_array)
    E.add_fitness_criteria("conflicts", conflicts, daytime_array=daytime_array)
    E.add_fitness_criteria("undersupport", undersupport, sections_array=sections_array)
    E.add_fitness_criteria("unwilling", unwilling, preference_array=preference_array)
    E.add_fitness_criteria("unpreferred", unpreferred, preference_array=preference_array)

    # Register some agents
    E.add_agent("swapper", swapper, k=1)
    E.add_agent("swapper", swapper, k=1)
    E.add_agent("swapper", swapper, k=1)

    # Seed the population with an initial random solution (numpy array of 43 rows by 17 columns as there are 17 sections
    # and 43 tas)

    # 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    L = np.random.choice([0, 1], size=(len(tas), len(sections)), p=[1. / 3, 2. / 3])
    E.add_solution(L)

    # Run the evolver
    E.evolve(1000000, 100, 10000)

    # Print final results
    # print('Final Results:', E)


if __name__ == '__main__':
    main()
