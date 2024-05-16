# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of SAA & Gurobi.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为SAA近似算法与Gurobi精确算法框架
"""
import numpy as np
import time, logging
from plugins import *
from data_preprocess import *
from sample_method import *
from cluster_models import *
from gurobipy import Model, GRB, GurobiError

def getsol(IS,AS,LS,SS,CF,U,V,H,CP,CH,PU,CT,D_sample,pr_sample, log_filename, max_attempts):
    """
    尝试解决给定的优化模型。如果在优化过程中出现异常，会尝试重新执行，最多重试 max_attempts 次。

    参数:
    IS: 场景的数量。
    AS: 资源种类的数量。
    LS: 存储位置的数量。
    SS: 样本数量。
    CF: 固定成本。
    U: 存储容量。
    V: 物品体积。
    H: 距离矩阵。
    CP: 采购价格。
    CH: 持有成本。
    G: 罚金成本。
    CT: 运输成本。
    D_sample: 样本需求数据。
    pr_sample: 样本概率。
    log_filename: 日志文件名。
    max_attempts: 最大尝试次数。

    返回:
    元组，包含优化结果的各种参数和决策变量值，例如最优解、成本详情、分配决策等。

    功能:
    构建用于第一阶段求解样本最优解的优化模型。
    """
    # 配置日志以追加模式
    logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s', encoding='utf-8')
    attempt = 0
    while attempt < max_attempts:
        try:
            # 创建新模型
            m = Model("getsol")
            m.setParam('LogFile', log_filename)
            # m.setParam('Threads', 12) 
                
            # create sets
            IS = range(IS)
            AS = range(AS)
            LS = range(LS)
            SS = range(SS)
            
            # create variables
            print('define variables ...\n')
            x = m.addVars(IS,LS,vtype=GRB.BINARY, name="x")
            y = m.addVars(AS,IS,vtype=GRB.INTEGER, name="y")
            q = m.addVars(SS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
            z = m.addVars(SS,AS,IS,vtype=GRB.INTEGER, name="z")
            w = m.addVars(SS,AS,IS,vtype=GRB.INTEGER, name="w")
            hc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="hc")
            tc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="tc")
            wc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="wc")
            
            # Non-negativity constraints
            m.addConstrs((y[a,i] >= 0 for a in AS for i in IS), "y non-negative")
            m.addConstrs((q[s,a,i,j] >= 0 for s in SS for a in AS for i in IS for j in IS), "q non-negative")
            m.addConstrs((z[s,a,i] >= 0 for s in SS for a in AS for i in IS), "z non-negative")
            m.addConstrs((w[s,a,j] >= 0 for s in SS for a in AS for j in IS), "w non-negative")
            
            f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
            fc = m.addVar(vtype=GRB.CONTINUOUS,name='fc')
            pc = m.addVar(vtype=GRB.CONTINUOUS,name='pc')
            
            # Non-negativity constraints
            m.addConstr((f >= 0),"f non-negative")
            m.addConstr((fc >= 0),"fc non-negative")
            m.addConstr((pc >= 0),"pc non-negative")
            m.addConstrs((hc[s] >= 0 for s in SS),"hc non-negative")
            m.addConstrs((tc[s] >= 0 for s in SS),"tc non-negative")
            m.addConstrs((wc[s] >= 0 for s in SS),"wc non-negative")
            
            print('define Constraint (2) ...\n')
            m.addConstrs((sum(y[a,i] * V[a] for a in AS) <= sum(x[i,l] * U[l] for l in LS) for i in IS), 
                        "Constraint (2)")
            
            print('define Constraint (3) ...\n')
            m.addConstrs((z[s,a,i] == y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in SS), 
                        "Constraint (3)")
            
            print('define Constraint (4) ...\n')
            # C03
            m.addConstrs((w[s,a,j] == D_sample[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in SS), 
                        "Constraint (4)")
            
            print('define Constraint (5) ...\n')
            # C04
            m.addConstrs((sum(x[i,l] for l in LS) <= 1 for i in IS), "Constraint (5)")
            
            
            print('objective functions')
            # C05
            m.addConstrs((wc[s] == sum(PU[a] * w[s,a,j] 
                                    for a in AS for j in IS) for s in SS), "Shortage Costs")
                
            m.addConstrs((hc[s] == sum(CH[a] * z[s,a,i] 
                                    for a in AS for i in IS) for s in SS), "Surplus Costs")
            
            m.addConstrs((tc[s] == sum(CT[a] * H[i,j] * q[s,a,i,j] 
                                    for a in AS for i in IS for j in IS) for s in SS), "Transportation Costs")
            
            print('define objective ...\n')
            
            # Objective
            m.addConstr((fc == sum(CF[l] * x[i,l] for i in IS for l in LS)), "Fixed Facility Costs")
            
            m.addConstr((pc == sum(CP[a] * y[a,i] for a in AS for i in IS)), "Procurement Costs")
            
            m.addConstr((f == fc + pc + sum(pr_sample[s] * (tc[s] + hc[s] + wc[s]) for s in SS)), "Objective Function")
            
            m.setObjective((f), GRB.MINIMIZE)
            
            print('solving ...\n')
            
            m.optimize()
            
            if m.status == GRB.OPTIMAL:
                print('solved!')
                
                Vx1 = np.zeros((IS[-1]+1,LS[-1]+1))
                Vy1 = np.zeros((AS[-1]+1,IS[-1]+1))
                for i in IS:
                    for l in LS:
                        Vx1[i,l] = x[(i,l)].x
                    for a in AS:
                        Vy1[a,i] = y[(a,i)].x

                Vf1 = m.getObjective().getValue()
                Vfc1 = sum(CF[l] * Vx1[i,l] for i in IS for l in LS)
                Vpc1 = sum(CP[a] * Vy1[a,i] for a in AS for i in IS)
                Vtc1 = sum(pr_sample[s] * tc[s].x for s in SS)
                Vhc1 = sum(pr_sample[s] * hc[s].x for s in SS)
                Vwc1 = sum(pr_sample[s] * wc[s].x for s in SS)        
                Vec1 = Vfc1+Vpc1+Vtc1+Vhc1
                
                return Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1  
                  
            
            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1
        
        except GurobiError as e:
        # except Exception as e:
            print('Encountered a Gurobi error. Please check the Gurobi log for more details.')
            print('Error code ' + str(e.errno) + ": " + str(e))
            logging.error('Error code ' + str(e.errno) + ": " + str(e))
            attempt += 1
            
    print(f"Try to find an optimal solution for {attempt + 1} attempts.")

def renew(IS,AS,LS,NS,CF,U,V,H,CP,CH,PU,CT,D,pr,new_x,new_y, log_filename, max_attempts):
    """
    重新解决优化模型。如果在优化过程中出现异常，会尝试重新执行，最多重试 max_attempts 次。

    参数:
    IS: 场景的数量。
    AS: 资源种类的数量。
    LS: 存储位置的数量。
    NS: 需求点的数量。
    CF: 固定成本。
    U: 存储容量。
    V: 物品体积。
    H: 距离矩阵。
    CP: 采购价格。
    CH: 持有成本。
    G: 罚金成本。
    CT: 运输成本。
    D: 需求数据。
    pr: 需求概率。
    new_x: 新的x决策变量。
    new_y: 新的y决策变量。
    log_filename: 日志文件名。
    max_attempts: 最大尝试次数。

    返回:
    元组，包含优化后的成本和决策变量。

    功能:
    基于新的决策变量以及上一阶段所有的样本最优解重新构建并解决优化模型，得到最终的近似结果。
    """
    # 配置日志以追加模式
    logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s', encoding='utf-8')
    attempt = 0
    while attempt < max_attempts:
        try:
            # 创建新模型
            m = Model("renew")
            m.setParam('LogFile', log_filename)
                
            # create sets
            IS = range(IS)
            AS = range(AS)
            LS = range(LS)
            NS = range(NS)
            
            # create variables
            print('define variables ...\n')
            q = m.addVars(NS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
            z = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="z")
            w = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="w")
            hc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="hc")
            tc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="tc")
            wc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="wc")
            
            # Non-negativity constraints
            m.addConstrs((q[s,a,i,j] >= 0 for s in NS for a in AS for i in IS for j in IS), "q non-negative")
            m.addConstrs((z[s,a,i] >= 0 for s in NS for a in AS for i in IS), "z non-negative")
            m.addConstrs((w[s,a,j] >= 0 for s in NS for a in AS for j in IS), "w non-negative")
            
            f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
            
            # Non-negativity constraints
            m.addConstr((f >= 0),"f non-negative")
            m.addConstrs((hc[s] >= 0 for s in NS),"hc non-negative")
            m.addConstrs((tc[s] >= 0 for s in NS),"tc non-negative")
            m.addConstrs((wc[s] >= 0 for s in NS),"wc non-negative")

            print('define Constraint (3) ...\n')
            m.addConstrs((z[s,a,i] == new_y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in NS), 
                        "Constraint (3)")
            
            print('define Constraint (4) ...\n')
            # C03
            m.addConstrs((w[s,a,j] == D[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in NS), 
                        "Constraint (4)")
            
            print('objective functions')
            # C05
            m.addConstrs((wc[s] == sum(PU[a] * w[s,a,j] 
                                    for a in AS for j in IS) for s in NS), "Shortage Costs")
                
            m.addConstrs((hc[s] == sum(CH[a] * z[s,a,i] 
                                    for a in AS for i in IS) for s in NS), "Surplus Costs")
            
            m.addConstrs((tc[s] == sum(CT[a] * H[i,j] * q[s,a,i,j] 
                                    for a in AS for i in IS for j in IS) for s in NS), "Transportation Costs")
            
            print('define objective ...\n')
            
            # Objective
            
            m.addConstr((f == sum(pr[s] * (tc[s] + hc[s] + wc[s]) for s in NS)), "Objective Function")
            
            m.setObjective((f), GRB.MINIMIZE)
            
            print('solving ...\n')
            
            m.optimize()
    
            if m.status == GRB.OPTIMAL:
                print('solved!')

                Vfc2 = sum(CF[l] * new_x[i,l] for i in IS for l in LS)
                Vpc2 = sum(CP[a] * new_y[a,i] for a in AS for i in IS)
                Vtc2 = sum(pr[s] * tc[s].x for s in NS)
                Vhc2 = sum(pr[s] * hc[s].x for s in NS)
                Vwc2 = sum(pr[s] * wc[s].x for s in NS)        
                Vf2 = Vfc2+Vpc2+Vtc2+Vhc2+Vwc2
                
                return Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2
        
            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1
        
        except GurobiError as e:
        # except Exception as e:
            print('Encountered a Gurobi error. Please check the Gurobi log for more details.')
            print('Error code ' + str(e.errno) + ": " + str(e))
            logging.error('Error code ' + str(e.errno) + ": " + str(e))
            attempt += 1

    print(f"Try to find an optimal solution for {attempt} attempts.")

def two_stage_sp_model(IS_init, NS_init, Input_file, Output_file, Raw_data_flag, log_filename, max_attempts, AS_init, LS_init, Food_index, Medicine_index):
    """
    执行Gurobi两阶段随机规划模型的精确解求解。

    参数:
    IS_init: 初始化的场景数量。
    NS_init: 初始化的需求点数量。
    Input_file: 输入文件路径。
    Output_file: 结果输出文件路径。
    Raw_data_flag: 是否使用原始数据标志。
    log_filename: 日志文件路径。
    max_attempts: 最大尝试次数。
    AS_init: 初始化的资源种类数量。
    LS_init: 初始化的存储位置数量。
    Food_index: 食品类资源索引。
    Medicine_index: 药品类资源索引。

    返回:
    返回一个元组，包括精确解最优解、花费的时间、决策变量Vx和Vy。

    功能:
    读取数据，构建模型并求解，最终将结果输出到文件。
    """
    # 配置日志以追加模式
    logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s')
    attempt = 0
    tic = time.perf_counter()
    while attempt < max_attempts:
        try:
            print('define parameters ...\n')
            # CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data(Input_file, IS_init, NS_init, AS_init, Food_index, Medicine_index, Raw_data_flag)
            
            # CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data_old(Input_file, IS_init, NS_init, AS_init, Food_index, Medicine_index)
            
            CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data_from_redis(IS_init, NS_init, AS_init, Food_index, Medicine_index)

            # create a new model
            m = Model("two-stage_SP")
            m.setParam('LogFile', log_filename)

            # create sets
            IS = range(IS_init)
            NS = range(NS_init)
            AS = range(AS_init)
            LS = range(LS_init)

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
            m.addConstrs((wc[s] == sum(PU[a] * w[s,a,j] 
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
            m.setParam('TimeLimit', 6000)

            print('solving ...\n')

            m.optimize()

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
                # 打印结果
                print(f"Method: gurobi_Original")
                print(f"I: {max(IS)+1}, S: {max(NS)+1}")    
                print(f"Costs: {float(Vf)}, gap: 0 %")
                print(f"Elapsed time: {elapsed_time} seconds.")
                # 记录结果
                logging.info('--------------------------------------------')
                logging.info(f"Method: gurobi_Original")
                logging.info(f"I: {max(IS)+1}, S: {max(NS)+1}")     
                logging.info(f"Costs: {float(Vf)}, gap: 0 %")
                logging.info(f"Elapsed time: {elapsed_time} seconds.")
                logging.info('--------------------------------------------')

                return Vf,elapsed_time,Vx,Vy.T

            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1

        except GurobiError as e:
        # except Exception as e:
            print('Error code ' + str(e.errno) + ": " + str(e))
            logging.error('Error code ' + str(e.errno) + ": " + str(e))
            print('Encountered a Gurobi error. Please check the Gurobi log for more details.')
            attempt += 1

    print(f"Try to find an optimal solution for {attempt} attempts.")

def solver(DATA_PROCESS_METHOD, CLUSTER_METHOD, SAMPLE_GENERATE_METHOD, GRAPH_METHOD, IS, NS, MS, SS_SAA, Graphs_sample_save_directory, Graphs_cluster_save_directory, Input_file, Output_file, gurobi_opt, Raw_data_flag, log_filename, max_attempts, AS, LS, Food_index, Medicine_index, DATA_PROCESS_PARAMS, CLUSTER_PARAMS, GRAPH_CONFIG):
    """
    SAA算法核心框架，整合数据处理、聚类分析、样本生成、图表生成和近似解求解过程。

    参数:
    DATA_PROCESS_METHOD: 数据处理方法。
    CLUSTER_METHOD: 聚类方法。
    SAMPLE_GENERATE_METHOD: 样本生成方法。
    GRAPH_METHOD: 图表生成方法。
    IS: 场景的数量。
    NS: 需求点的数量。
    MS: 样本组的数量。
    SS_SAA: 二阶段随机规划中样本大小。
    Graphs_sample_save_directory:样本图表保存目录。
    Graphs_cluster_save_directory: 聚类图表保存目录。
    Input_file: 输入文件路径。
    Output_file: 输出文件路径。
    gurobi_opt: Gurobi或其他求解器提供的已知全局最优结果。
    Raw_data_flag: 是否使用原始数据标志。
    log_filename: 日志文件名。
    max_attempts: 最大尝试次数。
    AS: 资源种类的数量。
    LS: 存储位置的数量。
    Food_index: 食品类资源索引。
    Medicine_index: 药品类资源索引。
    DATA_PROCESS_PARAMS: 数据处理参数。
    CLUSTER_PARAMS: 聚类参数。
    GRAPH_CONFIG: 图表配置参数。

    返回:
    返回一个元组，包括脚本名、最优解、花费的时间、gap值、决策变量Vx和Vy以及输出文件路径。

    功能:
    集成了从数据处理到模型求解的完整流程。它包括数据预处理、聚类、样本生成、绘图和优化求解等步骤。
    """
    # 配置日志以追加模式
    logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s', encoding='utf-8')
    
    tic = time.perf_counter()
    
    # CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data_old(Input_file, IS, NS, AS, Food_index, Medicine_index)

    # CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data(Input_file, IS, NS, AS, Food_index, Medicine_index, Raw_data_flag)
    
    CF, U, H, V, CP, CH, PU, CT, D, pr, demand = read_data_from_redis(IS, NS, AS, Food_index, Medicine_index)

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
    data_processor = DataProcessor(DATA_PROCESS_METHOD, DATA_PROCESS_PARAMS[DATA_PROCESS_METHOD])
    demand_process, demand_process_components, demand_process_methods = data_processor.apply_reduction(demand)

    # 聚类分析对象实例化
    cluster_analyzer = ClusteringMethod(CLUSTER_METHOD, CLUSTER_PARAMS[CLUSTER_METHOD])
    cluster_labels, cluster_methods  = cluster_analyzer.apply_clustering(demand_process)
    cluster_num = len(np.unique(cluster_labels))

    # 样本生成器对象实例化
    sample_generator = SampleGenerator(
        SAMPLE_GENERATE_METHOD,
        {'IS': IS} if SAMPLE_GENERATE_METHOD == 'Stratified' else {}
    )
    script_name = generate_script_name(demand_process_methods, cluster_methods, SAMPLE_GENERATE_METHOD)

    # 创建可视化降维
    selected_reduction_config = GRAPH_CONFIG[GRAPH_METHOD]
    grapher_processor = DataProcessor(
    selected_reduction_config['method'], 
    selected_reduction_config['params'][selected_reduction_config['method']]
    )
    demand_transformed, _, _ = grapher_processor.apply_reduction(demand)

    # 检查Graphs_cluster_save_directory是否为空或None
    if Graphs_cluster_save_directory and Graphs_cluster_save_directory.strip():
        # 如果Graphs_cluster_save_directory不是空字符串或None，则执行函数
        generate_cluster_plots(demand_transformed, cluster_labels, Graphs_cluster_save_directory, script_name, GRAPH_METHOD)
    else:
        # 如果Graphs_cluster_save_directory是空字符串或None，则跳过执行
        print("Cluster plots generation skipped due to empty or None Graphs_cluster_save_directory.")

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

        [Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1] = getsol(IS, AS, LS, SS, CF, U, V, H, CP, CH, PU, CT, D_sample, pr_sample, log_filename, max_attempts)

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
        [Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2] = renew(IS, AS, LS, NS, CF, U, V, H, CP, CH, PU, CT, D, pr, new_x, new_y, log_filename, max_attempts)

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

    # 检查Graphs_sample_save_directory是否为空或None
    if Graphs_sample_save_directory and Graphs_sample_save_directory.strip():
        # 如果Graphs_sample_save_directory不是空字符串或None，则执行函数
        generate_sample_plots(demand_transformed, samples_info, cluster_labels, Graphs_sample_save_directory, GRAPH_METHOD)
    else:
        # 如果Graphs_sample_save_directory是空字符串或None，则跳过执行
        print("Sample plots generation skipped due to empty or None Graphs_sample_save_directory.")

    # gap_percentage = calculate_gap(ff, MS, gurobi_opt)
    gap = float((opt_f - gurobi_opt) / gurobi_opt * 100)
    save_and_print_results(script_name, Output_file, Vx, Vy, IS, NS, MS, SS_SAA, opt_f, elapsed_time, cluster_num, gap)
    # 打印结果
    print(f"Method: {script_name}")
    print(f"I: {IS}, S: {NS}, M: {MS}, N: {SS_SAA}, clustering_num: {cluster_num}")    
    print(f"Costs: {float(opt_f[0])}, gap: {gap} %")
    print(f"Elapsed time: {elapsed_time} seconds.")
    logging.info('--------------------------------------------')
    logging.info(f"Method: {script_name}")
    logging.info(f"I: {IS}, S: {NS}, M: {MS}, N: {SS_SAA}, clustering_num: {cluster_num}")    
    logging.info(f"Costs: {float(opt_f[0])}, gap: {gap} %")
    logging.info(f"Elapsed time: {elapsed_time} seconds.")
    logging.info('--------------------------------------------')
    return script_name, opt_f, elapsed_time, gap, Vx, Vy.T, Output_file

if __name__ == "__main__":
    from config import *
    Input_data_path='data/raw_data.xlsx'
    NS_init=100
    IS_init=20
    store_data_to_redis(Input_data_path, IS_init, True)
    # 默认调用参数，仅测试时使用
    solver(
        DATA_PROCESS_METHOD='pca',
        CLUSTER_METHOD='spectral',
        SAMPLE_GENERATE_METHOD='Stratified',
        GRAPH_METHOD='3d',
        IS=IS_init,
        NS=NS_init,
        MS=10,
        SS_SAA=10,
        Graphs_sample_save_directory='./Graphs',
        Graphs_cluster_save_directory='./Graphs',
        Input_file='data/raw_data.xlsx',
        Output_file='result.xlsx',
        gurobi_opt=60704072.122205056,
        Raw_data_flag=True,
        log_filename='app.log',
        max_attempts=2, 
        AS=AS,
        LS=LS, 
        Food_index=Food_index, 
        Medicine_index=Medicine_index,
        DATA_PROCESS_PARAMS=DATA_PROCESS_PARAMS, 
        CLUSTER_PARAMS=CLUSTER_PARAMS, 
        GRAPH_CONFIG=GRAPH_CONFIG
    )
    # gurobi_opt = two_stage_sp_model(
    #     IS_init=IS_init, 
    #     NS_init=NS_init, 
    #     Input_file=Input_data_path,
    #     Output_file='result.xlsx',
    #     Raw_data_flag=True,
    #     log_filename='app.log',
    #     max_attempts=2,
    #     AS_init=AS,
    #     LS_init=LS, 
    #     Food_index=Food_index, 
    #     Medicine_index=Medicine_index
    # )
