import matplotlib.pyplot as plt

def plot_results(solvers, solver_names):
    """
    Plot the cumulative regret of multiple solvers.

    :param solvers: List of solver instances.
    :param solver_names: List of names corresponding to each solver.
    """
    for idx, solver in enumerate(solvers):
        time_list = range(len(solver.regrets))
        plt.plot(time_list, solver.regrets, label=solver_names[idx])
    plt.xlabel("Time Steps")
    plt.ylabel("Cumulative Regret")
    plt.title("%d-armed bandit" % solvers[0].bandit.K)
    plt.legend()
    plt.show()





    
