# -*- coding: utf-8 -*-

import numpy as np
import time
import config  # Importing the parameters and data reading method from config.py
from plugins import *
from solve_models import *
from data_preprocess import *
from sample_models import *
from cluster_models import *

def main():
    tic = time.perf_counter()

    # 使用config.py中的参数
    IS = config.IS
    AS = config.AS
    LS = config.LS
    NS = config.NS
    MS = config.MS
    SS_SAA = config.SS_SAA
    CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data()

    # 保存变量
    ff = np.zeros((MS, 1))
    ec = np.zeros((MS, 1))
    pc = np.zeros((MS, 1))
    wc = np.zeros((MS, 1))
    xx = np.zeros((IS, LS, MS))
    yy = np.zeros((AS, IS, MS))
    sum_sample = np.zeros((MS, IS))

    # solving original problem
    new_f = np.zeros((MS, 1))
    new_fc = np.zeros((MS, 1))
    new_pc = np.zeros((MS, 1))
    new_tc = np.zeros((MS, 1))
    new_hc = np.zeros((MS, 1))
    new_wc = np.zeros((MS, 1))
    
    # 数据处理对象
    data_processor = DataProcessor(config.DATA_PROCESS_METHOD, config.DATA_PROCESS_PARAMS[config.DATA_PROCESS_METHOD])
    demand_process, demand_process_components, demand_process_methods = data_processor.apply_reduction(demand)

    # 聚类分析对象
    cluster_analyzer = ClusteringMethod(config.CLUSTER_METHOD, config.CLUSTER_PARAMS[config.CLUSTER_METHOD])
    cluster_labels, cluster_methods  = cluster_analyzer.apply_clustering(demand_process)

    # 创建可视化降维
    # grapher_processor = DataProcessor(config.DIM2_REDUCTION_METHOD, config.DIM2_REDUCTION_PARAMS[config.DIM2_REDUCTION_METHOD])
    # demand_transformed, _, _ = grapher_processor.apply_reduction(demand)
    selected_reduction_config = config.DIM_REDUCTION_CONFIG['2d']
    grapher_processor = DataProcessor(
    selected_reduction_config['method'], 
    selected_reduction_config['params'][selected_reduction_config['method']]
    )
    demand_transformed, _, _ = grapher_processor.apply_reduction(demand)
    
    cluster_num = len(np.unique(cluster_labels))

    
    samples_info = []

    for m in range(MS):
    
        sample, sample_methods = stratified_random_sampling(demand, cluster_labels, cluster_num, IS)
        # sample, sample_methods = simple_random_sampling(cluster_labels)


        script_name = generate_script_name(demand_process_methods, cluster_methods, sample_methods)


        SS = len(sample)
        pr_sample = np.ones(SS) / SS

        D_sample = np.zeros((SS, AS, IS))
        for s in range(SS):
            for a in range(AS):
                for j in range(IS):
                    D_sample[s, a, j] = D[sample[s], a, j]

        demand_sample = np.zeros((SS, IS))
        for s in range(SS):
            for j in range(IS):
                demand_sample[s, j] = demand[sample[s], j]
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

        samples_info.append((sample, script_name, m))


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

    for sample, script_name, m in samples_info:
        # plot_cluster_3d_sampling(demand_transformed, cluster_labels, sample, config.Graphs_sample_save_directory, script_name, m)
        plot_cluster_sampling(demand_transformed, cluster_labels, sample, config.Graphs_sample_save_directory, script_name, m)

    save_and_print_results(script_name, config.IS, config.NS, config.MS, config.SS_SAA, opt_f, elapsed_time)

    # gap_percentage = calculate_gap(ff, MS, gurobi_opt)



if __name__ == "__main__":
    main()