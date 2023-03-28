"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (assign_ta.py)
March 27, 2023
"""
# import statements
from evo import Evo
import random as rnd
import numpy as np
from collections import defaultdict

# Universal variables

# load the CSV file containing information about the sections and store the values into a numpy array
SECTIONS = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
# load the CSV file containing information about the TAs and store the values into an array
TAS = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

# Constant - list of the maximum number of labs each of the 43 tas wants to work for
MAX_ASSIGNED_LIST = list(map(int, [item[2] for item in TAS]))
# Constant - list of the times for each of the 17 sections
DAYTIME_LIST = [item[2] for item in SECTIONS]
# Constant - list of the minimum amount of TAs that each of the 17 sections needs
MIN_TA_LIST = list(map(int, [item[-2] for item in SECTIONS]))
# Constant - 2d array of TA preferences
PREFERENCE_ARRAY = np.array([item[3:] for item in TAS])


# Objective functions - Determine the problems that each solution should address

def overallocation(L):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and TAs as rows
    Return:
        oa_penalty (int): total overallocation penalty across all tas
    """
    # calculate the sums of the rows of the solutions array to get a list of the number of labs each TA is assigned to
    labs = list(L.sum(axis=1))

    # add to the overallocation penalty if the number of labs assigned to a TA is more than their max
    oa_penalty = int(sum([x - y for x, y in zip(labs, MAX_ASSIGNED_LIST) if x > y]))

    return oa_penalty


def conflicts(L):
    """ Number of TAs with one or more time conflicts
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and tas as rows
    Return:
        time_conflicts (int): number of TAs with one or more time conflict
    """
    # retrieve the indices in the inputted solution that indicate a TA is assigned to a lab along with the time
    # associated with the section of that lab (AM I INTERPRETING THIS CORRECTLY???)
    ta_sections = np.where(L == 1, DAYTIME_LIST, L)

    # count number of conflicts, in which a TA is assigned to 2 sections that meet at the same time (each TA can count
    # up to a maximum of one conflict based on their schedule)
    time_conflicts = list(np.array([len(row[row != '0']) != len(set(row[row != '0'])) for row in ta_sections])).count(
        True)

    return time_conflicts


def undersupport(L):
    """ Total/sum of the undersupport penalty over all TAs
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and TAs as rows
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """
    # sum up each column of the solutions array to get the number of TAs assigned to each section
    labs = list(L.sum(axis=0))

    # sum up the total for undersupport - where there are less TAs assigned to that section than required
    total_undersupport = int(sum([y - x for x, y in zip(labs, MIN_TA_LIST) if y > x]))

    return total_undersupport


def unwilling(L):
    """ Total/sum of times when a TA is allocated to an unwilling section
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and TAs as rows
    Return:
        unwilling_total (int): total number of assignments where a TA is placed at a lab they are unwilling to work for
    """
    # get the indices from the solution array that indicate a TA to lab assignment as well as a TA's preference for
    # that section
    ta_sections = np.where(L == 1, PREFERENCE_ARRAY, 0)

    # count the number of instances where a TA is assigned to a lab they are unwilling to work for
    count_u = np.count_nonzero(ta_sections == 'U', axis=1)

    # get the sum of the list - add up the number of instances a TA is assigned to a lab they are unwilling to work at
    # for ALL the TAs
    unwilling_total = sum(list(count_u))

    return unwilling_total


def unpreferred(L):
    """ Total/sum of allocations where a TA is assigned to an unpreferred (but still willing) section
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and TAs as rows
    Returns:
        unpreferred_total (int): total number of times a TA is assigned to a willing section
    """
    # get the indices from the solution array that indicate a TA to lab assignment as well as a TA's preference for
    # that section
    ta_sections = np.where(L == 1, PREFERENCE_ARRAY, 0)

    # count number of tas that are assigned to a section they are only willing to work at
    count_W = np.count_nonzero(ta_sections == 'W', axis=1)

    # get the sum of the list - add up the number of instances a TA is assigned to a lab they are just willing to work
    # at for ALL the TAs
    unpreferred_total = sum(list(count_W))

    return unpreferred_total


# Agents - modify solutions so they better align with the objectives

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
    preference_list = PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA would prefer working at
    good_labs = np.where(np.array(preference_list[ta]) == 'P')

    # if there are candidate labs available, assign a TA in a section they prefer
    if len(good_labs[0]) > 0:
        addition = rnd.choice(good_labs[0])
        L[ta, addition] = 1

    return L


def add_ta_willing(solutions):
    """ Assigning a TA to a certain lab section they are only willing to work at
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # extract a solution
    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA would be willing to work at
    good_labs = np.where(np.array(preference_list[ta]) == 'W')

    # if there are candidate labs available, assign a TA in a section they are willing to work at
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
    # initializing a list that stores under-supported labs
    labs_in_need = []

    # extract a solution
    L = solutions[0]

    # sum up each column of the array to get the number of TAs assigned to each lab
    ta_num = list(map(sum, zip(*L)))

    # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
    # minimum number of TAs each lab needs
    assigned_vs_needed = list(zip(ta_num, MIN_TA_LIST))

    for i in range(len(assigned_vs_needed)):
        # store the labs that need more TAs in a list
        if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
            labs_in_need.append(i)

    # if there are undersupported labs, assign a random TA to a random lab that needs more TAs
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
    preference_list = PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(PREFERENCE_ARRAY.shape[0]))

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
    preference_list = PREFERENCE_ARRAY.tolist()

    # pick a random TA
    ta = rnd.choice(range(PREFERENCE_ARRAY.shape[0]))

    # look for the labs the chosen TA does not want to work at
    bad_labs = np.where(np.array(preference_list[ta]) == 'U')

    # if there are candidate labs available, remove a TA from a section they don't want to work for
    if len(bad_labs[0]) > 0:
        removal = rnd.choice(bad_labs[0])
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
    candidate_labs = []

    # extract a solution
    L = solutions[0]

    # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
    assignments = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section they are working at
    # WHAT IS THE PURPOSE OF THE TRY STATEMENT?
    for assignment in assignments:
        try:
            assignments_dict[assignment[0]].append(int(assignment[1]))
        except:
            assignments_dict[assignment[0]] = [int(assignment[1])]

    # go through each TA and each of their assignments
    for ta, labs in assignments_dict.items():
        for lab in labs:
            # get the times for each section a TA is assigned to
            time = DAYTIME_LIST[lab]
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
    candidate_labs = np.where(np.array(DAYTIME_LIST) == bad_time)

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
    # lists that store possible TAs and labs they could get removed from
    candidate_tas = []
    candidate_labs = []

    # extract a solution
    L = solutions[0]

    # calculate the sum of each row in the solution to get the number of labs each TA is assigned to
    assigned = list(L.sum(axis=1))

    # create a list with tuples, where the first element is the number of labs a TA is assigned to and the second is
    # the maximum number of labs they want to work at
    assigned_vs_max = list(zip(assigned, MAX_ASSIGNED_LIST))

    for i in range(len(assigned_vs_max)):
        # a TA is a candidate for removal from a lab if they are allocated too many labs
        if assigned_vs_max[i][0] > assigned_vs_max[i][1]:
            candidate_tas.append(i)

    # if there are TAs available to choose from, select one that will lose a lab assignment
    if len(candidate_tas) > 0:
        ta = rnd.choice(candidate_tas)

        # get the labs the TA is assigned to
        candidate_labs = np.where(np.array(L[ta]) == 1)

        # remove a TA from a random lab they're assigned to
        lab = rnd.choice(candidate_labs[0])
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


def main():
    # initialize the evolutionary programming framework
    E = Evo()

    # Register some objectives
    E.add_fitness_criteria("overallocation", overallocation)
    E.add_fitness_criteria("conflicts", conflicts)
    E.add_fitness_criteria("undersupport", undersupport)
    E.add_fitness_criteria("unwilling", unwilling)
    E.add_fitness_criteria("unpreferred", unpreferred)

    # Register some agents
    E.add_agent("swap_assignment", swap_assignment, k=1)
    E.add_agent("add_ta_preferred", add_ta_preferred, k=1)
    E.add_agent("add_ta_willing", add_ta_willing, k=1)
    E.add_agent("add_ta_undersupport", add_ta_undersupport, k=1)
    E.add_agent("remove_unpreferred", remove_unpreferred, k=1)
    E.add_agent("remove_unwilling", remove_unwilling, k=1)
    E.add_agent("remove_time_conflict", remove_time_conflict, k=1)
    E.add_agent("remove_ta_overallocated", remove_ta_overallocated, k=1)
    E.add_agent("swap_assignment", swap_assignment, k=1)
    E.add_agent("swap_labs", swap_labs, k=1)
    E.add_agent("swap_tas", swap_tas, k=1)
    E.add_agent("opposites", opposites, k=1)

    # Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
    # sections and 43 tas); 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    N = len(SECTIONS) * len(TAS)
    rnd_sol = np.array([rnd.randint(0, 1) for _ in range(N)]).reshape(43, 17)

    # Register the random solution into the framework
    E.add_solution(rnd_sol)

    # Run the evolver
    E.evolve(10000, 100, 1000)

    # Print final results
    print(E)


if __name__ == '__main__':
    main()
