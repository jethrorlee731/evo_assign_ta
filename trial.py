import pandas as pd
from evo import Evo
import random as rnd
import numpy as np
from collections import Counter, defaultdict
from collections import defaultdict


def overallocation(L):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows

    Return:
        oa_penalty (int): total overallocation penalty across all tas
    """
    # separate the solution from the other data
    solution = np.array(list(map(int, L[:731]))).reshape(43, 17)
    rest = L[731:]

    # get the maximum labs tas are willing to support & remove from the total array
    ta_data = rest[85:].reshape(43, 18)
    max_labs = list(map(int, [item[0] for item in ta_data]))

    # initialize empty list and variables
    sum_total = []
    oa_penalty = 0

    for row in solution:
        # get the sum of each row
        total = sum(row)
        # add it to the list
        sum_total.append(total)

    # convert 1d array to a list
    ta_array = list(max_labs)

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
    # separate the solution from the other data
    solution = np.array(list(map(int, L[:731]))).reshape(43, 17)
    rest = L[731:]
    section_data = rest[:85].reshape(17, 5)

    # 1d array of the times for each of the 17 sections
    daytime_array = [item[0] for item in section_data]

    # initialize variables and default dictionaries
    total_conflict = 0
    solutions_dict = defaultdict(int)
    day_dict = defaultdict(list)

    # numpy array containing index of where 1 is present in the L array
    solutions = np.argwhere(solution == 1)

    # create a dictionary with key: ta, value: section
    for sol in solutions:
        solutions_dict[sol[0]] = sol[1]

    for key, value in solutions_dict.items():
        # append to a new dictionary with key being the ta, value being the section time
        day_dict[key].append(daytime_array[value])

    for value in day_dict.values():
        if len(set(value)) != len(value):
            # there is a ta assigned to the same lab time over more than one section - add one to the counter
            total_conflict += 1

    return total_conflict


def undersupport(L):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
        sections_array (numpy array): 1d array of minimum ta number for each section
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """

    # separate the solution from the other data
    solution = np.array(list(map(int, L[:731]))).reshape(43, 17)
    rest = L[731:]

    section_data = rest[:85].reshape(17, 5)
    sections_array = np.array(list(map(int, [item[-1] for item in section_data])))

    # initialize total for undersupport
    total_undersupport = 0

    # sum up each column of the array - number of tas for each column
    ta_num = list(map(sum, zip(*solution)))

    sections_array = list(sections_array)

    for a, b in zip(ta_num, sections_array):
        if a < b:
            # add to total for undersupport
            total_undersupport += (b - a)

    return total_undersupport


def unwilling(L):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
    Return:
        unwilling_total (int): total of allocation a ta to an unwilling section
    """

    solution = L[:731].reshape(43, 17)
    rest = L[731:]
    ta_data = rest[85:].reshape(43, 18)

    # create 2d array of whether the ta is unwilling, willing, or preferred for each section
    prefs_array = np.array([item[1:] for item in ta_data])

    # initialize counter for number of unwilling
    unwilling_total = 0

    # https://stackoverflow.com/questions/44639976/zip-three-2-d-arrays-into-tuples-of-3
    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((solution, prefs_array)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == '1' and item[1] == 'U':
            # increase the number of unwilling counter if the ta is assigned and they say they are unwilling for that
            unwilling_total += 1

    return unwilling_total


def unpreferred(L):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
    Returns:
        unpreferred_total (int): total of allocation a ta to a willing section
    """
    solution = L[:731].reshape(43,17)
    rest = L[731:]
    ta_data = rest[85:].reshape(43, 18)

    # create 2d array of whether the ta is unwilling, willing, or preferred for each section
    prefs_array = np.array([item[1:] for item in ta_data])

    # initialize counter for number of unwilling
    unpreferred_total = 0

    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((solution, prefs_array)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == '1' and item[1] == 'W':
            # increase the number of willing counter if the ta is assigned and they say they are willing for that
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
    return section


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
    # print(sections)

    # load the CSV file containing information about the TAs and store the values into an array
    tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)
    # print(tas)

    E = Evo()

    # Register some objectives

    E.add_fitness_criteria("overallocation", overallocation)
    E.add_fitness_criteria("conflicts", conflicts)
    E.add_fitness_criteria("undersupport", undersupport)
    E.add_fitness_criteria("unwilling", unwilling)
    E.add_fitness_criteria("unpreferred", unpreferred)

    # Register some agents
    # E.add_agent("swapper", swapper, k=1)
    #
    # Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
    # # sections and 43 tas)
    # 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    # N = 30
    # FIGURE OUT HOW TO GENERATE RANDOM 43 ROWS BY 17 COLUMNS OF 0 AND 1S TO REPRESENT L

    from_tas = tas[:, 2:20]
    from_sections = sections[:, 2:7]

    # create an initial random solution (np array)
    rnd_sol = np.array([rnd.randint(0, 1) for _ in range(len(sections) * len(tas))])

    # # append essential section and maximum lab data
    expanded_sol = np.append(rnd_sol, from_sections)
    expanded_sol = np.append(expanded_sol, from_tas)

    # rnd_sol = np.array([rnd.randint(0, 1) for _ in range(len(sections) * len(tas))]).reshape(len(tas), len(sections))

    E.add_solution(expanded_sol)


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
