from evo import Evo
import assign_ta as TA
import agents as ag
import numpy as np
import random as rnd


def main():
    # initialize the evolutionary programming framework
    E = Evo()

    # Register some objectives
    E.add_fitness_criteria("overallocation", TA.overallocation)
    E.add_fitness_criteria("conflicts", TA.conflicts)
    E.add_fitness_criteria("undersupport", TA.undersupport)
    E.add_fitness_criteria("unwilling", TA.unwilling)
    E.add_fitness_criteria("unpreferred", TA.unpreferred)

    # Register some agents
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
    N = len(TA.SECTIONS) * len(TA.TAS)

    # Seed the population with 1000 random solutions
    # (numpy array of 17 columns by 43 rows as there are 17 sections and 43 tas)
    # 0 means the TA isn't assigned to that section and 1 means the TA is assigned to that section

    for i in range(101):
        rnd_sol = np.array([rnd.randint(0, 1) for _ in range(N)]).reshape(43, 17)

        # Register the random solution into the framework
        E.add_solution(rnd_sol)

    # Run the evolver
    E.evolve(1000000, 100, 10000)


if __name__ == '__main__':
    main()
