# -*- coding: utf-8 -*-
script_name = 'Stratified_SOM'

import pandas as pd
import numpy as np
import time
from minisom import MiniSom
from plugins import *
from solve_models import *
import config  # Importing the parameters and data reading method from config.py

tic = time.perf_counter()
print('define set ...\n')

# Unpack parameters from config
IS = config.IS
AS = config.AS
LS = config.LS
NS = config.NS
MS = config.MS
SS_SAA = config.SS_SAA  # Assuming SS_SAA is defined in config.py for SOM as it is for k-means++

print('define parameters ...\n')

# Read data using the method from config.py
CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data()

# to store variables
ff = np.zeros((MS, 1))
ec = np.zeros((MS, 1))
pc = np.zeros((MS, 1))
wc = np.zeros((MS, 1))
xx = np.zeros((IS, LS, MS))
yy = np.zeros((AS, IS, MS))

sum_sample = np.zeros((MS, IS))

som = MiniSom(x=5, y=5, input_len=demand.shape[1], sigma=0.7, learning_rate=0.5)
som.train_random(data=demand, num_iteration=1000)

winning_neurons = np.array([som.winner(x) for x in demand])
neuron_labels = {tuple(neuron): i for i, neuron in enumerate(np.unique(winning_neurons, axis=0))}
cluster_labels = np.array([neuron_labels[tuple(winner)] for winner in winning_neurons])

num_unique_labels = len(np.unique(cluster_labels))

for m in range(MS):
    # Stratified random sampling
    sample = []

    standard = np.zeros((num_unique_labels, 1))
    temp_num = np.zeros((num_unique_labels, 1))
    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i).flatten()
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        demand_sample = np.zeros((len(cluster_each), IS))
        for s in range(len(cluster_each)):
            for j in range(IS):
                demand_sample[s, j] = demand[int(cluster_each[s]), j]
        # determine scenario number for each sample by standard deviation
        mean_sample = np.mean(demand_sample, axis=0)
        standard[i] = np.sqrt(sum(sum(np.square(demand_sample - mean_sample.T))) / len(cluster_each))
        temp_num[i] = standard[i] * len(cluster_each)

    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i).flatten()
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        pick_num = np.rint(num_unique_labels * len(cluster_each) * standard[i] / sum(temp_num))
        pick_num = pick_num.astype(np.int32)[0]
        
        if pick_num == 0:
            continue
        elif pick_num == 1:
            temp = np.random.choice(len(cluster_each), 1, replace=False)
            sample.append(cluster_each[temp[0]])
        else:
            temp = np.random.choice(len(cluster_each), pick_num, replace=False)
            for j in range(pick_num):
                sample.append(cluster_each[temp[j]])

    SS = len(sample)
    pr_sample = np.ones(SS) / SS

    D_sample = np.zeros((SS, AS, IS))
    for s in range(SS):
        for a in range(AS):
            for j in range(IS):
                D_sample[s, a, j] = D[int(sample[s]), a, j]

    demand_sample = np.zeros((SS, IS))
    for s in range(SS):
        for j in range(IS):
            demand_sample[s, j] = demand[int(sample[s]), j]
    for j in range(IS):
        sum_sample[m, j] = sum(demand_sample[:, j])

    [Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1] = getsol(IS, AS, LS, SS, CF, U, V, H, CP, CH, G, CT, D_sample, pr_sample)
    # obtain variables
    ff[m] = Vf1
    ec[m] = Vec1
    pc[m] = Vpc1
    wc[m] = Vwc1
    xx[:, :, m] = np.round(Vx1)
    yy[:, :, m] = np.round(Vy1)

# solving original problem

new_f = np.zeros((MS, 1))
new_fc = np.zeros((MS, 1))
new_pc = np.zeros((MS, 1))
new_tc = np.zeros((MS, 1))
new_hc = np.zeros((MS, 1))
new_wc = np.zeros((MS, 1))

for m in range(MS):
    new_x = xx[:, :, m]
    new_y = yy[:, :, m]
    [Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2] = renew(IS, AS, LS, NS, CF, U, V, H, CP, CH, G, CT, D, pr, new_x, new_y)

    # obtain variables
    new_f[m] = Vf2
    new_fc[m] = Vfc2
    new_pc[m] = Vpc2
    new_tc[m] = Vtc2
    new_hc[m] = Vhc2
    new_wc[m] = Vwc2

# finding optimal solution
opt_f = min(new_f)
min_m = np.where(new_f == opt_f)

sum1 = 0
for m in range(MS):
    sum1 = sum1 + ff[m]

ave_f = sum1 / MS

gap = (opt_f - ave_f) / ave_f

costs = pd.DataFrame([new_f[min_m], new_fc[min_m], new_pc[min_m], new_tc[min_m], new_hc[min_m], new_wc[min_m]]).T
Vx = np.zeros((IS, LS))
Vy = np.zeros((AS, IS))
for i in range(IS):
    for l in range(LS):
        Vx[i, l] = xx[i, l, min_m[0]]
    for a in range(AS):
        Vy[a, i] = yy[a, i, min_m[0]]

toc = time.perf_counter()
elapsed_time = toc - tic
elapsed_time_df = pd.DataFrame([['Elapsed time', elapsed_time]], columns=['Metric', 'Value'])

save_and_print_results(script_name, config.IS, config.NS, config.MS, config.SS_SAA, opt_f, elapsed_time)


