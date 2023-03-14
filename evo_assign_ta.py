"""
Jethro R. Lee
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments
March 14, 2023
"""

import random as rnd
import copy


class Evo:

    def __init__(self):
        # using in a dictionary, so two solution-evaluations (key) that map to the same set of objective scores are
        # counted as duplicates
        self.pop = {}  # ((obj1, eval1), (obj2, eval2), ...) / solution-evaluation (key) ==> solution (value)
        # ex. step-downs from sort would have the function name, "stepDown"
        self.fitness = {}  # name of fitness function (key) ==> objective function (value)
        # the agents don't necessarily take in only one solution as input
        self.agents = {}  # name of the agent (key) ==> (agent operator, # of input solutions) (value)

    def size(self):
        """ The size of the solution population (helper function) """
        return len(self.pop)

    def add_fitness_criteria(self, name, f):
        # storing a fitness function by its name in our framework
        """ Registering an objective with the Evo framework
        name - The name of the objective (string)
        f - The objective function: f(solution)--> a number """
        self.fitness[name] = f

    # k = number of solutions the agent operates on
    # the name is used for logging to track how long the agent is running and which ones are producing the best results
    # operator takes solutions in, doesn't modify the solutions themselves
    def add_agent(self, name, op, k=1):
        """ Registering an agent with the Evo framework
        name - The name of the agent
        op - The operator: the function carried out by the agent / op(*solutions)--> new solution
        k - the number of input solutions (usually 1) """
        self.agents[name] = (op, k)

    def get_random_solutions(self, k=1):
        """ Picking k random solutions from the population as a list of solutions

        We are returning the DEEP copies of these solutions as a list """
        # this scenario should not happen because the population is always initialized with one random solution
        if self.size() == 0:
            return []
        else:
            popvals = tuple(self.pop.values())
            # we are using copies because we don't want to change the original solutions (similar to reproduction)
            # otherwise, so many solutions would get altered at once, leading to just one solution
            return [copy.deepcopy(rnd.choice(popvals)) for _ in range(k)]

    # when the agent runs, we will produce a new solution that needs to be added to the population
    def add_solution(self, sol):
        """ Add a new solution to the population """
        # insert the name of the function and the application of that function to the inputted solution as a tuple
        # evaluating the function to every objective in the population

        # applying every registered function to a number, returning a value each time
        eval = [(name, f(sol)) for name, f in self.fitness.items()]

        # adding the new solution with its associated evaluation to the dictionary
        self.pop[eval] = sol

    def run_agent(self, name):
        """ Invoke an agent against the current population """
        # fetch the operator and the number of solutions that the agent needs to run
        op, k = self.agents[name]

        # retrieves k random solutions
        picks = self.get_random_solutions(k)

        new_solution = op(picks)
        self.add_solution(new_solution)

    def evolve(self, n=1, dom=100):
        """ To run n random agents against the population
        n = # of agent invocations
        dom = # of iterations between discarding the dominated solutions """
        # dom determines how frequently we throw out the bad solutions (default is every 100 solutions,
        # but this value may not be the best)
        agent_names = list(self.agents.keys())
        for i in range(n):
            pick = rnd.choice(agent_names)
            self.run_agent(pick)
            if i % dom == 0:
                self.remove_dominated()

        pass


def main():
    pass


if __name__ == '__main__':
    main()
