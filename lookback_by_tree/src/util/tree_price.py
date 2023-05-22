import numpy as np
from math import exp, sqrt, pow

class TreePrice: # use two dimension array to store the tree

    def __init__(self, St, r, q, sigma, T, t, n):
        self.St = St
        self.r = r
        self.q = q
        self.sigma = sigma
        self.T = T
        self.t = t
        self.n = n

        self.delta_T = (self.T -self.t) / self.n
        self.u = exp(self.sigma * sqrt(self.delta_T))
        self.d = exp(- self.sigma * sqrt(self.delta_T))
        self.p = (exp((self.r - self.q) * self.delta_T) - self.d) / (self.u - self.d)

        # store the tree : 此 class 就是用於建立 tree，所以起始設定要先有 tree
        self.tree = np.zeros((self.n + 1, self.n + 1)) # two dimension array


    def get_tree_price(self):
        # 先把最後兩期的price算出來
        for time in range(self.n - 1, self.n + 1): # i = n-1, n
            for down_steps in range(0, time + 1): # j = 0 ~ i
                self.tree[down_steps, time] = self.St * pow(self.u, time - down_steps) * pow(self.d, down_steps)

        # 然後將最後兩期的price套用到前面期數
        for time in list(reversed(range(0, self.n - 1))): # i = n-2, n-3, n-4,..., 2, 1, 0
            for down_steps in range(0, time + 1):  # j = 0 ~ i
                self.tree[down_steps, time] = self.tree[down_steps + 1, time + 2]

        return self.tree




## for testing
if __name__ == "__main__":
    St = 100
    r = 0.05
    q = 0.02
    sigma = 0.5
    T = 0.5
    n = 4

    EuropeanPut = TreePrice(St, r, q, sigma, T, n)

    print(f"European Put value: {EuropeanPut.get_tree_price()}")


