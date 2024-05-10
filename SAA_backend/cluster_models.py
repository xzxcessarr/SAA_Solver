# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Clustering.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为聚类算法模块，使用面向对象的类创建方式调用
"""
def apply_kmeans_clustering(demand, n_clusters, init='k-means++', random_state=0):
    from sklearn.cluster import KMeans
    """
    参数:
    demand: 数据集。
    n_clusters: 聚类数目。
    init: 初始化方法，默认是 'k-means++'。
    random_state: 随机种子。
    返回:
    聚类标签。
    使用的聚类方法名称。
    """
    # 使用KMeans算法进行聚类
    cluster = KMeans(
        n_clusters=n_clusters, 
        init=init, 
        random_state=random_state
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "kmeans++"

def apply_spectral_clustering(demand, n_clusters, affinity='nearest_neighbors', n_neighbors=10, random_state=0):
    from sklearn.cluster import SpectralClustering
    """
    参数:
    demand: 数据集。
    n_clusters: 聚类数目。
    affinity: 亲和力类型，默认是 'nearest_neighbors'。
    n_neighbors: 邻居数，默认为10。
    random_state: 随机种子。
    返回:
    聚类标签。
    使用的聚类方法名称。
    """
    # 使用SpectralClustering算法进行聚类
    cluster = SpectralClustering(
        n_clusters=n_clusters, 
        affinity=affinity, 
        n_neighbors=n_neighbors, 
        random_state=random_state
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "Spectral"

def apply_optics_clustering(demand, min_samples=10, xi=0.05, min_cluster_size=0.1):
    from sklearn.cluster import OPTICS
    """
    参数:
    demand: 数据集。
    min_samples: 最小样本数。
    xi: 簇的稳定性参数。
    min_cluster_size: 最小簇大小。
    返回:
    聚类标签。
    使用的聚类方法名称。 
    """
    # 使用OPTICS算法进行聚类
    cluster = OPTICS(
        min_samples=min_samples, 
        xi=xi, 
        min_cluster_size=min_cluster_size
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "OPTICS"
 
def apply_meanshift_clustering(demand, bandwidth=None, bin_seeding=False, min_bin_freq=1, cluster_all=True, n_jobs=None, max_iter=300):
    from sklearn.cluster import MeanShift
    """
    使用MeanShift算法对数据进行聚类分析。
    
    参数:
    - demand: ndarray, 形状为 (n_samples, n_features)，聚类的输入数据。
    - bandwidth: float, 窗口大小，影响聚类的粒度。默认为 None，此时算法会尝试自动估计。
    - bin_seeding: bool, 是否使用更快的并且对内存友好的二进制近似。默认为 False。
    - min_bin_freq: int, 最小箱频率，用于过滤稀疏的箱。默认为 1。
    - cluster_all: bool, 是否将所有点都包括在聚类中，即使它们不属于任何簇。默认为 True。
    - n_jobs: int, 并行任务数。默认为 None，表示使用一个核心。
    - max_iter: int, 算法的最大迭代次数。默认为 300。

    返回:
    - labels: ndarray, 形状为 (n_samples,)，每个样本的聚类标签。
    - "MeanShift": 返回使用的聚类方法名称。
    """
    
    # 实例化MeanShift对象
    cluster = MeanShift(
        bandwidth=bandwidth, 
        bin_seeding=bin_seeding, 
        min_bin_freq=min_bin_freq, 
        cluster_all=cluster_all, 
        n_jobs=n_jobs, 
        max_iter=max_iter
    )
    
    # 应用MeanShift算法
    cluster.fit(demand)
    
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "MeanShift"

def apply_gaussian_mixture_clustering(demand, n_components, covariance_type='full', random_state=0):
    from sklearn.mixture import GaussianMixture
    """
    参数:
    demand: 数据集。
    n_components: 组件数目。
    covariance_type: 协方差类型。
    random_state: 随机种子。
    返回:
    聚类标签。
    使用的聚类方法名称。
    """
    # 使用GaussianMixture算法进行聚类
    gmm = GaussianMixture(
        n_components=n_components, 
        covariance_type=covariance_type, 
        random_state=random_state
    ).fit(demand)
    # 使用predict方法确定聚类标签
    cluster_labels = gmm.predict(demand)
    # 返回聚类标签和聚类方法名称
    return cluster_labels, "GMM"

def apply_dbscan_clustering(demand, min_samples=5, eps=0.1):
    from sklearn.cluster import DBSCAN
    """
    参数:
    demand: 数据集。
    min_samples: 最小样本数。
    eps: 邻域半径。
    返回:
    聚类标签。
    使用的聚类方法名称。
    """
    # 使用DBSCAN算法进行聚类
    cluster = DBSCAN(
        eps=eps, 
        min_samples=min_samples
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "DBSCAN"

def apply_agglomerative_clustering(distance_matrix, n_clusters, linkage='average'):
    from sklearn.cluster import AgglomerativeClustering
    """
    参数:
    distance_matrix: 距离矩阵。
    n_clusters: 聚类数目。
    linkage: 链接方式。
    返回:
    聚类标签。
    使用的聚类方法名称。
    """
    # 使用AgglomerativeClustering算法进行聚类
    cluster = AgglomerativeClustering(
        n_clusters=n_clusters, 
        linkage=linkage
    ).fit(distance_matrix)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "Agglomerative"

def apply_som_clustering(demand, x=5, y=3, sigma=0.7, learning_rate=0.5, num_iteration=1000):
    from minisom import MiniSom
    import numpy as np
    
    """
    x (int): 网格宽度，即 SOM 的 X 维度。
    y (int): 网格高度，即 SOM 的 Y 维度。
    input_len (int): 输入向量的维数。
    sigma (float, optional): 高斯函数的标准差，用于调整邻域函数的范围，通常设置为网格大小的一部分。
    learning_rate (float, optional): 学习速率，用于在学习过程中更新权重。
    decay_function (callable, optional): 随着时间变化调整学习速率和邻域函数的函数。
    neighborhood_function (str, optional): 邻域函数的类型，通常是 'gaussian' 或 'mexican_hat'。
    topology (str, optional): 网格的拓扑结构，可以是 'rectangular' 或 'hexagonal'。
    activation_distance (str, optional): 计算激活距离的方法，通常是 'euclidean' 或 'cosine'。
    random_seed (int, optional): 随机数生成器的种子，用于复现结果。
    """

    # 初始化并训练Self-Organizing Map(SOM)
    som = MiniSom(x=x, y=y, input_len=demand.shape[1], sigma=sigma, learning_rate=learning_rate)
    som.random_weights_init(data=demand)
    som.train_random(data=demand, num_iteration=num_iteration)

    # 获取每个样本的获胜神经元
    winning_neurons = np.array([som.winner(x) for x in demand])

    # 为每个唯一的获胜神经元分配一个标签
    neuron_labels = {tuple(neuron): i for i, neuron in enumerate(np.unique(winning_neurons, axis=0))}

    # 为每个样本分配聚类标签
    cluster_labels = np.array([neuron_labels[tuple(winner)] for winner in winning_neurons])

    # 返回SOM聚类标签
    return cluster_labels, "SOM"

class ClusteringMethod:
    """
    功能: 根据指定的聚类方法和参数应用聚类算法。
    方法:
    __init__(method, params): 初始化。
    apply_clustering(demand): 应用聚类算法。
    """
    def __init__(self, method, params):
        """
        初始化聚类方法实例。

        参数：
            method (str): 聚类方法名称。
            params (dict): 用于聚类方法的参数。
        """
        self.method = method
        self.params = params

    def apply_clustering(self, demand):
        """
        应用聚类算法。

        参数：
            demand (ndarray): 需要进行聚类的数据。

        返回：
            聚类结果，具体类型和内容依赖于具体聚类算法。
        """
        if self.method == 'kmeans':
            return apply_kmeans_clustering(demand, **self.params)
        elif self.method == 'spectral':
            return apply_spectral_clustering(demand, **self.params)
        elif self.method == 'optics':
            return apply_optics_clustering(demand, **self.params)
        elif self.method == 'meanshift':
            return apply_meanshift_clustering(demand, **self.params)
        elif self.method == 'gmm':
            return apply_gaussian_mixture_clustering(demand, **self.params)
        elif self.method == 'dbscan':
            return apply_dbscan_clustering(demand, **self.params)
        elif self.method == 'agglomerative':
            return apply_agglomerative_clustering(demand, **self.params)
        elif self.method == 'som':
            return apply_som_clustering(demand, **self.params)
        else:
            raise ValueError('未知的聚类方法: {}'.format(self.method))