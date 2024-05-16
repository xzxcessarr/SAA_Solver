# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Sampling.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为抽样模块，使用面向对象的类创建方式调用
"""

import numpy as np

# # 需要的输入数据
# demand = ...  # 需求数据，假设是一个NumPy数组
# cluster_labels = ...  # KMeans聚类的结果标签数组
# cluster_num = ...  # 分层抽样的层数
# IS = ...  # 需求数据的维度

# # 分层随机抽样
# stratified_sample_indices = stratified_random_sampling(demand, cluster_labels, cluster_num, IS)

# # 简单随机抽样
# simple_sample_indices = simple_random_sampling(cluster_labels)

# # 基于抽样索引获取需求数据样本
# stratified_demand_sample = demand[stratified_sample_indices, :]
# simple_demand_sample = demand[simple_sample_indices, :]

def stratified_random_sampling(demand, cluster_labels, cluster_num, IS):
    """
    分层随机抽样方法。
    
    参数：
        demand (ndarray): 包含需求数据的数组。
        cluster_labels (ndarray): 每个数据点对应的聚类标签。
        cluster_num (int): 聚类的数量。
        IS (int): 样本中具体需求的数量。

    返回：
        sample (list): 抽取的样本索引列表。
        "Stratified" (str): 表示使用的抽样方法。
    """
    #Stratified random sampling
    sample = []

    standard = np.zeros((cluster_num, 1))
    temp_num = np.zeros((cluster_num, 1))
    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        demand_sample = np.zeros((len(cluster_each), IS))
        for s in range(len(cluster_each)):
            for j in range(IS):
                demand_sample[s, j] = demand[int(cluster_each[s]), j]
        # determine scenario number for each sample by standard deviation
        mean_sample = np.mean(demand_sample, axis=0)
        temp_std = 0
        # calculate standard deviation
        standard[i] = np.sqrt(sum(sum(np.square(demand_sample - mean_sample.T))) / len(cluster_each))
        temp_num[i] = standard[i] * len(cluster_each)

    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        pick_num = np.rint(cluster_num * len(cluster_each) * standard[i] / sum(temp_num))
        pick_num = pick_num.astype(np.int32)[0]

        if pick_num == 0:
            continue
        elif pick_num == 1:
            temp = np.random.choice(len(cluster_each), 1, replace=False)
            sample.append(cluster_each[temp[0]])
        else:
            temp = np.random.choice(len(cluster_each), pick_num, replace=False)
            for j in range(pick_num):
                sample.append(cluster_each[temp[j]])
    return sample, "Stratified"
    
def simple_random_sampling(cluster_labels):
    """
    简单随机抽样方法。

    参数：
        cluster_labels (ndarray): 每个数据点对应的聚类标签。

    返回：
        sample (list): 抽取的样本索引列表。
        "Simple" (str): 表示使用的抽样方法。
    """
    # randomly select one from each group
    sample = []
    
    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        temp = np.random.choice(len(cluster_each), 1, replace=False)
        sample.append(cluster_each[temp[0]]) 
    return sample, "Simple"

class SampleGenerator:
    """
    功能: 根据指定的抽样方法和参数应用抽样。
    方法:
    __init__(method, params): 初始化。
    apply_reduction(demand): 应用降维。
    """
    def __init__(self, method, params):
        """
        样本生成器类，负责根据指定的抽样方法和参数生成样本。

        参数：
            method (str): 抽样方法名称，例如 "Simple" 或 "Stratified"。
            params (dict): 用于抽样方法的参数。
        """
        self.method = method
        self.params = params

    def generate(self, data, labels, cluster_num):
        """
        生成样本。

        参数：
            data (ndarray): 包含数据的数组。
            labels (ndarray): 数据点的聚类标签。
            cluster_num (int): 聚类的数量。

        返回：
            根据指定抽样方法生成的样本。
        """
        if self.method == 'Simple':
            return simple_random_sampling(labels)
        elif self.method == 'Stratified':
            return stratified_random_sampling(data, labels, cluster_num, **self.params)
        else:
            raise ValueError('未知的样本生成方法: {}'.format(self.method))