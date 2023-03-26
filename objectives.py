import numpy as np
import pandas as pd
from evo import Evo


# sections = 'sections.csv'
# ta = 'tas.csv'

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

# sections_df = pd.read_csv(sections)
# tas = pd.read_csv(ta)
arr = np.genfromtxt('test3.csv', delimiter=',', dtype=int)

def overallocation(assignments):
    sums = list(assignments.sum(axis=1))

    return int(sum([x - y for x,y in zip(sums, MAX_ASSIGNED_LIST) if x > y]))


def conflicts(assignments):
    ta_sections = np.where(assignments == 1, DAYTIME_LIST, assignments)
    time_conflicts = list(np.array([len(row[row != '0']) != len(set(row[row != '0'])) for row in ta_sections])).count(True)

    return time_conflicts

def undersupport(assignments):
    sums = list(assignments.sum(axis=0))

    return int(sum([y-x for x,y in zip(sums, MIN_TA_LIST) if y > x]))

def unwilling(assignments):
    ta_sections = np.where(assignments == 1, PREFERENCE_ARRAY, 0)
    count_u = np.count_nonzero(ta_sections == 'U', axis=1)

    return sum(list(count_u))

def unpreferred(assignments):
    ta_sections = np.where(assignments == 1, PREFERENCE_ARRAY, 0)
    count_W = np.count_nonzero(ta_sections == 'W', axis=1)

    return sum(list(count_W))

test2 = overallocation(arr)
ok = undersupport(arr)
test3 = conflicts(arr)
test4 = unwilling(arr)
test5 = unpreferred(arr)
print(test5)

