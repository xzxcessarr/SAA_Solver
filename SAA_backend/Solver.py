# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Test.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为批量计算模块，用于测试算法接口，请勿直接调用
"""

from solver_model import *
import os
from config import *

# 定义脚本参数
IS_NS_MS_SS_SAA_combinations = [
    # (20, 100, 10, 10),
    # (20, 200, 10, 20),
    # (20, 500, 10, 25),
    # (40, 100, 10, 10),
    # (40, 200, 10, 20),
    (40, 500, 10, 25)
]

data_process_methods = ['pca', 'truncated_svd', 'none']
cluster_methods = [
    # 'kmeans', 'spectral', 'gmm', 
    'som'
    # , 'meanshift', 'optics', 'dbscan', 'agglomerative'
]
sample_generate_methods = ['Stratified', 'Simple']
dim_reduction_methods = ['2d', '3d']

max_attempts = 2
epoch = 1
Input_file='data/old_data.xlsx'
Output_file='result.xlsx'

log_directory = './'
# 创建基于当前时间的日志文件名
log_filename = "app.log"
full_log_path = os.path.join(log_directory, log_filename)


# 配置基本的日志设置，包括文件名、日志级别和格式
# if not os.path.exists(full_log_path):
#     logging.basicConfig(filename=full_log_path, level=logging.INFO, format='%(message)s')

# # 记录启动信息
# logging.info("Application startup: Logging setup complete.")

# # 配置日志以追加模式
# logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s', encoding='utf-8')
# logging.info(f'You are using the raw data')

for IS, NS, MS, SS_SAA in IS_NS_MS_SS_SAA_combinations:
    print(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}")
    
    # 先计算gurobi_opt
    gurobi_opt , _, _, _= two_stage_sp_model(
        IS_init=IS, 
        NS_init=NS, 
        Input_file=Input_file,
        Output_file=Output_file,
        Raw_data_flag=True,
        log_filename=full_log_path,
        max_attempts=max_attempts, 
        AS=AS,
        LS=LS, 
        Food_index=Food_index, 
        Medicine_index=Medicine_index,
    )
    print(f"gurobi_opt的计算结果是: {gurobi_opt}")
    
    # 创建图表保存文件夹的名称
    graphs_dir_name = f"Graphs_IS={IS}_NS={NS}_MS={MS}_SS_SAA={SS_SAA}"
    graphs_directory = os.path.join('./Graphs', graphs_dir_name)
    
    graphs_directories = {}
    for data_process in data_process_methods:
        for cluster in cluster_methods:
            for sample_generate in sample_generate_methods:
                for current_epoch in range(epoch):  # 添加循环以实现重复计算
                    method_dir_name = f"{data_process}_{cluster}_{sample_generate}_3D"
                    method_directory = os.path.join(graphs_directory, method_dir_name)
                    
                    # 在每个方法组合目录下创建 'Samples' 和 'Clusters' 子目录
                    sample_directory = os.path.join(method_directory, 'Samples')
                    cluster_directory = os.path.join(method_directory, 'Clusters')
                    os.makedirs(sample_directory, exist_ok=True)
                    os.makedirs(cluster_directory, exist_ok=True)

                    # 更新graphs_directories字典
                    dir_key = f"{graphs_dir_name}/{method_dir_name}"
                    graphs_directories[dir_key] = {
                        'sample': sample_directory,
                        'cluster': cluster_directory
                    }

                    graphs_store_name = f"{graphs_dir_name}/{method_dir_name}"
                    # Call the solver function with the current combination of parameters
                # print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={dim_reduction}")
                    print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction=3D")
                    # logging.info(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction=3D")
                    try:
                        solver(
                            DATA_PROCESS_METHOD=data_process,
                            CLUSTER_METHOD=cluster,
                            SAMPLE_GENERATE_METHOD=sample_generate,
                            GRAPH_METHOD='3d',
                            IS=IS,
                            NS=NS,
                            MS=MS,
                            SS_SAA=SS_SAA,
                            Graphs_sample_save_directory=sample_directory,
                            Graphs_cluster_save_directory=cluster_directory,
                            Input_file=Input_file,
                            Output_file=Output_file,
                            gurobi_opt=gurobi_opt,
                            Raw_data_flag=True,
                            log_filename=full_log_path,
                            max_attempts=max_attempts, 
                            AS=AS,
                            LS=LS, 
                            Food_index=Food_index, 
                            Medicine_index=Medicine_index,
                            DATA_PROCESS_PARAMS=DATA_PROCESS_PARAMS, 
                            CLUSTER_PARAMS=CLUSTER_PARAMS, 
                            GRAPH_CONFIG=GRAPH_CONFIG
                        ) 
                    except Exception as e:
                        print(f"An error occurred while executing the solver with parameters: {e}")