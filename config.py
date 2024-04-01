# -*- coding: utf-8 -*-
"""
Configuration and data reading method for the two-stage SP model
"""
# 不推荐修改参数，修改需要调整输入数据的维度结构等信息
AS = 3  # 物资种类
LS = 3  # 仓库种类
n_clusters = 10
Water = 1
Food = 0.25
Medicine = 0.125

# 相关方法配置参数，相关方法均可自由修改和调用
# 数据降维处理配置
# DATA_PROCESS_METHOD = 'factor_analysis'  # 可选 'pca', 'truncated_svd', 'factor_analysis', 'tsne', 'none'
DATA_PROCESS_PARAMS = {
    'pca': {'n_components': 0.99},
    'truncated_svd': {'n_components': 0.99}, 
    'factor_analysis': {'variance_ratio_threshold': 0.99}, 
    # 'tsne': {'n_components': 2, 'perplexity': 30.0, 'random_state': 0},  # t-SNE仅用于可视化降维，不推荐使用来进行聚类前降维
    'none': {}  # 不进行降维
}

# 聚类配置
# CLUSTER_METHOD = 'kmeans'  # 可选 'kmeans', 'spectral', 'optics', 'meanshift', 'gmm', 'dbscan', 'agglomerative', 'som'
CLUSTER_PARAMS = {
    'kmeans': {'n_clusters': n_clusters, 'init': 'k-means++', 'random_state': 0},
    'spectral': {'n_clusters': n_clusters, 'affinity': 'nearest_neighbors', 'n_neighbors': 10, 'random_state': 0},
    'optics': {'min_samples': 10, 'xi': 0.05, 'min_cluster_size': 0.1},
    'meanshift': {'bandwidth': None, 'bin_seeding': False, 'min_bin_freq': 1, 'cluster_all': True, 'n_jobs': None, 'max_iter': 300},
    'gmm': {'n_components': n_clusters, 'covariance_type': 'full', 'random_state': 0},
    'dbscan': {'eps': 0.5, 'min_samples': 2},
    'agglomerative': {'n_clusters': n_clusters, 'linkage': 'average'},
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
GRAPH_CONFIG = {
    '2d': {
        'method': 'tsne',
        'params': {
            'tsne': {'n_components': 2},
            'pca': {'n_components': 2}
        }
    },
    '3d': {
        'method': 'tsne',
        'params': {
            'tsne': {'n_components': 3},
            'pca': {'n_components': 3}
        }
    }
}
