from evo import Evo
import random as rnd
import pandas as pd


def overallocation(L, max_col, data):
    """ Sum of the overallocation penalty over all TAs
    L (list): list generated from the system of the number of labs assigned
    max_col (string): name of column of the TAs max number of labs
    data (dataframe): original dataframe containing information about a TA's availability
    """
    oa_sum = 0

    # PROBABLY COULD CHANGE THIS INTO FUNCTIONAL PROGRAMMING INSTEAD?
    for item, value in data.items():
        for number in L:
            # if assigned is greater than the number of labs requested by the TA
            if L > int(data[max_col]):
                # compute the difference between the two
                diff = L - int(data[max_col])
                # add to the sum of the overallocation
                oa_sum = oa_sum + diff

    return oa_sum


def conflicts(L, data):
    """ Number of TAs with one or more time conflicts

    """


def undersupport(L, min_col, data):
    """ Total/sum of undersupport penalty over all TAs
    L (list): list generated from the system of the number of labs assigned
    min_col (string): name of column of the TAs min number of labs
    data (dataframe): original dataframe containing information about a TA's availability
    """
    us_sum = 0

    for item, value in data.items():
        for number in L:
            # if assigned is greater than the number of labs requested by the TA
            if L < int(data[min_col]):
                # compute the difference between the two
                diff = int(data[min_col]) - L
                # add to the sum of the overallocation
                us_sum = us_sum + diff

    return us_sum


def unwilling(L, data):
    """ Total/sum of allocating a TA to an unwilling section
    L (list): list generated from the system of the assignments for a particular lab
    data (dataframe): original dataframe containing information about a TA's availability
    """
    unwilling = 0

    for item, value in data.items():
        # count the number of times a TA is unwilling to monitor the lab they are assigned to
        for lab_sec in L:
            if data[lab_sec] == 'U':
                unwilling += 1

    return unwilling


def unpreferred(L, data):
    """ Total/sum of allocation a TA to an unpreferred (but still willing) section
    L (list): list generated from the system of the assignments for a particular lab
    data (dataframe): original dataframe containing information about a TA's availability
    """

    unpreferred = 0

    for item, value in data.items():
        # count the number of times a TA is unwilling to monitor the lab they are assigned to
        for lab_sec in L:
            if data[lab_sec] == 'W':
                unpreferred += 1

    return unpreferred


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


def main():
    # load the CSV file containing information about the sections
    sections = pd.read_csv('sections.csv', header=0)

    # load the CSV file containing information about the TAs
    tas = pd.read_csv('tas.csv', header=0)


# E = Evo()
#
# # Register some objectives
# E.add_fitness_criteria("ssd", sumstepsdown)
# E.add_fitness_criteria("ratio", sumratio)
#
# # Register some agents
# E.add_agent("swapper", swapper, k=1)
#
# # Seed the population with an initial random solution
# N = 30
# L = [rnd.randrange(1, 99) for _ in range(N)]
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
