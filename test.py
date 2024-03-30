# -*- coding: utf-8 -*-
# script_name = 'PCA_Stratified_kmeans++'

import pandas as pd
import numpy as np
import time
from sklearn.cluster import KMeans
import config  # Importing the parameters and data reading method from config.py
from plugins import *
from solve_models import *
from data_preprocess import *
from sample_models import *

script_name = config.script_name

tic = time.perf_counter()
print('define set ...\n')

# Unpack parameters from config
IS = config.IS
AS = config.AS
LS = config.LS
NS = config.NS
MS = config.MS
SS_SAA = config.SS_SAA

print('define parameters ...\n')

# Read data using the method from config.py
CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data()

demand_process, demand_process_components=apply_pca(demand, 0.99)

# to store variables
ff = np.zeros((MS, 1))
ec = np.zeros((MS, 1))
pc = np.zeros((MS, 1))
wc = np.zeros((MS, 1))
xx = np.zeros((IS, LS, MS))
yy = np.zeros((AS, IS, MS))

# samples = []
sum_sample = np.zeros((MS, IS))

cluster = KMeans(n_clusters=SS_SAA, init='k-means++', random_state=0).fit(demand_process)

# demand_transformed, _ = apply_pca(demand, 2)
demand_transformed=apply_tsne(demand, 3)

# solving sample problem
for m in range(MS):
    #Stratified random sampling
    # sample = stratified_random_sampling(demand, cluster.labels_, SS_SAA, IS)
    sample = simple_random_sampling(cluster.labels_)

    SS = len(sample)
    pr_sample = np.ones(SS) / SS
    # samples.append(sample)

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
        sum_sample[m, j] = sum(demand_sample)[j]

    [Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1] = getsol(IS, AS, LS, SS, CF, U, V, H, CP, CH, G, CT, D_sample, pr_sample)
    # obtain variables
    ff[m] = Vf1
    ec[m] = Vec1
    pc[m] = Vpc1
    wc[m] = Vwc1
    xx[:, :, m] = np.round(Vx1)
    yy[:, :, m] = np.round(Vy1)

    # plot_cluster_sampling(demand_transformed, cluster.labels_, sample, config.Graphs_sample_save_directory, script_name, m)
    plot_cluster_3d_sampling(demand_transformed, cluster.labels_, sample, config.Graphs_sample_save_directory, script_name, m)

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
print(demand_process_components)


