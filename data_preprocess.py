import numpy as np

def apply_pca(demand, n_components=0.99):
    from sklearn.decomposition import PCA
    """
    应用PCA进行降维，适用于稠密数据集。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组。
    n_components -- 保留的成分数或解释的方差比例。默认为0.95，即保留95%的方差。
    
    返回:
    pca_result -- PCA降维后的数据。
    """
    pca = PCA(n_components=n_components, svd_solver="auto")
    pca_demand = pca.fit_transform(demand)
    return pca_demand, pca.n_components_, "PCA"

def apply_truncated_svd(demand, n_components=0.99):
    from sklearn.decomposition import TruncatedSVD
    from scipy.sparse import csr_matrix
    """
    应用TruncatedSVD进行降维，适用于稀疏数据集，参考数据优先使用这个方法。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组或类似数组的数据结构。
    n_components -- 保留的方差比例。默认为0.99，即保留99%的方差。
    
    返回:
    svd_result -- TruncatedSVD降维后的数据。
    n_components -- 选择的成分数。
    """
    demand = csr_matrix(demand)

    if not 0 < n_components <= 1:
        raise ValueError("n_components must be a float in the range (0, 1].")
    
    # 初始化TruncatedSVD，这里我们先指定一个较大的n_components
    svd = TruncatedSVD(n_components=min(demand.shape)-1)
    svd.fit(demand)
    
    # 计算累积可解释方差
    cumulative_variance = np.cumsum(svd.explained_variance_ratio_)
    # 找到超过阈值的成分数
    n_components_selected = np.argmax(cumulative_variance >= n_components) + 1
    
    # 使用找到的成分数重新拟合TruncatedSVD
    svd = TruncatedSVD(n_components=n_components_selected)
    svd_demand = svd.fit_transform(demand)
    
    return svd_demand, n_components_selected, "SVD"

def apply_factor_analysis(demand, variance_ratio_threshold=0.99):
    from sklearn.decomposition import PCA, FactorAnalysis
    """
    应用因子分析进行降维。
    
    参数:
    demand -- 待降维的数据，应为二维NumPy数组或类似数组的数据结构。
    variance_ratio_threshold -- 保留的方差比例阈值，默认为0.99。
    
    返回:
    fa_result -- 因子分析降维后的数据。
    n_factors -- 选择的因子数。
    """
    # 使用PCA确定累计方差达到阈值所需的成分数
    pca = PCA().fit(demand)
    cumulative_variance_ratio = np.cumsum(pca.explained_variance_ratio_)
    n_factors = np.argmax(cumulative_variance_ratio >= variance_ratio_threshold) + 1
    
    # 初始化因子分析对象，使用确定的因子数
    fa = FactorAnalysis(n_components=n_factors)
    
    # 对数据进行拟合与降维
    fa.fit(demand)
    fa_result = fa.transform(demand)
    
    return fa_result, n_factors, "Factor"

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

class DataProcessor:
    def __init__(self, method, params):
        self.method = method
        self.params = params

    def apply_reduction(self, demand):
        if self.method == 'pca':
            return apply_pca(demand, **self.params)
        elif self.method == 'truncated_svd':
            return apply_truncated_svd(demand, **self.params)
        elif self.method == 'factor_analysis':
            return apply_factor_analysis(demand, **self.params)
        elif self.method == 'tsne':
            return apply_tsne(demand, **self.params)
        elif self.method == 'none':
            return demand, -1, "Original"
        else:
            raise ValueError(f'未知的降维方法: {self.method}')
            
