# -*- coding: utf-8 -*-
"""
Configuration and data reading method for the two-stage SP model
"""
# Parameters
IS = 20  # Set of locations
AS = 3  # Set of item types
LS = 3  # Set of size categories
NS = 100  # Scenario样本总量
SS_SAA = 10  # Scenario number of samples单个样本容量
MS = 10  # Sample number样本数量
Water = 1
Food = Water/4
Medicine = Water/8
Input_file = 'input/data.xlsx'
Output_file = 'result.xlsx'
Graphs_sample_save_directory = "./Graphs"
data_preprocess="PCA"
cluster_methods="kmeans++"
sample_methods="Stratified"

# 使用下划线连接各部分构建script_name，如果data_preprocess不为空则包含它
if data_preprocess:
    script_name = f"{data_preprocess}_{cluster_methods}_{sample_methods}"
else:
    script_name = f"{cluster_methods}_{sample_methods}"




