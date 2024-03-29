# -*- coding: utf-8 -*-
script_name = 'Simple_kmeans++'

"""
Integrating kmeans into SAA
"""

import pandas as pd
import numpy as np
import time
from sklearn.cluster import KMeans
from plugins import append_df_to_excel
from plugins import save_and_print_results
from models import getsol
from models import renew
import config  # Importing the parameters and data reading method from config.py

tic = time.perf_counter()
print('define set ...\n')

# Unpack parameters from config
IS = config.IS
AS = config.AS
LS = config.LS
NS = config.NS
SS_SAA = config.SS_SAA
MS = config.MS

print('define parameters ...\n')
filename = 'data.xlsx'

# Read data using the method from config.py
CF, U, H, V, CP, CH, G, CT, D, pr, demand = config.read_data(filename)

# to store variables
ff = np.zeros((MS, 1))
ec = np.zeros((MS, 1))
pc = np.zeros((MS, 1))
wc = np.zeros((MS, 1))
xx = np.zeros((IS, LS, MS))
yy = np.zeros((AS, IS, MS))

# solving sample problem
cluster = KMeans(n_clusters=SS_SAA, init='k-means++', random_state=0).fit(demand)

samples = []
sum_sample = np.zeros((MS, IS))

for m in range(MS):
    
    # randomly select one from each group
    sample = []
    for i in np.unique(cluster.labels_):
        cluster_each = np.argwhere(cluster.labels_ == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        temp = np.random.choice(len(cluster_each), 1, replace=False)
        sample.append(cluster_each[temp[0]]) 
    
    SS = len(sample)
    pr_sample = np.ones(SS) / SS
    samples.append(sample)
    
    D_sample = np.zeros((SS, AS, IS))
    for s in range(SS):
        for a in range(AS):
            for j in range(IS):
                D_sample[s, a, j] = D[int(sample[s]), a, j]
                
    [Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1] = getsol(IS, AS, LS, SS, CF, U, V, H, CP, CH, G, CT, D_sample, pr_sample)
    # obtain variables
    ff[m] = Vf1
    ec[m] = Vec1
    pc[m] = Vpc1
    wc[m] = Vwc1
    xx[:, :, m] = np.round(Vx1)
    yy[:, :, m] = np.round(Vy1)
    total_demand = 0

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

save_and_print_results(script_name, config.IS, config.NS, opt_f, elapsed_time)


