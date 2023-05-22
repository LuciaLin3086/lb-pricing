import numpy as np
from math import exp
from tree_price import TreePrice


# input variable
# St = 50
# St_max = 50
# r = 0.1
# q = 0
# sigma = 0.4
# T = 0.25
# t = 0
# n = 100
# E_A = "A"

St = 100
St_max = 110
r = 0.05
q = 0.02
sigma = 0.65
T = 0.8
t = 0.1
n = 100
# E_A = "E"

# 用class儲存資料，讓tree上的price丟入之後，可以指定出相同位置所存放的Smax list、put value list
class StoreNodeList:

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



tree = TreePrice(St, r, q, sigma, T, t, n)
tree_price = tree.get_tree_price()

for E_A in ["E", "A"]:
    # 因為numpy.array中只能存同樣的數據形態，而list可以存不同的數據形態，所以用list
    node_list_tree = np.zeros((n + 1, n + 1)).tolist() # 有(n+1)個list，每個list有(n+1)個元素

    # 要先將今天的Smax放入Smax_tree
    first_node = StoreNodeList(tree_price[0, 0]) # 指定位置:first_node的位置等於tree_price[0, 0]的位置
    # 指定好位置後，將這個位置所存放的S_max中放入St_max
    first_node.Smax_list = [St_max] # S_max是存放list，所以加[]
    node_list_tree[0][0] = first_node # Smax_tree中存放node位置

    # forward-tracking找到每個node的Smax
    for time in range(1, n + 1):
        for down_steps in range(time + 1):
            node = StoreNodeList(tree_price[down_steps, time])
            node_list_tree[down_steps][time] = node
            #  node_list_tree[down_steps][time] = StoreNodeList(tree_price[down_steps, time]) 此寫法同上兩行

            if down_steps == 0: # 最上面只有一個parent
                node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)

            elif down_steps == time: # 最下面只有一個parent
                node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps - 1][time - 1].Smax_list)

            else: # 中間都有兩個父母
                node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps][time - 1].Smax_list)
                node_list_tree[down_steps][time].forward_tracking(node_list_tree[down_steps - 1][time - 1].Smax_list)


    # payoff for every Smax of each terminal node
    for down_steps in range(n + 1):
        node_list_tree[down_steps][n].get_payoff()

    # backward induction for put value

    for time in list(reversed(range(0, n))):
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

                p = tree.p
                delta_T = tree.delta_T
                if E_A == "A":
                    exercise_value = val - node.price
                    intrinsic_value = exp(-r * delta_T) * (p * up_put + (1 - p) * down_put)
                    put = max(exercise_value, intrinsic_value)
                else:
                    put = exp(-r * delta_T) * (p * up_put + (1 - p) * down_put)

                node.put_list.append(put)

    if E_A == "A":
        print(f"American option value = {node_list_tree[0][0].put_list[0]:.6f}")
    else:
        print(f"European option value = {node_list_tree[0][0].put_list[0]:.6f}")








