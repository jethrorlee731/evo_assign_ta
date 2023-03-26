from evo_copy import Evo
import random as rnd
import numpy as np
from collections import Counter, defaultdict

# load the CSV file containing information about the sections and store the values into a numpy array
sections = np.loadtxt('sections.csv', skiprows=1, delimiter=',', dtype=str)

# load the CSV file containing information about the TAs and store the values into an array
tas = np.loadtxt('tas.csv', skiprows=1, delimiter=',', dtype=str)


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

    # # calculate how many labs each TA is assigned to
    # for sol in L:
    #     print(sol)

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
    return oa_penalty


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
    assignments_dict = defaultdict(list)
    day_dict = defaultdict(list)

    # numpy array containing index of where 1 is present in the L array
    assignments = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section
    for assignment in assignments:
        assignments_dict[assignment[0]].append(int(assignment[1]))

    if daytime_array is not None:
        for key, value in assignments_dict.items():
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
    # for assignments in L.transpose():
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


def add_ta_preferred(L, preference_array):
    """ Assigning a TA to a certain lab section they prefer to work at
    Args:
        L (numpy array): 2D array with sections as columns and tas as rows
        preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    good_assignments = []

    # get the preferences that TAs have for working in particular sections and store them in a list
    preferences = list(preference_array)

    # look for combinations of TAs and labs they would prefer working at
    for i in range(len(preferences)):
        for j in range(len(preferences[i])):
            # store a TA and a section they prefer to work at
            if preferences[i][j] == 'P':
                good_assignments.append((i, j))

    # if there are candidate TAs available to be assigned, assign a TA in a section they prefer
    if len(good_assignments > 0):
        addition = rnd.choice(good_assignments)
        L[addition[0], addition[1]] = 1

    return L


def add_ta_willing(L, preference_array):
    """ Assigning a TA to a certain lab section they are only willing to work at
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
        preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    good_assignments = []

    # get the preferences that TAs have for working in particular sections and store them in a list
    preferences = list(preference_array)

    # look for combinations of TAs and labs they are only willing to work at
    for i in range(len(preferences)):
        for j in range(len(preferences[i])):
            # store a TA who is willing to work in a lab they are assigned to as well as that section
            if preferences[i][j] == 'W':
                good_assignments.append((i, j))

    # if there are candidate TAs available to be assigned, assign a TA to a section they're willing to help
    if len(good_assignments > 0):
        addition = rnd.choice(good_assignments)
        L[addition[0], addition[1]] = 1

    return L


def add_ta_undersupport(L, sections_array):
    """ Assigning a TA to a certain lab section that needs more assistance
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
        sections_array (numpy array): 1D array containing the minimum number of TAs each section needs
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # intializing a list that stores undersupported labs
    labs_in_need = []

    # sum up each column of the array to get the number of TAs assigned to each lab
    ta_num = list(map(sum, zip(*L)))

    # gather the minimum number of TAs each lab needs and store those values in a list
    sections_array = list(sections_array)

    # create a list of tuples, where the first element is the number of TAs assigned to a lab and the second is the
    # minimum number of TAs each lab needs
    assigned_vs_needed = list(zip(ta_num, sections_array))

    for i in range(len(assigned_vs_needed)):
        # store the labs that need more TAs in a list
        if assigned_vs_needed[i][0] < assigned_vs_needed[i][1]:
            labs_in_need.append(i)

        # if there are undersupported labs, assign a random TA to a random lab that needs more TAs
        if len(labs_in_need) > 0:
            lab = rnd.choice(labs_in_need)
            ta = rnd.randrange(len(ta_num))
            L[ta, lab] = 1

    return L


def remove_unpreferred(L, preference_array):
    """ Removing a random TA who doesn't want to at a lab section they're assigned to
    Args:
        L (numpy array): 2D array with sections in columns and TAs in rows
        preference_array (numpy array): 2D array of whether TAs are unwilling, willing, or preferred for each section
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    bad_assignments = []

    # get the preferences that TAs have for working in particular sections and store them in a list
    preferences = list(preference_array)

    # look for combinations of TAs and labs they don't prefer to work at
    for i in range(len(preferences)):
        for j in range(len(preferences[i])):
            # store a TA and the lab they do not prefer to work at
            if preferences[i][j] == 'U':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from a section they don't prefer
    if len(bad_assignments > 0):
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


def remove_willing(L, preference_array):
    """ Removing a random TA who is only willing to work for a lab section they're assigned to
    Args:
        L (numpy array): 2D array with sections as columns and TAs as rows
        preference_array (numpy array): 2d array of whether TAs are unwilling, willing, or preferred for each section
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    bad_assignments = []

    # get the preferences TAs have for working in particular sections and store them in a list
    preferences = list(preference_array)

    # look for combinations of TAs and labs they are only willing to work at
    for i in range(len(preferences)):
        for j in range(len(preferences[i])):
            # store a TA and the lab they are only willing to work for
            if preferences[i][j] == 'W':
                bad_assignments.append((i, j))

    # if there are candidate TAs available to be removed, remove a TA from the section they're only willing to assist
    if len(bad_assignments > 0):
        removal = rnd.choice(bad_assignments)
        L[removal[0], removal[1]] = 0

    return L


def remove_time_conflict(L, daytime_array):
    """ Removing a random TA from a certain lab section if they have a time conflict
    Args:
        L (numpy array): 2D array with sections in columns and TAs in rows
        daytime_array (numpy array): 1D array of the times for each of the 17 sections
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    # initialize variables and default dictionaries
    day_dict = defaultdict(list)
    assignments_dict = defaultdict(list)
    bad_assignments = []

    # numpy array containing indices of where 1 is present (indicating a TA is working at a specific lab) in the L array
    assignments = np.argwhere(L == 1)

    # create a dictionary with key: ta, value: section they're assigned to
    for assignment in assignments:
        assignments_dict[assignment[0]].append(int(assignment[1]))

    # gathering the times of the labs that a TA is assigned to
    if daytime_array is not None:
        for key, value in assignments.items():
            # append to a new dictionary with key being the TA, value being a tuple with the section & lab section time
            for lab in value:
                day_dict[key].append((lab, daytime_array[lab]))

        # store all the TAs with a time conflict
        if len(day_dict.keys()) > 0:
            times = []

            # inspect TAs who are assigned to multiple labs
            for ta in day_dict.keys():
                for lab_info in day_dict[ta]():
                    # store the times a TA has to work at a lab in a list
                    times.append(lab_info[1])

                # create a frequency distribution of the times a TA has to be at a lab
                times_dict = dict(Counter(times))
                for key, value in times_dict.items():
                    # if a TA is working for two or more labs that run simultaneously, save the labs' shared time and
                    # the TA
                    if value > 1:
                        bad_time = key
                        candidate_ta = ta

            # go through all the TAs with time conflicts
            for ta in day_dict.keys():
                if ta == candidate_ta:
                    # go through the labs that the TA is assigned to that run at the same time as other labs the TA is
                    # assigned to
                    for lab_info in day_dict[ta]():
                        if lab_info[1] == bad_time:
                            # save the actual lab
                            bad_lab = lab_info

                # save tuples containing a TA and a lab they may not be able to attend due to time conflicts
                bad_assignments.append((ta, bad_lab))

        # if there are candidate TAs available to be removed, remove a TA with a time conflict
        if len(bad_assignments > 0):
            removal = rnd.choice(bad_assignments)
            L[removal[0], removal[1]] = 0

    return L


def remove_ta_overallocated(L, sections_array, ta_array):
    """ Removing a random TA who is over-allocated too many labs
    Args:
        L (numpy array): 2D array with sections in columns and TAs in rows
        sections_array (numpy array): 1D array containng the minimum number of TAs each section needs
        ta_array (numpy array): 1D array containing the max amount of labs each TA wants to be assigned to
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the agent's changes
    """
    pass


def swapper(L):
    """
    Swap two random TA to lab assignments
    Args:
        L (numpy array): 2D array with sections in columns and TAs in rows
    Returns:
        L (numpy array): an updated version of the inputted 2D array that reflects the swapper's changes
    """

    row = rnd.randrange(len(L))
    section = L[row]
    i = rnd.randrange(0, len(section))
    j = rnd.randrange(0, len(section))

    section[i], section[j] = section[j], section[i]
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
