"""
Colbe Chang, JC Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
HW4: An Evolutionary Approach to TA/Lab Assignments
March 27, 2023
"""

import random as rnd
import copy
from functools import reduce
import pickle
<<<<<<< HEAD
import time
=======
import pandas as pd
>>>>>>> 7229a0562ac133ab7e191b8e269a05b9fbf4e2e5


class Evo:
    """
    Core framework class for evolutionary programming on a 2D array of TA and lab assignments
    Attributes:
        pop (dict): maps evaluation scores to solutions; solution-evaluation (key) ==> solution (value)
        fitness (dict): name of fitness function (key) ==> objective function (value)
        agents(dict): name of the agent (key) ==> (agent operator, # of input solutions) (value)
    """

    def __init__(self):
<<<<<<< HEAD
        self.pop = {}
        self.fitness = {}
        self.agents = {}  #
=======
        # using in a dictionary, so two solution-evaluations (key) that map to the same set of objective scores are
        # counted as duplicates
        # ((obj1, eval1), (obj2, eval2), ...) / solution-evaluation (key) ==> solution (value)
        self.pop = {}

        # name of fitness function (key) ==> objective function (value)
        self.fitness = {}

        # the agents don't necessarily take in only one solution as input
        # name of the agent (key) ==> (agent operator, # of input solutions) (value)
        self.agents = {}
>>>>>>> 7229a0562ac133ab7e191b8e269a05b9fbf4e2e5

        # dataframe for storing results
        self.df = pd.DataFrame(columns=['groupname', 'overallocation', 'conflicts', 'undersupport',
                                        'unwilling', 'unpreferred'])
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
            an empty list or a list of k random solutions
        """
        # this scenario should not happen because the population is always initialized with one random solution
        if self.size() == 0:
            return []
        else:
            popvals = tuple(self.pop.values())
            # we are using deep copies because we don't want to change the original solutions (similar to reproduction)
            # otherwise, so many solutions would get altered at once, leading to just one solution
            return [copy.deepcopy(rnd.choice(popvals)) for _ in range(k)]

    def add_solution(self, sol):
        """ Add a new solution to the population
        Args:
            sol (numpy array) - a solution that gets added to the population
        Returns:
            None, just registers the solution within the framework in self.pop
        """
        # insert the name of the function, any optional parameters, and the application of that function to the
        # inputted solution as a tuple

        # evaluating the function to every objective in the population

        # applying every registered function to a number, returning a value each time
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

        new_solution = op(picks)
        self.add_solution(new_solution)

    def evolve(self, n=1, dom=100, status=100, sync =1000, time_limit=600):
        """ To run n random agents against the population
        Args:
            n (int) - # of agent invocations
            dom (int) - # of iterations between discarding the dominated solutions
            status (int) - # of iterations between the last shown solution and the most recently shown one
            sync (int) - # of iterations between printing current population to the screen
            time_limit (int) - # of seconds the optimizer runs for
        Returns:
            None, just runs the agents against the population

        Citation for time limit functionality:
        https://stackoverflow.com/questions/2831775/running-a-python-script-for-a-user-specified-amount-of-time
        """
        # retrieve the time this function started running
        start_time = time.time()

        # run the evolve function for the user-specified amount of seconds
<<<<<<< HEAD
        while (time.time() - start_time) < time_limit:
            agent_names = list(self.agents.keys())
            for i in range(n):
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

                # Clean up population
                self.remove_dominated()

                # resave the non-dominated solutions back to the file
                with open('solutions.dat', 'wb') as file:
                    pickle.dump(self.pop, file)

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
=======
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
>>>>>>> 7229a0562ac133ab7e191b8e269a05b9fbf4e2e5

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
        pscores = [score for _, score in p]
        qscores = [score for _, score in q]
        score_diffs = list(map(lambda x, y: y - x, pscores, qscores))
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)
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
        self.pop = {k: self.pop[k] for k in nds}

    def __str__(self):
<<<<<<< HEAD
        """ Output the solutions in the population
        Args:
            None
        Returns:
            rslt (str) - the remaining solutions registered in the population
        """
        rslt = ""
        for eval, sol in self.pop.items():
            rslt += str(dict(eval)) + ":\t" + str(sol) + "\n"
        return rslt
=======
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
>>>>>>> 7229a0562ac133ab7e191b8e269a05b9fbf4e2e5
