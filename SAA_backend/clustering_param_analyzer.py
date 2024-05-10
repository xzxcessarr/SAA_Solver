# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Analyze Clustering Params.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为聚类算法参数分析模块，目前还在测试之中，请勿直接调用
"""

import numpy as np
from sklearn.cluster import KMeans, SpectralClustering, OPTICS, MeanShift, DBSCAN, AgglomerativeClustering, estimate_bandwidth
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.model_selection import GridSearchCV
from data_preprocess import DataProcessor
from plugins import read_data
import logging

def analyze_clustering_params(cluster_method, IS, NS, AS, Food_index, Medicine_index, Raw_data_flag, Input_file, cluster_params, log_filename, data_processor_method, variance_ratio):
    
    # 配置日志以追加模式
    logging.info("开始分析聚类参数")
    logging.info(f"聚类方法: {cluster_method}, 城市数量: {IS}, 场景数量: {NS}, 物资种类数量: {AS}, 食物指数: {Food_index}, 药品指数: {Medicine_index}, 是否使用原始数据: {Raw_data_flag}, 输入文件: {Input_file}, 数据处理方法: {data_processor_method}, 解释的方差比例: {variance_ratio}")

    # 读取数据
    CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data(Input_file, IS, NS, AS, Food_index, Medicine_index, Raw_data_flag)

    # 数据处理参数
    DATA_PROCESS_PARAMS = {
        'pca': {'n_components': variance_ratio},
        'truncated_svd': {'n_components': variance_ratio}, 
        'factor_analysis': {'variance_ratio_threshold': variance_ratio}, 
        'none': {}  # 不进行降维
    }

    # 数据处理对象实例化
    data_processor = DataProcessor(data_processor_method, DATA_PROCESS_PARAMS[data_processor_method])
    demand_processed, _, _ = data_processor.apply_reduction(demand)

    # 初始化返回的参数字典
    best_params = {}
    best_params_range = {}

    if cluster_method in ['kmeans', 'spectral', 'gmm', 'agglomerative']:
        # 使用肘部法和聚类评估指标确定最佳聚类数
        max_clusters = min(50, demand_processed.shape[0] // 2)  # 确保聚类数不超过样本数的一半
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1): 
            if cluster_method == 'kmeans':
                clusterer = KMeans(n_clusters=k, random_state=42)
            elif cluster_method == 'spectral':
                clusterer = SpectralClustering(n_clusters=k, random_state=42)
            elif cluster_method == 'gmm':
                clusterer = GaussianMixture(n_components=k, random_state=42)
            else:  # 'agglomerative'
                clusterer = AgglomerativeClustering(n_clusters=k)

            cluster_labels = clusterer.fit_predict(demand_processed)
            
            silhouette_scores.append(silhouette_score(demand_processed, cluster_labels))
        
        # 使用轮廓系数选择最佳聚类数
        best_k = np.argmax(silhouette_scores) + 2
        
        best_params = {'n_clusters': int(best_k)}
        best_params_range = {'n_clusters': f'{max(2, best_k - 2)} ~ {min(max_clusters, best_k + 2)}'}
        logging.info(f"最优聚类数: {best_k}, 推荐聚类数范围: {best_params_range['n_clusters']}")

    elif cluster_method in ['optics', 'dbscan']:
        # 使用网格搜索和轮廓系数确定最佳参数
        if cluster_method == 'optics':
            param_grid = {
                'min_samples': [2, 5, 10], 
                'max_eps': [np.inf, 0.5, 1.0], 
                'cluster_method': ['xi', 'dbscan'],
                'xi': [0.01, 0.05, 0.1], 
                'min_cluster_size': [2, 5, 10]
            }
            clusterer = OPTICS()
            
        else:  # 'dbscan'
            param_grid = {
                'eps': [0.1, 0.5, 1.0], 
                'min_samples': [2, 5, 10]
            }
            clusterer = DBSCAN()

        grid_search = GridSearchCV(clusterer, param_grid, scoring='silhouette')
        grid_search.fit(demand_processed)
        best_params = {k: int(v) if isinstance(v, np.generic) else v for k, v in grid_search.best_params_.items()}
        
        for param, value in best_params.items():
            if param == 'bandwidth' and value is None:
                best_params_range[param] = 'None'
            else:
                param_range = param_grid[param]
                best_index = param_range.index(value)
                lower_bound = param_range[max(0, best_index - 1)]
                upper_bound = param_range[min(len(param_range) - 1, best_index + 1)]
                best_params_range[param] = f'{lower_bound} ~ {upper_bound}'

        logging.info(f"最优参数: {best_params}, 推荐参数范围: {best_params_range}")

    elif cluster_method == 'meanshift':
        # MeanShift 的 bandwidth 参数可能需要根据数据动态选择
        # 计算 bandwidth 的推荐范围
        bandwidths = []
        quantiles = [0.1, 0.2, 0.3, 0.4, 0.5]
        for quantile in quantiles:
            bandwidth = estimate_bandwidth(demand_processed, quantile=quantile)
            if bandwidth is not None:
                bandwidths.append(bandwidth)
        
        # 如果 bandwidths 列表为空或只有一个元素,则使用默认值
        if len(bandwidths) < 2:
            bandwidths = [0.1, 0.5, 1.0]  # 或其他默认值

        # 使用轮廓系数评估
        best_score = -1
        best_bandwidth = None
        for bandwidth in bandwidths:
            clusterer = MeanShift(bandwidth=bandwidth)
            cluster_labels = clusterer.fit_predict(demand_processed)
            if len(set(cluster_labels)) > 1:  # 检查是否至少有两个聚类
                score = silhouette_score(demand_processed, cluster_labels)
                if score > best_score:
                    best_score = score
                    best_bandwidth = bandwidth

        # 生成 bandwidth 的推荐范围
        best_params['bandwidth'] = best_bandwidth
        best_params_range['bandwidth'] = f'{min(bandwidths)} ~ {max(bandwidths)}'
        logging.info(f"MeanShift 最优 bandwidth: {best_bandwidth}, 推荐范围: {best_params_range['bandwidth']}")

    else:  # 'som'
        # SOM 没有通用的最优参数选择方法,使用当前配置的参数
        best_params = {k: int(v) if isinstance(v, np.generic) else v for k, v in cluster_params.items()}
        best_params_range = {param: f'{value}' for param, value in cluster_params.items()}
        
    return best_params, best_params_range