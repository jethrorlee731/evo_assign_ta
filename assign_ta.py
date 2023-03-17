from evo import Evo
import random as rnd


def sumstepsdown(L):
    """ Objective: Count total magnitude of steps down (larger to smaller value) """
    return sum([x - y for x, y in zip(L, L[1:]) if y < x])


def sumratio(L):
    """ Ratio of sum of first-half values to 2nd half values"""
    sz = len(L)
    return round(sum(L[:sz//2]) / sum(L[sz//2+1:]), 5)


# Creating agents (all agents take in solutions)
def swapper(solutions):
    """ Swap two random values """
    L = solutions[0]
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    return L


def main():
    E = Evo()

    # Register some objectives
    E.add_fitness_criteria("ssd", sumstepsdown)
    E.add_fitness_criteria("ratio", sumratio)

    # Register some agents
    E.add_agent("swapper", swapper, k=1)

    # Seed the population with an initial random solution
    N = 30
    L = [rnd.randrange(1, 99) for _ in range(N)]
    E.add_solution(L)
    print(E)

    # Run the evolver
    E.evolve(1000000, 100, 10000)

    # Print final results
    print(E)


if __name__ == '__main__':
    main()
