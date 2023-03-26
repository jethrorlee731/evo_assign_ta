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
    # initialize empty variable
    oa_penalty = 0

    # List of sum of each row
    sum_total = list(np.sum(L, axis=1))

    for a, b in zip(sum_total, MAX_ASSIGNED_LIST):
        if a > b:
            # add to overallocation penalty the difference of how much was actually assigned and the ta's max
            oa_penalty += (a - b)

    return oa_penalty


def conflicts(L):
    """ Number of TAs with one or more time conflicts
    Args:
        L (numpy array): 2d array with sections as columns and tas as rows
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
    for sol in solutions:
        try:
            solutions_dict[sol[0]].append(int(sol[1]))
        except:
            solutions_dict[sol[0]] = [int(sol[1])]

    for key, value in solutions_dict.items():
        for number in value:
            number = DAYTIME_LIST[number]
            # append to a new dictionary with key being the ta, value being the section time
            day_dict[key].append(number)

    for value in day_dict.values():
        if len(set(value)) != len(value):
            # there is a ta assigned to the same lab time over more than one section - add one to the counter
            total_conflict += 1

    return total_conflict


def undersupport(L):
    """ Total/sum of undersupport penalty over all TAs
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
    Return:
        total_undersupport (int): total undersupport penalty over all tas
    """
    # initialize total for undersupport
    total_undersupport = 0

    # sum up each column of the array - number of tas for each column
    ta_num = list(map(sum, zip(*L)))

    for a, b in zip(ta_num, MIN_TA_LIST):
        if a < b:
            # add to total for undersupport
            total_undersupport += (b - a)

    return total_undersupport


def unwilling(L):
    """ Total/sum of allocating a TA to an unwilling section
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
    Return:
        unwilling_total (int): total of allocation a ta to an unwilling section
    """
    # initialize counter for number of unwilling
    unwilling_total = 0

    # https://stackoverflow.com/questions/44639976/zip-three-2-d-arrays-into-tuples-of-3
    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((L, PREFERENCE_ARRAY)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == 1 and item[1] == 'U':
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
    # initialize counter for number of unwilling
    unpreferred_total = 0

    # pair up one by one the two 2d arrays element by element; new_list is a list of tuples with the
    # first element being from L and the second element being from sections_array
    new_list = list(map(tuple, np.dstack((L, PREFERENCE_ARRAY)).reshape(-1, 2)))

    for item in new_list:
        if item[0] == 1 and item[1] == 'W':
            # increase the number of willing counter if the ta is assigned and they say they are willing for that
            unpreferred_total += 1

    return unpreferred_total

#####################################################################################################
# JC'S AGENTS
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
        if len(candidate_tas) == 0:
            for j in range(len(preferences)):
                # if a TA is willing to work in the lab to receive a TA, hasn't reached their section limit,
                # and has no time conflicts with that section, they are a candidate TA for that section
                if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                    lab_time = daytime_array[lab_to_receive_ta]
                    for key, value in day_dict.items():
                        if key == j and lab_time not in value:
                            candidate_tas.append(j)

        # if there are candidate TAs available, choose one at random to be assigned to the lab
        if len(candidate_tas) > 0:
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
            if len(candidate_tas) == 0:
                for j in range(len(preferences)):
                    # if a TA prefers to work in the lab to receive a TA, hasn't reached their section limit,
                    # and has no time conflicts with that section, they are a candidate TA for that section
                    if preferences[j][i] == 'W' and (lab_total[i] < ta_array[i]):
                        lab_time = daytime_array[lab_to_receive_ta]
                        for key, value in day_dict.items():
                            if key == j and lab_time not in value:
                                candidate_tas.append(j)

            # if there are candidate TAs available, choose one at random to be assigned to the lab
            if len(candidate_tas) > 0:
                ta_to_be_assigned = rnd.choice(candidate_tas)
                L[ta_to_be_assigned, lab_to_receive_ta] = 1

            else:
                # don't assign a TA to the lab section to be assigned a new TA if no candidates are available
                break

    return L


def _time_conflict(daytime_array, lab_to_lose_ta, day_dict, unassigned_tas, j):
    lab_time = daytime_array[lab_to_lose_ta]
    for key, value in day_dict.items():
        if key == j and lab_time in value:
            unassigned_tas.append(j)

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
            _time_conflict(daytime_array, lab_to_lose_ta, day_dict, unassigned_tas, j)

            # if the TA is assigned too many labs and is only willing to work for the section to lose a TA, remove them
            # from that section
            for a, b in zip(lab_total, ta_array):
                if a > b and preferences[j][i] == 'W':
                    unassigned_tas.append(j)

        # if there are candidate TAs available to be removed, unassigned each one from the lab to lose a TA
        if len(unassigned_tas) > 0:
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

#####################################################################################################
# # JETHRO'S AGENTS
# def add_ta_preferred(L, preference_array):
#     """ Assigning a TA to a certain lab section they prefer to work at
#     Args:
#         L (numpy array): 2D array with sections as columns and tas as rows
#         preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     good_assignments = []
#
#     # get the preferences that TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # look for combinations of TAs and labs they would prefer working at
#     for i in range(len(preferences)):
#         for j in range(len(preferences[i])):
#             # store a TA and a section they prefer to work at
#             if preferences[i][j] == 'P':
#                 good_assignments.append((i, j))
#
#     # if there are candidate TAs available to be assigned, assign a TA in a section they prefer
#     if len(good_assignments > 0):
#         addition = rnd.choice(good_assignments)
#         L[addition[0], addition[1]] = 1
#
#     return L
#
#
# def add_ta_willing(L, preference_array):
#     """ Assigning a TA to a certain lab section they are only willing to work at
#     Args:
#         L (numpy array): 2D array with sections as columns and TAs as rows
#         preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     good_assignments = []
#
#     # get the preferences that TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # look for combinations of TAs and labs they are only willing to work at
#     for i in range(len(preferences)):
#         for j in range(len(preferences[i])):
#             # store a TA who is willing to work in a lab they are assigned to as well as that section
#             if preferences[i][j] == 'W':
#                 good_assignments.append((i, j))
#
#     # if there are candidate TAs available to be assigned, assign a TA to a section they're willing to help
#     if len(good_assignments > 0):
#         addition = rnd.choice(good_assignments)
#         L[addition[0], addition[1]] = 1
#
#     return L
#
#
# def add_ta_undersupport(L, sections_array):
#     """ Assigning a TA to a certain lab section that needs more assistance
#     Args:
#         L (numpy array): 2D array with sections as columns and TAs as rows
#         sections_array (numpy array): 1D array containing the minimum number of TAs each section needs
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     # intializing a list that stores undersupported labs
#     labs_in_need = []
#
#     # sum up each column of the array to get the number of TAs assigned to each lab
#     ta_num = list(map(sum, zip(*L)))
#
#     # gather the minimum number of TAs each lab needs and store those values in a list
#     sections_array = list(sections_array)
#
#     # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
#     # minimum number of TAs each lab needs
#     assigned_vs_needed = list(zip(ta_num, sections_array))
#
#     for i in range(len(assigned_vs_needed)):
#         # store the labs that need more TAs in a list
#         if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
#             labs_in_need.append(i)
#
#         # if there are undersupported labs, assign a random TA to a random lab that needs more TAs
#         if len(labs_in_need) > 0:
#             lab = rnd.choice(labs_in_need)
#             ta = rnd.randrange(len(ta_num))
#             L[ta, lab] = 1
#
#     return L
#
#
# def remove_unpreferred(L, preference_array):
#     """ Removing a random TA who doesn't want to at a lab section they're assigned to
#     Args:
#         L (numpy array): 2D array with sections in columns and TAs in rows
#         preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     bad_assignments = []
#
#     # get the preferences that TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # look for combinations of TAs and labs they don't prefer to work at
#     for i in range(len(preferences)):
#         for j in range(len(preferences[i])):
#             # store a TA and the lab they do not prefer to work at
#             if preferences[i][j] == 'U':
#                 bad_assignments.append((i, j))
#
#     # if there are candidate TAs available to be removed, remove a TA from a section they don't prefer
#     if len(bad_assignments > 0):
#         removal = rnd.choice(bad_assignments)
#         L[removal[0], removal[1]] = 0
#
#     return L
#
#
# def remove_willing(L, preference_array):
#     """ Removing a random TA who is only willing to work for a lab section they're assigned to
#     Args:
#         L (numpy array): 2D array with sections as columns and TAs as rows
#         preference_array (numpy array): 2d array of whether TAs are unwilling, willing, or preferred for each section
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     bad_assignments = []
#
#     # get the preferences TAs have for working in particular sections and store them in a list
#     preferences = list(preference_array)
#
#     # look for combinations of TAs and labs they are only willing to work at
#     for i in range(len(preferences)):
#         for j in range(len(preferences[i])):
#             # store a TA and the lab they are only willing to work for
#             if preferences[i][j] == 'W':
#                 bad_assignments.append((i, j))
#
#     # if there are candidate TAs available to be removed, remove a TA from the section they're only willing to assist
#     if len(bad_assignments > 0):
#         removal = rnd.choice(bad_assignments)
#         L[removal[0], removal[1]] = 0
#
#     return L
#
#
# def remove_time_conflict(L, daytime_array):
#     """ Removing a random TA from a certain lab section if they have a time conflict
#     Args:
#         L (numpy array): 2D array with sections in columns and TAs in rows
#         daytime_array (numpy array): 1D array of the times for each of the 17 sections
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
#     """
#     # initialize variables and default dictionaries
#     day_dict = defaultdict(list)
#     assignments_dict = defaultdict(list)
#     bad_assignments = []
#
#     # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
#     assignments = np.argwhere(L == 1)
#
#     # create a dictionary with key: ta, value: section they're assigned to
#     for assignment in assignments:
#         assignments_dict[assignment[0]].append(int(assignment[1]))
#
#     # gathering the times of the labs that a TA is assigned to
#     if daytime_array is not None:
#         for key, value in assignments.items():
#             # append to a new dictionary with key being the TA, value being a tuple with the section & lab section time
#             for lab in value:
#                 day_dict[key].append((lab, daytime_array[lab]))
#
#         # store all the TAs with a time conflict
#         if len(day_dict.keys()) > 0:
#             times = []
#
#             # inspect TAs who are assigned to multiple labs
#             for ta in day_dict.keys():
#                 for lab_info in day_dict[ta]():
#                     # store the times a TA has to work at a lab in a list
#                     times.append(lab_info[1])
#
#                 # create a frequency distribution of the times a TA has to be at a lab
#                 times_dict = dict(Counter(times))
#                 for key, value in times_dict.items():
#                     # if a TA is working for two or more labs that run simultaneously, save the labs' shared time and
#                     # the TA
#                     if value > 1:
#                         bad_time = key
#                         candidate_ta = ta
#
#             # go through all the TAs with time conflicts
#             for ta in day_dict.keys():
#                 if ta == candidate_ta:
#                     # go through the labs that the TA is assigned to that run at the same time as other labs the TA is
#                     # assigned to
#                     for lab_info in day_dict[ta]():
#                         if lab_info[1] == bad_time:
#                             # save the actual lab
#                             bad_lab = lab_info
#
#                 # save tuples containing a TA and a lab they may not be able to attend due to time conflicts
#                 bad_assignments.append((ta, bad_lab))
#
#         # if there are candidate TAs available to be removed, remove a TA with a time conflict
#         if len(bad_assignments > 0):
#             removal = rnd.choice(bad_assignments)
#             L[removal[0], removal[1]] = 0
#
#     return L
#
#
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
#
# def swapper(L):
#     """
#     Swap two random TA to lab assignments
#     Args:
#         L (numpy array): 2D array with sections in columns and TAs in rows
#     Returns:
#         L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
#     """
#
#     row = rnd.randrange(len(L))
#     section = L[row]
#     i = rnd.randrange(0, len(section))
#     j = rnd.randrange(0, len(section))
#
#     section[i], section[j] = section[j], section[i]
#     return L


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
    E.add_agent("swapper", swapper, k=1)

    N = len(sections) * len(tas)
    # Seed the population with an initial random solution (numpy array of 17 columns by 43 rows as there are 17
    # sections and 43 tas); 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    rnd_sol = np.array([rnd.randint(0, 1) for _ in range(N)]).reshape(43, 17)

    E.add_solution(rnd_sol)

    # Run the evolver
    E.evolve(1000000, 100, 10000)
    #
    # # Print final results
    print(E)


if __name__ == '__main__':
    main()
