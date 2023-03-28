"""
JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments
March 27, 2023
"""

import random as rnd
import copy
from functools import reduce
import time
import pickle
import pandas as pd


class Evo:

    def __init__(self):
        # using in a dictionary, so two solution-evaluations (key) that map to the same set of objective scores are
        # counted as duplicates
        # ((obj1, eval1), (obj2, eval2), ...) / solution-evaluation (key) ==> solution (value)
        self.pop = {}

        # name of fitness function (key) ==> objective function (value)
        self.fitness = {}

        # the agents don't necessarily take in only one solution as input
        # name of the agent (key) ==> (agent operator, # of input solutions) (value)
        self.agents = {}

        # dataframe for storing results
        self.df = pd.DataFrame(columns=['groupname', 'overallocation', 'conflicts', 'undersupport',
                                        'unwilling', 'unpreferred'])
    def size(self):
        """ The size of the solution population (helper function) """
        return len(self.pop)

    def add_fitness_criteria(self, name, f):
        # storing a fitness function by its name in our framework
        """ Registering an objective with the Evo framework
        name - The name of the objective (string)
        f - The objective function: f(solution)--> a number
        self.fitness[name] = f
        """
        self.fitness[name] = (f)

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
        eval = tuple([(name, f(sol)) for name, f in self.fitness.items()])

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

    # ADD A 10 MINUTE TIMER TO THIS FUNCTION
    def evolve(self, n=1, dom=100, status=100, sync=1000, time_limit=600):
        """ To run n random agents against the population
        Args:
            n (int) - # of agent invocations
            dom (int) - # of iterations between discarding the dominated solutions
            status (int) - # of iterations between the last shown solution and the most recently shown one
            sync - # iterations between saving population to disk
            time_limit (int) - # of seconds the optimizer runs for

        Citation for time limit functionality:
        https://stackoverflow.com/questions/2831775/running-a-python-script-for-a-user-specified-amount-of-time
        """
        # dom determines how frequently we throw out the bad solutions (default is every 100 solutions,
        # but this value may not be the best)

        # retrieve the time this function started running
        start_time = time.time()

        # run the evolve function for the user-specified amount of seconds
        agent_names = list(self.agents.keys())
        for i in range(n):
            if (time.time() - start_time) > time_limit:
                break
            pick = rnd.choice(agent_names)  # pick an agent to run
            self.run_agent(pick)
            if i % dom == 0:
                # remove the dominated solutions every 100 times by default
                self.remove_dominated()

            if i % status == 0:  # print the population
                self.remove_dominated()
                # print("Iteration: ", i)
                # print("Population Size: ", self.size())
                print(self)

            if i % sync == 0:
                try:
                    with open('solutions.dat', 'rb') as file:

                        # load saved population into a dictionary object
                        loaded = pickle.load(file)

                        # merge loaded solutions into my population
                        for eval, sol in loaded.items():
                            self.pop[eval] = sol
                except Exception as e:
                    print(e)

            # Clean up population
            self.remove_dominated()

            # resave the non-dominated solutions back to the file
            with open('solutions.dat', 'wb') as file:
                pickle.dump(self.pop, file)

    @staticmethod
    def _dominates(p, q):
        pscores = [score for _, score in p]
        qscores = [score for _, score in q]
        score_diffs = list(map(lambda x, y: y - x, pscores, qscores))
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)
        return min_diff >= 0.0 and max_diff > 0.0

    @staticmethod
    # not a public method to be used outside the framework
    # shared by every instance of the class but hidden by the user
    def _reduce_nds(S, p):
        return S - {q for q in S if Evo._dominates(p, q)}

    def remove_dominated(self):
        nds = reduce(Evo._reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k: self.pop[k] for k in nds}

    def best_pop(self):
        for eval, sol in self.pop.items():
            sum(eval.values())

    def __str__(self):
        """ Output the solutions in the population """
        for eval, sol in self.pop.items():

            rslt = dict(eval)

            # groupname column across all rows of the dataframe
            name_dict = {'groupname': 'CJJCM'}

            # combine the two dictionaries together
            combined_dict = {**name_dict, **rslt}

            # dictionary of each of the columns and its values
            rslt_df = pd.DataFrame([combined_dict])

            # put the two dataframes together
            self.df = pd.concat([self.df, rslt_df])

            # save solutions (dataframe) to a csv file
            self.df.to_csv('CJJCM_sol.csv', index=False)

        return self.df.to_string(index=False)
