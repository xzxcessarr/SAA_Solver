# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Graph Generate.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为算法过程图模块，请勿直接调用
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
from plugins import *
from config import *
from shapely.geometry import MultiPoint
from shapely.ops import unary_union, polygonize
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.collections import PatchCollection

def stratified_random_sampling(demand, cluster_labels, cluster_num, IS):
    sample = []
    standard = np.zeros(cluster_num)
    temp_num = np.zeros(cluster_num)

    for i in np.unique(cluster_labels):
        cluster_indices = np.where(cluster_labels == i)[0]
        demand_sample = demand[cluster_indices, :IS]  # Ensure slicing is within bounds
        
        # Calculate the mean and standard deviation
        mean_sample = np.mean(demand_sample, axis=0)
        std_dev = np.std(demand_sample, axis=0)
        
        # Store the standard deviation for this cluster
        standard[i] = np.mean(std_dev)  # Using mean of std deviations across scenarios
        temp_num[i] = standard[i] * len(cluster_indices)

    # Determine the number of samples to pick from each cluster
    for i in np.unique(cluster_labels):
        cluster_indices = np.where(cluster_labels == i)[0]
        if standard[i] == 0:
            continue  # Skip if standard deviation is zero
        proportion = standard[i] / np.sum(standard)
        pick_num = int(np.round(proportion * len(cluster_indices)))

        if pick_num > 0:
            sampled_indices = np.random.choice(cluster_indices, size=pick_num, replace=False)
            sample.extend(sampled_indices.tolist())
    
    return sample


# 绘制3D散点图
def plot_3d(demand_transformed, save_directory, script_name):
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(demand_transformed[:, 0], demand_transformed[:, 1], demand_transformed[:, 2], color='black')
    ax.set_title('3D Scatter Plot')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    ax.set_zlabel('Dimension 3')
    ax.view_init(elev=20., azim=45)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_path = os.path.join(save_directory, f'{script_name}_scatter_3D.jpg')
    plt.savefig(save_path, format='jpg')
    plt.close()

# 绘制2D散点图
def plot_2d(demand_transformed, save_directory, script_name):
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111)
    ax.scatter(demand_transformed[:, 0], demand_transformed[:, 1], color='black')
    ax.set_title('2D Scatter Plot')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_path = os.path.join(save_directory, f'{script_name}_scatter_2D.jpg')
    plt.savefig(save_path, format='jpg')
    plt.close()

# t-SNE仅用于可视化降维，不推荐使用来进行聚类前降维
def apply_tsne(demand, n_components=2, perplexity=30.0, random_state=0):
    from sklearn.manifold import TSNE
    """
    应用t-SNE进行降维。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组。
    n_components -- 降维后的维数。t-SNE通常用于将数据降至2维或3维以便可视化。
    perplexity -- t-SNE的复杂度参数，建议取值在5到50之间。默认为30。
    random_state -- 随机种子用于可重复性。默认为0。
    
    返回:
    tsne_result -- t-SNE降维后的数据。
    """
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state)
    tsne_demand = tsne.fit_transform(demand)
    return tsne_demand, n_components, "t-SNE"

def plot_clusters_2d(demand_transformed, cluster_labels, save_directory, script_name):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    
    # 根据聚类标签绘制散点图
    scatter = ax.scatter(demand_transformed[:, 0], demand_transformed[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6)
    
    # 为每个聚类绘制凹包
    labels = np.unique(cluster_labels)
    patches = []
    for label in labels:
        # 找到此聚类的所有点
        cluster_points = demand_transformed[cluster_labels == label]
        if len(cluster_points) > 2:  # 凹包至少需要三个点
            # 创建MultiPoint对象
            multi_point = MultiPoint(cluster_points)
            # 计算凹包
            concave_hull = multi_point.convex_hull  # 这里使用了凸包，你可以替换为更合适的凹包算法
            # 添加缓冲区，负值将收缩，正值将扩张
            buffered_hull = concave_hull.buffer(0.2)  # 缓冲区大小可以根据需要调整
            if buffered_hull.geom_type == 'Polygon':
                # 创建路径并添加到patches
                verts = np.array(buffered_hull.exterior.coords.xy).T
                codes = np.full(len(verts), Path.LINETO)
                codes[0] = Path.MOVETO
                codes[-1] = Path.CLOSEPOLY
                path = Path(verts, codes)
                patch = PathPatch(path, facecolor='none', edgecolor='black', lw=1.5)
                patches.append(patch)
    
    # 添加patches到axes
    for patch in patches:
        ax.add_patch(patch)
    
    ax.set_title('2D Clustering with K-means++')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    # plt.colorbar(scatter)
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_path = os.path.join(save_directory, f'{script_name}_cluster_2D.jpg')
    plt.savefig(save_path, format='jpg')
    plt.close()

def plot_sample_clusters_2d(demand_transformed, cluster_labels, demand, IS, save_directory, script_name):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    cluster_num = len(np.unique(cluster_labels))
    sample_indices = stratified_random_sampling(demand, cluster_labels, cluster_num, IS)
    
    # 绘制所有点和采样点
    scatter = ax.scatter(demand_transformed[:, 0], demand_transformed[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6)
    ax.scatter(demand_transformed[sample_indices, 0], demand_transformed[sample_indices, 1], c='red', s=50, marker='x', label='sample')
    
    # 添加有缓冲区的凸包
    patches = []
    for label in np.unique(cluster_labels):
        cluster_points = demand_transformed[cluster_labels == label]
        if len(cluster_points) > 2:  # 确保有足够的点来形成凸包
            multi_point = MultiPoint(cluster_points)
            convex_hull = multi_point.convex_hull  # 计算凸包
            buffered_hull = convex_hull.buffer(0.2)  # 添加缓冲区

            # 从缓冲凸包创建 PathPatch
            if buffered_hull.geom_type == 'Polygon':
                verts = np.array(buffered_hull.exterior.coords.xy).T
                codes = np.full(len(verts), Path.LINETO)
                codes[0] = Path.MOVETO
                codes[-1] = Path.CLOSEPOLY
                path = Path(verts, codes)
                patch = PathPatch(path, facecolor='none', edgecolor='black', lw=1.5)
                patches.append(patch)

    # 将 patches 添加到 axes 上
    for patch in patches:
        ax.add_patch(patch)

    ax.set_title('2D Clustering with K-means++')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    ax.legend()

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_path = os.path.join(save_directory, f'{script_name}_cluster_2D.jpg')
    plt.savefig(save_path, format='jpg')
    plt.close()


Input_file = 'data/raw_data.xlsx'

CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data(Input_file, 40, 100, AS, Food_index, Medicine_index, True)

# 降维到3维
demand_transformed_3d, _, _ = apply_tsne(demand, n_components=3)
plot_3d(demand_transformed_3d, "graph", "script_name_3D")

# 降维到2维
demand_transformed_2d, _, _ = apply_tsne(demand, n_components=2)
plot_2d(demand_transformed_2d, "graph", "script_name_2D")

# K-means++ 聚类
kmeans = KMeans(n_clusters=5, init='k-means++')
cluster_labels = kmeans.fit_predict(demand_transformed_2d)

plot_clusters_2d(demand_transformed_2d, cluster_labels, "graph", "cluster_2D")
plot_sample_clusters_2d(demand_transformed_2d, cluster_labels, demand, 40,  "graph", "sample_2D")


