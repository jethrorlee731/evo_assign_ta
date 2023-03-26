import numpy as np
import pandas as pd
from evo import Evo


sections = 'sections.csv'
ta = 'tas.csv'

sections_df = pd.read_csv(sections)
tas = pd.read_csv(ta)
arr = np.genfromtxt('test3.csv', delimiter=',', dtype=int)


def overallocation(assignments):
    max_assigned = list(tas.max_assigned)
    sums = list(assignments.sum(axis=1))

    return int(sum([x - y for x,y in zip(sums, max_assigned) if x > y]))


def conflicts(assignments):
    section_times = list(sections_df.daytime)
    ta_sections = np.where(assignments == 1, section_times, assignments)
    time_conflicts = list(np.array([len(row[row != '0']) != len(set(row[row != '0'])) for row in ta_sections])).count(True)

    return time_conflicts

def undersupport(assignments):
    min_ta = sections_df.min_ta
    sums = list(assignments.sum(axis=0))

    return int(sum([y-x for x,y in zip(sums, min_ta) if y > x]))

def unwilling(assignments):
    preferences = tas.iloc[:, -17:].values
    ta_sections = np.where(assignments == 1, preferences, 0)
    count_u = np.count_nonzero(ta_sections == 'U', axis=1)

    return sum(list(count_u))

def unpreferred(assignments):
    preferences = tas.iloc[:, -17:].values
    ta_sections = np.where(assignments == 1, preferences, 0)
    count_W = np.count_nonzero(ta_sections == 'W', axis=1)

    return sum(list(count_W))

test2 = overallocation(arr)
ok = undersupport(arr)
test3 = conflicts(arr)
test4 = unwilling(arr)
test5 = unpreferred(arr)
print(test5)

