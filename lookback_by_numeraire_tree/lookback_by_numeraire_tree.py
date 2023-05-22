import numpy as np
from math import exp, sqrt, pow

# hyperparameter
St = 50 # St_max must be the same as St.
r = 0.1
q = 0
sigma = 0.4
T = 0.25
t = 0
n = 100


class NumeraireTree:

    def __init__(self, St, r, q, sigma, T, t, n, E_A):
        self.St = St
        self.r = r
        self.q = q
        self.sigma = sigma
        self.T = T
        self.t = t
        self.n = n
        self.E_A = E_A

        self.delta_T = (self.T - self.t)/ self.n
        self.u = exp(self.sigma * sqrt(self.delta_T))
        self.d = exp(- self.sigma * sqrt(self.delta_T)) # d = 1/u

        self.mu = exp((self.r - self.q) * self.delta_T)
        self.p = (self.mu * self.u - 1) / (self.mu * (self.u - self.d))

        self.numeraire_tree = np.zeros((self.n + 1, self.n + 1))
        self.put_tree = np.zeros((self.n + 1, self.n + 1))

        self.create_numeraire_tree()


    def create_numeraire_tree(self):
        for time in range(self.n + 1):
            for down_steps in range(time + 1):
                power = time - down_steps
                self.numeraire_tree[down_steps, time] = pow(self.u, power)


    def backward_induction(self):
        # terminal node
        for down_steps in range(self.n + 1):
            self.put_tree[down_steps, self.n] = max(self.numeraire_tree[down_steps, self.n] - 1, 0)

        for time in list(reversed(range(0, self.n))):
            for down_steps in range(time + 1):
                if down_steps < time:
                    if self.E_A == "A":
                        exercise_value = max(self.numeraire_tree[down_steps, time] - 1, 0)
                        intrinsic_value = self.mu * exp(- self.r * self.delta_T) * \
                                                      ((1 - self.p) * self.put_tree[down_steps, time + 1] + self.p * self.put_tree[down_steps + 2, time + 1])
                        self.put_tree[down_steps, time] = max(exercise_value, intrinsic_value)
                    else:
                        self.put_tree[down_steps, time] = self.mu * exp(- self.r * self.delta_T) * \
                                                      ((1 - self.p) * self.put_tree[down_steps, time + 1] + self.p * self.put_tree[down_steps + 2, time + 1])
                # 要注意最下面那期的backward方法不同
                elif down_steps == time:
                    if self.E_A == "A":
                        exercise_value = max(self.numeraire_tree[down_steps, time] - 1, 0)
                        intrinsic_value = self.mu * exp(- self.r * self.delta_T) * \
                                                          ((1 - self.p) * self.put_tree[down_steps, time + 1] + self.p * self.put_tree[down_steps + 1, time + 1])
                        self.put_tree[down_steps, time] = max(exercise_value, intrinsic_value)
                    else:
                        self.put_tree[down_steps, time] = self.mu * exp(- self.r * self.delta_T) * \
                                                          ((1 - self.p) * self.put_tree[down_steps, time + 1] + self.p * self.put_tree[down_steps + 1, time + 1])

        return self.put_tree



European_tree = NumeraireTree(St, r, q, sigma, T, t, n, "E")
put_tree = European_tree.backward_induction()
put_value = St * put_tree[0, 0] # 最後記得將股價乘回來
print(f"European option value = {put_value:.6f}")

American_tree = NumeraireTree(St, r, q, sigma, T, t, n, "A")
put_tree = American_tree.backward_induction()
put_value = St * put_tree[0, 0] # 最後記得將股價乘回來
print(f"American option value = {put_value:.6f}")






