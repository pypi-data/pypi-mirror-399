# Solver for the Multi-Armed Bandit problem
import numpy as np




class Solver:
    def __init__(self, bandit):
        self.bandit = bandit
        self.counts = np.zeros(self.bandit.K)  # Number of times each arm was pulled
        self.regret = 0. # Current cumulative regret
        self.actions = []  # History of actions taken
        self.regrets = []  # History of regrets


    def update_regret(self, k):
        """
        Update the cumulative regret after pulling arm k.

        :param k: Index of the arm that was pulled.
        """
        self.regret += self.bandit.best_prob - self.bandit.probs[k]
        self.regrets.append(self.regret)

    def run_one_step(self):
        """
        Run one step of the solver. This method should be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def run(self, n_steps):
        """
        Run the solver for a specified number of steps.

        :param n_steps: Number of steps to run the solver.
        """
        for _ in range(n_steps):
            k = self.run_one_step()
            self.counts[k] += 1
            self.actions.append(k)
            self.update_regret(k)
    




if __name__ == "__main__":
    from PepperPepper.RL.HORL.MAB.BernoulliBandit import BernoulliBandit
    np.random.seed(1)
    K = 10
    bandit = BernoulliBandit(K)
    solver = Solver(bandit)

    print("Initialized Solver for Bernoulli Bandit with {} arms.".format(K))



    