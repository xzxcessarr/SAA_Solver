from main import *  # 假设solver函数定义在main.py文件中
import os

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
    'kmeans', 'spectral', 'gmm', 'som'
]
sample_generate_methods = ['Stratified', 'Simple']
dim_reduction_methods = ['2d', '3d']

max_attempts = 2

for IS, NS, MS, SS_SAA in IS_NS_MS_SS_SAA_combinations:
    print(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}")
    
    # 先计算gurobi_opt
    gurobi_opt = two_stage_sp_model(
        IS_init=IS, 
        NS_init=NS, 
        Input_file='input/data.xlsx',
        Output_file='result.xlsx'
    )
    print(f"gurobi_opt的计算结果是: {gurobi_opt}")
    
    # 创建图表保存文件夹的名称
    graphs_dir_name = f"Graphs_IS={IS}_NS={NS}_MS={MS}_SS_SAA={SS_SAA}"
    graphs_sample_save_directory = os.path.join('./Graphs', graphs_dir_name, 'Samples')
    graphs_cluster_save_directory = os.path.join('./Graphs', graphs_dir_name, 'Clusters')
    
    # 检查文件夹是否存在，如果不存在，则创建它们
    os.makedirs(graphs_sample_save_directory, exist_ok=True)
    os.makedirs(graphs_cluster_save_directory, exist_ok=True)
    
    for data_process in data_process_methods:
        for cluster in cluster_methods:
            # for sample_generate in sample_generate_methods:
                # for dim_reduction in dim_reduction_methods:
                    # Call the solver function with the current combination of parameters
                # print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={dim_reduction}")
            print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling=Stratified")
            attempt = 0
            while attempt < max_attempts:
                try:
                    solver(
                        DATA_PROCESS_METHOD=data_process,
                        CLUSTER_METHOD=cluster,
                        SAMPLE_GENERATE_METHOD='Stratified',
                        GRAPH_METHOD='3d',
                        IS=IS,
                        NS=NS,
                        MS=MS,
                        SS_SAA=SS_SAA,
                        Graphs_sample_save_directory=graphs_sample_save_directory,
                        Graphs_cluster_save_directory=graphs_cluster_save_directory,
                        Input_file='input/data.xlsx',
                        Output_file='result.xlsx',
                        gurobi_opt=gurobi_opt
                    )
                    break
                except Exception as e:
                    attempt += 1
                    print(f"An error occurred while executing the solver with parameters: {e}")