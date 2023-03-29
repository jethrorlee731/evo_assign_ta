"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (assign_ta.py)
March 28, 2023

assign_ta.py - a program that gets run to initiate the evolution process
"""
# import statements
from evo import Evo
import objectives as ob
import agents as ag
import numpy as np
import random as rnd
import pandas as pd


def main():
    # initialize the evolutionary programming framework
    E = Evo()

    # Register objectives
    E.add_fitness_criteria("overallocation", ob.overallocation)
    E.add_fitness_criteria("conflicts", ob.conflicts)
    E.add_fitness_criteria("undersupport", ob.undersupport)
    E.add_fitness_criteria("unwilling", ob.unwilling)
    E.add_fitness_criteria("unpreferred", ob.unpreferred)

    # Register agents
    E.add_agent("swap_assignment", ag.swap_assignment, k=1)
    E.add_agent("add_ta_preferred", ag.add_ta_preferred, k=1)
    E.add_agent("add_ta_undersupport", ag.add_ta_undersupport, k=1)
    E.add_agent("remove_unpreferred", ag.remove_unpreferred, k=1)
    E.add_agent("remove_unwilling", ag.remove_unwilling, k=1)
    E.add_agent("remove_time_conflict", ag.remove_time_conflict, k=1)
    E.add_agent("remove_ta_overallocated", ag.remove_ta_overallocated, k=1)
    E.add_agent("swap_assignment", ag.swap_assignment, k=1)
    E.add_agent("swap_labs", ag.swap_labs, k=1)
    E.add_agent("swap_tas", ag.swap_tas, k=1)
    E.add_agent("opposites", ag.opposites, k=1)

    # determine the size of the array to create
    N = len(ob.SECTIONS) * len(ob.TAS)

    # Seed the population with 100 random solutions
    # (a solution is a numpy array of 17 columns and 43 rows as there are 17 sections and 43 TAs)
    # 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section
    for i in range(101):
        rnd_sol = np.array([rnd.randint(0, 1) for _ in range(N)]).reshape(43, 17)

        # Register the random solution into the framework
        E.add_solution(rnd_sol)

    # Run the evolver
    E.evolve(1000000, 100, 10000)

    # print out the population in the console
    print(E.pop)

    # initialize empty dataframe
    df = pd.DataFrame(columns=['groupname', 'overallocation', 'conflicts', 'undersupport',
                               'unwilling', 'unpreferred'])

    for eval, sol in E.pop.items():
        # obtain an evaluation and store it as a dictionary
        rslt = dict(eval)

        # define the groupname column across all rows of the dataframe (defining the name of the solution)
        name_dict = {'groupname': 'CJJCM'}

        # combine the group name and evaluation dictionaries together
        combined_dict = {**name_dict, **rslt}

        # convert the dictionary containing the name of solution and its evaluation scores to a dictionary
        rslt_df = pd.DataFrame([combined_dict])

        # store the dataframe containing the name of a solution and its evaluation scores in the framework
        df = pd.concat([df, rslt_df])

        # save solutions (in the form of a dataframe) to a CSV file
        df.to_csv('CJJCM_sol.csv', index=False)


if __name__ == '__main__':
    main()
