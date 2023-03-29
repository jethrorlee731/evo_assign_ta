"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (assign_ta.py)
March 28, 2023

assign_ta.py - objectives for the framework to evaluate the solutions produced
"""
import numpy as np

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
    oa_penalty = int(sum(list(map(lambda x, y: x - y if x > y else 0, labs, MAX_ASSIGNED_LIST))))

    return oa_penalty

def conflicts(L):
    """
    Number of TAs with one or more time conflicts
    Args:
        L (numpy array): a solution in the form of a 2D array with sections as columns and tas as rows
    Return:
        time_conflicts (int): number of TAs with one or more time conflict
    """
    # retrieve the indices in the inputted solution that indicate a TA is assigned to a lab along with the time
    # associated with the section of that lab
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
    total_undersupport = int(sum(map(lambda x, y: x - y if x > y else 0, MIN_TA_LIST, labs)))

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
