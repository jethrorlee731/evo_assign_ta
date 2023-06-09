"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments (evo.py)
March 28, 2023

evo.py - core framework for evolutionary programming on a 2d array of ta and lab assignments
"""
import random as rnd
import copy
from functools import reduce
import pickle
import time
import os


class Evo:
    """
    Core framework class for evolutionary programming on a 2D array of TA and lab assignments
    Attributes:
        pop (dict): maps evaluation scores to solutions; solution-evaluation (key) ==> solution (value)
        fitness (dict): name of fitness function (key) ==> objective function (value)
        agents(dict): name of the agent (key) ==> (agent operator, # of input solutions) (value)
    """

    def __init__(self):
        self.pop = {}
        self.fitness = {}
        self.agents = {}

    def size(self):
        """ The size of the solution population (helper function)
        Args:
            None
        Returns:
            len(self.pop) (int) - the length of a solution population
        """
        return len(self.pop)

    def add_fitness_criteria(self, name, f, **kwargs):
        """ Registering a fitness function by its name with the Evo framework
        Args:
            name (str)- The name of the objective
            f (func)- The objective function: f(solution)--> a number
            **kwargs - The inputs for the objective function
        Returns:
            None, just registers the fitness function
        """
        self.fitness[name] = (f, kwargs)

    def add_agent(self, name, op, k=1):
        """ Registering an agent with the Evo framework
        name (str)- The name of the agent
        op (str)- The operator: the function carried out by the agent / op(*solutions)--> new solution
        k (int) - the number of input solutions (usually 1)
        """
        self.agents[name] = (op, k)

    def get_random_solutions(self, k=1):
        """ Picking k random solutions from the population as a list of solutions
        We are returning the DEEP copies of these solutions as a list
        Args:
            k (int) - the number of random solutions that gets chosen randomly
        Returns:
            random_sol (list): an empty list or a list of k random solutions
        """
        # this scenario should not happen because the population is always initialized with one random solution
        if self.size() == 0:
            return []
        else:
            # get the solutions
            popvals = tuple(self.pop.values())
            # we are using deep copies because we don't want to change the original solutions (similar to reproduction)
            random_sol = [copy.deepcopy(rnd.choice(popvals)) for _ in range(k)]

        return random_sol

    def add_solution(self, sol):
        """ Add a new solution to the population
        Args:
            sol (numpy array) - a solution that gets added to the population
        Returns:
            None, just registers the solution within the framework in self.pop
        """
        # map the name of the function and the application of that function with optional parameters to a number,
        # returning a value each time
        eval = tuple([(name, (f(sol, **kwargs))) for name, (f, kwargs) in self.fitness.items()])

        # adding the new solution with its associated evaluation to the dictionary
        self.pop[eval] = sol

    def run_agent(self, name):
        """ Invoke an agent against the current population
        Args:
             name (str) - the name of the agent that runs against the current population
        Returns:
            None, just invokes the agent
        """
        # fetch the operator and the number of solutions that the agent needs to run
        op, k = self.agents[name]

        # retrieves k random solutions
        picks = self.get_random_solutions(k)

        # operate on the picked random solutions
        new_solution = op(picks)

        # add the new solution that results after the operation to the framework
        self.add_solution(new_solution)

    def evolve(self, n=1, dom=100, status=100, sync=1000, time_limit=600):
        """ To run n random agents against the population
        Args:
            n (int) - # of agent invocations
            dom (int) - # of iterations between discarding the dominated solutions
            status (int) - # of iterations between the last printed solution and the most recently shown one
            sync (int) - # iterations between saving population to disk
            time_limit (int) - # of seconds the optimizer runs for
        Returns:
            None, just runs the agents against the population

        Citation for time limit functionality:
        https://stackoverflow.com/questions/2831775/running-a-python-script-for-a-user-specified-amount-of-time
        """
        if os.path.exists('solutions.dat'):
            # remove solutions.dat file if it already exists
            os.remove('solutions.dat')

        # retrieve the time this function started running
        start_time = time.time()

        # get the agents that will run
        agent_names = list(self.agents.keys())

        for i in range(n):
            # stop the evolution process after the specified time limit (10 minutes by default)
            if (time.time() - start_time) > time_limit:
                break
            pick = rnd.choice(agent_names)  # pick an agent to run
            self.run_agent(pick)
            if i % dom == 0:
                # remove the dominated solutions every 100 times by default
                self.remove_dominated()

            if i % status == 0:  # print the population
                self.remove_dominated()
                print("Iteration: ", i)
                print("Population Size: ", self.size())
                print(self)

            if i % sync == 0:
                try:
                    with open('solutions.dat', 'rb') as file:

                        # load saved population into a dictionary object
                        loaded = pickle.load(file)

                        # merge loaded solutions into the population
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
        """
        Determines whether one solution is better than the other
        Args:
            p (numpy array): one solution that gets compared
            q (numpy array): the other solution that gets compared
        Returns:
            a boolean value indicating whether p dominates q
        """
        # get the evaluation scores for one solution
        pscores = [score for _, score in p]

        # get the evaluation scores for the other solution
        qscores = [score for _, score in q]

        # calculate the differences in the scores between the two solutions
        score_diffs = list(map(lambda x, y: y - x, pscores, qscores))

        # calculate the minimum and maximum differences
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)

        # p dominates q if the minimum difference is at least 0 and the maximum difference is positive
        return min_diff >= 0.0 and max_diff > 0.0

    @staticmethod
    def _reduce_nds(S, p):
        """
        Reduces the solutions dominated by p
        Args:
             S (set) - set of solutions
             p (numpy array) - a solution that may dominate another
        Returns:
            a set of non-dominated solutions
        """
        return S - {q for q in S if Evo._dominates(p, q)}

    def remove_dominated(self):
        """
        Cleans up the population by discarding dominated solutions
        Args:
            None
        Returns:
            None, just registers the non-dominated solutions in the population
        """
        nds = reduce(Evo._reduce_nds, self.pop.keys(), self.pop.keys())

        # update the internal pop with only non-dominated solutions
        self.pop = {k: self.pop[k] for k in nds}

    def __str__(self):
        """ Output the solutions in the population and save them to a CSV file
        Args:
            None
        Returns:
            rslt(str): contains the 5 objectives mapped to respective scores as well as the numpy array solution
        """
        # initialize empty string
        rslt = ''
        for eval, sol in self.pop.items():
            # result string: all 5 objectives mapped to evaluation scores and the numpy array solution
            rslt += str(dict(eval)) + ":\t" + str(sol) + "\n"

        return rslt
