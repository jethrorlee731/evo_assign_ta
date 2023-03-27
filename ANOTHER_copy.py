from evo import Evo
import random as rnd
import numpy as np

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
    oa_penalty = int(sum([x - y for x,y in zip(sums, MAX_ASSIGNED_LIST) if x > y]))

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
    time_conflicts = list(np.array([len(row[row != '0']) != len(set(row[row != '0'])) for row in ta_sections])).count(True)

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
    total_undersupport = int(sum([y-x for x,y in zip(sums, MIN_TA_LIST) if y > x]))

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


#####################################################################################################
# JC'S AGENTS
# def add_ta(L, sections_array, ta_array, preference_array, daytime_array):
#     """ Assigning a TA to a certain lab section
#     This code is very messy and will likely need to be cleaned up
#     Args:
#         L (numpy array): 2d array with sections as columns and tas as rows
#         sections_array (numpy array): 1d array of minimum TA number for each section
#         ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
#         preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
#         daytime_array (numpy array): 1d array of the times for each of the 17 sections
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     candidate_tas = []
#     lab_total = []
#     solutions_dict = defaultdict(int)
#     day_dict = defaultdict(list)
#
#     # get the number of labs each TA is assigned to and store those values in a list
#     for row in L:
#         # get the sum of each row
#         total = sum(row)
#         # add it to the list
#         lab_total.append(total)
#
#     # convert 1d array containing the max amount of labs each TA wants to be assigned to a list
#     ta_array = list(ta_array)
#     # sum up each column of the array - number of TAs assigned to each lab
#     ta_num = list(map(sum, zip(*L)))
#     # gather the minimum number of TAs each lab needs and store those values in a list
#     sections_array = list(sections_array)
#
#     # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
#     # minimum number of TAs each lab needs
#     assigned_vs_needed = list(zip(ta_num, sections_array))
#
#     # get the preferences TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # numpy array containing index of where 1 is present in the L array
#     solutions = np.argwhere(L == 1)
#
#     # create a dictionary with key: ta, value: section
#     for solution in solutions:
#         solutions_dict[solution[0]] = solution[1]
#
#     for key, value in solutions_dict.items():
#         # append to a new dictionary with key being the ta, value being the section time
#         day_dict[key] = daytime_array[value]
#
#     # can definitely break apart into functions
#
#     for i in range(len(assigned_vs_needed)):
#         lab_to_receive_ta = i
#
#         # Labs that need more TAs are prioritized first
#         if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
#             # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
#             # first element being from L and the second element being from sections_array
#             for j in range(len(preferences)):
#                 # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit, and would have
#                 # no time conflicts, they are a candidate TA for that section
#                 if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
#                     lab_time = daytime_array[lab_to_receive_ta]
#                     for key, value in day_dict.items():
#                         if key == j and lab_time not in value:
#                             candidate_tas.append(j)
#
#         # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
#         # instead
#         if len(candidate_tas) == 0:
#             for j in range(len(preferences)):
#                 # if a TA is willing to work in the lab to receive a TA, hasn't reached their section limit,
#                 # and has no time conflicts with that section, they are a candidate TA for that section
#                 if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
#                     lab_time = daytime_array[lab_to_receive_ta]
#                     for key, value in day_dict.items():
#                         if key == j and lab_time not in value:
#                             candidate_tas.append(j)
#
#         # if there are candidate TAs available, choose one at random to be assigned to the lab
#         if len(candidate_tas) > 0:
#             ta_to_be_assigned = rnd.choice(candidate_tas)
#             L[ta_to_be_assigned, lab_to_receive_ta] = 1
#
#         else:
#             # now focus on labs that have enough TAs
#             if assigned_vs_needed[i][0] >= assigned_vs_needed[i][1]:
#                 lab_to_receive_ta = i
#                 # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
#                 # first element being from L and the second element being from sections_array
#                 for j in range(len(preferences)):
#                     # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit, and has
#                     # no time conflicts with that section, they are a candidate TA for that section
#                     if preferences[j][i] == 'P' and (lab_total[i] < ta_array[i]):
#                         candidate_tas.append(j)
#
#             # if no eligible TAs can be assigned to the lab, select from the TAs who are willing to work at that section
#             # instead
#             if len(candidate_tas) == 0:
#                 for j in range(len(preferences)):
#                     # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit,
#                     # and has no time conflicts with that section, they are a candidate TA for that section
#                     if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
#                         lab_time = daytime_array[lab_to_receive_ta]
#                         for key, value in day_dict.items():
#                             if key == j and lab_time not in value:
#                                 candidate_tas.append(j)
#
#             # if there are candidate TAs available, choose one at random to be assigned to the lab
#             if len(candidate_tas) > 0:
#                 ta_to_be_assigned = rnd.choice(candidate_tas)
#                 L[ta_to_be_assigned, lab_to_receive_ta] = 1
#
#             else:
#                 # don't assign a TA to the lab section to be assigned a new TA if no candidates are available
#                 break
#
#     return L
#
#
# def _time_conflict(daytime_array, lab_to_lose_ta, day_dict, unassigned_tas, j):
#
#     lab_time = daytime_array[lab_to_lose_ta]
#
#     allkeys = list(day_dict.keys())
#     allvals = list(day_dict.values())
#
#     if allkeys[0] == j and lab_time in allvals[0]:
#         unassigned_tas.append(j)
#         del day_dict[allkeys[0]]
#
#     _time_conflict(daytime_array, lab_to_lose_ta, day_dict, unassigned_tas, j)
#
#
# def _unassign_tas(unassigned_tas, L, lab_to_lose_ta):
#     if len(unassigned_tas) > 0:
#
#         ta = unassigned_tas[0]
#
#         if L[ta, lab_to_lose_ta] >= 1:
#             L[ta, lab_to_lose_ta] = 0
#
#         _unassign_tas(unassigned_tas[1:], L, lab_to_lose_ta)
#
#
#
# def remove_ta(L, sections_array, ta_array, preference_array, daytime_array):
#     """ Removing a TA(s) from a certain lab section
#     NEED TO ACCOUNT TIME CONFLICTS AND OVERALLOCATIONS
#     Also need to consider preferred vs. willing
#     This code is very messy and will likely need to be cleaned up
#     Args:
#         L (numpy array): 2D array with sections as columns and tas as rows
#         sections_array (numpy array): 1d array of minimum TA number for each section
#         ta_array (numpy array): 1d array containing the max amount of labs each ta wants to be assigned to
#         preference_array (numpy array): 2d array of whether the ta is unwilling, willing, or preferred for each section
#         daytime_array (numpy array): 1d array of the times for each of the 17 sections
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     unassigned_tas = []
#     lab_total = []
#     day_dict = defaultdict(list)
#
#     # get the labs of TAs each TA is assigned to and store those values in a list
#     for row in L:
#         # get the sum of each row
#         total = sum(row)
#         # add it to the list
#         lab_total.append(total)
#
#     # convert 1d array containing the max amount of labs each TA wants to be assigned to a list
#     ta_array = list(ta_array)
#     # sum up each column of the array - number of TAs assigned to each lab
#     ta_num = list(map(sum, zip(*L)))
#     # gather the minimum number of TAs each lab needs and store those values in a list
#     sections_array = list(sections_array)
#
#     # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
#     # minimum number of TAs each lab needs
#     assigned_vs_needed = list(zip(ta_num, sections_array))
#
#     # get the preferences TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # can definitely break apart into functions
#
#     for i in range(len(assigned_vs_needed)):
#
#         lab_to_lose_ta = i
#         # pair up one by one the two 2D arrays element by element; new_list is a list of tuples with the
#         # first element being from L and the second element being from sections_array
#         for j in range(len(preferences)):
#             # if a TA does not prefer to work in a lab they are assigned to, remove them from that section
#             if preferences[j][i] == 'U':
#                 unassigned_tas.append(j)
#
#             # if a TA has a time conflict in a lab they are assigned to, remove them from that section
#             _time_conflict(daytime_array, lab_to_lose_ta, day_dict, unassigned_tas, j)
#
#             # if the TA is assigned too many labs and is only willing to work for the section to lose a TA, remove them
#             # from that section
#             for a, b in zip(lab_total, ta_array):
#                 if a > b and preferences[j][i] == 'W':
#                     unassigned_tas.append(j)
#
#         # if there are candidate TAs available to be removed, unassigned each one from the lab to lose a TA
#         _unassign_tas(unassigned_tas, L, lab_to_lose_ta)
#
#     return L
#
#
# def swapper(L):
#     """
#     Swap two random values in each row for a specified row
#     Args:
#         L (numpy array): 2D array with sections as columns and tas as rows
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
#     """
#     # uncomment the following to iterate swapper
#     # over multiple rows at a time
#     # for val in range(rows):
#     row = rnd.randrange(len(L))
#     section = L[row]
#     i = rnd.randrange(0, len(section))
#     j = rnd.randrange(0, len(section))
#
#     section[i], section[j] = section[j], section[i]
#     return section

#####################################################################################################
# # JETHRO'S AGENTS
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
    """ Removing a random TA who doesn't want to at a lab section they're assigned to
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
            if preference_list[i][j] == 'U':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from a section they don't prefer
    if len(bad_assignments) > 0:
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


def remove_willing(solutions):
    """ Removing a random TA who is only willing to work for a lab section they're assigned to
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
            if preference_list[i][j] == 'W':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from the section they're only willing to assist
    if len(bad_assignments) > 0:
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


# def remove_time_conflict(L):
#     """ Removing a random TA from a certain lab section if they have a time conflict
#     Args:
#         L (numpy array): 2D array with sections in columns and TAs in rows
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     # initialize variables and default dictionaries
#     total_conflict = 0
#     solutions_dict = defaultdict(list)
#     day_dict = defaultdict(list)
#     bad_assignments = []
#
#     # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
#     solutions = np.argwhere(L == 1)
#
#     # create a dictionary with key: ta, value: section
#     for sol in solutions:
#         try:
#             solutions_dict[sol[0]].append(int(sol[1]))
#         except:
#             solutions_dict[sol[0]] = [int(sol[1])]
#
#     for key, value in solutions_dict.items():
#         for number in value:
#             number = DAYTIME_LIST[number]
#             # append to a new dictionary with key being the ta, value being the section times (list)
#             day_dict[key].append(number)
#
#     # store all the TAs with a time conflict
#     if len(day_dict.values()) > 0:
#         # inspect TAs who are assigned to multiple labs
#         for key, value in day_dict.items():
#
#             if set(value) != value:
#                 # empty list to hold unique elements from the list
#                 newlist = []
#                 # empty list to hold the duplicate elements from the list
#                 duplist = []
#                 for number in value:
#                     if number not in newlist:
#                         newlist.append(number)
#                     else:
#                         duplist.append(number)
#                 # save the ta and bad time (save the first bad time if there is multiple)
#                 candidate_ta = key
#                 bad_time = duplist[0]
#         # NOW THAT I GOT THE TA NUMBER AND THE DUPLICATED TIME, I NEED TO MAP IT BACK TO THE TA SECTION. NOT SURE HOW
#         # TO DO THAT. BECAUSE THEN I CAN USE THE TA NUMBER, AND TA SECTION TO THEN REMOVE IT
#
#     bad_assignments.append((candidate_ta,))
#     # if there are candidate TAs available to be removed, remove a TA with a time conflict
#     if len(bad_assignments) > 0:
#         removal = rnd.choice(bad_assignments)
#         L[removal[0], removal[1]] = 0
#
#     return L

# def remove_ta_overallocated(L, sections_array, ta_array):
#     """ Removing a random TA who is over-allocated too many labs
#     Args:
#         L (numpy array): 2D array with sections in columns and TAs in rows
#         sections_array (numpy array): 1D array containng the minimum number of TAs each section needs
#         ta_array (numpy array): 1D array containing the max amount of labs each TA wants to be assigned to
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     pass
#

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
    # print(L)
    lab1 = int(rnd.randrange(L.shape[1]))
    lab2 = lab1
    while lab2 == lab1:
        lab2 = int(rnd.randrange(L.shape[1]))

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
    # print(L)
    ta1 = int(rnd.randrange(L.shape[0]))
    ta2 = ta1
    while ta2 == ta1:
        ta2 = int(rnd.randrange(L.shape[0]))

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
    E.add_agent("remove_willing", remove_willing, k=1)
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
