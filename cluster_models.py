
def apply_kmeans_clustering(demand, n_clusters, init='k-means++', random_state=0):
    from sklearn.cluster import KMeans
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
    # 使用MeanShift算法进行聚类
    cluster = MeanShift(
        bandwidth=bandwidth, 
        bin_seeding=bin_seeding, 
        min_bin_freq=min_bin_freq, 
        cluster_all=cluster_all, 
        n_jobs=n_jobs, 
        max_iter=max_iter
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "MeanShift"

def apply_gaussian_mixture_clustering(demand, n_components, covariance_type='full', random_state=0):
    from sklearn.mixture import GaussianMixture
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
    # 使用DBSCAN算法进行聚类
    cluster = DBSCAN(
        eps=eps, 
        min_samples=min_samples
    ).fit(demand)
    # 返回聚类标签和聚类方法名称
    return cluster.labels_, "DBSCAN"

def apply_agglomerative_clustering(distance_matrix, n_clusters, linkage='average'):
    from sklearn.cluster import AgglomerativeClustering
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
    
    # 初始化并训练Self-Organizing Map(SOM)
    som = MiniSom(x=x, y=y, input_len=demand.shape[1], sigma=sigma, learning_rate=learning_rate)
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
    def __init__(self, method, params):
        self.method = method
        self.params = params

    def apply_clustering(self, demand):
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