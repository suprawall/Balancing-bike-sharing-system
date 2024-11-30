import numpy as np

class DBP_UCB:
    def __init__(self, prices, budget, num_users):
        self.prices = prices
        self.budget = budget
        self.num_users = num_users
        self.estimate = {p: 0 for p in prices}  # F(p)
        self.counts = {p: 0 for p in prices}  # N(p)
    
    def compute_ucb(self, n):
        ucb = {}
        for p in self.prices:
            if self.counts[p] == 0:
                ucb[p] = np.inf  # Exploration initiale
            else:
                ucb[p] = self.estimate[p] + np.sqrt(2 * np.log(n) / self.counts[p])
        return ucb
    
    def choose_price(self, n):
        ucb = self.compute_ucb(n)
        return max(ucb, key=ucb.get)

    def update(self, price, accepted):
        self.counts[price] += 1
        self.estimate[price] += (accepted - self.estimate[price]) / self.counts[price]
