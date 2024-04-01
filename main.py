# -*- coding: utf-8 -*-

import numpy as np
import time
import config  # Importing the parameters and data reading method from config.py
from plugins import *
from solve_models import *
from data_preprocess import *
from sample_models import *
from cluster_models import *

def two_stage_sp_model(IS_init, NS_init, Input_file, Output_file):
    from gurobipy import Model, GRB, GurobiError
    max_attempts = 3
    attempt = 0
    tic = time.perf_counter()
    while attempt < max_attempts:
        try:
            print('define parameters ...\n')
            CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data(Input_file, IS_init, NS_init, config.AS, config.Food, config.Medicine)
            # create a new model
            m = Model("two-stage_SP")

            # create sets
            IS = range(IS_init)
            NS = range(NS_init)
            AS = range(config.AS)
            LS = range(config.LS)

            # create variables
            print('define variables ...\n')
            x = m.addVars(IS,LS,vtype=GRB.BINARY, name="x")
            y = m.addVars(AS,IS,vtype=GRB.INTEGER, name="y")
            q = m.addVars(NS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
            z = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="z")
            w = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="w")
            hc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="hc")
            tc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="tc")
            wc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="wc")

            # Non-negativity constraints
            m.addConstrs((y[a,i] >= 0 for a in AS for i in IS), "y non-negative")
            m.addConstrs((q[s,a,i,j] >= 0 for s in NS for a in AS for i in IS for j in IS), "q non-negative")
            m.addConstrs((z[s,a,i] >= 0 for s in NS for a in AS for i in IS), "z non-negative")
            m.addConstrs((w[s,a,j] >= 0 for s in NS for a in AS for j in IS), "w non-negative")

            f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
            fc = m.addVar(vtype=GRB.CONTINUOUS,name='fc')
            pc = m.addVar(vtype=GRB.CONTINUOUS,name='pc')

            # Non-negativity constraints
            m.addConstr((f >= 0),"f non-negative")
            m.addConstr((fc >= 0),"fc non-negative")
            m.addConstr((pc >= 0),"pc non-negative")
            m.addConstrs((hc[s] >= 0 for s in NS),"hc non-negative")
            m.addConstrs((tc[s] >= 0 for s in NS),"tc non-negative")
            m.addConstrs((wc[s] >= 0 for s in NS),"wc non-negative")

            print('define Constraint (2) ...\n')
            m.addConstrs((sum(y[a,i] * V[a] for a in AS) <= sum(x[i,l] * U[l] for l in LS) for i in IS), 
                        "Constraint (2)")

            print('define Constraint (3) ...\n')
            m.addConstrs((z[s,a,i] == y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in NS), 
                        "Constraint (3)")

            print('define Constraint (4) ...\n')
            # C03
            m.addConstrs((w[s,a,j] == D[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in NS), 
                        "Constraint (4)")

            print('define Constraint (5) ...\n')
            # C04
            m.addConstrs((sum(x[i,l] for l in LS) <= 1 for i in IS), "Constraint (5)")


            print('objective functions')
            # C05
            m.addConstrs((wc[s] == sum(G[a] * w[s,a,j] 
                                    for a in AS for j in IS) for s in NS), "Shortage Costs")
                
            m.addConstrs((hc[s] == sum(CH[a] * z[s,a,i] 
                                    for a in AS for i in IS) for s in NS), "Surplus Costs")

            m.addConstrs((tc[s] == sum(CT[a] * H[i,j] * q[s,a,i,j] 
                                    for a in AS for i in IS for j in IS) for s in NS), "Transportation Costs")

            print('define objective ...\n')

            # Objective
            m.addConstr((fc == sum(CF[l] * x[i,l] for i in IS for l in LS)), "Fixed Facility Costs")

            m.addConstr((pc == sum(CP[a] * y[a,i] for a in AS for i in IS)), "Procurement Costs")

            m.addConstr((f == fc + pc + sum(pr[s] * (tc[s] + hc[s] + wc[s]) for s in NS)), "Objective Function")

            m.setObjective((f), GRB.MINIMIZE)

            #output result within given time
            m.setParam('TimeLimit', 3600)

            print('solving ...\n')

            m.optimize()
            # m.setParam('LogFile', 'gurobi.log')

            # Work in progress
            if m.status == GRB.OPTIMAL:

                Vx = np.zeros((IS[-1]+1,LS[-1]+1))
                Vy = np.zeros((AS[-1]+1,IS[-1]+1))
                Vq = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1,IS[-1]+1))
                Vz = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1))
                Vw = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1))
                #Vtc = np.zeros((NS[-1]+1,1))
                #Vhc = np.zeros((NS[-1]+1,1))
                #Vwc = np.zeros((NS[-1]+1,1))
                for i in IS:
                    for l in LS:
                        Vx[i,l] = x[(i,l)].x
                    for a in AS:
                        Vy[a,i] = y[(a,i)].x
                        for s in NS:
                            for j in IS:
                                Vq[s,a,i,j] = q[(s,a,i,j)].x
                            Vz[s,a,i] = z[(s,a,i)].x
                            Vw[s,a,i] = w[(s,a,i)].x
                            #Vtc[s,1] = tc[s].x
                            #Vhc[s,1] = w[s].x
                            #Vwc[s,1] = w[s].x
                Vfc = fc.x
                Vpc = pc.x
                Vtc = sum(pr[s] * tc[s].x for s in NS)
                Vhc = sum(pr[s] * hc[s].x for s in NS)
                Vwc = sum(pr[s] * wc[s].x for s in NS)        
                Vf = m.getObjective().getValue()
                
                toc = time.perf_counter()
                elapsed_time = toc - tic

                save_and_print_results('gurobi_Original', Output_file, Vx, Vy, IS_init, NS_init, 0, 0, Vf, elapsed_time, 0, 0)

                return Vf

            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1

        # except GurobiError as e:
        except Exception as e:
            # print('Error code ' + str(e.errno) + ": " + str(e))
            print('Encountered a error. Please check the code!')
            attempt += 1

    print(f"Try to find an optimal solution for {attempt} attempts.")

def solver(DATA_PROCESS_METHOD, CLUSTER_METHOD, SAMPLE_GENERATE_METHOD, GRAPH_METHOD, IS, NS, MS, SS_SAA, Graphs_sample_save_directory, Graphs_cluster_save_directory, Input_file, Output_file, gurobi_opt):
    tic = time.perf_counter()
    
    CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data(Input_file, IS, NS, config.AS, config.Food, config.Medicine)

    # 保存变量
    ff = np.zeros((MS, 1))
    ec = np.zeros((MS, 1))
    pc = np.zeros((MS, 1))
    wc = np.zeros((MS, 1))
    xx = np.zeros((IS, config.LS, MS))
    yy = np.zeros((config.AS, IS, MS))
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
        {'IS': IS} if SAMPLE_GENERATE_METHOD == 'Stratified' else {}
    )
    script_name = generate_script_name(demand_process_methods, cluster_methods, SAMPLE_GENERATE_METHOD)

    # 创建可视化降维
    selected_reduction_config = config.GRAPH_CONFIG[GRAPH_METHOD]
    grapher_processor = DataProcessor(
    selected_reduction_config['method'], 
    selected_reduction_config['params'][selected_reduction_config['method']]
    )
    demand_transformed, _, _ = grapher_processor.apply_reduction(demand)

    generate_cluster_plots(demand_transformed, cluster_labels, Graphs_cluster_save_directory, script_name, GRAPH_METHOD)

    for m in range(MS):

        sample, sample_methods = sample_generator.generate(demand, cluster_labels, cluster_num)

        SS = len(sample)
        pr_sample = np.ones(SS) / SS

        D_sample = np.zeros((SS, config.AS, IS))
        for s in range(SS):
            for a in range(config.AS):
                for j in range(IS):
                    D_sample[s, a, j] = D[sample[s], a, j]

        demand_sample = np.zeros((SS, IS))
        for s in range(SS):
            for j in range(IS):
                demand_sample[s, j] = demand[sample[s], j]
        for j in range(IS):
            sum_sample[m, j] = sum(demand_sample)[j]

        [Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1] = getsol(IS, config.AS, config.LS, SS, CF, U, V, H, CP, CH, G, CT, D_sample, pr_sample)

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
        [Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2] = renew(IS, config.AS, config.LS, NS, CF, U, V, H, CP, CH, G, CT, D, pr, new_x, new_y)

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
    Vx = np.zeros((IS, config.LS))
    Vy = np.zeros((config.AS, IS))
    for i in range(IS):
        for l in range(config.LS):
            Vx[i, l] = xx[i, l, min_m[0]]
        for a in range(config.AS):
            Vy[a, i] = yy[a, i, min_m[0]]

    toc = time.perf_counter()
    elapsed_time = toc - tic

    generate_sample_plots(demand_transformed, samples_info, cluster_labels, Graphs_sample_save_directory, GRAPH_METHOD)

    # gap_percentage = calculate_gap(ff, MS, gurobi_opt)
    gap = float((opt_f - gurobi_opt) / gurobi_opt * 100)
    save_and_print_results(script_name, Output_file, Vx, Vy, IS, NS, MS, SS_SAA, opt_f, elapsed_time, cluster_num, gap)

# if __name__ == "__main__":
    #默认调用参数，仅测试时使用
    # solver(
    #     DATA_PROCESS_METHOD='pca',
    #     CLUSTER_METHOD='kmeans',
    #     SAMPLE_GENERATE_METHOD='Stratified',
    #     GRAPH_METHOD='3d',
    #     IS=20,
    #     NS=100,
    #     MS=10,
    #     SS_SAA=10,
    #     Graphs_sample_save_directory='./Graphs',
    #     Graphs_cluster_save_directory='./Graphs',
    #     Input_file='input/data.xlsx',
    #     Output_file='result.xlsx',
    #     gurobi_opt=60704072.1222051
    # )
    # gurobi_opt = two_stage_sp_model(
    #     IS_init=20, 
    #     NS_init=100, 
    #     Input_file='input/data.xlsx',
    #     Output_file='result.xlsx'
    # )