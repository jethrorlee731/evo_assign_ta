from evo import Evo
import random as rnd
import numpy as np
from collections import defaultdict

# load the CSV file containing information about the sections and store the values into a numpy array
sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
# load the CSV file containing information about the TAs and store the values into an array
tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)

# Constant - list of max_assigned for the 43 tas
MAX_ASSIGNED_LIST = list(map(int, [item[2] for item in tas]))
# Constant - list of the times for each of the 17 sections
DAYTIME_LIST = [item[2] for item in sections]
# Constant - list of minimum amount of tas for each of the 17 sections
MIN_TA_LIST = list(map(int, [item[-2] for item in sections]))
# Constant - 2d array of ta preferences
PREFERENCE_ARRAY = np.array([item[3:] for item in tas])


def overallocation(L):
    """ Sum of the overallocation penalty over all TAs
    Args:
        L (numpy array): a 2D array with sections as columns and TAs as rows
    Return:
        oa_penalty (int): total overallocation penalty across all tas
    """
    # list of sum of each row (each ta)
    sums = list(L.sum(axis=1))

    # add overallocation penalty if the number of assigned to the ta is more than their max
    oa_penalty = int(sum([x - y for x, y in zip(sums, MAX_ASSIGNED_LIST) if x > y]))

    return oa_penalty


def conflicts(L):
    """ Number of TAs with one or more time conflicts
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
    Return:
        time_conflicts (int): number of tas with one or more time conflict
    """

    ta_sections = np.where(L == 1, DAYTIME_LIST, L)

    # count number of conflicts if a ta is assigned to 2 sections at the same time
    time_conflicts = list(np.array([len(row[row != '0']) != len(set(row[row != '0'])) for row in ta_sections])).count(
        True)

    return time_conflicts


def undersupport(L):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """
    # sum up each column of the array - number of tas for each section
    sums = list(L.sum(axis=0))

    # sum up the total for unsupport - where there are less tas assigned to that section than required
    total_undersupport = int(sum([y - x for x, y in zip(sums, MIN_TA_LIST) if y > x]))

    return total_undersupport


def unwilling(L):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
    Return:
        unwilling_total (int): total of allocation a ta to an unwilling section
    """

    ta_sections = np.where(L == 1, PREFERENCE_ARRAY, 0)

    # count number of tas that are assigned to an unwilling section
    count_u = np.count_nonzero(ta_sections == 'U', axis=1)

    # get the sum of the list
    unwilling_total = sum(list(count_u))

    return unwilling_total


def unpreferred(L):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
    Returns:
        unpreferred_total (int): total of allocation a ta to a willing section
    """
    ta_sections = np.where(L == 1, PREFERENCE_ARRAY, 0)

    # count number of tas that are assigned to a willing section
    count_W = np.count_nonzero(ta_sections == 'W', axis=1)

    # get the sum of the list
    unpreferred_total = sum(list(count_W))

    return unpreferred_total


def add_ta_preferred(solutions):
    """ Assigning a TA to a certain lab section they prefer to work at
    Args:
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    good_assignments = []

    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = PREFERENCE_ARRAY.tolist()

    # look for combinations of TAs and labs they would prefer working at
    for i in range(len(preference_list)):
        for j in range(len(preference_list[i])):
            # store a TA and a section they prefer to work at
            if preference_list[i][j] == 'P':
                good_assignments.append((i, j))

    # if there are candidate TAs available to be assigned, assign a TA in a section they prefer
    if len(good_assignments) > 0:
        addition = rnd.choice(good_assignments)
        L[addition[0], addition[1]] = 1

    return L


def add_ta_willing(solutions):
    """ Assigning a TA to a certain lab section they are only willing to work at
    Args:
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    good_assignments = []

    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = PREFERENCE_ARRAY.tolist()

    # look for combinations of TAs and labs they are only willing to work at
    for i in range(len(preference_list)):
        for j in range(len(preference_list[i])):
            # store a TA who is willing to work in a lab they are assigned to as well as that section
            if preference_list[i][j] == 'W':
                good_assignments.append((i, j))

    # if there are candidate TAs available to be assigned, assign a TA to a section they're willing to help
    if len(good_assignments) > 0:
        addition = rnd.choice(good_assignments)
        L[addition[0], addition[1]] = 1

    return L


def add_ta_undersupport(solutions):
    """ Assigning a TA to a certain lab section that needs more assistance
    Args:
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # intializing a list that stores undersupported labs
    labs_in_need = []

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
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    bad_assignments = []

    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = PREFERENCE_ARRAY.tolist()

    # look for combinations of TAs and labs they don't prefer to work at
    for i in range(len(preference_list)):
        for j in range(len(preference_list[i])):
            # store a TA and the lab they do not prefer to work at
            if preference_list[i][j] == 'W':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from a section they don't prefer
    if len(bad_assignments) > 0:
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


def remove_unwilling(solutions):
    """ Removing a random TA who is not willing to work for a lab section they're assigned to
    Args:
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    bad_assignments = []

    L = solutions[0]

    # get the preferences that TAs have for working in particular sections and store them in a list
    preference_list = PREFERENCE_ARRAY.tolist()

    # look for combinations of TAs and labs they are only willing to work at
    for i in range(len(preference_list)):
        for j in range(len(preference_list[i])):
            # store a TA and the lab they are only willing to work for
            if preference_list[i][j] == 'U':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from the section they're only willing to assist
    if len(bad_assignments) > 0:
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


def remove_time_conflict(solutions):
    """ Removing a random TA from a certain lab section if they have a time conflict
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # initialize variables and default dictionaries
    solutions_dict = defaultdict(list)
    day_dict = defaultdict(list)
    candidate_labs = []
    viable_lab = False

    L = solutions[0]

    # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
    solutions = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section
    for sol in solutions:
        try:
            solutions_dict[sol[0]].append(int(sol[1]))
        except:
            solutions_dict[sol[0]] = [int(sol[1])]

    for ta, labs in solutions_dict.items():
        for lab in labs:
            time = DAYTIME_LIST[lab]
            # append to a new dictionary with key being the ta, value being the section times (list)
            day_dict[ta].append(time)

    # store all the TAs with a time conflict
    if len(day_dict.values()) > 0:
        # inspect TAs who are assigned to multiple labs
        for ta, times in day_dict.items():

            if set(times) != times:
                # empty list to hold unique the times that a TA must be at a lab
                ta_times = []

                for time in times:
                    if time not in times:
                        ta_times.append(time)
                    else:
                        bad_time = time
                        candidate_ta = ta
                        continue

    for i in range(len(DAYTIME_LIST)):
        if DAYTIME_LIST[i] == bad_time:
            candidate_labs.append(i)
    #
    while not viable_lab:
        lab = rnd.choice(candidate_labs)
        if L[candidate_ta, lab] == 1:
            L[candidate_ta, lab] = 0
            viable_lab = True

    return L


def remove_ta_overallocated(solutions):
    """ Removing a random TA from a lab who is over-allocated too many labs
    Args:
        solutions (list of numpy arrays): list of 2D arrays with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    L = solutions[0]
    candidate_tas = []
    candidate_labs = []

    assigned = list(L.sum(axis=1))
    assigned_vs_max = list(zip(assigned, MAX_ASSIGNED_LIST))
    for i in range(len(assigned_vs_max)):
        if assigned_vs_max[i][0] > assigned_vs_max[i][1]:
            candidate_tas.append(i)

    if len(candidate_tas) > 0:
        ta = rnd.choice(candidate_tas)

        for i in range(len(L[ta])):
            if L[ta][i] == 1:
                candidate_labs.append(i)

        lab = rnd.choice(candidate_labs)

        L[ta, lab] = 0

    return L


def swap_assignment(solutions):
    """
    Swap two random TA-lab assignments
    Args:
        solutions
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    L = solutions[0]
    row = rnd.randrange(len(L))
    ta_assignments = L[row, :]
    i = rnd.randrange(0, len(ta_assignments))
    j = rnd.randrange(0, len(ta_assignments))

    ta_assignments[i], ta_assignments[j] = ta_assignments[j], ta_assignments[i]
    return L


def swap_labs(solutions):
    """
    Swap two random lab assignments to different TAs
    Args:
        solutions (list of numpy arrays): a list containing possible TA-lab assignments that could work
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """
    L = solutions[0]
    lab1 = rnd.randrange(L.shape[1])
    lab2 = lab1
    while lab2 == lab1:
        lab2 = rnd.randrange(L.shape[1])

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
    L = solutions[0]
    ta1 = rnd.randrange(L.shape[0])
    ta2 = ta1
    while ta2 == ta1:
        ta2 = rnd.randrange(L.shape[0])

    L[[ta1, ta2]] = L[[ta2, ta1]]

    return L


def opposites(solutions):
    """
    Create the complete opposite solution of the input
    Args:
        solutions (list of numpy arrays): a list containing possible TA-lab assignments that could work
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes ( all prior 0s
                         are 1s and vice versa
    """
    L = solutions[0]
    for row in L:
        for ind, num in enumerate(row):
            if num == 0:
                row[ind] = 1
            else:
                row[ind] = 0
    return L


def main():
    # load the CSV file containing information about the sections and store the values into a numpy array
    # sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)
    # print(sections)

    # load the CSV file containing information about the TAs and store the values into an array
    # tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)
    # print(tas)

    # create an initial random solution (np array 17 x 43)
    # L = np.random.choice([0, 1], size=(len(sections), len(tas)), p=[1. / 3, 2. / 3])
    # print(L)
    # print(len(sections))
    # print(len(tas))
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

    N = len(sections) * len(tas)
    # Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
    # sections and 43 tas); 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    rnd_sol = np.array([rnd.randint(0, 1) for _ in range(N)]).reshape(43, 17)

    E.add_solution(rnd_sol)

    # Run the evolver
    # E.evolve(1000000, 100, 10000)
    E.evolve(10000, 100, 1000)
    #
    # # Print final results
    print(E)


if __name__ == '__main__':
    main()
