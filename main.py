# -*- coding: utf-8 -*-

import numpy as np
import time
import config  # Importing the parameters and data reading method from config.py
from plugins import *
from solve_models import *
from data_preprocess import *
from sample_models import *
from cluster_models import *

def solver(DATA_PROCESS_METHOD, CLUSTER_METHOD, SAMPLE_GENERATE_METHOD, DIM_REDUCTION_METHOD):
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

    new_f = np.zeros((MS, 1))
    new_fc = np.zeros((MS, 1))
    new_pc = np.zeros((MS, 1))
    new_tc = np.zeros((MS, 1))
    new_hc = np.zeros((MS, 1))
    new_wc = np.zeros((MS, 1))  

    samples_info = []
    
    # 数据处理对象实例化
    data_processor = DataProcessor(DATA_PROCESS_METHOD, config.DATA_PROCESS_PARAMS[DATA_PROCESS_METHOD])
    demand_process, demand_process_components, demand_process_methods = data_processor.apply_reduction(demand)

    # 聚类分析对象实例化
    cluster_analyzer = ClusteringMethod(CLUSTER_METHOD, config.CLUSTER_PARAMS[CLUSTER_METHOD])
    cluster_labels, cluster_methods  = cluster_analyzer.apply_clustering(demand_process)
    cluster_num = len(np.unique(cluster_labels))

    # 样本生成器对象实例化
    sample_generator = SampleGenerator(
        SAMPLE_GENERATE_METHOD,
        config.SAMPLE_GENERATE_PARAMS[SAMPLE_GENERATE_METHOD]
    )
    script_name = generate_script_name(demand_process_methods, cluster_methods, SAMPLE_GENERATE_METHOD)

    # 创建可视化降维
    selected_reduction_config = config.DIM_REDUCTION_CONFIG[DIM_REDUCTION_METHOD]
    grapher_processor = DataProcessor(
    selected_reduction_config['method'], 
    selected_reduction_config['params'][selected_reduction_config['method']]
    )
    demand_transformed, _, _ = grapher_processor.apply_reduction(demand)

    # plot_cluster(demand_transformed, cluster_labels, config.Graphs_sample_save_directory, script_name)
    plot_cluster_3d(demand_transformed, cluster_labels, config.Graphs_sample_save_directory, script_name)

    for m in range(MS):

        sample, sample_methods = sample_generator.generate(demand, cluster_labels, cluster_num)

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

    # generate_cluster_plots(demand_transformed, samples_info, cluster_labels)

    # gap_percentage = calculate_gap(ff, MS, config.gurobi_opt)
    gap = float((opt_f - config.gurobi_opt) / config.gurobi_opt * 100)
    save_and_print_results(script_name, config.IS, config.NS, config.MS, config.SS_SAA, opt_f, elapsed_time, cluster_num, gap)


if __name__ == "__main__":
    solver('pca','kmeans','Stratified','2d')