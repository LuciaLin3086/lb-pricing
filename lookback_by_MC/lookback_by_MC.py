import numpy as np
import pandas as pd
from math import exp, log, sqrt

# input variable
# St = 50
# St_max = 50
# r = 0.1
# q = 0
# sigma = 0.4
# T = 0.25
# t = 0
# n = 100

# hyperparameter
N = 10000
rep = 20

St = 100
St_max = 110
r = 0.05
q = 0.02
sigma = 0.65
T = 0.8
t = 0
n = 100


class PriceSimulator:
    def __init__(self, N, n, St, St_max , r, q, sigma, T, t):
        self.N = N
        self.n = n
        self.St = St
        self.St_max  = St_max
        self.r = r
        self.q = q
        self.sigma = sigma
        self.T = T
        self.t = t

        self.delta_T = (self.T - self.t) / self.n

    def price_simulate(self):
        std_normal_sample = pd.DataFrame(np.random.randn(int(self.n), int(self.N))) # 一個column代表一個path
        normal_sample = std_normal_sample * self.sigma * sqrt(self.delta_T) + \
               (self.r - self.q - self.sigma ** 2 / 2) * self.delta_T
        path_price = normal_sample.cumsum(axis = 0) # 沿著row走，代表分別對每個column運算
        lnSt = path_price + log(self.St)
        St = np.exp(lnSt) # St為 n * N 的dataframe，每個column為第1期到第n期的模擬股價路徑
        # 將St_max新增為第一列
        St_max = pd.DataFrame([[self.St_max]* self.N] )
        St = pd.concat([St_max, St], axis=0)

        return St


class Payoff:
    def __init__(self, price):
        self.price = price # dataframe

    def get_payoff(self):
        Smax = self.price.max(axis = 0) # 找出每個path中的最大股價，Smax為一個有N個元素的row
        # 用np.where來算(Smax - ST)跟0比較大小
        # If (Smax - self.price.iloc[-1, :]) > 0, then return (Smax - self.price.iloc[-1, :])
        # If NOT, then return 0.
        # .iloc指定位置，-1代表最後一個
        payoff = np.where((Smax - self.price.iloc[-1, :]) > 0, (Smax - self.price.iloc[-1, :]), 0)

        return payoff


# repeat for 20 times
values_ls = []
for i in range(rep):
    price_simulate = PriceSimulator(N, n, St, St_max, r, q, sigma, T, t)
    price = price_simulate.price_simulate()

    lookback_payoff = Payoff(price)
    payoff = lookback_payoff.get_payoff()

    value = exp(-r * (T - t)) * payoff.mean()
    values_ls.append(value)

values_arr = np.array(values_ls)
CI1 = values_arr.mean() - 2 * values_arr.std()
CI2 = values_arr.mean() + 2 * values_arr.std()


print(f"95% CI: [{CI1:.6f}, {CI2:.6f}]")
print(f"European option value = {values_arr.mean():.6f}")


