#### 重構包裝成class

import numpy as np
from math import exp, sqrt, pow

# input variable
St = 50
St_max = 50
r = 0.1
q = 0
sigma = 0.4
T = 0.25
t = 0
n = 100
E_A = "A"

class PriceTree: # use two dimension array to store the tree

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
        self.price_tree = np.zeros((self.n + 1, self.n + 1)) # two dimension array


    def get_price_tree(self):
        # 先把最後兩期的price算出來
        for time in range(self.n - 1, self.n + 1): # i = n-1, n
            for down_steps in range(0, time + 1): # j = 0 ~ i
                self.price_tree[down_steps, time] = self.St * pow(self.u, time - down_steps) * pow(self.d, down_steps)

        # 然後將最後兩期的price套用到前面期數
        for time in list(reversed(range(0, self.n - 1))): # i = n-2, n-3, n-4,..., 2, 1, 0
            for down_steps in range(0, time + 1):  # j = 0 ~ i
                self.price_tree[down_steps, time] = self.price_tree[down_steps + 1, time + 2]

        return self.price_tree

# 用class儲存資料，讓tree上的price丟入之後，可以指定出相同位置所存放的Smax list、put value list
class StoreNodeList():

    def __init__(self, price):
        self.price = price

        self.Smax_list = []
        self.put_list = []

    def forward_tracking(self, Smax_from_parents):
        # 直接更動S_max
        for i in Smax_from_parents:
            if i >= self.price:
                self.Smax_list.append(i)
            else:
                self.Smax_list.append(self.price)

        self.Smax_list = list(set(self.Smax_list)) # set：只會留不重複的元素

    def get_payoff(self):
        # payoff for every Smax of each terminal node
        for i in self.Smax_list:
            self.put_list.append(max(i - self.price, 0))



class ForwardTracking(PriceTree, StoreNodeList): # Inheritance

    def __init__(self, price_tree, St, St_max, r, q, sigma, T, t, n):
        PriceTree.__init__(self, St, r, q, sigma, T, t, n)
        StoreNodeList.__init__(self, price_tree)


        self.St_max = St_max

        self.get_Smax_list()
        self.get_put_list()

    def get_Smax_list(self):
        PriceTree.__init__(self, St, r, q, sigma, T, t, n).p
        node_list_tree = np.zeros((self.n + 1, self.n + 1)).tolist()

        # 要先將今天的Smax放入Smax_tree
        first_node = StoreNodeList.__init__(self, price_tree[0, 0])  # 指定位置:first_node的位置等於tree_price[0, 0]的位置
        # 指定好位置後，將這個位置所存放的S_max中放入St_max
        super().__init__(price_tree[0, 0]).Smax_list = [self.St_max]  # S_max是存放list，所以加[]
        node_list_tree[0][0] = first_node  # Smax_tree中存放node位置

        # forward-tracking找到每個node的Smax
        for time in range(1, self.n + 1):
            for down_steps in range(time + 1):
                node = super().__init__(price_tree[down_steps, time])
                node_list_tree[down_steps][time] = node
                # node_list_tree[down_steps][time] = super.__init__(price_tree[down_steps, time]) 此寫法同上兩行

                if down_steps == 0:  # 最上面只有一個parent
                    node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)

                elif down_steps == time:  # 最下面只有一個parent
                    node_list_tree[down_steps][time].forward_tracking(
                        node_list_tree[down_steps - 1][time - 1].Smax_list)

                else:  # 中間都有兩個父母
                    node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)
                    node_list_tree[down_steps][time].forward_tracking(
                        node_list_tree[down_steps - 1][time - 1].Smax_list)

        return node_list_tree


    def get_put_list(self):
        node_list_tree = self.get_Smax_list()

        # payoff for every Smax of each terminal node
        for down_steps in range(self.n + 1):
            node_list_tree[down_steps][self.n].get_payoff()

        # backward induction for put value
        for time in list(reversed(range(0, self.n))):
            for down_steps in range(0, time + 1):
                node = node_list_tree[down_steps][time]
                up_node = node_list_tree[down_steps][time + 1]
                down_node = node_list_tree[down_steps + 1][time + 1]

                for val in node.Smax_list:
                    for up_val in up_node.Smax_list:
                        if val in up_node.Smax_list:
                            if val == up_val:
                                up_put = up_node.put_list[up_node.Smax_list.index(up_val)]
                                break
                        else:
                            up_put = up_node.put_list[up_node.Smax_list.index(up_node.price)]

                    for down_val in down_node.Smax_list:
                        if val == down_val:
                            down_put = down_node.put_list[down_node.Smax_list.index(down_val)]
                            break

                    if E_A == "A":
                        exercise_value = val - node.price
                        intrinsic_value = exp(-r * self.delta_T) * (self.p * up_put + (1 - self.p) * down_put)
                        put = max(exercise_value, intrinsic_value)
                    else:
                        put = exp(-r * self.delta_T) * (self.p * up_put + (1 - self.p) * down_put)

                    node.put_list.append(put)

        return node_list_tree

    # def get_Smax_list(self, price_tree, St_max, n):
    #     node_list_tree = np.zeros((n + 1, n + 1)).tolist()
    #
    #     # 要先將今天的Smax放入Smax_tree
    #     first_node = super.__init__(price_tree[0, 0])  # 指定位置:first_node的位置等於tree_price[0, 0]的位置
    #     # 指定好位置後，將這個位置所存放的S_max中放入St_max
    #     first_node.Smax_list = [St_max]  # S_max是存放list，所以加[]
    #     node_list_tree[0][0] = first_node  # Smax_tree中存放node位置
    #
    #     # forward-tracking找到每個node的Smax
    #     for time in range(1, n + 1):
    #         for down_steps in range(time + 1):
    #             node = super.__init__(price_tree[down_steps, time])
    #             node_list_tree[down_steps][time] = node
    #             # node_list_tree[down_steps][time] = super.__init__(price_tree[down_steps, time]) 此寫法同上兩行
    #
    #             if down_steps == 0:  # 最上面只有一個parent
    #                 node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)
    #
    #             elif down_steps == time:  # 最下面只有一個parent
    #                 node_list_tree[down_steps][time].forward_tracking(
    #                     node_list_tree[down_steps - 1][time - 1].Smax_list)
    #
    #             else:  # 中間都有兩個父母
    #                 node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)
    #                 node_list_tree[down_steps][time].forward_tracking(
    #                     node_list_tree[down_steps - 1][time - 1].Smax_list)
    #
    #     return node_list_tree

    # def get_put_list(self):
    #     node_list_tree = self.get_Smax_list()
    #
    #     # for time in range(n + 1):
    #     #     for down_steps in range(time + 1):
    #     #         node = super.__init__(price_tree[down_steps, time])
    #     #         node_list_tree[down_steps][time] = node
    #
    #     # payoff for every Smax of each terminal node
    #     for down_steps in range(n + 1):
    #         node_list_tree[down_steps][n].get_payoff()
    #
    #     # backward induction for put value
    #     for time in list(reversed(range(0, n))):
    #         for down_steps in range(0, time + 1):
    #             node = node_list_tree[down_steps][time]
    #             up_node = node_list_tree[down_steps][time + 1]
    #             down_node = node_list_tree[down_steps + 1][time + 1]
    #
    #             for val in node.Smax_list:
    #                 for up_val in up_node.Smax_list:
    #                     if val in up_node.Smax_list:
    #                         if val == up_val:
    #                             up_put = up_node.put_list[up_node.Smax_list.index(up_val)]
    #                             break
    #                     else:
    #                         up_put = up_node.put_list[up_node.Smax_list.index(up_node.price)]
    #
    #                 for down_val in down_node.Smax_list:
    #                     if val == down_val:
    #                         down_put = down_node.put_list[down_node.Smax_list.index(down_val)]
    #                         break
    #
    #                 p = tree.p
    #                 delta_T = tree.delta_T
    #                 if E_A == "A":
    #                     exercise_value = val - node.price
    #                     intrinsic_value = exp(-r * delta_T) * (p * up_put + (1 - p) * down_put)
    #                     put = max(exercise_value, intrinsic_value)
    #                 else:
    #                     put = exp(-r * delta_T) * (p * up_put + (1 - p) * down_put)
    #
    #                 node.put_list.append(put)
    #
    #     return node_list_tree






tree = PriceTree(St, r, q, sigma, T, t, n)
price_tree = tree.get_price_tree()

forward_tracking = ForwardTracking(price_tree, St, St_max, r, q, sigma, T, t, n)
node_list_tree = forward_tracking.get_put_list()

print(f"option value = {node_list_tree[0][0].put_list[0]:.6f}")




