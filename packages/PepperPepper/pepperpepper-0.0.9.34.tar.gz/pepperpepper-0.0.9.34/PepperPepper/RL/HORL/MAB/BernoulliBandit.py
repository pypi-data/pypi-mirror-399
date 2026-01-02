# Multi-armed Bandit (MAB) conforming to the Bernoulli distribution.
import numpy as np
import matplotlib.pyplot as plt

class BernoulliBandit:
    def __init__(self, K):
        """
        Initialize the Bernoulli Bandit with given success probabilities for each arm.

        :param K: Number of arms.
        """
        self.probs = np.random.uniform(size=K) # Success probabilities for each arm
        self.best_idx = np.argmax(self.probs) # Index of the best arm
        self.best_prob = self.probs[self.best_idx] # Probability of the best arm
        self.K = K

    
    def step(self, k):
        """
        Simulate pulling arm k.

        :param k: Index of the arm to pull.
        :return: Reward (1 for success, 0 for failure).
        """
        if np.random.rand() < self.probs[k]:
            return 1
        else:
            return 0
        



if __name__ == "__main__":
    np.random.seed(1)
    K = 10
    bandit_10_arm = BernoulliBandit(K)
    print("Arm probabilities:", bandit_10_arm.probs)
    print("Best arm index:", bandit_10_arm.best_idx)
    print("Best arm probability:", bandit_10_arm.best_prob)
    
