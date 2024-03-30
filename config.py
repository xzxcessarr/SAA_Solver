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
Food = 0.25
Medicine = 0.125
Input_file = 'input/data.xlsx'
Output_file = 'result.xlsx'
Graphs_sample_save_directory = "./Graphs"
data_preprocess_methods="PCA"
cluster_methods="kmeans++"
sample_methods="Stratified"






