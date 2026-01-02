# epsilonGreedy Algorithm for Multi-Armed Bandit Problems
import numpy as np
from PepperPepper.RL.HORL.MAB.Solver import Solver
class EpsilonGreedy(Solver):
    """
    Epsilon-Greedy algorithm for Multi-Armed Bandit problems.
    """
    def __init__(self, bandit, epsilon=0.01, init_prob=1.0):
        super().__init__(bandit)
        self.epsilon = epsilon

        # Initialize estimated values for each arm
        self.estimates = np.array([init_prob] * bandit.K)

    def run_one_step(self):
        if np.random.rand() < self.epsilon:
            k = np.random.randint(0, self.bandit.K)  # Explore: random arm
        else:
            k = np.argmax(self.estimates)  # Exploit: best estimated arm
        reward = self.bandit.step(k)
        self.estimates[k] += 1. / (self.counts[k] + 1) * (reward - self.estimates[k])
        return k

