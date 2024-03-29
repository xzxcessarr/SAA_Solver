import pandas as pd
import numpy as np
import time
from sklearn.cluster import MeanShift
from sklearn.decomposition import PCA  # Import PCA module
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
MS = config.MS
SS_SAA = config.SS_SAA

print('define parameters ...\n')
filename = 'data.xlsx'

# Read data using the method from config.py
CF, U, H, V, CP, CH, G, CT, D, pr, demand = config.read_data(filename)

# Apply PCA
pca = PCA(n_components=IS)  # Choose the number of components for PCA
demand_pca = pca.fit_transform(demand)

# to store variables
ff = np.zeros((MS, 1))
ec = np.zeros((MS, 1))
pc = np.zeros((MS, 1))
wc = np.zeros((MS, 1))
xx = np.zeros((IS, LS, MS))
yy = np.zeros((AS, IS, MS))

# samples = []
sum_sample = np.zeros((MS, IS))

cluster = MeanShift().fit(demand_pca)
labels_unique = np.unique(cluster.labels_)
n_clusters = len(labels_unique)  # MeanShift产生的实际聚类数量

# 如果聚类数量超过预设的SS_SAA，按照聚类密度选择前SS_SAA个
if n_clusters > SS_SAA:
    cluster_counts = np.bincount(cluster.labels_)
    cluster_density = cluster_counts / np.max(cluster_counts)
    # 选择密度最大的前SS_SAA个聚类
    selected_clusters = np.argsort(cluster_density)[::-1][:SS_SAA]
else:
    selected_clusters = labels_unique

# solving sample problem
for m in range(MS):
    #Stratified random sampling
    sample = []

    standard = np.zeros((len(selected_clusters), 1))
    temp_num = np.zeros((len(selected_clusters), 1))
    for idx, i in enumerate(selected_clusters):
        cluster_each = np.argwhere(cluster.labels_ == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        demand_sample = demand[cluster_each, :]
        # 计算每个样本的标准偏差
        mean_sample = np.mean(demand_sample, axis=0)
        standard[idx] = np.sqrt(np.mean(np.square(demand_sample - mean_sample)))
        temp_num[idx] = standard[idx] * len(cluster_each)
    
    # 确定每个样本的情景数量
    for idx, i in enumerate(selected_clusters):
        cluster_each = np.argwhere(cluster.labels_ == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        pick_num = np.rint(len(selected_clusters) * len(cluster_each) * standard[idx] / sum(temp_num))
        pick_num = pick_num.astype(np.int32)[0]

        if pick_num == 0:
            continue
        elif pick_num == 1:
            temp = np.random.choice(len(cluster_each), 1, replace=False)
            sample.append(cluster_each[temp[0]])
        else:
            temp = np.random.choice(len(cluster_each), pick_num, replace=False)
            sample.extend(cluster_each[temp_idx] for temp_idx in temp)

    SS = len(sample)
    pr_sample = np.ones(SS) / SS
    # samples.append(sample)

    D_sample = np.zeros((SS, AS, IS))
    for s, idx in enumerate(sample):
        for a in range(AS):
            for j in range(IS):
                D_sample[s, a, j] = D[int(idx), a, j]

    demand_sample = demand[sample]
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
print("Elapsed time is " + str(elapsed_time) + " seconds.")
elapsed_time_df = pd.DataFrame([['Elapsed time', elapsed_time]], columns=['Metric', 'Value'])

location = pd.DataFrame(Vx)
inventory = pd.DataFrame(Vy).T
append_df_to_excel('data.xlsx', costs, sheet_name='result', index=False, header=False, startrow=1)
append_df_to_excel('data.xlsx', location, sheet_name='result', index=False, header=False, startrow=1, startcol=costs.shape[0] + 2)
append_df_to_excel('data.xlsx', inventory, sheet_name='result', index=False, header=False, startrow=1, startcol=costs.shape[0] + location.shape[0] + 2)
append_df_to_excel('data.xlsx', elapsed_time_df, sheet_name='result', index=False, header=False, startrow=costs.shape[0] + inventory.shape[0] + location.shape[0] + 2)


