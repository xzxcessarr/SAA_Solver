# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Default Params.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为算法默认参数
"""
# 不推荐修改参数，修改需要调整输入数据的维度结构等信息
AS = 3  # 物资种类
LS = 3  # 仓库种类
Water_index = 1
Food_index = 0.25
Medicine_index = 0.125
variance_ratio = 0.99

"""
Configuration and data reading method for the two-stage SP model
以下是对论文中降维方法和聚类方法的一些关键观点和潜在的考虑事项说明：

降维方法:

1. PCA (Principal Component Analysis):
   - 通常用于稠密数据集的主成分分析。
   - n_components 参数设置为保留的主成分数量或保留的方差比例，使用方差比例来自动选择成分数量。

2. Truncated SVD:
   - 适用于稀疏数据集，首先使用较大的 n_components 拟合 SVD，然后根据累积方差选择成分数量。

3. Factor Analysis:
   - 用于探索数据中的潜在变量，适用于稠密数据集，但通常会根据模型拟合度和解释性来选择因子数量。

4. t-SNE:
   - 主要用于数据可视化，不推荐用于聚类前的降维，因为可能会过度扭曲数据结构。

聚类方法:

1. KMeans:
   - 经典聚类算法，适用于稠密数据集，init='k-means++' 和 random_state=0 有助于结果的稳定性和重现性。

2. Spectral Clustering:
   - 适用于寻找非凸形状或大小不均的聚类，适用于稠密数据。

3. OPTICS:
   - 适用于捕捉不同密度的聚类，适用于稠密和稀疏数据。

4. MeanShift:
   - 不需要指定聚类数量，适用于稠密数据。

5. Gaussian Mixture (GMM):
   - 基于概率的聚类，适用于稠密数据。

6. DBSCAN:
   - 适用于捕捉任意形状的聚类，适用于稠密和稀疏数据。

7. Agglomerative Clustering:
   - 层次聚类算法，适用于稠密数据集。

8. Self-Organizing Map (SOM):
   - SOM 是一种神经网络算法，适用于可视化较高维度的数据。

请注意，选择哪种方法和参数配置，需要根据数据集的特性和聚类任务的需求进行细致调整。
"""

# 相关方法配置参数，相关方法均可自由修改和调用
# 数据降维处理配置
# DATA_PROCESS_METHOD = 'factor_analysis'  # 可选 'pca', 'truncated_svd', 'factor_analysis', 'tsne', 'none'
DATA_PROCESS_PARAMS = {
    'pca': {'n_components': variance_ratio},
    'truncated_svd': {'n_components': variance_ratio}, 
    'factor_analysis': {'variance_ratio_threshold': variance_ratio}, 
    # 'tsne': {'n_components': 2, 'perplexity': 30.0, 'random_state': 0},  # t-SNE仅用于可视化降维，不推荐使用来进行聚类前降维
    'none': {}  # 不进行降维
}

# 聚类配置
# CLUSTER_METHOD = 'kmeans'  # 可选 'kmeans', 'spectral', 'optics', 'meanshift', 'gmm', 'dbscan', 'agglomerative', 'som'
CLUSTER_PARAMS = {
   'kmeans': {'n_clusters': 10, 'init': 'k-means++', 'random_state': 0},
   # 'spectral': {'n_clusters': 10, 'affinity': 'nearest_neighbors', 'n_neighbors': 10, 'random_state': 0},
   'spectral': {'n_clusters': 10, 'affinity': 'rbf', 'gamma': 1.0, 'random_state':0},
   'gmm': {'n_components': 10, 'covariance_type': 'full', 'random_state': 0},
   'agglomerative': {'n_clusters': 10, 'linkage': 'average'},

   'optics': {'min_samples': 10, 'xi': 0.05, 'min_cluster_size': 0.1},
   'meanshift': {'bandwidth': None, 'bin_seeding': False, 'min_bin_freq': 1, 'cluster_all': True, 'n_jobs': None, 'max_iter': 300},
   'dbscan': {'eps': 0.5, 'min_samples': 2},
   
   'som': {'x': 5, 'y': 3, 'sigma': 0.7, 'learning_rate': 0.5, 'num_iteration': 1000},
}

# 抽样配置
# SAMPLE_GENERATE_METHOD  = 'Stratified'  # 可选 'simple_random', 'stratified_random'
SAMPLE_GENERATE_PARAMS = {
    'Stratified': {}, 
    'Simple': {}
}

# 通用可视化配置
# GRAPH_METHOD = '2d'
GRAPH_PROCESS_METHOD = 'tsne'
GRAPH_CONFIG = {
    '2d': {
        'method': GRAPH_PROCESS_METHOD,
        'params': {
            'tsne': {'n_components': 2},
            'pca': {'n_components': 2}
        }
    },
    '3d': {
        'method': GRAPH_PROCESS_METHOD,
        'params': {
            'tsne': {'n_components': 3},
            'pca': {'n_components': 3}
        }
    }
}
